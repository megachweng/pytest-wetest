# Metadata

```python
def test_meta():
    """
    @! key_1 : value_1
    @! key_2 : value_2
    """
    assert 1
```
**Notice**: metadata only exists in test method or test function. **comment('#')** cannot be parsed 
```json
# content of json report
{
  ...
  "tests": [
    {
      "nodeid": "test_me.py::test_meta",
      "metadata": {
        "key_1": "value_1",
        "key_2": "value_2"
      },
      ...
}
```

# Node_id

## Custom node_id
```python
def test_original():
    """@ my_name"""
    assert 1

# the output
test_demo.py::my_name PASSED 
```
## None-ascii node_id
```python
def test_original():
    """@ 中文node_id"""
    assert 1

# the output
test_demo.py::中文node_id PASSED 
```

## Parametrize none-ascii ids
```python
import pytest
@pytest.mark.parametrize('val',[1, 2],ids=['一', '二'])
def test_original(val):
    """@ 中文node_id"""
    assert 1

# the output
test_demo.py::中文node_id[一] PASSED 
test_demo.py::中文node_id[二] PASSED 
```

# Atomic test suit
```python
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



# the output
test_multi_scope_atomic.py::test_fn1 FAILED                              [ 10%]
test_multi_scope_atomic.py::test_fn2 SKIPPED                             [ 20%]
test_multi_scope_atomic.py::TestCls::test_1 FAILED                       [ 30%]
test_multi_scope_atomic.py::TestCls::test_2 PASSED                       [ 40%]
test_multi_scope_atomic.py::TestCls::test_3 SKIPPED                      [ 50%]
test_multi_scope_atomic.py::TestCls::test_4 PASSED                       [ 60%]
test_multi_scope_atomic.py::TestCls::test_5 SKIPPED                      [ 70%]
test_multi_scope_atomic.py::test_fn3 SKIPPED                             [ 80%]
test_multi_scope_atomic.py::test_fn4 FAILED                              [ 90%]
test_multi_scope_atomic.py::test_fn5 SKIPPED                             [100%]

```