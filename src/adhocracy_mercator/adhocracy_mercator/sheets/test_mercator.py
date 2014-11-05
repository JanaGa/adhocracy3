from pyramid import testing
from pytest import mark
from pytest import fixture
from pytest import raises


@fixture()
def integration(config):
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.registry')
    config.include('adhocracy_mercator.sheets.mercator')


@mark.usefixtures('integration')
class TestIncludeme:

    def test_includeme_register_userinfo_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import IUserInfo
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IUserInfo)
        assert get_sheet(context, IUserInfo)

    def test_includeme_register_organizationinfo_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import IOrganizationInfo
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IOrganizationInfo)
        assert get_sheet(context, IOrganizationInfo)

    def test_includeme_register_introduction_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import IIntroduction
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IIntroduction)
        assert get_sheet(context, IIntroduction)

    def test_includeme_register_details_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import IDetails
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IDetails)
        assert get_sheet(context, IDetails)

    def test_includeme_register_story_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import IStory
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IStory)
        assert get_sheet(context, IStory)

    def test_includeme_register_outcome_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import IOutcome
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IOutcome)
        assert get_sheet(context, IOutcome)

    def test_includeme_register_steps_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import ISteps
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=ISteps)
        assert get_sheet(context, ISteps)

    def test_includeme_register_value_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import IValue
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IValue)
        assert get_sheet(context, IValue)

    def test_includeme_register_finance_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import IFinance
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IFinance)
        assert get_sheet(context, IFinance)

    def test_includeme_register_experience_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import IExperience
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IExperience)
        assert get_sheet(context, IExperience)

    def test_includeme_register_heardfrom_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import IHeardFrom
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IHeardFrom)
        assert get_sheet(context, IHeardFrom)


class TestUserInfoSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator import userinfo_meta
        return userinfo_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_mercator.sheets.mercator import IUserInfo
        from adhocracy_mercator.sheets.mercator import UserInfoSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IUserInfo
        assert inst.meta.schema_class == UserInfoSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'family_name': '',
                  'personal_name': '',
                  'country': 'DE'}
        assert inst.get() == wanted


class TestOrganizationInfoSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator import organizationinfo_meta
        return organizationinfo_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_mercator.sheets.mercator import IOrganizationInfo
        from adhocracy_mercator.sheets.mercator import OrganizationInfoSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IOrganizationInfo
        assert inst.meta.schema_class == OrganizationInfoSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'country': 'DE',
                  'help_request': '',
                  'name': '',
                  'planned_date': '',
                  'status': 'other',
                  'status_other': '',
                  'website': '',
                  }
        assert inst.get() == wanted


class TestOrganizationInfoSchema:

    @fixture
    def inst(self):
        from adhocracy_mercator.sheets.mercator import OrganizationInfoSchema
        return OrganizationInfoSchema()

    @fixture
    def cstruct_required(self):
        return {'country': 'DE',
                'name': 'Name',
                'status': 'planned_nonprofit',
                }

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'status': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required   # cstruct and appstruct are the same here
        assert inst.deserialize(cstruct_required) == wanted

    def test_deserialize_with_status_other_and_no_description(
            self, inst, cstruct_required):
        from colander import Invalid
        cstruct = cstruct_required
        cstruct['status'] = 'other'
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'status_other':
                                        'Required iff status == other'}

    def test_deserialize_without_name(self, inst, cstruct_required):
        from colander import Invalid
        cstruct = cstruct_required
        cstruct['status'] = 'planned_nonprofit'
        cstruct['name'] = None
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'name': 'Required iff status != other'}

    def test_deserialize_without_country(self, inst, cstruct_required):
        from colander import Invalid
        cstruct = cstruct_required
        cstruct['status'] = 'planned_nonprofit'
        cstruct['country'] = None
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'country':
                                        'Required iff status != other'}

    def test_deserialize_with_status_and_description(self, inst,
                                                     cstruct_required):
        cstruct = cstruct_required
        cstruct['status'] = 'other'
        cstruct['status_other'] = 'Description'
        wanted = cstruct
        assert inst.deserialize(cstruct_required) == wanted


class TestIntroductionSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator import introduction_meta
        return introduction_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_mercator.sheets.mercator import IIntroduction
        from adhocracy_mercator.sheets.mercator import IntroductionSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IIntroduction
        assert inst.meta.schema_class == IntroductionSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'teaser': '', 'title': ''}
        assert inst.get() == wanted


class TestDetailsSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator import details_meta
        return details_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    @fixture
    def resource(self):
        from adhocracy_mercator.sheets.mercator import IDetails
        return testing.DummyResource(__provides__=IDetails)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_mercator.sheets.mercator import IDetails
        from adhocracy_mercator.sheets.mercator import DetailsSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IDetails
        assert inst.meta.schema_class == DetailsSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'description': '',
                  'location_is_specific': False,
                  'location_specific_1': '',
                  'location_specific_2': '',
                  'location_specific_3': '',
                  'location_is_linked_to_ruhr': False,
                  'location_is_online': False,
                  }
        assert inst.get() == wanted


class TestLocationIndex:

    def _make_resource(self, pool_graph, details_appstruct={}):
        from adhocracy_core.interfaces import IResource
        from adhocracy_mercator.sheets.mercator import IMercatorSubResources
        from adhocracy_mercator.sheets.mercator import IDetails
        from adhocracy_core.utils import get_sheet
        resource = testing.DummyResource(__provides__=[IResource,
                                                       IMercatorSubResources])
        pool_graph['res'] = resource
        sub_resources_sheet = get_sheet(resource, IMercatorSubResources)
        details_resource = testing.DummyResource(__provides__=[IResource,
                                                               IDetails])
        details_sheet = get_sheet(details_resource, IDetails)
        details_sheet.set(details_appstruct)
        pool_graph['details'] = details_resource
        sub_resources_sheet.set({'details': details_resource})
        return resource

    @mark.usefixtures('integration')
    def test_index_location_default(self, pool_graph):
        from adhocracy_mercator.sheets.mercator import index_location
        resource = self._make_resource(pool_graph=pool_graph)
        result = index_location(resource, 'default')
        assert result == 'default'

    @mark.usefixtures('integration')
    def test_index_location_is_linked_to_ruhr(self, pool_graph):
        from adhocracy_mercator.sheets.mercator import index_location
        resource = self._make_resource(
            pool_graph=pool_graph,
            details_appstruct={'location_is_linked_to_ruhr': True})
        result = index_location(resource, 'default')
        assert result == ['linked_to_ruhr']

    @mark.usefixtures('integration')
    def test_index_location_is_online_and_linked_to_ruhr(self, pool_graph):
        from adhocracy_mercator.sheets.mercator import index_location
        resource = self._make_resource(
            pool_graph=pool_graph,
            details_appstruct={'location_is_online': True,
                               'location_is_linked_to_ruhr': True})
        result = index_location(resource, 'default')
        assert set(result) == set(['online', 'linked_to_ruhr'])


class TestOutcomeSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator import outcome_meta
        return outcome_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_mercator.sheets.mercator import IOutcome
        from adhocracy_mercator.sheets.mercator import OutcomeSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IOutcome
        assert inst.meta.schema_class == OutcomeSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'outcome': ''}
        assert inst.get() == wanted


class TestFinanceSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator import finance_meta
        return finance_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_mercator.sheets.mercator import IFinance
        from adhocracy_mercator.sheets.mercator import FinanceSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IFinance
        assert inst.meta.schema_class == FinanceSchema

    def test_get_empty(self, meta, context):
        from decimal import Decimal
        inst = meta.sheet_class(meta, context)
        wanted = {'budget': Decimal(0),
                  'granted': False,
                  'other_sources': '',
                  'requested_funding': Decimal(0)}
        assert inst.get() == wanted


class TestExperienceSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator import experience_meta
        return experience_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_mercator.sheets.mercator import IExperience
        from adhocracy_mercator.sheets.mercator import ExperienceSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IExperience
        assert inst.meta.schema_class == ExperienceSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'experience': '',
                  }
        assert inst.get() == wanted
