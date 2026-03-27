from fairsoft_core.evaluation import run_fairsoft_evaluation
from importlib.metadata import version, PackageNotFoundError

__all__ = ["run_fairsoft_evaluation"]

try:
    __version__ = version("fairsoft-core")
except PackageNotFoundError:
    __version__ = "unknown"