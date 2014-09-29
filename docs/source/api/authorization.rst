Permission system:
------------------

Principals:
...........

groups (set of users):

   - Authenticated (all authenticated users, standard group)
   - Everyone (all authenticated and anonymous users, standard group)
   - gods (initial custom group, no permission checks)
   - admins (custom group)
   - managers (custom group)
   ...

users:
   - god (initial user)
   ...

Principals are mapped to global permission :term:`roles` or :term:`local roles`
(only for a specific context).


Roles (mapping to permissions):
...............................

Roles with example permission mapping:

    - reader: can view:
        view the proposal

    - contributor: can add content:
        add comment to the proposal
        add voting to the proposal

    - editor: can edit content:
        edit proposal

    - creator: edit meta stuff: permissions, transition to workflow states, ...:
        edit proposal
        change workflow state to draft
        change permissions

    - reviewer: do transition to specific workflow states:
        change workflow state to accepted/denied

    - manager: edit meta stuff: permissions, transition to workflow states, ...:
        add ...
        edit ...
        change workflow state ..
        change permissions

    - admin: create an configure the participation process, manage principals:
        set workflow
        manage principals

Roles are inherited within the object hierarchy in the database.
The creator is the principal who created the local context.
The creator role is automatically set for a specific local context and is not
inherited.

ACL (Access Control List):
..........................

List with ACEs (Access Control Entry): [<Action>, <Principal>, <Permission>]

Action: Allow | Deny
Principal: UserId | group:GroupID | role:RoleID
Permission: view, edit, add, ...

Every resource in the object hierarchy has a local ACL.

To check permission all ACEs are searched starting with the ACL of the
requested resource, and then searching the parent's ACLs recursively.
The Action of the first ACE with matching permission is returned.


Customizing
...........

1. map users to group
2. map roles to principals
3. use workflow system to  locally add :term:`local roles` mapped to principals
4. locally add :term:`local roles` (change permission to allow others to edit)
5. map permissions to roles:
    - use only configuration for this
    - default mapping should just work for most use cases

Questions
---------
FIXME: remove this section?

what is the difference between role and group, on a conceptual level?
(why do we need both?)  i'm assuming that groups are a pyramid
concept, and roles are something we want to build on top?

- For the basic pyramid authorization system there are only principals, no
  matter if you call them user/group or role.
  On our conceptual level we have a different semantic for user, group and role.
  You can see roles as groups with a default set of permissions.

is there multiple inheritance?

- no

does "inheritance" always mean "content type inheritance"?

- in this context `inheritance` means inheritance from parent to child in
  the object hierarchy

can groups be members of groups?

- no. but it would be easy to implement that.

Do we need workflows at all?  or can we assume ACLs and roles don't change at
run time?

- For the year 2014: ACL won't change during runtime and workflows are not needed


API
---

The user object must contain a list of roles and a list of groups she
is a member of.  This is necessary because the UI looks different for
different roles (at the very least, we want to see a different icon
for every role in the login widget).

If the FE sends a request to the BE that it has no authorisation for,
it will receive an error (depending on the situation either 4xx to
conceal the existence of secret resources, or 3xx to explicitly deny
access).

There are (at least) four approaches to implement an API that the FE
can use to query BE about permissions without actually performin an
access operation an observing the response:

1. OPTIONS protocol.  This is expressive enough to decide if user is
   allowed to edit a resource or not, but not enough to inspect or
   edit permissions of self (by ordinary users) or other users (by
   admin).

2. (future work) Add permission object to meta api (CAVEAT: this makes
   version resources change unexpectedly).

3. (future work) Change HTTP response to contain not only the resource
   but also permission information in a larger json object.

4. (future work) New HTTP end-point for permission requests.
