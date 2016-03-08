from pyrsistent import discard
from pyrsistent import freeze
from pytest import fixture
from pytest import mark
from pytest import raises
from unittest.mock import Mock
import pytest
from substanced.workflow import WorkflowError


@fixture
def registry(registry_with_content):
    return registry_with_content


class TestAdhocracyACLWorkflow:

    @fixture
    def inst(self):
        from . import AdhocracyACLWorkflow
        inst = AdhocracyACLWorkflow('draft', 'sample')
        return inst

    def test_create(self, inst):
        from substanced.workflow import IWorkflow
        from adhocracy_core.interfaces import IAdhocracyWorkflow
        assert IWorkflow.providedBy(inst)
        assert IAdhocracyWorkflow.providedBy(inst)
        from zope.interface.verify import verifyObject
        assert verifyObject(IAdhocracyWorkflow, inst)

    def test_get_next_states(self, inst, context, request, mock_workflow):
        fut = inst.__class__.get_next_states
        mock_workflow.state_of.return_value = 'draft'
        mock_workflow.get_transitions.return_value = [{'to_state': 'announced'}]
        assert fut(mock_workflow, context, request) == ['announced']
        assert mock_workflow.get_transitions.called_with(context, request,
                                                         from_state='draft')

    def test_get_next_states_with_two_transitions_same_state(
            self, inst, context, request, mock_workflow):
        fut = inst.__class__.get_next_states
        mock_workflow.state_of.return_value = 'draft'
        mock_workflow.get_transitions.return_value = [{'to_state': 'announced'},
                                                      {'to_state': 'announced'}]
        assert fut(mock_workflow, context, request) == ['announced']
        assert mock_workflow.get_transitions.called_with(context, request,
                                                         from_state='draft')


class TestAddWorkflow:

    @fixture
    def registry(self, mock_content_registry):
        registry = Mock(content=mock_content_registry)
        registry.content.permissions = ['view']
        return registry

    @fixture
    def cstruct(self) -> dict:
        """Return example workflow cstruct with required data."""
        cstruct = freeze(
            {'initial_state': 'draft',
             'states': {'draft': {'acm': {'principals':           ['moderator'],
                                          'permissions': [['view', 'Deny']]}},
                        'announced': {'acl': []}},
             'transitions': {'to_announced': {'from_state': 'draft',
                                              'to_state': 'announced',
                                              'permission': 'do_transition',
                                              'callback': None,
                                              }},
             })
        return cstruct

    def call_fut(self, registry, cstruct, name):
        from .sample import add_workflow
        return add_workflow(registry, cstruct, name)

    def test_add_cstruct_to_workflows_meta(self, registry, cstruct):
        self.call_fut(registry, cstruct, 'sample')
        meta = registry.content.workflows_meta['sample']
        assert 'name' not in meta
        assert meta['states']
        assert meta['transitions']
        assert meta['initial_state']

    def test_create_workflow_and_add_to_workflows_meta(self, registry, cstruct):
        from substanced.workflow import ACLWorkflow
        self.call_fut(registry, cstruct, 'sample')
        workflow = registry.content.workflows['sample']
        assert workflow.type == 'sample'
        assert isinstance(workflow, ACLWorkflow)

    def test_create_workflow_and_add_states(self, registry, cstruct):
        self.call_fut(registry, cstruct, 'sample')
        workflow = registry.content.workflows['sample']
        states = sorted(workflow.get_states(None, None),
                        key=lambda x: x['name'])
        assert states[0]['initial'] is False
        assert workflow._states['draft'].acl == [('Deny', 'role:moderator', 'view')]
        assert states[1]['initial'] is True

    def test_create_workflow_and_add_transitions(self, registry, cstruct):
        transition_data = cstruct['transitions']['to_announced']
        new_cstruct = cstruct.transform(('transitions', 'to_announced', 'name'), 'to_announced')
        self.call_fut(registry, new_cstruct, 'sample')
        workflow = registry.content.workflows['sample']
        assert workflow._transitions['to_announced'] == transition_data.update({'name': 'to_announced'})

    def test_raise_if_cstruct_not_valid(self, registry, cstruct):
        from adhocracy_core.exceptions import ConfigurationError
        cstruct = cstruct.transform(('transitions', 'to_announced', 'from_state'), discard)
        with raises(ConfigurationError) as err:
            self.call_fut(registry, cstruct, 'sample')
        assert 'Required' in err.value.__str__()

    @fixture
    def mock_workflow(self, monkeypatch):
        from adhocracy_core.workflows import AdhocracyACLWorkflow
        mock = Mock(spec=AdhocracyACLWorkflow)
        monkeypatch.setattr('adhocracy_core.workflows.AdhocracyACLWorkflow',
                            mock)
        return mock

    def test_create_workflow_and_check(self, registry, cstruct, mock_workflow):
        self.call_fut(registry, cstruct, 'sample')
        assert mock_workflow.return_value.check.called

    def test_raise_if_workflow_error(self, registry, cstruct, mock_workflow):
        from substanced.workflow import WorkflowError
        from adhocracy_core.exceptions import ConfigurationError
        mock_workflow.return_value.check.side_effect = WorkflowError('msg')
        with raises(ConfigurationError) as err:
            self.call_fut(registry, cstruct, 'sample')
        assert 'msg' in err.value.__str__()


@mark.usefixtures('integration')
class TestTransitionToStates:

    def _add_workflow(self, registry, name):
        from . import add_workflow
        cstruct = freeze(
            {'initial_state': 'draft',
             'states': {'draft': {'acm': {'principals':           ['moderator'],
                                          'permissions': [['view', 'Deny']]}},
                        'announced': {'acl': []},
                        'participate': {'acl': []}},
             'transitions': {'to_announced': {'from_state': 'draft',
                                              'to_state': 'announced',
                                              'permission': 'do_transition',
                                              'callback': None,
                                              },
                             'to_participate': {'from_state': 'announced',
                                                'to_state': 'participate',
                                                'permission': 'do_transition',
                                                'callback': None,
                             }},
             })
        add_workflow(registry, cstruct, name)

    @fixture
    def resource_meta(self, resource_meta):
        return resource_meta._replace(workflow_name='test_workflow')

    def call_fut(self, *args, **kwargs):
        from . import transition_to_states
        return transition_to_states(*args, **kwargs)

    def test_do_all_transitions_needed_to_set_state(self, integration, context,
                                                    resource_meta):
        registry = integration.registry
        self._add_workflow(registry, 'test_workflow')
        registry.content.resources_meta[resource_meta.iresource] = resource_meta
        self.call_fut(context, ['announced', 'participate'], registry)

        workflow = registry.content.workflows['test_workflow']
        assert workflow.state_of(context) is 'participate'

    def test_error_if_state_already_set(self, integration, context,
                                         resource_meta):
        from pyramid.request import Request
        registry = integration.registry
        self._add_workflow(registry, 'test_workflow')
        registry.content.resources_meta[resource_meta.iresource] = resource_meta
        request = Request.blank('/dummy')
        request.registry = registry
        workflow = registry.content.workflows['test_workflow']
        workflow.initialize(context)
        workflow.transition_to_state(context, request, 'announced')
        workflow.transition_to_state(context, request, 'participate')

        with pytest.raises(WorkflowError):
            self.call_fut(context, ['announced', 'participate'], registry)

    def test_optionally_reset_to_initial_state(self, integration, context,
                                               resource_meta):
        registry = integration.registry
        self._add_workflow(registry, 'test_workflow')
        registry.content.resources_meta[resource_meta.iresource] = resource_meta
        self.call_fut(context, ['announced', 'participate'], registry)

        self.call_fut(context, [], registry, reset=True)
        workflow = registry.content.workflows['test_workflow']
        assert workflow.state_of(context) is 'draft'

