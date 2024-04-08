"""Component to detect conversational flow discontinuation breakdowns.

This breakdown corresponds to an unexpected reply from the conversational agent,
more specifically a reply that affects negatively the naturalness of the
conversation. For example, it includes delayed reply, i.e., the agent replies
to an utterance that was received at least two utterances before, and utterance
with a dialogue act that mismatches the dialogue policy.
"""

from typing import Tuple

import networkx as nx
from dialoguekit.core.dialogue import Dialogue
from dialoguekit.participant import DialogueParticipant

from .breakdown_detector import BreakdownDetector


class FlowDiscontinuationDetector(BreakdownDetector):
    def __init__(
        self,
        dialogue_flow: nx.DiGraph,
        breakdown_name: str = "Flow discontinuation",
    ) -> None:
        """Initializes the flow discontinuation breakdown detector.

        Args:
            dialogue_flow: Dialogue flow of the CRS.
            breakdown_name: Name of the breakdown detected. Defaults to "Flow
              discontinuation".
        """
        super().__init__(breakdown_name)
        self._dialogue_flow = dialogue_flow

    def detect_breakdown(self, dialogue: Dialogue) -> Tuple[str]:
        """Detects flow discontinuation breakdowns in a given dialogue.

        Args:
            dialogue: Dialogue.

        Returns:
            Intent sequence leading to the breakdown.
        """
        path = []
        for utterance in dialogue.utterances:
            intents = utterance.intent.label.split("+")
            if utterance.participant == DialogueParticipant.AGENT.name:
                path.extend([f"A_{intent}" for intent in intents])
            else:
                path.extend([f"U_{intent}" for intent in intents])

            if not nx.is_path(self._dialogue_flow, path):
                return tuple(path)

        return ()
