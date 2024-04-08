"""Interface defining a breakdown detection component."""

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import DefaultDict, List, Tuple

import nltk
import pandas as pd
from dialoguekit.core.dialogue import Dialogue
from tabulate import tabulate


class BreakdownDetector(ABC):
    def __init__(self, breakdown_name: str) -> None:
        """Initializes the breakdown detector.

        Args:
            breakdown_name: Name of the breakdown detected.
        """
        self._breakdown_name = breakdown_name

    @property
    def breakdown_name(self) -> str:
        """Returns the name of the breakdown detected."""
        return self._breakdown_name

    @abstractmethod
    def detect_breakdown(self, dialogue: Dialogue) -> Tuple[str]:
        """Detects breakdown in a given dialogue.

        Args:
            dialogue: Dialogue.

        Returns:
            Sequence of intents causing the breakdown. Agent's intents are
            prefixed with A_ and user's intents with U_.

        Raises:
            NotImplementedError: If not implemented in derived class.
        """
        raise NotImplementedError

    def detect_breakdowns(
        self, dialogues: List[Dialogue]
    ) -> DefaultDict[Tuple[str], int]:
        """Detects breakdown dialogues.

        Args:
            dialogues: Dialogues.

        Returns:
            Count of breakdowns per sequence of intents.
        """
        breakdowns = defaultdict(int)
        for dialogue in dialogues:
            logging.debug(
                f"breakdown detected:{self.detect_breakdown(dialogue)}"
            )
            seq = self.detect_breakdown(dialogue)
            if seq:
                breakdowns[seq] += 1
        return breakdowns

    def _find_conversational_patterns(
        self, breakdowns: List[List[str]], n: int = 3
    ) -> pd.DataFrame:
        """Finds problematic conversational patterns based on detected breakdowns.

        Args:
            breakdowns: Sequences of intents leading to breakdown.
            n: Maximum length of intent sequences (conversational patterns).
              Defaults to 3.

        Returns:
            List of problematic conversational patterns and their number of
            occurrence.
        """
        sequences = [" ".join(breakdown) for breakdown in breakdowns]

        df = pd.DataFrame()
        for i in range(2, n + 1):
            df = pd.concat(
                [df, pd.Series(nltk.ngrams(sequences, i)).value_counts()],
                axis=0,
            )
        return df

    def get_breakdown_summary(
        self,
        breakdowns: DefaultDict[List[str], int],
        n: int = 3,
        output_file: str = None,
    ) -> pd.DataFrame:
        """Returns a summary of the detected breakdowns in a given dialogue.

        It includes the number of breakdowns detected for sequences of intents.

        Args:
            breakdowns: Count of breakdowns per sequence of intents.
            n: Maximum length of intent sequences to include in the summary.
              Defaults to 3.
            output_file: Path to the output file to save the report. If set to
              None, the report is printed in the console. Defaults to None.

        Returns:
            Report of the detected breakdowns.
        """
        full_breakdowns = pd.DataFrame.from_dict(
            breakdowns,
            orient="index",
            columns=["Count"],
        )
        full_breakdowns.index.set_names(["Sequence of intents"], inplace=True)

        summary_table = self._find_conversational_patterns(
            list(breakdowns.keys()), n=n
        )

        if output_file:
            with pd.ExcelWriter(
                output_file,
                mode="a",
                engine="openpyxl",
                if_sheet_exists="replace",
            ) as writer:
                full_breakdowns.to_excel(
                    writer,
                    sheet_name=self._breakdown_name,
                )
        else:
            print("\nBreakdown Summary\n")
            print(tabulate(summary_table, headers="keys", tablefmt="psql"))
            print(f"Detailed Breakdown Detection for {self._breakdown_name}\n")
            print(tabulate(full_breakdowns, headers="keys", tablefmt="psql"))
        return full_breakdowns
