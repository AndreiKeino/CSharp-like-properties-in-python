# CSharp-like-properties-in-python.  
### Properties in python that looks a bit like C# ones   
### These can be though of as an alternative implementation of the @property decorator.
## Pros:
### 1. A bit less of typing.
### 2. Better code structuring.
## Cons:
### 1. The implementation can miss something that can be done with good old property declaration.
### 2. A lot of things works "behind the scene", i.e. implicitly .

##### functions get_all_nested and free_var are borrowed from repository at https://github.com/sansyrox/nestd  
##### with many thanks to sansyrox 
   
##### To use this code copy the file cslike_props.py in your project.   
examle of usage:  

```python

from cslike_props import cprop, pprop, _del_cprop_attr

@cprop
class TestClass:

    def __init__(self, test_prop_one, test_prop_py, test_prop_two):
        self.test_prop_one = test_prop_one
        self.test_prop_two = test_prop_two
        self.test_prop_py = test_prop_py

    def funct(self):
        print('in TestClass:funct')

    # if uncommented there will be AttributeError: attribute test_prop_one_get_v already exists
    # def test_prop_one_get_v(self):
    #     pass

    @pprop
    def test_prop_one(self):
        # property name will be the same as the function name - test_prop_one
        # the getter declaration, underlying getter name is test_prop_one_get_v
        def get_v(self):
            return self._test_prop_one * 5

        # the setter declaration, underlying setter name is test_prop_one_set_v
        def set_v(self, value):
            self._test_prop_one = value * 5

        # the deleter declaration, underlying deleter name is test_prop_one_del_v
        def del_v(self):
            self._del_cprop_attr(self.test_prop_one_get_v.attr_names)

        # if uncommented there will be
        # ValueError: test_prop_one property should define no more than three inner functions
        # def delete2(self):
        #     pass

    # example of pure pythonic property for comparison with
    # example of the C# - like property test_prop_one property
    # As it can be seen here is a bit more code than in the test_prop_one example,
    # the functions in the property definition could be spread over the entire class
    # without any consequences
    # whereas the C# - like property requires
    # all the functions in the property definition are nested inside
    # property definition ->

    def test_prop_py_get(self):
        return self._test_prop_py * 5 ** 3

    def test_prop_py_set(self, value):
        self._test_prop_py = value * 5 ** 3

    def test_prop_py_delete(self):
        attrs = ['test_prop_py_get', 'test_prop_py_set', 'test_prop_py_delete']
        _del_cprop_attr(self, attrs)
        del self._test_prop_py

    test_prop_py = property(test_prop_py_get, test_prop_py_set, test_prop_py_delete)

    # <- example of pure pythonic property for comparison with
    # example of the C# - like property test_prop_one property

    @pprop
    def test_prop_two(self):
        # attribute name will be the same as the function name - test_prop_two

        def get_v(self):
            return self._test_prop_two * 5 ** 2

        def set_v(self, value):
            self._test_prop_two = value * 5 ** 2

x, y, z = 555, 5, 55555


t = TestClass(test_prop_one=x, test_prop_py=y, test_prop_two=z)

assert t.test_prop_one == x * 5 ** 2
assert t.test_prop_py == y * 5 ** 3 * 5 ** 3
assert t.test_prop_two == z * 5 ** 2 * 5 ** 2

a = 25
t.test_prop_one = a
b = 5
t.test_prop_two = b

assert t._test_prop_one == a * 5
assert t._test_prop_two == b * 5 ** 2

assert t.test_prop_one == a * 5 * 5
assert t.test_prop_two == b * 5 ** 2 * 5 ** 2


attr_one_names = ['_test_prop_one', 'test_prop_one_get_v', 'test_prop_one_set_v', 'test_prop_one']
assert t.test_prop_one_get_v.attr_names == \
       attr_one_names

for a in attr_one_names:
    assert hasattr(TestClass, a)

del t.test_prop_one

for a in attr_one_names:
    assert not hasattr(TestClass, a)

assert t.test_prop_two_get_v.attr_names == \
       ['_test_prop_two', 'test_prop_two_get_v', 'test_prop_two_set_v', 'test_prop_two']

attr_py_names = ['test_prop_py_get', 'test_prop_py_set', 'test_prop_py_delete']

for a in attr_py_names:
    assert hasattr(TestClass, a)

del t.test_prop_py

for a in attr_py_names:
    assert not hasattr(TestClass, a)

assert not hasattr(TestClass, '_test_prop_py')


```
