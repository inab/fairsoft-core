import json
from importlib.resources import files


def load_feedback_rules() -> dict:
    feedback_file = files("fairsoft_core.feedback").joinpath("FAIR_indicators_feedback.json")
    return json.loads(feedback_file.read_text(encoding="utf-8"))


def get_feedback(result):
    # open FAIR_indicators_feedback
    feedback_per_indicator = load_feedback_rules()

    feedback = {
        "F": {"strengths": [], "improvements": []},
        "A": {"strengths": [], "improvements": []},
        "I": {"strengths": [], "improvements": []},
        "R": {"strengths": [], "improvements": []},
    }

    for indicator in feedback_per_indicator.keys():
        if indicator[0] in ["F", "A", "I", "R"]:
            if result.get(indicator) == True:
                feedback[indicator[0]]["strengths"].append(
                    feedback_per_indicator[indicator]["strengths"]
                )
            elif result.get(indicator) == False:
                feedback[indicator[0]]["improvements"].append(
                    feedback_per_indicator[indicator]["improvements"]
                )

    return feedback
