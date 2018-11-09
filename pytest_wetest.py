# -*- coding: utf-8 -*-
import pytest
from _pytest.python import Module, Class, Instance, Package, Function
from _pytest.main import Session
from collections import Counter, OrderedDict
from contextlib import contextmanager
import logging
import time
import pytest
import json

from utl import get_test_source, send_to_breed, meta_generator, LoggingHandler
from utl import determiner, validator, encoder


class WetestConfig:
    """
    Wetest plugin custom section
    [wetest]
    k:v
    k:v
    """

    def __init__(self, config):
        if config:
            self.wetest_sections = config.inicfg.config.sections.get('wetest', dict())
        else:
            self.wetest_sections = dict()

    def get_ini(self, k, default=None):
        """pytest getini"""
        val = self.wetest_sections.get(k, '').strip()
        if val:
            return val
        return default


class JSONReport:
    """The JSON report pytest plugin."""

    def __init__(self, config=None):
        self.config = config
        self.wetest_config = WetestConfig(config)
        self.start_time = None
        self.tests = OrderedDict()
        self.warnings = []
        self.report = None
        self.logger = logging.getLogger()
        self.breed_parse_result = None

    @property
    def want_metadata(self):
        mark = self.wetest_config.get_ini('metadata', 'false')
        return mark.lower() == 'true'

    @property
    def title(self):
        title = self.wetest_config.get_ini('title')
        if not title:
            return None
        return title

    @property
    def report_file(self):
        file = self.wetest_config.get_ini('json_report_file') or ''
        if file == 'auto':
            return time.strftime("%Y-%m-%d-%H.%M.%S.json")

        if file.lower() == 'none' or not file:
            return None
        else:
            return file

    @property
    def test_source(self):
        ip = self.wetest_config.get_ini('CI_server') or ''
        return get_test_source(ip)

    @property
    def breed_server_base_url(self):
        base_url = self.wetest_config.get_ini('breed_server') or ''
        if base_url.lower() == 'none' or not base_url:
            return None
        return base_url

    def pytest_configure(self, config):
        # When the plugin is used directly from code, it may have been
        # initialized without a config.
        if self.config is None:
            self.config = config

    def pytest_sessionstart(self, session):
        self.start_time = time.time()

    def pytest_runtest_protocol(self, item, nextitem):
        item._json_log = {}

    @contextmanager
    def capture_log(self, item, when):
        handler = LoggingHandler()
        self.logger.addHandler(handler)
        try:
            yield
        finally:
            self.logger.removeHandler(handler)
        item._json_log[when] = handler.records

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_setup(self, item):
        with self.capture_log(item, 'setup'):
            yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        with self.capture_log(item, 'call'):
            yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_teardown(self, item):
        with self.capture_log(item, 'teardown'):
            yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        try:
            test = self.tests[item]
        except KeyError:
            test = self.json_testitem(item)
            self.tests[item] = test
        # Update total test outcome, if necessary. The total outcome can be
        # different from the outcome of the setup/call/teardown stage.
        outcome = self.config.hook.pytest_report_teststatus(report=report)[0]
        if outcome not in ['passed', '']:
            test['outcome'] = outcome
        test[call.when] = self.json_teststage(item, report)

    def pytest_sessionfinish(self, session):
        json_report = dict(
            title=self.title,
            created=time.time(),
            duration=time.time() - self.start_time,
            exitcode=session.exitstatus,
            root=str(session.fspath),
            environment=getattr(self.config, '_metadata', {}),
            summary=self.json_summary(),
            source=self.test_source,
        )
        json_report['tests'] = list(self.tests.values())
        json_report['warnings'] = self.warnings

        if self.report_file:
            self.save_report(json_report)

        if self.breed_server_base_url:
            self.breed_parse_result = send_to_breed(self.breed_server_base_url, json_report)

    def pytest_logwarning(self, code, fslocation, message, nodeid):
        self.warnings.append({
            'code': code,
            'path': str(fslocation),
            'nodeid': nodeid,
            'message': message,
        })

    def pytest_terminal_summary(self, terminalreporter):
        if self.report_file:
            terminalreporter.write_sep('=', 'JSON report')
            terminalreporter.write_line(f'report written to: {self.report_file}')
        if self.breed_server_base_url:
            terminalreporter.write_sep('=', 'Sent to Breed server')
            terminalreporter.write_line(f'{self.breed_parse_result}')

    def add_metadata(self, docstring):
        if self.want_metadata:
            return {'metadata': meta_generator(
                docstring,
                self.wetest_config.get_ini('meta_delimiter', '@!'),
                self.wetest_config.get_ini('meta_assignment_symbol', ':')
            )}
        return {}

    def save_report(self, json_report):
        """Save the JSON report to file."""
        with open(self.report_file, 'w') as f:
            indent = self.wetest_config.get_ini('json_report_indent')
            json.dump(
                json_report,
                f,
                indent=int(indent) if indent else None,
            )

    def json_location(self, node):
        """Return JSON-serializable node location."""
        try:
            path, line, domain = node.location
        except AttributeError:
            return {}
        return {
            'path': path,
            'lineno': line,
            'domain': domain,
        }

    def json_testitem(self, item):
        """Return JSON-serializable test item."""
        return {
            'nodeid': item.nodeid,
            # Adding the location in the collector dict *and* here appears
            # redundant, but the docs say they may be different
            **self.json_location(item),
            **self.add_metadata(item.obj.__doc__ or ''),
            # item.keywords is actually a dict, but we just save the keys
            'keywords': list(item.keywords),
            # The outcome will be overridden in case of failure
            'outcome': 'passed',
        }

    def json_teststage(self, item, report):
        """Return JSON-serializable test stage (setup/call/teardown)."""
        stage = {
            'duration': report.duration,
            'outcome': report.outcome,
            **self.json_streams(item, report.when),
        }
        if report.longreprtext:
            stage['longrepr'] = report.longreprtext
        return stage

    def json_streams(self, item, when):
        """Return JSON-serializable output of the standard streams."""
        return {key: val for when_, key, val in item._report_sections if
                when_ == when and key in ['stdout', 'stderr']}

    def json_summary(self):
        """Return JSON-serializable test result summary."""
        summary = Counter([t['outcome'] for t in self.tests.values()])
        summary['total'] = sum(summary.values())
        return summary


class ChineseNode:
    def __init__(self, config):
        self.config = WetestConfig(config)

    def pytest_itemcollected(self, item):
        parts = []
        custom_cls_id = None

        def traveller(item):
            nonlocal parts, custom_cls_id
            if isinstance(item, Function):
                custom_func_id = getattr(item.obj, '__doc__', None)
                func_id = item.originalname or item.name

                custom_func_id = determiner(
                    custom_func_id,
                    self.config.get_ini('node_id_delimiter', '@')
                )

                if custom_func_id:
                    func_id = validator(custom_func_id)
                parts.append(func_id)

            if isinstance(item, Instance):
                custom_cls_id = getattr(item.obj, '__doc__', None)
                parts.append(item.name)
            if isinstance(item, Class):
                cls_id = item.name

                custom_cls_id = determiner(
                    custom_cls_id,
                    self.config.get_ini('node_id_delimiter', '@')
                )

                if custom_cls_id:
                    cls_id = validator(custom_cls_id)
                parts.append(cls_id)

            if isinstance(item, Module) and not isinstance(item, Package):
                parts.append(item.nodeid)

            if isinstance(item, Package):
                # todo 支持模块级
                pass

            if not isinstance(item, Session):
                traveller(item.parent)

        if self.config.get_ini('chinese_node_id', 'false').lower() == 'true':
            traveller(item)
            node_id = '::'.join(reversed(parts))
            params = getattr(item, '_genid', None)
            if params:
                node_id = f"{node_id}[{validator(encoder(params))}]"
            item._nodeid = node_id


class Atomic:
    def __init__(self, config):
        self.config = WetestConfig(config)
        if self.config.get_ini('atomic', 'false').lower() == 'true':
            self.state = True
        else:
            self.state = False

    def pytest_configure(self, config):
        """Register the "run" marker."""
        if self.state:
            config_line = (
                'atomic: specify a atomic test. '
            )
            config.addinivalue_line('markers', config_line)

    def pytest_runtest_setup(self, item):
        if item.get_closest_marker('atomic'):
            item.parent._previous_failed = False
        if getattr(item.parent, '_previous_failed', False) and not item.get_closest_marker('electronic'):
            pytest.skip(item.parent._skip_reason)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item):
        outcome = yield
        report = outcome.get_result()
        if report.failed and item.get_closest_marker('atomic'):
            item.parent._previous_failed = True
            item.parent._skip_reason = item.get_closest_marker('atomic').args[0] if item.get_closest_marker(
                'atomic').args else 'This is atomic testsuit!'


def pytest_configure(config):
    if config.option.wetest:
        json_report_plugin = JSONReport(config)
        config.pluginmanager.register(json_report_plugin, 'breed_adapter')

        chinese_node_plugin = ChineseNode(config)
        config.pluginmanager.register(chinese_node_plugin, 'chinese_node')

        atomic_plugin = Atomic(config)
        config.pluginmanager.register(atomic_plugin, 'atomic')


def pytest_addoption(parser):
    group = parser.getgroup('wetest', 'Welian wetest')
    group.addoption(
        '--wetest',
        default=False,
        action='store_true',
        help=
        "activate wetest plugin"
        "configurations should under [wetest] section in pytest.ini."
        "available options :"
        " title,"
        " json_report_file,"
        " json_report_indent,"
        " metadata,"
        " meta_delimiter,"
        " meta_assignment_symbol,"
        " chinese_node_id,"
        " node_id_delimiter,"
        " CI_server,"
        " breed_server,"
        "atomic"
    )
