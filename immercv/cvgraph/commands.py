from neomodel import db

from immercv.cvgraph.forms import form_for_node_properties, \
    form_for_node_link
from immercv.cvgraph.models import editable_params, get_node_by_id, Person, Note, \
    Project, Role, PerformedRel, Company

COMMAND_FUNCTIONS = {
    # Created via application of `command` decorator.
    #
    # (labels, operation, relationship_name): update-function,
}


def apply_command(request, params):
    labels = params.pop('_labels')[0]
    node_id = params.pop('_id', [None])[0]
    if node_id is not None:
        node_id = int(node_id)
    operation = params.pop('_operation')[0]
    relationship_name = params.pop('_relationship_name', [None])[0]
    key = (labels, operation, relationship_name)
    fn = COMMAND_FUNCTIONS.get(key)
    if callable(fn):
        fn(request, params, node_id)


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


def create_note(node_class, params, node_id):
    node = get_node_by_id(node_class, node_id)
    params = editable_params(params, ':Note')
    form = form_for_node_properties(Note, params.keys(), params)
    if form.is_valid():
        note = create_node_from_params(Note, form.cleaned_data)
        node.notes.connect(note)


@command(':Company', 'delete')
def delete_company(request, params, node_id):
    company = get_node_by_id(Company, node_id)
    company.delete()


@command(':Company', 'update')
def update_company(request, params, node_id):
    company = get_node_by_id(Company, node_id)
    params = editable_params(params, ':Company')
    form = form_for_node_properties(company, params.keys(), params)
    if form.is_valid():
        set_node_properties_from_params(company, form.cleaned_data)
        company.save()


@command(':Company', 'create', 'notes')
def create_project_note(request, params, node_id):
    create_note(Company, params, node_id)


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
    create_note(Person, params, node_id)


@command(':Person', 'create', 'projects')
def create_person_project(request, params, node_id):
    person = get_node_by_id(Person, node_id)
    params = editable_params(params, ':Project')
    form = form_for_node_properties(Project, params.keys(), params)
    if form.is_valid():
        project = create_node_from_params(Project, form.cleaned_data)
        person.projects.connect(project)


@command(':Person', 'create', 'roles')
def create_person_role(request, params, node_id):
    person = get_node_by_id(Person, node_id)
    params = editable_params(params, ':Role')
    form = form_for_node_properties(Role, params.keys(), params)
    if form.is_valid():
        role = create_node_from_params(Role, form.cleaned_data)
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


@command(':Project', 'create', 'notes')
def create_project_note(request, params, node_id):
    create_note(Project, params, node_id)


@command(':Role', 'create', 'companies')
def create_role_company(request, params, node_id):
    role = get_node_by_id(Role, node_id)
    params = editable_params(params, ':Company')
    form = form_for_node_properties(Company, params.keys(), params)
    if form.is_valid():
        company = create_node_from_params(Company, form.cleaned_data)
        role.companies.connect(company)


@command(':Role', 'link', 'companies')
def link_role_company(request, params, node_id):
    role = get_node_by_id(Role, node_id)
    form = form_for_node_link(Company, params)
    if form.is_valid():
        other_node_id = int(form.cleaned_data['link_to'])
        company = get_node_by_id(Company, other_node_id)
        role.companies.connect(company)


@command(':Role', 'unlink', 'companies')
def unlink_role_company(request, params, node_id):
    role = get_node_by_id(Role, node_id)
    company = get_node_by_id(Company, int(params['_other_node_id']))
    print('**************')
    role.companies.disconnect(company)


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


@command(':Role', 'create', 'notes')
def create_project_note(request, params, node_id):
    create_note(Role, params, node_id)


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
