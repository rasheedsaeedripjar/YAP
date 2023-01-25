 # YAP (YAML to Ansible Playbook)
This script takes one or more Kubernetes YAML files (*currently only supporting urls*) and inserts them into a targeted ansible playbook file.  

## Motivation
When wanting to use existing YAML files, for example the <a href=’https://github.com/prometheus-operator/prometheus-operator’>Prometheus-operator</a>, there is tremendous pain (and error) copying and pasting these templates into existing playbooks. This script therefore intends to mitigate this pain. 

### Notes: 

- Only YAML files are supported from a server. URLS must end in a .yaml or .yml.
- Currently, the only supported ansible king state is *present*. You can add more in the validate_ansible_kind_state function. 
- The targeted ansible playbook file must exist.

### How to
The script is ran via the CLI. There are currently three supported options using these flags:

- *--url-*: Looks at a URL with a single config. You will be prompt to insert a title and a [ansible] state. 
- *--url-alot*: Looks at a URL with multiple configs. They will be split using a delimiter (default "---"). The default title will be when it was discovered from the script (e.g., Config number 1, Config number 2, Config number *n*, ...) and the default state is present. This one requires cleaning after fetching.
- *--csv-file*: This method fetches one or more yaml files (which each have a single config) along with their desired title and state from a CSV. 

**CLI examples:** <br />
```python3 yap.py target.yml --url https://raw.githubusercontent.com/prometheus-operator/kube-prometheus/main/manifests/setup/0alertmanagerConfigCustomResourceDefinition.yaml```

```python3 yap.py /Users/rasaeed/Documents/GitHub/YAP/target.yml --url-big https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/master/bundle.yaml```

```python3 yap.py /Users/rasaeed/Documents/GitHub/YAP/target.yml --csv-file example.csv```
