import unittest

from pyramid import testing
import colander


class HandleError400ColanderInvalidUnitTest(unittest.TestCase):

    def make_one(self, error, request):
        from adhocracy.rest.exceptions import handle_error_400_colander_invalid
        return handle_error_400_colander_invalid(error, request)

    def test_render_exception_error(self):
        from cornice.util import _JSONError
        import json
        request = testing.DummyRequest()
        invalid0 = colander.SchemaNode(typ=colander.String(), name='parent0',
                                       msg='msg_parent')
        invalid1 = colander.SchemaNode(typ=colander.String(), name='child1')
        invalid2 = colander.SchemaNode(typ=colander.String(), name='child2')
        error0 = colander.Invalid(invalid0)
        error1 = colander.Invalid(invalid1)
        error2 = colander.Invalid(invalid2)
        error0.add(error1, 1)
        error1.add(error2, 0)

        inst = self.make_one(error0, request)

        assert isinstance(inst, _JSONError)
        assert inst.status == '400 Bad Request'
        wanted = {'status': 'error',
                  'errors': [['body', 'parent0.child1.child2', '']]}
        assert json.loads(inst.body.decode()) == wanted


class HandleError500ExceptionUnitTest(unittest.TestCase):

    def make_one(self, error, request):
        from adhocracy.rest.exceptions import handle_error_500_exception
        return handle_error_500_exception(error, request)

    def test_render_exception_error(self):
        from cornice.util import _JSONError
        import json
        request = testing.DummyRequest()
        error = Exception('arg1')

        inst = self.make_one(error, request)

        assert isinstance(inst, _JSONError)
        assert inst.status == '500 Internal Server Error'
        wanted = {'status': 'error',
                  'errors': [['internal', "('arg1',)", '']]}
        assert json.loads(inst.body.decode()) == wanted
