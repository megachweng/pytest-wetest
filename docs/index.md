# Welcome to pytest-wetest

This is a pytest plugin for [Welian](https://welian.com) API Automation test framework

## How to Use
```python
# content of pytest.ini
[pytest]
addopts: --wetest
```
 
# Avaliable options

> All options bellow must under `[wetest]` section in `pytest.ini`

- `title`: the title in json report, default is None

- `json_report_file`:Json file name, can be `none`, `auto`,`arbitrary file name`

- `json_report_indent`: json indentation

- `metadata`: `true`, `false`, default is false

- `meta_delimiter`: the delimiter in test method docstring to determine metadata line. default is `@!`

- `meta_assignment_symbol` the symbol to split key and value, default is `:`

- `CI_server`:address of CI, to determine whether tests are executed by `CI` or `Local`

- `breed_server`: address of breed server interface which the json file will send to

- `chinese_node_id`: enable or disable chinese_node_id `true` or `false` default is `false`

- `node_id_delimiter`: the delimiter to extract node_id in test method docstring, default is `@`

- `atomic`: enable or disable atomic and electronic test suit

## options example
```ini
# content of pytest.ini
[pytest]
addopts : --wetest

[wetest]
atomic                 :true
title                  : dummy title
json_report_file       : wetest.json
json_report_indent     : 4
CI_server              : 192.168.1.199
breed_server           : http://192.168.1.199:62180
metadata               : true
meta_delimiter         : @!
meta_assignment_symbol : :
chinese_node_id        : true
node_id_delimiter      : @
```

