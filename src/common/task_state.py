import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional


PENDING = "未完成"
RUNNING = "进行中"
COMPLETED = "已完成"
FAILED = "失败"


class TaskStateDB:
    """按批次保存流水线步骤状态：一个 batch_name 一行，一个步骤一个字段。"""

    def __init__(self, db_path: str, pipeline_names: Iterable[str]):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.pipeline_names = tuple(pipeline_names)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _quote_identifier(name: str) -> str:
        if not name.replace("_", "").isalnum():
            raise ValueError(f"非法字段名：{name}")
        return f'"{name}"'

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS batch_tasks (
                    batch_name TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    overall_status TEXT NOT NULL DEFAULT '未完成',
                    error_step TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            existing = {
                row["name"] for row in conn.execute("PRAGMA table_info(batch_tasks)")
            }
            for pipeline_name in self.pipeline_names:
                if pipeline_name not in existing:
                    column = self._quote_identifier(pipeline_name)
                    conn.execute(
                        f"ALTER TABLE batch_tasks ADD COLUMN {column} "
                        "TEXT NOT NULL DEFAULT '未完成'"
                    )
            conn.commit()

    def ensure_batch(self, batch_name: str, project_name: str) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO batch_tasks (
                    batch_name, project_name, overall_status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(batch_name) DO UPDATE SET
                    project_name = excluded.project_name,
                    updated_at = excluded.updated_at
            """, (batch_name, project_name, PENDING, now, now))
            conn.commit()

    def get_step_status(self, batch_name: str, pipeline_name: str) -> str:
        column = self._quote_identifier(pipeline_name)
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT {column} FROM batch_tasks WHERE batch_name = ?",
                (batch_name,),
            ).fetchone()
        if row is None:
            raise KeyError(f"批次不存在：{batch_name}")
        return row[pipeline_name]

    def is_completed(self, batch_name: str, pipeline_name: str) -> bool:
        return self.get_step_status(batch_name, pipeline_name) == COMPLETED

    def set_step_status(
        self,
        batch_name: str,
        pipeline_name: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        if status not in {PENDING, RUNNING, COMPLETED, FAILED}:
            raise ValueError(f"不支持的任务状态：{status}")

        column = self._quote_identifier(pipeline_name)
        now = datetime.now().isoformat(timespec="seconds")
        error_step = pipeline_name if status == FAILED else None
        overall_status = FAILED if status == FAILED else RUNNING

        with self._connect() as conn:
            conn.execute(
                f"""
                UPDATE batch_tasks
                SET {column} = ?, overall_status = ?, error_step = ?,
                    error_message = ?, updated_at = ?
                WHERE batch_name = ?
                """,
                (status, overall_status, error_step, error_message, now, batch_name),
            )
            conn.commit()

    def mark_batch_completed(self, batch_name: str) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute("""
                UPDATE batch_tasks
                SET overall_status = ?, error_step = NULL, error_message = NULL,
                    updated_at = ?
                WHERE batch_name = ?
            """, (COMPLETED, now, batch_name))
            conn.commit()

    def get_batch(self, batch_name: str) -> Dict[str, str]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM batch_tasks WHERE batch_name = ?", (batch_name,)
            ).fetchone()
        if row is None:
            raise KeyError(f"批次不存在：{batch_name}")
        return dict(row)

    def reset_from(self, batch_name: str, pipeline_name: str) -> None:
        """将指定步骤及后续步骤重置为未完成，便于重新运行。"""
        try:
            start = self.pipeline_names.index(pipeline_name)
        except ValueError as exc:
            raise KeyError(f"未知步骤：{pipeline_name}") from exc

        assignments = []
        values = []
        for name in self.pipeline_names[start:]:
            assignments.append(f"{self._quote_identifier(name)} = ?")
            values.append(PENDING)
        assignments.extend([
            "overall_status = ?", "error_step = NULL", "error_message = NULL",
            "updated_at = ?",
        ])
        values.extend([PENDING, datetime.now().isoformat(timespec="seconds"), batch_name])

        with self._connect() as conn:
            conn.execute(
                f"UPDATE batch_tasks SET {', '.join(assignments)} WHERE batch_name = ?",
                values,
            )
            conn.commit()
