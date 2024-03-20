# VOLT-CLI-TOOL

VSOL OLT EMS Management Tool. Such as like creating profiles and other device settings by using YAML file. This project development was inspired by Ansible Automation Tool.

`version: 0.1.0-b3`

## Requirements

- python ^3.8
- python-poetry 

## Tested Software/Hardware Version
- V2.3.0R/V2.1.8
- V2.3.0R/V2.1.8

## Setup and Installation

### Install `python-poetry`

```
curl -sSL https://install.python-poetry.org | python3 -
```

### Install `volt-cli`

```
. script/setup
```

### Create `volt-cli-config.ini`

```
[ems-server]
base_url = https://bsems-vsol.net/emsWebServer/
username = ems
password = ems
timeout = 30
```

## Usages

### Validate Config Yaml

```
volt-cli check-config <olt-configs.yml>
```

### Apply Config Yaml

```
volt-cli apply-config <olt-configs.yml> <olt-mac>
```

## Helper Tools

### Generate Config Files base on env (prod, stag)
```
cd scripts/profile_generators
cd prod/ && ./render_prod.sh <output dir> # production env
cd staging/ && ./render_qa.sh <output dir> # staging env
```

### Apply Multiple Config Files
```
./scripts/batch_apply_cfgs <directories | files> <mac address>
```
