import argparse
import subprocess
import re
from typing import IO, Sequence


def extract_jira(query: bytes) -> str | None:
    jira_regex = re.compile("([A-Z][A-Z0-9]+-[0-9]+")
    jira_id = jira_regex.search(query.decode("utf-8"))
    if jira_id:
        return jira_id.group(1)
    return None


def current_branch_name() -> bytes | None:
    cmd = "git branch --show-current"
    try:
        return subprocess.check_output(cmd.split(), stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print(f"Error while running {cmd}")
        return None


def check_and_update_commit_msg(file_obj: IO[bytes]) -> int:
    commit_msg = file_obj.read()
    if extract_jira(commit_msg):
        print("Jira id already present in commit message.")
        return 0

    branch_name = current_branch_name()
    if not branch_name:
        return 1

    jira_id = extract_jira(branch_name)
    if not jira_id:
        print("No jira id found in branch name.")
        return 1

    file_obj.seek(0)
    file_obj.write(commit_msg + f" [{jira_id}]".encode())
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Commit message file name")
    args = parser.parse_args(argv)

    retval = 1
    filename = args.filename[0]
    with open(filename, "rb+") as file_obj:
        retval = check_and_update_commit_msg(file_obj)
    return retval


if __name__ == "__main__":
    raise SystemExit(main())
