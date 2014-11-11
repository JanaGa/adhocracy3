from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark

import colander

from adhocracy_core.sheets.rate import IRateable


@fixture
def context(context, service):
    context['rates'] = service
    return context


@fixture
def integration(config):
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets.rate')


def _make_rateable(provides=IRateable):
    return testing.DummyResource(__provides__=provides)


class TestRateSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.rate import rate_meta
        return rate_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.rate import IRate
        from adhocracy_core.sheets.rate import RateSchema
        from adhocracy_core.sheets import GenericResourceSheet
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, GenericResourceSheet)
        assert inst.meta.isheet == IRate
        assert inst.meta.schema_class == RateSchema
        assert inst.meta.create_mandatory

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'subject': '',
                              'object': '',
                              'rate': 0,
                              }


@mark.usefixtures('integration')
class TestRateSchema:

    @fixture
    def subject(self):
        from adhocracy_core.sheets.rate import ICanRate
        return testing.DummyResource(__provides__=ICanRate)

    def test_deserialize_valid(self, context, cornice_request, subject):
        from adhocracy_core.sheets.rate import RateSchema
        schema = RateSchema().bind(request=cornice_request, context=context)
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '1'}
        assert schema.deserialize(data) == {'subject': subject,
                                            'object': object,
                                            'rate': 1}

    def test_deserialize_valid_minus_one(self, context, cornice_request,
                                         subject):
        from adhocracy_core.sheets.rate import RateSchema
        schema = RateSchema().bind(request=cornice_request, context=context)
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '-1'}
        assert schema.deserialize(data) == {'subject': subject,
                                            'object': object,
                                            'rate': -1}

    def test_deserialize_invalid_rate(self, context, cornice_request, subject):
        from adhocracy_core.sheets.rate import RateSchema
        schema = RateSchema().bind(request=cornice_request, context=context)
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '77'}
        with raises(colander.Invalid):
            schema.deserialize(data)

    def test_deserialize_invalid_subject(self, context, cornice_request):
        from adhocracy_core.sheets.rate import RateSchema
        schema = RateSchema().bind(request=cornice_request, context=context)
        subject = testing.DummyResource()
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '0'}
        with raises(colander.Invalid):
            schema.deserialize(data)

    def test_deserialize_invalid_subject_missing(self, context,
                                                 cornice_request):
        from adhocracy_core.sheets.rate import RateSchema
        schema = RateSchema().bind(request=cornice_request, context=context)
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '', 'object': '/object', 'rate': '0'}
        with raises(colander.Invalid):
            schema.deserialize(data)

    def test_deserialize_invalid_object(self, context, cornice_request,
                                        subject):
        from adhocracy_core.sheets.rate import RateSchema
        schema = RateSchema().bind(request=cornice_request, context=context)
        context['subject'] = subject
        object = testing.DummyResource()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '0'}
        with raises(colander.Invalid):
            schema.deserialize(data)

    def test_deserialize_invalid_object_missing(self, context, cornice_request,
                                        subject):
        from adhocracy_core.sheets.rate import RateSchema
        schema = RateSchema().bind(request=cornice_request, context=context)
        context['subject'] = subject
        data = {'subject': '/subject', 'object': '', 'rate': '0'}
        with raises(colander.Invalid):
            schema.deserialize(data)

    def test_deserialize_valid_likeable(self, context, cornice_request,
                                        subject):
        from adhocracy_core.sheets.rate import ILikeable
        from adhocracy_core.sheets.rate import RateSchema
        schema = RateSchema().bind(request=cornice_request, context=context)
        context['subject'] = subject
        object = _make_rateable(ILikeable)
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '1'}
        assert schema.deserialize(data) == {'subject': subject,
                                            'object': object,
                                            'rate': 1}

    def test_deserialize_invalid_rate_with_likeable(self, context,
                                                    cornice_request, subject):
        from adhocracy_core.sheets.rate import ILikeable
        from adhocracy_core.sheets.rate import RateSchema
        schema = RateSchema().bind(request=cornice_request, context=context)
        context['subject'] = subject
        object = _make_rateable(ILikeable)
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '-1'}
        with raises(colander.Invalid):
            assert schema.deserialize(data)


@mark.usefixtures('integration')
class TestRateValidators:

    def test_rateable_rate_validator(self, registry):
        from adhocracy_core.interfaces import IRateValidator
        rateable = _make_rateable()
        validator = registry.getAdapter(rateable, IRateValidator)
        assert validator.validate(1) is True
        assert validator.validate(0) is True
        assert validator.validate(-1) is True
        assert validator.validate(2) is False
        assert validator.validate(-2) is False

    def test_likeable_rate_validator(self, registry):
        from adhocracy_core.interfaces import IRateValidator
        from adhocracy_core.sheets.rate import ILikeable
        rateable = _make_rateable(ILikeable)
        validator = registry.getAdapter(rateable, IRateValidator)
        assert validator.validate(1) is True
        assert validator.validate(0) is True
        assert validator.validate(-1) is False
        assert validator.validate(2) is False


@fixture
def mock_sheet(context, mock_sheet, registry):
    from adhocracy_core.testing import add_and_register_sheet
    from .rate import IRate
    mock_sheet.meta = mock_sheet.meta._replace(isheet=IRate)
    add_and_register_sheet(context, mock_sheet, registry)
    return mock_sheet


def test_index_rate(context, mock_sheet):
    from .rate import index_rate
    context['referenced'] = testing.DummyResource()
    mock_sheet.get.return_value = {'rate': 1}
    assert index_rate(context, None) == 1


@mark.usefixtures('integration')
def test_includeme_register_rate_sheet(config, context):
    from adhocracy_core.sheets.rate import IRate
    from adhocracy_core.utils import get_sheet
    context = testing.DummyResource(__provides__=IRate)
    inst = get_sheet(context, IRate)
    assert inst.meta.isheet is IRate


@mark.usefixtures('integration')
def test_includeme_register_index_rate(registry, context):
    from .rate import IRate
    from substanced.interfaces import IIndexView
    assert registry.adapters.lookup((IRate,), IIndexView, name='adhocracy|rate')
