import requests
from requests.exceptions import HTTPError
from sys import argv
from pathlib import Path
from csv import DictReader

#
# Utils
#
def insert_newline(file, amount=1):
    """It's awkward writing \n on a mac keyboard so..."""
    file.write('\n' * amount)

def insert_spaces(amount, text) -> str:
    """
    YAML files don't allow tabs. Therefore, in order to 
    make the formatting valid, we need to insert the right
    number of tabs.
    """
    return (" " * amount) + text

def remove_all_whitespace(text) -> str:
    return text.strip().replace(' ', '')

#
# Validations
#
def validate_url(url) -> bool:
    """Checks if the provided url ends in either yml and yaml"""
    for valid_extension in ['yml', 'yaml']:
        if url.endswith(valid_extension):
            return
    raise ValueError('The provide url does not end in yml/yml. Please provide a valid link.')

def validate_file(file):
    if not Path(file).exists():
        raise FileExistsError(f'The passed file does not exist... please first create it. File: {file}')

def validate_ansible_kind_state(state):
    if state not in ['present']:
        raise ValueError('Not a valid ansible state! Passed state:', {state})

#
# Fetch
#
def fetch(url) -> str:
    """
    You guys like JavaScript so this should feel natural. 
    It's not async though as I wrote this as 6am so I'm not
    feeling to generous. 
    """
    if 'https://raw.githubusercontent.com/' not in url:
        raise ValueError('The passed url is not a raw.githubusercontent.com url.')

    resp = requests.get(url)
    if resp.status_code != 200:
        raise HTTPError(f"Resp is not 200. Response code: {resp.status_code}")
    return resp.text


#
# Write to yaml fileß
#
def add_yaml_to_file(target_yml, text, state='', title=''):
    """
    I know this is absolutly disgusting but it works!
    """

    if not title: 
        title = input('Title of action: ')

    if not state:
        state = input('Insert ansible-playbook state: ').lower()
    validate_ansible_kind_state(state)

    with open(target_yml, 'a') as file:
        insert_newline(file)
        file.write(f"- name: {title}")

        insert_newline(file)
        file.write(insert_spaces(2, 'k8s:'))

        insert_newline(file)
        file.write(insert_spaces(4, f"state: {state}"))

        insert_newline(file)
        file.write(insert_spaces(4, 'definition:'))

        insert_newline(file)
        for line in text.split('\n'):
            file.write(insert_spaces(6, line))
            insert_newline(file)

#
# Parse
#
def parse_url(file, url):
    validate_file(file)
    validate_url(url)

    print(
        'Ensure details are correct \n', 
            f'\t - file: {file}', '\n',
            f'\t - url: {url}', '\n',
        'If your happy with these details please type "y" otherwise the operation will be cancelled',
    )
    exit('You have chosen not to proceed.') if input() != 'y' else add_yaml_to_file(file, fetch(url))


def parse_file(yaml_file, csv_file):
    validate_file(yaml_file)
    validate_file(csv_file)

    data = []
    with open(csv_file) as file:
        reader = DictReader(file)
        for row in reader:
            data.append(row)

    # Let's validate some things beforehand others we'll have to manage
    # issues with version control...
    for _ in data:
        # Remove all whitespace
        _['state'] = remove_all_whitespace(_['state'])
        validate_ansible_kind_state(_['state'])

    for _ in data:
        # If we get a resp, add the text here so we don't have to make a call again
        _['yaml'] = fetch(remove_all_whitespace(_['url']))   

    for _ in data:
        add_yaml_to_file(yaml_file, _['yaml'], _['state'], _['title'])

#
# Main
#
def main(arguments):
     # -f is the flag used to indicate to look at a .csv file
    if '-f' not in arguments and len(arguments) == 3:
        # passing the yaml_file and raw_github_url
        parse_url(arguments[1], arguments[2])
    elif '-f' in arguments and len(arguments) == 4:
        # passing the yaml_file and csv_path
        parse_file(arguments[1], arguments[3])
    else: 
        raise ValueError('No idea what youve done ')
    

if __name__ == '__main__':
    # args should look like: 
    #   python3 yap.py absolute_filepath_to_yaml raw_github_url
    #   python3 yap.py absolute_filepath_to_yaml -f absolute_filepath_to_csv
    main(argv)