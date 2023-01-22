# CSharp-like-properties-in-python
properties in python that looks a bit like C# ones 
to use this code copy the file cslike_props.py in your project
examle of usage:

```python
from cslike_props import cprop, pprop

@cprop
class TestClass:

    def __init__(self, test_prop_one, test_prop_two):
        self.test_prop_one = test_prop_one
        self.test_prop_two = test_prop_two

    def funct(self):
        print('in TestClass:funct')

    # if uncommented there will be AttributeError: attribute test_prop_one_get_v already exists
    # def test_prop_one_get_v(self):
    #     pass

    @pprop
    def test_prop_one(self):
        # attribute name will be the same as the function name - test_prop_one

        def get_v(self):
            return self._test_prop_one

        def set_v(self, value):
            self._test_prop_one = value

        def del_v(self):
            self._del_cprop_attr(self.test_prop_one_get_v.attr_names)

        # if uncommented there will be
        # ValueError: test_prop_one property should define no more than three inner functions
        # def delete2(self):
        #     pass

    @pprop
    def test_prop_two(self):
        # attribute name will be the same as the function name - test_prop_two

        def get_v(self):
            return self._test_prop_two

        def set_v(self, value):
            self._test_prop_two = value


t = TestClass(test_prop_two=555, test_prop_one=55555)
t.test_prop_one = 5 * 5

t.test_prop_two = 5

assert t.test_prop_two == 5
assert t.test_prop_one == 5 * 5

attr_one_names = ['_test_prop_one', 'test_prop_one_get_v', 'test_prop_one_set_v', 'test_prop_one']
assert t.test_prop_one_get_v.attr_names == \
       attr_one_names

for a in attr_one_names:
    assert hasattr(TestClass, a) #  or hasattr(t, a)

del t.test_prop_one

for a in attr_one_names:
    assert (not hasattr(TestClass, a))

assert t.test_prop_two_get_v.attr_names == \
       ['_test_prop_two', 'test_prop_two_get_v', 'test_prop_two_set_v', 'test_prop_two']

```
