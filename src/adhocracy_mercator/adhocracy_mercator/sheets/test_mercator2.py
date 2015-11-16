from datetime import datetime
from datetime import timedelta

from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises


class TestUserInfoSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator2 import userinfo_meta
        return userinfo_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_mercator.sheets.mercator2 import IUserInfo
        from adhocracy_mercator.sheets.mercator2 import UserInfoSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IUserInfo
        assert inst.meta.schema_class == UserInfoSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'first_name': '',
                  'last_name': '',
                  }
        assert inst.get() == wanted


class TestOrganizationInfoSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator2 import organizationinfo_meta
        return organizationinfo_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_mercator.sheets.mercator2 import IOrganizationInfo
        from adhocracy_mercator.sheets.mercator2 import OrganizationInfoSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IOrganizationInfo
        assert inst.meta.schema_class == OrganizationInfoSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'name': '',
                  'city': '',
                  'country': 'DE',
                  'help_request': '',
                  'registration_date': None,
                  'website': '',
                  'contact_email': '',
                  'status': 'other',
                  'status_other': '',
                  }
        assert inst.get() == wanted

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestOrganizationInfoSchema:

    @fixture
    def inst(self):
        from adhocracy_mercator.sheets.mercator2 import OrganizationInfoSchema
        return OrganizationInfoSchema()

    @fixture
    def cstruct_required(self):
        return {'country': 'DE',
                'name': 'Name',
                'status': 'planned_nonprofit',
                'contact_email': 'anna@example.com',
                'registration_date': '2015-02-18T14:17:24+00:00',
                'city': 'Berlin',
                }

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'city': 'Required',
                                        'contact_email': 'Required',
                                        'country': 'Required',
                                        'name': 'Required',
                                        'registration_date': 'Required',
                                        'status': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        from pytz import UTC
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == \
            {'country': 'DE',
             'name': 'Name',
             'status': 'planned_nonprofit',
             'contact_email': 'anna@example.com',
             'registration_date': datetime(2015, 2, 18,
                                           14, 17, 24, 0, tzinfo=UTC),
             'city': 'Berlin',
            }

    def test_deserialize_with_status_other_and_no_description(
            self, inst, cstruct_required):
        from colander import Invalid
        cstruct = cstruct_required
        cstruct['status'] = 'other'
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'status_other':
                                        'Required iff status == other'}

    def test_deserialize_with_status_support_needed_and_no_help_request(
            self, inst, cstruct_required):
        from colander import Invalid
        cstruct = cstruct_required
        cstruct['status'] = 'support_needed'
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'help_request':
                                        'Required iff status == support_needed'}


class TestPartnersSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator2 import partners_meta
        return partners_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import IPartners
        from adhocracy_mercator.sheets.mercator2 import PartnersSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == IPartners
        assert inst.meta.schema_class == PartnersSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'partner1_name': '',
                  'partner1_website': '',
                  'partner1_country': 'DE',
                  'partner2_name': '',
                  'partner2_website': '',
                  'partner2_country': 'DE',
                  'partner3_name': '',
                  'partner3_website': '',
                  'partner3_country': 'DE',
                  'other_partners': '',
                  'has_partners': False}
        assert inst.get() == wanted

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)

class TestTopicSchema:

    @fixture
    def inst(self):
        from .mercator2 import TopicSchema
        return TopicSchema()

    @fixture
    def cstruct_required(self):
        return {'topic': 'urban_development'}

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'topic': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == \
            {'topic': 'urban_development'}

class TestTopicSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator2 import topic_meta
        return topic_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import ITopic
        from adhocracy_mercator.sheets.mercator2 import TopicSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == ITopic
        assert inst.meta.schema_class == TopicSchema

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestDurationSchema:

    @fixture
    def inst(self):
        from .mercator2 import DurationSchema
        return DurationSchema()

    @fixture
    def cstruct_required(self):
        return {'duration': '6'}

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'duration': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == \
            {'duration': 6}


class TestDurationSheet:

    @fixture
    def meta(self):
        from .mercator2 import duration_meta
        return duration_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import IDuration
        from adhocracy_mercator.sheets.mercator2 import DurationSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == IDuration
        assert inst.meta.schema_class == DurationSchema

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestLocationSchema:

    @fixture
    def inst(self):
        from .mercator2 import LocationSchema
        return LocationSchema()

    @fixture
    def cstruct_required(self):
        return {'city': 'Berlin',
                'country': 'DE',
                'has_link_to_ruhr': 'false',
                'link_to_ruhr': ''
        }

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'city': 'Required',
                                        'country': 'Required',
                                        'has_link_to_ruhr': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == \
              {'city': 'Berlin',
               'country': 'DE',
               'has_link_to_ruhr': False}

class TestLocationSheet:

    @fixture
    def meta(self):
        from .mercator2 import location_meta
        return location_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import ILocation
        from adhocracy_mercator.sheets.mercator2 import LocationSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == ILocation
        assert inst.meta.schema_class == LocationSchema

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestLocationSchema:

    @fixture
    def inst(self):
        from .mercator2 import StatusSchema
        return StatusSchema()

    @fixture
    def cstruct_required(self):
        return {'status': 'other'}

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'status': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == {'status': 'other'}


class TestLocationSheet:

    @fixture
    def meta(self):
        from .mercator2 import status_meta
        return status_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import IStatus
        from adhocracy_mercator.sheets.mercator2 import StatusSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == IStatus
        assert inst.meta.schema_class == StatusSchema

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestRoadToImpactSchema:

    @fixture
    def inst(self):
        from .mercator2 import RoadToImpactSchema
        return RoadToImpactSchema()

    @fixture
    def cstruct_required(self):
        return {'challenge': 'the challenge',
                'aim': 'the aim',
                'plan': 'the plan',
                'doing': 'the actions',
                'team': 'the team',
                'other': 'extra'}

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'aim': 'Required',
                                        'challenge': 'Required',
                                        'doing': 'Required',
                                        'other': 'Required',
                                        'plan': 'Required',
                                        'team': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == cstruct_required


class TestRoadToImpactSheet:

    @fixture
    def meta(self):
        from .mercator2 import roadtoimpact_meta
        return roadtoimpact_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import IRoadToImpact
        from adhocracy_mercator.sheets.mercator2 import RoadToImpactSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == IRoadToImpact
        assert inst.meta.schema_class == RoadToImpactSchema

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestSelectionCriteriaSchema:

    @fixture
    def inst(self):
        from .mercator2 import SelectionCriteriaSchema
        return SelectionCriteriaSchema()

    @fixture
    def cstruct_required(self):
        return {'connection_and_cohesion_europe': 'content connection',
                'difference': 'content difference',
                'practical_relevance': 'content relevance'}

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == \
            {'connection_and_cohesion_europe': 'Required',
             'difference': 'Required',
             'practical_relevance': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == cstruct_required


class TestSelectionCriteriaSheet:

    @fixture
    def meta(self):
        from .mercator2 import selectioncriteria_meta
        return selectioncriteria_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import ISelectionCriteria
        from adhocracy_mercator.sheets.mercator2 import SelectionCriteriaSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == ISelectionCriteria
        assert inst.meta.schema_class == SelectionCriteriaSchema

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestFinancialPlanningSchema:

    @fixture
    def inst(self):
        from .mercator2 import FinancialPlanningSchema
        return FinancialPlanningSchema()

    @fixture
    def cstruct_required(self):
        return {'budget': '10000',
                'requested_funding': '500',
                'major_expenses': 'travel'}

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == \
            {'budget': 'Required',
             'major_expenses': 'Required',
             'requested_funding': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == \
            {'budget': 10000,
             'requested_funding': 500,
             'major_expenses': 'travel'}


class TestFinancialPlanningSheet:

    @fixture
    def meta(self):
        from .mercator2 import financialplanning_meta
        return financialplanning_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import IFinancialPlanning
        from adhocracy_mercator.sheets.mercator2 import FinancialPlanningSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == IFinancialPlanning
        assert inst.meta.schema_class == FinancialPlanningSchema

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestCommunitySchema:

    @fixture
    def inst(self):
        from .mercator2 import CommunitySchema
        return CommunitySchema()

    @fixture
    def cstruct_required(self):
        return {'expected_feedback': 'Nice comments',
                'heard_from': 'website'}

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == \
            {'expected_feedback': 'Required',
             'heard_from': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == cstruct_required


class TestCommunitySheet:

    @fixture
    def meta(self):
        from .mercator2 import community_meta
        return community_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import ICommunity
        from adhocracy_mercator.sheets.mercator2 import CommunitySchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == ICommunity
        assert inst.meta.schema_class == CommunitySchema

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestWinnerInfoSchema:

    @fixture
    def inst(self):
        from .mercator2 import WinnerInfoSchema
        return WinnerInfoSchema()

    @fixture
    def cstruct_required(self):
        return {'explanation': 'Relevant project',
                'funding': '10000'}

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        assert inst.deserialize(cstruct) == {}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == \
            {'explanation': 'Relevant project',
             'funding': 10000}


class TestWinnerInfoSheet:

    @fixture
    def meta(self):
        from .mercator2 import winnerinfo_meta
        return winnerinfo_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import IWinnerInfo
        from adhocracy_mercator.sheets.mercator2 import WinnerInfoSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == IWinnerInfo
        assert inst.meta.schema_class == WinnerInfoSchema

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)
