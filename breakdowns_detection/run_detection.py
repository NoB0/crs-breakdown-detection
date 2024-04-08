"""Main command line interface for breakdowns detection.

It runs the different breakdowns detection component on the given dialogues and
creates a summary of the results.
"""

import argparse
import json
import logging
import time
from typing import List

import matplotlib.pyplot as plt
import networkx as nx
from dialoguekit.utils.dialogue_reader import json_to_dialogues
from pyvis.network import Network

from breakdowns_detection.breakdown_detectors import (
    BreakdownDetector,
    DialogueOfDeafDetector,
    FlowDiscontinuationDetector,
    SystemFailureDetector,
)

logging.basicConfig(
    format="[%(asctime)s] %(levelname)-12s %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main(args: argparse.Namespace) -> None:
    """Runs the breakdown detection components and saves a summary of detected
    breakdowns.

    Args:
        args: Parsed arguments.
    """
    dialogues = json_to_dialogues(
        args.dialogues_path, agent_id="agent", user_id="simulator"
    )
    logging.info(
        f"Loaded {len(dialogues)} dialogues from {args.dialogues_path}"
    )

    dialogue_flow = nx.node_link_graph(
        json.load(open(args.dialogue_flow, "r"))
    )
    logger.info(f"Dialogue flow loaded from {args.dialogue_flow}")
    if args.debug:
        logger.info(
            "An interactive visualization of the dialogue flow is saved in "
            "dialogue_flow.html"
        )
        _visualize_flow(dialogue_flow)

    breakdown_detectors = _create_breakdown_detectors(
        dialogue_flow=dialogue_flow, components_names=args.breakdown_components
    )

    breakdown_count = {}
    for breakdown_detector in breakdown_detectors:
        logger.info(f"Running {breakdown_detector.breakdown_name}")
        breakdowns = breakdown_detector.detect_breakdowns(dialogues)
        summary = breakdown_detector.get_breakdown_summary(
            breakdowns, args.n, args.output_file
        )
        breakdown_count[breakdown_detector.breakdown_name] = (
            summary["Count"].sum() if not summary.empty else 0
        )

    # Plot number of breakdowns per breakdown type
    plt.bar(breakdown_count.keys(), breakdown_count.values())
    plt.title("Number of breakdowns per breakdown type")
    plt.xlabel("Breakdown type")
    plt.ylabel("Number of breakdowns")
    plt.savefig(f"data/figures/breakdowns_per_type_{time.time()}.png")
    logging.info(f"Breakdown count: {breakdown_count}")


def _visualize_flow(dialogue_flow: nx.DiGraph) -> None:
    """Visualizes the dialogue flow.

    Args:
        dialogue_flow: Dialogue flow of the CRS.
    """
    nt = Network(directed=True, filter_menu=True, select_menu=True)
    nt.from_nx(dialogue_flow)
    nt.toggle_physics(True)
    nt.show("dialogue_flow_composite.html")


def _create_breakdown_detectors(
    dialogue_flow: nx.DiGraph,
    components_names: List[str] = [
        "system_failure",
        "flow_discontinuation",
        "dialogue_of_the_deaf",
    ],
) -> List[BreakdownDetector]:
    """Creates the breakdown detectors for the analysis.

    Args:
        dialogue_flow: Dialogue flow of the CRS.
        components_names: Names of the breakdown detection components to use. By
          defaults all detectors are created.

    Returns:
        List of breakdown detectors.

    Raises:
        ValueError: If an unknown breakdown detection component is requested.
    """
    detectors = []
    for component_name in components_names:
        if component_name == "system_failure":
            detectors.append(SystemFailureDetector())
        elif component_name == "flow_discontinuation":
            detectors.append(FlowDiscontinuationDetector(dialogue_flow))
        elif component_name == "dialogue_of_the_deaf":
            detectors.append(DialogueOfDeafDetector())
        else:
            raise ValueError(
                f"Unknown breakdown detection component {component_name}"
            )
    return detectors


def parse_args() -> argparse.Namespace:
    """Defines accepted arguments and returns the parsed values.

    Returns:
        A namespace object containing the arguments.
    """
    parser = argparse.ArgumentParser(prog="run_detection.py")
    parser.add_argument(
        "dialogues_path",
        type=str,
        help="Path to the dialogues file.",
    )
    parser.add_argument(
        "dialogue_flow",
        type=str,
        help="Path to the dialogue flow JSON file.",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        help="Path to the Excel file where to save the summary.",
    )
    parser.add_argument(
        "--breakdown-components",
        nargs="*",
        type=str,
        default=[
            "system_failure",
            "flow_discontinuation",
            "dialogue_of_the_deaf",
        ],
        help="Components to use for breakdown detection. By default, all are "
        "used.",
    )
    parser.add_argument(
        "-n",
        type=int,
        default=3,
        help="Maximum length of the conversational pattern in summary.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Activate debug mode.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    main(args)
