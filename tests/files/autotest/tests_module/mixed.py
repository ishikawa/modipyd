import tests_module
import other_module

class RegularObject(object):
    pass

class RegularObject2(other_module.RegularObjectInOtherModule):
    pass

class TestMixed(tests_module.TestCase):
    def test_it(self):
        pass
