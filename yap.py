import requests
from requests.exceptions import HTTPError
from sys import argv
from pathlib import Path
from csv import DictReader
import re

#
# Utils
#
# TODO: Typehint for file arg
def insert_newline(file, amount=1) -> None:
    """Inserts a newline into a file.

    Args:
        file (str): Absolute filepath.
        amount (int, optional): How many new lines we want inserted.
    """
    file.write("\n" * amount)


def insert_spaces(amount: int, text: str) -> str:
    """YAML files use spaces rather than tabs, despite using the tab key when working
    with them.

    Args:
        amount (_type_):
        text (_type_): The text we want to insert after the space.

    Returns:
        str:
    """
    return " " * amount + text


def remove_all_whitespace(text: str) -> str:
    """Removes all whitespace from a str...

    Args:
        text (str):

    Returns:
        str:
    """
    return text.strip().replace(" ", "")


#
# Validattors
#
def validate_url(url: str):
    """Validates if the passed URL ends in a yaml file extension.

    Args:
        url (str):

    Raises:
        ValueError: If it's not a yaml file extension.
    """
    for valid_extension in ("yml", "yaml"):
        if url.endswith(valid_extension):
            return
    raise ValueError(
        "The provide url does not end in yml/yml. Please provide a valid link."
    )


def validate_file(file: str):
    """Checks if a file exists.

    Args:
        file (str): Absolute filepath.

    Raises:
        FileExistsError:
    """
    if not Path(file).exists():
        raise FileExistsError(
            f"The passed file does not exist... please first create it. File: {file}"
        )


def validate_ansible_kind_state(state: str):
    if state not in ("present",):
        raise ValueError("Not a valid ansible state! Passed state:", {state})


#
# Fetch
#
def fetch(url) -> str:
    """Fetches the text from a url.

    I know you peeps like JavaScript so this should feel natural.
    It's not async though as I wrote this as 6am so I'm not
    feeling too generous.

    Args:
        url (str):

    Raises:
        HTTPError: If we don't get a response code of 200.

    Returns:
        str:
    """
    resp = requests.get(url)
    if resp.status_code != 200:
        raise HTTPError(f"Response code is not 200. Response code: {resp.status_code}")
    return resp.text


#
# Write to yaml files
#
def add_yaml_to_file(
    ansbile_playbook_file: str,
    yaml: str,
    ansible_state: str = "",
    playbook_title: str = "",
    escape_brackets=False,
):
    """Adds the yaml to the targeted ansible playbook file.

    Args:
        ansbile_playbook_file (str): Absolute filepath.
        yaml (str): Contents of a single YAML.
        ansible_state (str, optional): The state we wish to make this. Defaults to ''.
        playbook_title (str, optional): The title you wish to appear. Defaults to ''.
        escape_brackets (bool, optional): If the YAML contains any {{ of this }}, you may want t
        tell ansible not to process this. Setting this to false wraps {% raw %} and {% endraw %}. Defaults to False.
    """

    if not playbook_title:
        playbook_title = input("Title of action: ")

    if not ansible_state:
        ansible_state = input("Insert ansible-playbook state: ").lower()
    validate_ansible_kind_state(ansible_state)

    if escape_brackets:
        # This regex finds all {{ things like thiss }}. It captures the first {
        # and the last }, and all the contents inside.
        for match in set(re.findall("(\{{(?:\[??[^\[]*?\}}))", yaml)):
            yaml = yaml.replace(match, "{% raw %}" + match + "{% endraw %}")

    with open(ansbile_playbook_file, "a") as file:
        insert_newline(file)
        file.write(f"- name: {playbook_title}")

        insert_newline(file)
        file.write(insert_spaces(2, "k8s:"))

        insert_newline(file)
        file.write(insert_spaces(4, f"state: {ansible_state}"))

        insert_newline(file)
        file.write(insert_spaces(4, "definition:"))

        insert_newline(file)
        for line in yaml.split("\n"):
            # Each line of YAML will already have its own spaces so just
            # add ours beforehand.
            file.write(insert_spaces(6, line))
            insert_newline(file)


#
# Parse
#
def parse_url(file: str, url: str):
    """Fetches the contents from a remote server and inserts contents into the target file.

    Args:
        file (str): Absolute filepath.
        url (str):
    """
    validate_file(file)
    validate_url(url)

    print(
        "Ensure details are correct \n",
        f"\t - file: {file}",
        "\n",
        f"\t - url: {url}",
        "\n",
        'If your happy with these details please type "y" otherwise the operation will be cancelled',
    )
    exit("You have chosen not to proceed.") if input() != "y" else add_yaml_to_file(
        file, fetch(url)
    )


def parse_url_big(file: str, url: str, delimiter="---"):
    """Fetches the contents from a remote server and inserts contents into the target file.
    Splits each config from the provided delimiter. Each seperate config will be given the name
    'Config number {n}'...

    Args:
        file (str): Absolute filepath.
        url (str):
    """
    validate_file(file)
    validate_url(url)

    yamls = []
    string = ""
    for line in fetch(url).split("\n"):
        if line == delimiter:
            # Let's see if we've actually added anything first
            if len(string):
                yamls.append(string)
                string = ""
            continue
        string += line + "\n"
    # Add the remaining data
    yamls.append(string)

    print(len(yamls))
    for config_number, yaml in enumerate(yamls):
        add_yaml_to_file(
            file, yaml, "present", f"Discovered config number {config_number}"
        )


def parse_file(ansbile_playbook_file: str, csv_file: str):
    """Parses a CSV file.

    See 'example.csv'.

    Args:
        ansbile_playbook_file (str): Absolute filepath.
        csv_file (str): Absolute filepath.
    """
    validate_file(ansbile_playbook_file)
    validate_file(csv_file)

    targets = []
    with open(csv_file) as file:
        reader = DictReader(file)
        for row in reader:
            targets.append(row)

    # Let's validate some things beforehand others we'll have to manage
    # issues with version control...
    for target in targets:
        # Remove all whitespace
        target["state"] = remove_all_whitespace(target["state"])
        validate_ansible_kind_state(target["state"])

        try:
            yaml = fetch(remove_all_whitespace(target["url"]))
        except HTTPError:
            raise Exception(f"Unable to fetch yaml data for '{target['title']}'.")

        add_yaml_to_file(ansbile_playbook_file, yaml, target["state"], target["title"])


#
# Main
#
def main(arguments):
    # -f is the flag used to indicate to look at a .csv file
    print(len(arguments))
    if len(arguments) != 4:
        raise ValueError(
            "There should only be an ansible playbook target, a flag, and the target for the flag... bruh."
        )

    ansible_playnook_file, flag, target = arguments[1:]
    if flag == "--url":
        parse_url(ansible_playnook_file, target)
    elif flag == "--url-big":
        parse_url_big(ansible_playnook_file, target)
    elif flag == "--csv-file":
        parse_file(ansible_playnook_file, target)
    else:
        raise ValueError("Invalid flag my dude")


if __name__ == "__main__":
    # args should look like:
    #   python3 yap.py absolute_filepath_to_yaml --url raw_github_url
    #   python3 yap.py absolute_filepath_to_yaml --url-big raw_github_url
    #   python3 yap.py absolute_filepath_to_yaml --csv-file absolute_filepath_to_csv
    main(argv)
