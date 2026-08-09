import importlib.util
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Tuple

from common.task_state import COMPLETED, FAILED, RUNNING, TaskStateDB


@dataclass(frozen=True)
class PipelineStep:
    name: str
    filename: str
    entrypoint: str
    args: Tuple[str, ...]


class PipelineRunner:
    def __init__(self, config, steps: List[PipelineStep], logger):
        self.config = config
        self.steps = steps
        self.logger = logger
        self.root = Path(__file__).resolve().parent.parent
        self.state = TaskStateDB(
            config.paths["state_db"], [step.name for step in steps]
        )
        self.state.ensure_batch(config.batch_name, config.project_name)

    def _load_callable(self, step: PipelineStep) -> Callable:
        module_path = self.root / "pipelines" / step.filename
        if not module_path.exists():
            raise FileNotFoundError(f"步骤脚本不存在：{module_path}")

        module_name = f"pipeline_{step.name}"
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"无法加载步骤脚本：{module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        func = getattr(module, step.entrypoint, None)
        if not callable(func):
            raise AttributeError(
                f"{step.filename} 中不存在可调用函数 {step.entrypoint}"
            )
        return func

    def _resolve_args(self, step: PipelineStep):
        values = []
        for key in step.args:
            if key in self.config.paths:
                values.append(self.config.paths[key])
            elif key in self.config.ocr:
                values.append(self.config.ocr[key])
            else:
                raise KeyError(f"步骤 {step.name} 引用了未知配置项：{key}")
        return values

    @staticmethod
    def show_error(title: str, message: str) -> None:
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(title, message)
            root.destroy()
        except Exception:
            # 无图形环境时仍通过控制台和日志反馈。
            pass

    def run(self) -> None:
        """
        按照 self.steps 中定义的顺序串行执行全部步骤。

        执行规则：
        1. 每个步骤执行前检查 SQLite 状态；
        2. 如果已经完成，则跳过；
        3. 如果未完成、失败或进行中，则重新执行；
        4. 执行前将状态更新为“进行中”；
        5. 当前步骤完整执行结束后，更新为“已完成”；
        6. 当前步骤完成后，才会进入下一个步骤；
        7. 任意步骤出现异常，更新为“失败”，弹窗并退出程序。
        """

        batch_name = self.config.batch_name

        for step in self.steps:
            # 读取当前步骤状态
            current_status = self.state.get_step_status(
                batch_name,
                step.name,
            )

            # 已完成的步骤不再重复执行
            if current_status == COMPLETED:
                self.logger.info(
                    "步骤已完成，跳过：%s",
                    step.name,
                )
                continue

            self.logger.info(
                "开始执行步骤：%s，原状态：%s",
                step.name,
                current_status,
            )

            # 开始执行前，先写入“进行中”
            self.state.set_step_status(
                batch_name,
                step.name,
                RUNNING,
            )

            try:
                # 动态加载当前步骤函数
                func = self._load_callable(step)

                # 获取当前步骤所需参数
                args = self._resolve_args(step)

                # 同步调用当前步骤
                # 只有这个函数完整返回后，才会继续执行下面的代码
                result = func(*args)

                # 约定：步骤函数主动返回 False，视为执行失败
                if result is False:
                    raise RuntimeError(
                        f"步骤 {step.name} 执行失败：返回值为 False"
                    )

            except Exception as exc:
                detail = "".join(
                    traceback.format_exception(
                        type(exc),
                        exc,
                        exc.__traceback__,
                    )
                )

                # 当前步骤写入“失败”
                self.state.set_step_status(
                    batch_name,
                    step.name,
                    FAILED,
                    str(exc),
                )

                self.logger.error(
                    "步骤执行失败：%s\n%s",
                    step.name,
                    detail,
                )

                self.show_error(
                    "数据处理失败",
                    (
                        f"批次：{batch_name}\n"
                        f"步骤：{step.name}\n"
                        f"错误：{exc}"
                    ),
                )

                # 任意步骤失败，立即终止整个流水线
                raise SystemExit(1) from exc

            else:
                # 只有当前步骤完整执行成功，才写入“已完成”
                self.state.set_step_status(
                    batch_name,
                    step.name,
                    COMPLETED,
                )

                self.logger.info(
                    "步骤已完成并写入状态：%s",
                    step.name,
                )

                # 此处结束后，for 循环才会进入下一个步骤

        # for 循环正常结束，说明所有步骤均已完成或已被跳过
        self.state.mark_batch_completed(
            batch_name
        )

        self.logger.info(
            "批次全部处理完成：%s",
            batch_name,
        )
