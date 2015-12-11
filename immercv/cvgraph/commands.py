from neomodel import db

from immercv.cvgraph.forms import form_for_node_properties
from immercv.cvgraph.models import editable_params, get_node_by_id, Person, Note, \
    Project, Role, PerformedRel

COMMAND_FUNCTIONS = {
    # Created via application of `command` decorator.
    #
    # (labels, operation, relationship_name): update-function,
}


def apply_command(request, properties):
    labels = properties.pop('_labels')[0]
    node_id = properties.pop('_id', [None])[0]
    if node_id is not None:
        node_id = int(node_id)
    operation = properties.pop('_operation')[0]
    relationship_name = properties.pop('_relationship_name', [None])[0]
    key = (labels, operation, relationship_name)
    fn = COMMAND_FUNCTIONS.get(key)
    if callable(fn):
        fn(request, properties, node_id)


def command(labels, operation, relationship=None):
    def command_decorator(fn):
        COMMAND_FUNCTIONS[(labels, operation, relationship)] = fn
        return fn
    return command_decorator


def create_node_from_params(cls, params):
    node = cls()
    set_node_properties_from_params(node, params)
    node.save()
    return node


def set_node_properties_from_params(node, params):
    for k, v in params.items():
        property = getattr(node.__class__, k)
        if not property.required and v == '':
            v = None
        setattr(node, k, v)


@command(':Note', 'delete')
def delete_note(request, params, node_id):
    note = get_node_by_id(Note, node_id)
    note.delete()


@command(':Note', 'update')
def update_note(request, params, node_id):
    note = get_node_by_id(Note, node_id)
    params = editable_params(params, ':Note')
    form = form_for_node_properties(note, params.keys(), params)
    if form.is_valid():
        set_node_properties_from_params(note, form.cleaned_data)
        note.save()


@command(':Person', 'create', 'notes')
def create_person_note(request, params, node_id):
    person = get_node_by_id(Person, node_id)
    params = editable_params(params, ':Note')
    form = form_for_node_properties(Note, params.keys(), params)
    if form.is_valid():
        note = create_node_from_params(Note, params)
        person.notes.connect(note)


@command(':Person', 'create', 'projects')
def create_person_project(request, params, node_id):
    person = get_node_by_id(Person, node_id)
    params = editable_params(params, ':Project')
    form = form_for_node_properties(Project, params.keys(), params)
    if form.is_valid():
        project = create_node_from_params(Project, params)
        person.projects.connect(project)


@command(':Person', 'create', 'roles')
def create_person_role(request, params, node_id):
    person = get_node_by_id(Person, node_id)
    params = editable_params(params, ':Role')
    form = form_for_node_properties(Role, params.keys(), params)
    if form.is_valid():
        role = create_node_from_params(Role, params)
        person.roles.connect(role)


@command(':Person', 'update')
def update_person(request, params, node_id):
    params = editable_params(params, ':Person')
    person = get_node_by_id(Person, node_id)
    set_node_properties_from_params(person, params)
    person.save()


@command(':Project', 'delete')
def delete_project(request, params, node_id):
    project = get_node_by_id(Project, node_id)
    project.delete()


@command(':Project', 'update')
def update_project(request, params, node_id):
    project = get_node_by_id(Project, node_id)
    params = editable_params(params, ':Project')
    form = form_for_node_properties(project, params.keys(), params)
    if form.is_valid():
        set_node_properties_from_params(project, form.cleaned_data)
        project.save()


@command(':Role', 'delete')
def delete_role(request, params, node_id):
    role = get_node_by_id(Role, node_id)
    role.delete()


@command(':Role', 'update')
def update_role(request, params, node_id):
    role = get_node_by_id(Role, node_id)
    params = editable_params(params, ':Role')
    form = form_for_node_properties(role, params.keys(), params)
    if form.is_valid():
        set_node_properties_from_params(role, form.cleaned_data)
        role.save()


@command('(:Person)-[:PERFORMED]->(:Role)', 'update')
def update_performed(request, params, node_id):
    rel = db.cypher_query(
        'MATCH (:Person)-[r:PERFORMED]->(:Role) WHERE ID(r)={this} RETURN r',
        dict(this=node_id),
    )
    performed = PerformedRel.inflate(rel[0][0][0])
    form = form_for_node_properties(performed, params.keys(), params)
    if form.is_valid():
        set_node_properties_from_params(performed, form.cleaned_data)
        performed.save()
