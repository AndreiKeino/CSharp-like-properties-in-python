import inspect
import types
from dataclasses import dataclass
from typing import Callable, Any, Type, Final, Set, List, Tuple, ClassVar, Dict, Optional

# https://github.com/sansyrox/nestd
# functions get_all_nested and free_var are borrowed from repository at https://github.com/sansyrox/nestd
# with many thanks to sansyrox


def free_var(val):
    """A function that wraps free variables."""

    def nested():
        return val

    return nested.__closure__[0]


def get_all_nested(fx, *context_vars):
    """Return all nested functions of a function.

    Arguments:
        fx (function or method): A function object with inner function(s).
        *context_vars: context variables corressponding inner functions in the order of occurence.

    Returns:
        A list of tuples, with the first element as the function name and the second element as function object.
        e.g. [("inner_function", <class function....>), ....]
    """
    if not isinstance(fx, (types.FunctionType, types.MethodType)):
        raise Exception("Supplied param is not a function or a method type")

    fx = fx.__code__
    context_variables = list(context_vars)

    output = []
    for const in fx.co_consts:
        if isinstance(const, types.CodeType):
            context = tuple(
                free_var(context_variables[0]) for name in const.co_freevars
            )
            context_variables = context_variables[1:]
            output.append(
                (
                    const.co_name,
                    types.FunctionType(const, globals(), None, None, context),
                )
            )

    return output


@dataclass
class PropVal:
    get_f_name: str = ''
    get_f_func: Optional[Callable[[], Any]] = None
    set_f_name: str = ''
    set_f_func: Optional[Callable[[Any], None]] = None
    del_f_name: str = ''
    del_f_func: Optional[Callable[[], None]] = None

    prop_name: str = ''

    _good: ClassVar[List[str]] = ['get_v', 'set_v', 'del_v']


def _del_cprop_attr(self: Type, attrs: List[str]):
    # delete attributes from a class
    klass = type(self)

    for a in attrs:
        delattr(klass, a)
        d = dir(self)
        if a in d:
            delattr(self, a)


# decorator to decorate class enabled for use C# - like properties
def cprop(klass: Type, arg_1=5): # Class c-Sharp - like decorator of PRoperty Void (without parametes)
    props: List[PropVal] = []
    good = PropVal._good  # ['get_v', 'set_v', 'del_v']
    good_names: Final[Set[str]] = set(good)
    # find all functions decorated with 'pprop' decorator:
    for k, f in klass.__dict__.items():
        if inspect.isfunction(f) and hasattr(f, 'ppropdecor'):
            inner_functions = get_all_nested(f, [])
            all_inner_functions = dict(inner_functions)

            if len(all_inner_functions) == 0:
                raise ValueError(f'{k} property should define at least one inner function')

            if len(all_inner_functions) > 3:
                raise ValueError(f'{k} property should define no more than three inner functions')

            banned = [k for k in all_inner_functions.keys() if k not in good_names]
            if len(banned) > 0:
                raise ValueError((f'{k} property havs not acceptable item(s): {banned}, '
                                 f'acceptable items are: {good_names}'))

            if not good[0] in all_inner_functions.keys():
                raise ValueError(f'{k} property must have function {good[0]}')

            if not good[1] in all_inner_functions.keys() and good[2] in all_inner_functions.keys():
                raise ValueError((f'{k} property to have function {good[2]} ' 
                                  f'must have function {good[1]}'))
            props.append(PropVal(get_f_name=good[0],
                                 get_f_func=all_inner_functions[good[0]],
                                 set_f_name=(set_name := (good[1] if good[1] in all_inner_functions.keys()
                                                          else '')),
                                 set_f_func=(all_inner_functions[good[1]] if set_name else None),
                                 del_f_name=(del_name := (good[2] if good[2]
                                                          in all_inner_functions.keys() else '')),
                                 del_f_func=(all_inner_functions[good[2]] if del_name else None),
                                 prop_name=k))

    existing_keys = klass.__dict__.keys()

    def check_name(attribute_name: str):
        if attribute_name in existing_keys:
            raise AttributeError(f'attribute {attribute_name} already exists')

    for p in props:
        attr_names = []

        def set_attrib(aname: str, value: Any) -> None:
            check_name(aname)
            setattr(klass, aname, value)
            attr_names.append(aname)
        delattr(klass, p.prop_name)

        attr_name = '_' + p.prop_name
        set_attrib(attr_name, None)
        prop_funcs = [p.get_f_func]
        get_func_name = p.prop_name + '_' + p.get_f_name
        set_attrib(get_func_name,  p.get_f_func)
        if p.set_f_func:
            prop_funcs.append(p.set_f_func)
            func_name = p.prop_name + '_' + p.set_f_name
            check_name(func_name)
            set_attrib(func_name, p.set_f_func)

            if p.del_f_func:
                prop_funcs.append(p.del_f_func)
                func_name = p.prop_name + '_' + p.del_f_name
                setattr(klass, func_name, p.del_f_func)

        # finally set the property itself
        check_name(p.prop_name)
        setattr(klass, p.prop_name, property(*prop_funcs))
        attr_names.append(p.prop_name)

        # set the list of names of attributes
        getattr(klass, get_func_name).attr_names = attr_names

        # set the function _del_cprop_attr as class method
        setattr(klass, '_del_cprop_attr', _del_cprop_attr)
    return klass


# # decorator to decorate C# - like properties
def pprop(fn, arg_1=5) -> Callable[..., Any]:  # property c-Sharp - like decorator of PRoperty Void (without parametes)
    fn.ppropdecor = True
    return fn


__version__ = 0.01

if __name__ == '__main__':
    # some tests
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
