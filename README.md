# Conversational Breakdowns Detection

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Python version](https://img.shields.io/badge/python-3.9-blue)

This repository contains the data related to the case study presented in the paper "_Identifying Breakdowns in Conversational Recommender Systems using User Simulation_" presented to the ACM Conversational User Interfaces conference 2024.

The paper proposes a methodology to automatically detect breakdowns in conversational recommender systems using user simulation. It can serve as a diagnostic or development tool. An overview of the methodology is presented in the following figure:

![Methodology Overview](./docs/methodology_flowchart.png)

## Data

The simulated dialogues for each iteration of the case study are provided in the `data/simulated_dialogues` directory. We also provide the interaction model used to detect **conversation flow discontinuation** breakdowns in the `data/dialogue_flow.json` file.

Using the data provided, you can run the breakdown detection (see this [section](#run-breakdown-detection)) and retrieve the results presented in the paper.

## Breakdown Detection

The breakdown detection module comprises a set of breakdown detectors and a script to automatically detect breakdowns in dialogues. Below, we describe the types of breakdowns supported:

  * **System failure**: This detector simply verifies that no system errors are thrown during conversation generation between the agent and the user. This failure can help to identify underlying bugs that were not detected during integration tests.
  * **Dialogue of the deaf**:  It identifies the agent's utterances and dialogue acts that are identical and consecutive. This failure can indicate a pitfall in the dialogue policy from which the conversational agent cannot escape. Indeed, the goal of recommending an item to the user cannot be achieved if the agent keeps repeating the same utterance for multiple turns, i.e., the conversation does not progress. Moreover, such situations can easily frustrate users, who will most likely stop interacting with the agent.
  * **Conversation flow discontinuation**: This failure corresponds to an unexpected reply from either of the dialogue participants, more specifically a reply that affects negatively the naturalness of the conversation. It includes delayed replies, i.e., the participant replies to an utterance that was received at least two utterances before, and unexpected responses, i.e., a sequence of utterances with dialogue acts that should not follow each other.

### Run Breakdown Detection

Make sure to install the required dependencies by running the following command:

```bash
pip install -r requirements.txt
```

Execute the following command to perform breakdown detection on a set of dialogues:

```bash
python -m breakdowns_detection.run_detection <dialogues_path> <dialogue_flow> [--output_file <output_file> --breakdown-components <components> --debug]
```

To save the report in an Excel file, use the `--output_file` argument, otherwise, the report will be printed in the console. For more details about the arguments, run the following command:

```bash
python -m breakdowns_detection.run_detection --help
```

## Citation

If you use the resources presented in this repository, please cite:

```bibtex
@misc{Bernard:2024:arXiv,
 author={Bernard, Nolwenn and Balog, Krisztian},
 title={Identifying Breakdowns in Conversational Recommender Systems using User Simulation},
 year=2024,
 eprint={2405.14249},
 archiveprefix={arXiv},
 primaryclass={cs.IR}
}
```

## Contact

Should you have any questions, please contact Nolwenn Bernard at nolwenn.m.bernard@uis.no
