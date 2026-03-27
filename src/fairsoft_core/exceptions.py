class FairsoftError(Exception):
    """Base exception for fairsoft-core."""


class InstanceCreationError(FairsoftError):
    """Raised when Instance construction fails."""


class IndicatorComputationError(FairsoftError):
    """Raised when indicator computation fails."""


class FairScoreComputationError(FairsoftError):
    """Raised when score computation or feedback generation fails."""
