from typing import List
from langchain.tools import BaseTool

from .jd_generator import JDGeneratorTool
from .timeline_estimator import TimelineEstimatorTool
from .salary_benchmark import SalaryBenchmarkTool
from .offer_letter_generator import OfferLetterGeneratorTool


def get_all_tools() -> List[BaseTool]:
    """Get all available HR tools."""
    return [
        JDGeneratorTool(),
        TimelineEstimatorTool(),
        SalaryBenchmarkTool(),
        OfferLetterGeneratorTool(),
    ]


__all__ = [
    "JDGeneratorTool",
    "TimelineEstimatorTool", 
    "SalaryBenchmarkTool",
    "OfferLetterGeneratorTool",
    "get_all_tools",
]