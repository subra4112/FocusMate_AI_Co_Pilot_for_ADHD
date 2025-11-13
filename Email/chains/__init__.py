"""LangChain chains for FocusMate."""

from .email_analysis import (
    EmailAnalysis,
    EmailAnalysisChain,
    build_email_analysis_chain,
)

__all__ = [
    "EmailAnalysis",
    "EmailAnalysisChain",
    "build_email_analysis_chain",
]
