import argparse
import logging
import os
import sys
import subprocess
import shlex
import re


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(
        description="Detects improper exception handling in Python code.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "path",
        help="Path to the Python file or directory to analyze.",
        type=str
    )

    parser.add_argument(
        "--report_file",
        help="Path to save the report (optional).  If not provided, output will be to stdout.",
        type=str,
        required=False
    )

    parser.add_argument(
        "--exclude",
        help="Comma-separated list of files or directories to exclude from analysis.",
        type=str,
        required=False,
        default=""
    )

    parser.add_argument(
        "--tool",
        help="Specify the static analysis tool to use (bandit, flake8, pylint, pyre-check). Default: bandit",
        type=str,
        choices=['bandit', 'flake8', 'pylint', 'pyre-check'],
        default='bandit'
    )

    return parser


def check_path(path):
    """
    Checks if the provided path exists and is either a file or a directory.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path exists, False otherwise.
    """
    if not os.path.exists(path):
        logging.error(f"Error: Path '{path}' does not exist.")
        return False
    return True


def analyze_with_bandit(path, exclude):
    """
    Analyzes Python code using Bandit to detect improper exception handling.

    Args:
        path (str): The path to the Python file or directory to analyze.
        exclude (str): Comma-separated list of files/directories to exclude.

    Returns:
        str: Bandit's output as a string.
    """
    try:
        exclude_list = [f"--exclude={e.strip()}" for e in exclude.split(',') if e.strip()]
        command = ["bandit", "-r", path, "-f", "txt"] + exclude_list
        logging.info(f"Running Bandit with command: {' '.join(shlex.quote(arg) for arg in command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Bandit analysis failed: {e}")
        return f"Bandit analysis failed: {e}\n{e.stderr}"
    except Exception as e:
        logging.error(f"Error running Bandit: {e}")
        return f"Error running Bandit: {e}"

def analyze_with_flake8(path, exclude):
    """
    Analyzes Python code using Flake8 to detect improper exception handling and other issues.

    Args:
        path (str): The path to the Python file or directory to analyze.
        exclude (str): Comma-separated list of files/directories to exclude.

    Returns:
        str: Flake8's output as a string.
    """
    try:
         # Flake8 uses --exclude differently, it's a single string with comma-separated patterns
        command = ["flake8", path, "--extend-ignore=E722,B001,B028", "--select=E,W,F,C90", "--max-complexity=10"]
        exclude_list = [e.strip() for e in exclude.split(',') if e.strip()]
        if exclude_list:
            command.extend(["--exclude", ",".join(exclude_list)])

        logging.info(f"Running Flake8 with command: {' '.join(shlex.quote(arg) for arg in command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Flake8 analysis failed: {e}")
        return f"Flake8 analysis failed: {e}\n{e.stderr}"
    except Exception as e:
        logging.error(f"Error running Flake8: {e}")
        return f"Error running Flake8: {e}"

def analyze_with_pylint(path, exclude):
    """
    Analyzes Python code using Pylint to detect improper exception handling and other issues.

    Args:
        path (str): The path to the Python file or directory to analyze.
        exclude (str): Comma-separated list of files/directories to exclude.

    Returns:
        str: Pylint's output as a string.
    """
    try:

        command = ["pylint", path, "--disable=C0301,W0703,W0702,broad-except"]
        exclude_list = [e.strip() for e in exclude.split(',') if e.strip()]
        if exclude_list:
            command.extend(["--ignore", ",".join(exclude_list)])
        logging.info(f"Running Pylint with command: {' '.join(shlex.quote(arg) for arg in command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Pylint analysis failed: {e}")
        return f"Pylint analysis failed: {e}\n{e.stderr}"
    except Exception as e:
        logging.error(f"Error running Pylint: {e}")
        return f"Error running Pylint: {e}"

def analyze_with_pyre(path, exclude):
    """
    Analyzes Python code using Pyre to detect improper exception handling and other issues.

    Args:
        path (str): The path to the Python file or directory to analyze.
        exclude (str): Comma-separated list of files/directories to exclude.

    Returns:
        str: Pyre's output as a string.
    """
    try:
        # Pyre configuration and command setup might be more complex
        # This is a simplified example, adapt it based on your specific needs and Pyre setup
        command = ["pyre", "analyze", path]
        logging.info(f"Running Pyre with command: {' '.join(shlex.quote(arg) for arg in command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Pyre analysis failed: {e}")
        return f"Pyre analysis failed: {e}\n{e.stderr}"
    except FileNotFoundError:
        logging.error("Pyre is not installed or not in PATH. Please install Pyre.")
        return "Pyre is not installed or not in PATH. Please install Pyre."
    except Exception as e:
        logging.error(f"Error running Pyre: {e}")
        return f"Error running Pyre: {e}"


def main():
    """
    Main function to drive the exception handling checker.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Input validation
    if not check_path(args.path):
        sys.exit(1)

    analysis_results = ""
    # Choose analysis tool
    if args.tool == 'bandit':
        analysis_results = analyze_with_bandit(args.path, args.exclude)
    elif args.tool == 'flake8':
        analysis_results = analyze_with_flake8(args.path, args.exclude)
    elif args.tool == 'pylint':
        analysis_results = analyze_with_pylint(args.path, args.exclude)
    elif args.tool == 'pyre-check':
        analysis_results = analyze_with_pyre(args.path, args.exclude)
    else:
        logging.error(f"Invalid tool specified: {args.tool}")
        sys.exit(1)

    # Output the results
    if args.report_file:
        try:
            with open(args.report_file, "w") as f:
                f.write(analysis_results)
            logging.info(f"Report saved to {args.report_file}")
        except IOError as e:
            logging.error(f"Error writing to report file: {e}")
            sys.exit(1)
    else:
        print(analysis_results)


if __name__ == "__main__":
    main()