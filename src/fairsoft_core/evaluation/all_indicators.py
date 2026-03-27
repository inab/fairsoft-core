from typing import Any

from fairsoft_core.exceptions import (
    FairScoreComputationError,
    IndicatorComputationError,
    InstanceCreationError,
)
from fairsoft_core.feedback.feedback import get_feedback
from fairsoft_core.indicators.computation import IndicatorComputation
from fairsoft_core.models.instance import Instance
from fairsoft_core.scoring.fair_scores import compute_fair_scores


def run_fairsoft_evaluation(tool_metadata: dict[str, Any]) -> dict[str, Any]:
    try:
        instance = Instance(**tool_metadata)
    except Exception as e:
        raise InstanceCreationError(str(e)) from e

    try:
        computation = IndicatorComputation(instance)
        computation.compute_indicators()
    except Exception as e:
        raise IndicatorComputationError(str(e)) from e

    try:
        result = compute_fair_scores(instance)
        logs = vars(instance.logs)
        feedback = get_feedback(result)
    except Exception as e:
        raise FairScoreComputationError(str(e)) from e

    return {
        "result": result,
        "logs": logs,
        "feedback": feedback,
    }
