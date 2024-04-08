"""Component for detecting system failures."""

from typing import Tuple

from dialoguekit.core.dialogue import Dialogue
from dialoguekit.participant import DialogueParticipant

from .breakdown_detector import BreakdownDetector


class SystemFailureDetector(BreakdownDetector):
    def __init__(self, breakdown_name: str = "System failure") -> None:
        """Initializes the system failure detector.

        Args:
            breakdown_name: Name of the breakdown detected. Defaults to "System
              failure".
        """
        super().__init__(breakdown_name)

    def detect_breakdown(self, dialogue: Dialogue) -> Tuple[str]:
        """Detects system failure in a given dialogue.

        RecursionError are not considered as system failures.They indicate an
        infinite loop in the dialogue that correspond to a dialogue of deaf
        breakdown.

        Args:
            dialogue: Dialogue.

        Returns:
            Intent sequence leading to the breakdown.
        """
        intent_sequence = ()
        # Check if the dialogue has a system error. In the future, a further
        # analysis of the error trace can be done to draw more insights.
        error = dialogue.metadata.get("error", {}).get("error_type", None)
        if error is not None and error != "RecursionError":
            for utterance in dialogue.utterances:
                if utterance.participant == DialogueParticipant.AGENT.name:
                    intent_sequence = intent_sequence + (
                        f"A_{utterance.intent.label}",
                    )
                else:
                    intent_sequence = intent_sequence + (
                        f"U_{utterance.intent.label}",
                    )

        return intent_sequence
