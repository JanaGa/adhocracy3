"""Finite state machines for resources."""
from colander import Invalid

from pyramid.interfaces import IRequest
from pyramid.registry import Registry
from substanced.workflow import ACLWorkflow
from substanced.workflow import WorkflowError
from substanced.workflow import IWorkflow
from zope.interface import implementer

from adhocracy_core.authorization import acm_to_acl
from adhocracy_core.authorization import create_fake_god_request
from adhocracy_core.exceptions import ConfigurationError
from adhocracy_core.interfaces import IAdhocracyWorkflow
from adhocracy_core.workflows.schemas import create_workflow_meta_schema


@implementer(IAdhocracyWorkflow)
class AdhocracyACLWorkflow(ACLWorkflow):

    """Workflow that sets the :term:`acl` when entering a State."""

    def get_next_states(self, context, request: IRequest) -> list:
        """Get states you can trigger a transition to."""
        state = self.state_of(context)
        transitions = self.get_transitions(context, request, from_state=state)
        states = [t['to_state'] for t in transitions]
        return list(set(states))


def add_workflow(registry: Registry, cstruct: dict, name: str):
    """Create and add workflow to registry.

    :param registry: registry to register the workflow and store meta data.
    :param cstruct: meta data :term:`cstruct` to create the workflow. The data
        schema is :class:`adhocracy_core.workflows.schemas.Workflow`.
    :param name: identifier for the workflow
    :raises adhocracy_core.exceptions.ConfigurationError: if the validation
        for :term:`cstruct` and the sanity checks in
        class:`substanced.workflow.Workflow` fails.
    """
    error_msg = 'Cannot create workflow {0}: {1}'
    try:
        appstruct = _validate_workflow_cstruct(cstruct)
        workflow = _create_workflow(registry, appstruct, name)
    except Invalid as error:
        msg = error_msg.format(name, str(error.asdict()))
        raise ConfigurationError(msg)
    except WorkflowError as error:
        msg = error_msg.format(name, str(error))
        raise ConfigurationError(msg)
    _add_workflow_to_registry(registry, appstruct, workflow, name)


def transition_to_states(context, states: [str], registry: Registry,
                         reset=False):
    """Initialize workflow if needed and do transitions to the given states.

    :raises substanced.workflow.WorkflowError: if transition is missing to
    do transitions to `states`.
    """
    request = create_fake_god_request(registry)
    workflow = registry.content.get_workflow(context)
    # TODO: raise if workflow is None
    if not workflow.has_state(context) or reset:
        workflow.initialize(context)
    current_state = workflow.state_of(context)
    wanted_state = states and states[-1]
    if wanted_state == current_state:
        return
    for state in states:
        workflow.transition_to_state(context, request, state)


def _validate_workflow_cstruct(cstruct: dict) -> dict:
    """Deserialize workflow :term:`cstruct` and return :term:`appstruct`."""
    schema = create_workflow_meta_schema(cstruct)
    appstruct = schema.deserialize(cstruct)
    return appstruct


def _create_workflow(registry: Registry,
                     appstruct: dict,
                     name: str) -> ACLWorkflow:
    initial_state = appstruct['initial_state']
    workflow = AdhocracyACLWorkflow(initial_state=initial_state, type=name)
    for name, data in appstruct['states'].items():
        acl = acm_to_acl(data['acm'], registry)
        workflow.add_state(name, callback=None, acl=acl)
    for name, data in appstruct['transitions'].items():
        workflow.add_transition(name, **data)
    workflow.check()
    return workflow


def _add_workflow_to_registry(registry: Registry, appstruct: dict,
                              workflow: IWorkflow,
                              name: str):
    registry.content.workflows_meta[name] = appstruct
    registry.content.workflows[name] = workflow


def includeme(config):  # pragma: no cover
    """Include workflows."""
    config.include('.sample')
    config.include('.standard')
    config.include('.subscriber')
