import json
import os

import pytest


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*Welian wetest:*',
        '*--wetest*activate wetest plugin*',
    ])


@pytest.mark.parametrize('addopt', ['--wetest', ' '])
def test_plugin_switch(testdir, addopt):
    testdir.makeini(f"""
    [pytest]
    addopts : {addopt}
    """)

    testdir.makepyfile(f"""
    import pytest

    @pytest.fixture(params=['chinese_node', 'breed_adapter','atomic'])
    def plugin_list(request):
        return request.config.pluginmanager.hasplugin(request.param)
    
    def test_do_we_have_plugin(plugin_list):
        assert {'not' if not addopt.strip() else ''} plugin_list
""")

    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_do_we_have_plugin* PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_custom_section_valid(testdir):
    testdir.makeini(f"""
    [pytest]
    addopts : --wetest
    [wetest]
    """)
    testdir.makepyfile(f"""
    import pytest
    def test_custom_section():
        assert 1
    """)
    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_custom_section* PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


class TestFunctionality:
    @pytest.mark.parametrize('title', [' ', 'ascii title', '中文标题'],
                             ids=['empty title', 'pure ascii title', 'none Ascii title'])
    def test_report_title(self, testdir, title):
        testdir.makeini(f"""
            [pytest]
            addopts : --wetest
            [wetest]
            title : {title.strip()}
            json_report_file: tmp.json
            """)

        testdir.makepyfile(f"""
            import pytest
            def test_json_report():
                assert 1
            """)
        result = testdir.runpytest('-v')

        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines([
            '*::test_json_report* PASSED*',
            'report written to: tmp.json'
        ])
        with open('tmp.json') as f:
            j = json.load(f)
            if not title.strip():
                assert j['title'] is None
            else:
                assert j['title'] == title

        # make sure that that we get a '0' exit code for the testsuite
        assert result.ret == 0

    @pytest.mark.parametrize('file_name', ['auto', 'none', 'custom.json', ' '], ids=[
        'auto file name',
        'arbitrary none',
        'custom file',
        'empty'
    ])
    def test_report_file_name(self, file_name, testdir):
        testdir.makeini(f"""
                    [pytest]
                    addopts : --wetest
                    [wetest]
                    json_report_file: {file_name.strip()}
                    """)

        testdir.makepyfile(f"""
                    import pytest
                    def test_json_report_file():
                        assert 1
                    """)
        result = testdir.runpytest('-v')

        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines([
            '*::test_json_report_file* PASSED*',
        ])
        files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith(".json")]
        if file_name not in ['none', ' ']:
            result.stdout.fnmatch_lines([
                'report written to: *'
            ])
            assert files
        else:
            assert not files
        # make sure that that we get a '0' exit code for the testsuite
        assert result.ret == 0

    @pytest.mark.parametrize('state', ['true', 'false', ' '], ids=[
        'enable metadata',
        'disable metadata',
        'empty'
    ])
    def test_metadata_switch(self, state, testdir):
        testdir.makeini(f"""
        [pytest]
        addopts: --wetest
        [wetest]
        json_report_file:tmp.json
        metadata:{state.strip()}
        """)

        testdir.makepyfile(f'''
        def test_metadata():
            """
            @! key1:value1
            @! key2:value2
            """
            assert 1
        ''')
        result = testdir.runpytest('-v')

        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines([
            '*::test_metadata* PASSED*',
            'report written to: tmp.json'
        ])
        with open('tmp.json') as f:
            j = json.load(f)
            if state == 'true':
                assert j['tests'][0]['metadata'] == {
                    'key1': 'value1',
                    'key2': 'value2'
                }
            else:
                assert not j['tests'][0].get('metadata')

            # make sure that that we get a '0' exit code for the testsuite
            assert result.ret == 0

    @pytest.mark.parametrize('meta_delimiter', [' ', '*', '!@'])
    @pytest.mark.parametrize('meta_assignment_symbol', [' ', '*', '!@'])
    def test_meta_delimiter(self, meta_delimiter, meta_assignment_symbol, testdir):

        testdir.makeini(f'''
        [pytest]
        addopts: --wetest
        [wetest]
        json_report_file:tmp.json
        metadata : true
        meta_delimiter : {meta_delimiter.strip()}
        meta_assignment_symbol : {meta_assignment_symbol.strip()}
        ''')

        if not meta_delimiter.strip():
            meta_delimiter = '@!'
        if not meta_assignment_symbol.strip():
            meta_assignment_symbol = ':'

        testdir.makepyfile(f'''
        def test_delimiter():
            """
            {meta_delimiter} key1{meta_assignment_symbol}value1
            {meta_delimiter} key2{meta_assignment_symbol}value2
            """
            assert 1
        ''')
        result = testdir.runpytest('-v')

        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines([
            '*::test_delimiter* PASSED*',
            'report written to: tmp.json'
        ])
        with open('tmp.json') as f:
            j = json.load(f)
            assert j['tests'][0]['metadata'] == {
                'key1': 'value1',
                'key2': 'value2'
            }

            # make sure that that we get a '0' exit code for the testsuite
            assert result.ret == 0

    @pytest.mark.parametrize('state', ['true', 'false', ' '], ids=[
        'enable chinese node_id',
        'disable chinese node_id',
        'empty'
    ])
    def test_node_id_switch(self, state, testdir):
        testdir.makeini(f"""
                [pytest]
                addopts: --wetest
                [wetest]
                chinese_node_id : {state.strip()}
                """)

        testdir.makepyfile(f'''
                def test_node_id():
                    """@ 中文nodeID
                    """
                    assert 1
                ''')
        result = testdir.runpytest('-v')

        # fnmatch_lines does an assertion internally
        if state == 'true':
            result.stdout.fnmatch_lines([
                '*::中文nodeID* PASSED*',
            ])
        else:
            result.stdout.fnmatch_lines([
                '*::test_node_id* PASSED*',
            ])

    @pytest.mark.parametrize('delimiter', [' ', '*', '!@'], ids=[
        'empty',
        '*',
        '!@'
    ])
    def test_node_id_delimiter(self, delimiter, testdir):
        testdir.makeini(f"""
                [pytest]
                addopts: --wetest
                [wetest]
                chinese_node_id : true
                node_id_delimiter: {delimiter.strip()}
                """)

        testdir.makepyfile(f'''
                def test_node_id():
                    """{delimiter.strip() or '@'} 中文nodeID
                    """
                    assert 1
                ''')
        result = testdir.runpytest('-v')

        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines([
            '*::中文nodeID* PASSED*',
        ])


class TestAtomic:

    def test_fuc_atomic(self, testdir):
        testdir.makeini(f'''
            [pytest]
            addopts: --wetest
            [wetest]
            atomic: true
        ''')

        testdir.makepyfile(f'''
            import pytest
            @pytest.mark.atomic
            def test_1():
                assert 0
            def test_2():
                assert 0
            def test_3():
                assert 0
        ''')

        result = testdir.runpytest('-v')
        result.stdout.fnmatch_lines([
            '*test_1*FAILED*',
            '*test_2*SKIPPED*',
            '*test_3*SKIPPED*',
        ])

    def test_fuc_atomic_electronic(self, testdir):
        testdir.makeini(f'''
            [pytest]
            addopts: --wetest
            [wetest]
            atomic: true
        ''')

        testdir.makepyfile(f'''
            import pytest
            @pytest.mark.atomic
            def test_1():
                assert 0
            def test_2():
                assert 0
            @pytest.mark.electronic
            def test_3():
                assert 0
            def test_4():
                assert 0
            def test_5():
                assert 0
        ''')

        result = testdir.runpytest('-v')
        result.stdout.fnmatch_lines([
            '*test_1*FAILED*',
            '*test_2*SKIPPED*',
            '*test_3*FAILED*',
            '*test_4*SKIPPED*',
            '*test_5*SKIPPED*',
        ])

    def test_fuc_multi_atomic_electronic(self, testdir):
        testdir.makeini(f'''
               [pytest]
               addopts: --wetest
               [wetest]
               atomic: true
           ''')

        testdir.makepyfile(f'''
            import pytest
            @pytest.mark.atomic
            def test_1():
               assert 0
            def test_2():
               assert 0
            @pytest.mark.electronic
            def test_3():
               assert 0
            @pytest.mark.atomic
            def test_4():
               assert 0
            def test_5():
               assert 0
            @pytest.mark.electronic
            def test_6():
               assert 0            
            def test_7():
               assert 0            
            @pytest.mark.atomic
            def test_8():
               assert 1
            def test_9():
               assert 1
           ''')

        result = testdir.runpytest('-v')
        result.stdout.fnmatch_lines([
            '*test_1*FAILED*',
            '*test_2*SKIPPED*',
            '*test_3*FAILED*',
            '*test_4*FAILED*',
            '*test_5*SKIPPED*',
            '*test_6*FAILED*',
            '*test_7*SKIPPED*',
            '*test_8*PASSED*',
            '*test_9*PASSED*',
        ])

    def test_cls_atomic_electronic(self, testdir):
        testdir.makeini(f'''
        [pytest]
        addopts: --wetest
        [wetest]
        atomic: true
        ''')

        testdir.makepyfile(f'''
        import pytest
        class TestCls:
            @pytest.mark.atomic
            def test_1(self):
                assert 0
        
            @pytest.mark.electronic
            def test_2(self):
                assert 1
        
            def test_3(self):
                assert 0
        
            @pytest.mark.electronic
            def test_4(self):
                assert 1
        
            def test_5(self):
                assert 0
        ''')
        result = testdir.runpytest('-v')
        result.stdout.fnmatch_lines([
            '*test_1*FAILED*',
            '*test_2*PASSED*',
            '*test_3*SKIPPED*',
            '*test_4*PASSED*',
            '*test_5*SKIPPED*',
        ])

    def test_multi_scope_atomic(self, testdir):
        testdir.makeini(f'''
        [pytest]
        addopts: --wetest
        [wetest]
        atomic: true
        ''')

        testdir.makepyfile(f'''
        import pytest
        
        @pytest.mark.atomic
        def test_fn1():
            assert 0
        
        def test_fn2():
            assert 0
            
        class TestCls:
            @pytest.mark.atomic
            def test_1(self):
                assert 0

            @pytest.mark.electronic
            def test_2(self):
                assert 1

            def test_3(self):
                assert 0

            @pytest.mark.electronic
            def test_4(self):
                assert 1

            def test_5(self):
                assert 0
        
        def test_fn3():
            assert 0

        @pytest.mark.atomic
        def test_fn4():
            assert 0

        def test_fn5():
            assert 0
        ''')
        result = testdir.runpytest('-v')
        result.stdout.fnmatch_lines([
            '*test_fn1*FAILED*',
            '*test_fn2*SKIPPED*',
            '*test_1*FAILED*',
            '*test_2*PASSED*',
            '*test_3*SKIPPED*',
            '*test_4*PASSED*',
            '*test_5*SKIPPED*',
            '*test_fn3*SKIPPED*',
            '*test_fn4*FAILED*',
            '*test_fn5*SKIPPED*',
        ])
