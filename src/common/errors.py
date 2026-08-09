class PipelineError(RuntimeError):
    """流水线步骤执行失败。"""


class OCRFatalError(PipelineError):
    """OCR 识别失败，必须立即停止整个程序。"""
