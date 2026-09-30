from pathlib import Path

from common.config import AppConfig
from common.logger import setup_logger
from common.pipeline_runner import PipelineRunner, PipelineStep


STEPS = [
    PipelineStep("check_pageimages", "0check_pageimages.py", "run", ("input_dir", "tif_dir", "pic_check_file")),
    PipelineStep("prepare_images", "1zhengliPics.py", "run", ("input_dir", "output_dir")),
    PipelineStep("ocr", "2thread_ocr.py", "scanbook", ("output_dir", "url", "error_file")),
    PipelineStep("repair_error_images", "4pic_save.py", "run", ("error_file",)),
    PipelineStep("count_chars", "6count_char_pic.py", "run", ("output_dir", "charnum_file")),
    PipelineStep("split_task", "7split_task.py", "run", ("output_dir","json_extract_dir","charnum_file","task_split_file",)),
    PipelineStep("copy_counterpart_page", "9copy_counterpart_page.py", "run", ("output_dir", "json_extract_dir")),
    PipelineStep("delete_old_images", "5deleteDirs.py", "run", ("output_dir",)),
]


def run():
    config_path = Path(__file__).resolve().parent / "setting.yaml"
    config = AppConfig(str(config_path))
    logger = setup_logger(config.paths["log_dir"])
    PipelineRunner(config, STEPS, logger).run()


if __name__ == "__main__":
    run()
