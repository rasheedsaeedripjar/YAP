# YAP (YAML to Ansible Playbook)
This script converts one or more YAML files, local or from remote, and converts them into a runnable ansbible playbook. 

## Motivation
When wanting to use existing YAML files, for example the prometheus-operator, there is trumednous pain copying
and pasting YAML files into an ansible playbook. Moreover, mistakes can be made due to indetation erorrs. Therefore, 
this script handles mulitple cases where you may want this behaviour. 

