"""Component to detect dialogue of deaf breakdowns.

It identifies the agent's utterances and dialogue acts that are identical and
consecutive. This breakdown can indicate a pitfall in the dialogue policy from
which the conversational agent cannot escape.
"""

import statistics
from difflib import SequenceMatcher
from typing import List, Tuple

from dialoguekit.core.dialogue import Dialogue
from dialoguekit.core.utterance import Utterance
from dialoguekit.participant import DialogueParticipant

from .breakdown_detector import BreakdownDetector


class DialogueOfDeafDetector(BreakdownDetector):
    def __init__(self, breakdown_name: str = "Dialogue of deaf") -> None:
        """Initializes the dialogue of deaf breakdown detector.

        Args:
            breakdown_name: Name of the breakdown detected. Defaults to "
              Dialogue of deaf".
        """
        super().__init__(breakdown_name)

    def detect_breakdown(self, dialogue: Dialogue) -> Tuple[str]:
        """Detects dialogue of deaf breakdown in a given dialogue.

        We consider that more than two consecutive identical agent utterances
        are a dialogue of deaf breakdown.

        Args:
            dialogue: Dialogue.

        Returns:
            Intent sequence leading to the breakdown.
        """
        intent_sequence = ()

        # Check if the dialogue ended because of a recursion error
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

        agent_utterances = [
            utterance
            for utterance in dialogue.utterances
            if utterance.participant == DialogueParticipant.AGENT.name
        ]
        sequence_matcher = SequenceMatcher()
        for i in range(len(agent_utterances) - 2):
            same_intent = (
                agent_utterances[i].intent.label
                == agent_utterances[i + 1].intent.label
                == agent_utterances[i + 2].intent.label
            )
            resemblance = self._compute_utterance_resemblance(
                agent_utterances[i],
                agent_utterances[i + 1 : i + 3],
                sequence_matcher,
            )
            if same_intent and resemblance >= 0.9:
                # An agent is always followed by a user utterance.
                for utterance in dialogue.utterances[: i * 2]:
                    if utterance.participant == DialogueParticipant.AGENT.name:
                        intent_sequence = intent_sequence + (
                            f"A_{utterance.intent.label}",
                        )
                    else:
                        intent_sequence = intent_sequence + (
                            f"U_{utterance.intent.label}",
                        )
                #
                return intent_sequence
        return intent_sequence

    def _compute_utterance_resemblance(
        self,
        utterance: Utterance,
        previous_utterances: List[Utterance],
        sequence_matcher: SequenceMatcher,
    ) -> float:
        """Computes the resemblance between an utterance and the 2 previous
        utterances.

        Args:
            utterance: Utterance.
            previous_utterances: Previous utterances.
            sequence_matcher: Sequence matcher.

        Returns:
            Resemblance between three consecutive agent utterances.
        """
        sequence_matcher.set_seqs(utterance.text, previous_utterances[0].text)
        resemblance1 = sequence_matcher.ratio()
        sequence_matcher.set_seqs(utterance.text, previous_utterances[-1].text)
        resemblance2 = sequence_matcher.ratio()
        resemblance = statistics.mean([resemblance1, resemblance2])
        return resemblance
