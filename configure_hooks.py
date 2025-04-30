"""
This module is used to configure pre commit hooks and commit message checker
"""

import os
import subprocess
import sys


def run_commands() -> None:
    """
    This method lays down set of commands to be executed.
    """

    if sys.prefix == sys.base_prefix:
        print(
            "Error: The virtual environment is not activated. Please activate the virtual environment and run the script again."
        )
        sys.exit(1)

    print("Installing Custom Git Hooks...")
    if os.path.exists(".git/hooks"):
        try:
            print("Installing Commit Message Checker...")
            subprocess.check_call(["cp", "commit-msg", ".git/hooks/commit-msg"])

            subprocess.check_call(["chmod", "+x", ".git/hooks/commit-msg"])
            print("Installed Commit Message Checker Successfully.")
        except subprocess.CalledProcessError:
            print(
                "Error installing Commit Message Checker. Make sure commit-msg file is present in the directory and you have proper write premissions."
            )
            print("\nSkipping Commit Message Checker Installation...")

        try:
            print("Installing Commit Message Preparer...")
            subprocess.check_call(
                ["cp", "prepare-commit-msg", ".git/hooks/prepare-commit-msg"]
            )

            subprocess.check_call(
                ["chmod", "+x", ".git/hooks/prepare-commit-msg"]
            )
            print("Installed Commit Message Preparer Successfully.")
        except subprocess.CalledProcessError:
            print(
                "Error installing Commit Message Preparer. Make sure prepare-commit-msg file is present in the directory and you have proper write premissions."
            )
            print("\nSkipping Commit Message Preparer Installation...")

    else:
        print(
            ".git/hooks directory does not exist. Skipping Git Hooks Installation."
        )

    print("Installing pre commit hooks...")
    try:
        subprocess.check_call([sys.executable, "-m", "pre_commit", "install"])
        print("Installed pre commit hooks Successfully.")
    except subprocess.CalledProcessError:
        print("Error installing pre commit hooks.")


if __name__ == "__main__":
    run_commands()
