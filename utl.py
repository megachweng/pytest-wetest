import logging
import socket
import re
import requests


def get_test_source(ci_address):
    """判断测试来源0：CI 1：本地调试"""
    sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sc.connect(('114.114.114.114', 1))
    if str(sc.getsockname()[0]) == ci_address:
        return 'CI'
    else:
        return 'Local'


def meta_generator(docstring: str, meta_delimiter: str, meta_assignment_symbol: str):
    lines = docstring.splitlines()
    meta = {}
    reg = f'^\s*{re.escape(meta_delimiter)}\s*(\S+)\s*{re.escape(meta_assignment_symbol)}\s*(.*)'
    for line in lines:
        try:
            groups = re.match(reg, line).groups()
            meta[groups[0]] = groups[1]
        except AttributeError:
            pass
    return meta


def send_to_breed(base_url, json_report):
    s = requests.post(f"{base_url}/report/parse", json=json_report)
    return s.text


class LoggingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        d = dict(record.__dict__)
        d['msg'] = record.getMessage()
        d['args'] = None
        d['exc_info'] = None
        d.pop('message', None)
        self.records.append(d)


def validator(node_id: str):
    node_id = node_id.strip()
    for char in '[]()/ \\':
        node_id = node_id.replace(char, '_')
    return node_id.replace('::', '_')


def encoder(escaped: str):
    return escaped.encode().decode('unicode-escape')


def determiner(docstring: str, node_id_delimiter: str):
    if docstring:
        lines = [line.strip() for line in docstring.splitlines() if line.strip() != '']
        if lines[0].startswith(f'{node_id_delimiter} '):
            return lines[0][2:]
    return False
