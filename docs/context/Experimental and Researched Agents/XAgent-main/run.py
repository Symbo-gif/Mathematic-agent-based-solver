# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from contextlib import redirect_stdout
import argparse
from copy import deepcopy
from XAgent.config import CONFIG, ARGS
from command import CommandLine, CommandLineParam


def parse_args() -> argparse.Namespace:
    """
    Parse the command line arguments and return them as an argparse.Namespace object.

    Returns:
        argparse.Namespace: An object containing command line arguments and their values.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--task", type=str, required=True, help="The task description.")
    parser.add_argument("--upload-files", nargs='+', dest="upload_files", help="List of files to upload.")
    parser.add_argument("--model", type=str, help="Model identifier for the task.")
    parser.add_argument("--record-dir", type=str, dest="record_dir", help="Directory to record task execution logs.")
    parser.add_argument("--mode", type=str, default="auto", help="Operational mode: 'auto' or 'manual'.")
    parser.add_argument("--quiet", action="store_true", default=False, help="Run in quiet mode; minimal output.")
    parser.add_argument("--max-subtask-chain-length", type=int, dest="max_subtask_chain_length",
                        help="Maximum length of subtask chain.")
    parser.add_argument("--enable-ask-human-for-help", action="store_true", dest="enable_ask_human_for_help",
                        help="Flag to enable asking for human assistance.")
    parser.add_argument("--max-plan-refine-chain-length", type=int, dest="max_plan_refine_chain_length",
                        help="Maximum length of plan refinement chain.")
    parser.add_argument("--max-plan-tree-depth", type=int, dest="max_plan_tree_depth",
                        help="Maximum depth of the plan tree.")
    parser.add_argument("--max-plan-tree-width", type=int, dest="max_plan_tree_width",
                        help="Maximum width of the plan tree.")
    parser.add_argument("--max-retry-times", type=int, dest="max_retry_times", help="Maximum number of retry attempts.")
    parser.add_argument("--config-file", type=str, default=os.getenv('CONFIG_FILE', 'assets/config.yml'),
                        dest="config_file", help="Path to the configuration file.")

    return parser.parse_args()


def execute_command_line_process(args: argparse.Namespace, quiet_mode: bool = False) -> None:
    """
    Execute the command line process based on the parsed arguments. If quiet mode is enabled,
    redirect stdout to a file specified by the recorder's record_root_dir.

    Args:
        args (argparse.Namespace): Parsed command line arguments.
        quiet_mode (bool): Whether to run in quiet mode, outputting to a file instead of the terminal.
    """
    args_dict = vars(args)
    for key, value in args_dict.items():
        if value is not None:
            if key == 'model':
                ARGS['default_completion_kwargs'] = deepcopy(CONFIG['default_completion_kwargs'])
                ARGS['default_completion_kwargs']['model'] = value
            else:
                ARGS[key] = value

    # Redirect stdout to a file if quiet mode is true
    if quiet_mode:
        from XAgent.running_recorder import recorder
        record_file_path = os.path.join(recorder.record_root_dir, "command_line.ansi")
        with open(record_file_path, "w", encoding="utf-8") as file, redirect_stdout(file):
            start_command_line(args_dict)
    else:
        start_command_line(args_dict)


def start_command_line(args_dict: dict) -> None:
    """
    Start the command line interface with the provided arguments.

    Args:
        args_dict (dict): A dictionary of command line arguments.
    """
    param = CommandLineParam(
        task=args_dict['task'],
        upload_files=args_dict.get('upload_files'),
        role="Assistant",
        mode=args_dict["mode"],
    )
    cmd = CommandLine(param)
    cmd.start()


if __name__ == '__main__':
    args = parse_args()
    os.environ['CONFIG_FILE'] = args.config_file

    # The quiet_mode argument is passed directly to the function
    execute_command_line_process(args, quiet_mode=args.quiet)
