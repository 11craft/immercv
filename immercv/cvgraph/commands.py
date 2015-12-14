from neomodel import db

from immercv.cvgraph.forms import form_for_node_properties, \
    form_for_node_link
from immercv.cvgraph.models import editable_params, get_node_by_id, Person, Note, \
    Project, Role, PerformedRel, Company, Topic, label_string

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
        fn(request, labels, params, node_id)


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


def generic_create_related(node_class, other_node_class, rel_name,
                           request, labels, params, node_id):
    node = get_node_by_id(node_class, node_id)
    other_labels = label_string(other_node_class.inherited_labels())
    params = editable_params(params, other_labels)
    form = form_for_node_properties(other_node_class, params.keys(), params)
    if form.is_valid():
        other_node = create_node_from_params(other_node_class, form.cleaned_data)
        rel = getattr(node, rel_name)
        rel.connect(other_node)
        return node, other_node


def generic_link_related(node_class, other_node_class, rel_name,
                         request, labels, params, node_id):
    node = get_node_by_id(node_class, node_id)
    form = form_for_node_link(other_node_class, params)
    if form.is_valid():
        other_node_id = int(form.cleaned_data['link_to'])
        other_node = get_node_by_id(other_node_class, other_node_id)
        rel = getattr(node, rel_name)
        rel.connect(other_node)
        return node, other_node


def generic_unlink_related(node_class, other_node_class, rel_name,
                           request, labels, params, node_id):
    node = get_node_by_id(node_class, node_id)
    other_node_id = int(params['_other_node_id'])
    other_node = get_node_by_id(other_node_class, other_node_id)
    rel = getattr(node, rel_name)
    rel.disconnect(other_node)


def generic_delete(node_class, request, labels, params, node_id):
    node = get_node_by_id(node_class, node_id)
    node.delete()


def generic_update_node(node_class, request, labels, params, node_id):
    node = get_node_by_id(node_class, node_id)
    params = editable_params(params, labels)
    form = form_for_node_properties(node, params.keys(), params)
    if form.is_valid():
        set_node_properties_from_params(node, form.cleaned_data)
        node.save()
        return node


def generic_update_rel(rel_class, request, labels, params, node_id):
    labels = labels.replace(')-[', ')-[r')
    query = 'MATCH ({}) WHERE ID(r)={{this}} RETURN r'.format(labels)
    query_params = dict(this=node_id)
    results, meta = db.cypher_query(query, query_params)
    rel = rel_class.inflate(results[0][0])
    form = form_for_node_properties(rel, params.keys(), params)
    if form.is_valid():
        set_node_properties_from_params(rel, form.cleaned_data)
        rel.save()
        return rel


@command(':Company', 'delete')
def delete_company(request, labels, params, node_id):
    generic_delete(Company, request, labels, params, node_id)


@command(':Company', 'update')
def update_company(request, labels, params, node_id):
    generic_update_node(Company, request, labels, params, node_id)


@command(':Company', 'create', 'notes')
def create_company_note(request, labels, params, node_id):
    generic_create_related(Company, Note, 'notes', request, labels, params, node_id)


@command(':Note', 'delete')
def delete_note(request, labels, params, node_id):
    generic_delete(Note, request, labels, params, node_id)


@command(':Note', 'update')
def update_note(request, labels, params, node_id):
    generic_update_node(Note, request, labels, params, node_id)


@command(':Person', 'create', 'notes')
def create_person_note(request, labels, params, node_id):
    generic_create_related(Person, Note, 'notes', request, labels, params, node_id)


@command(':Person', 'create', 'projects')
def create_person_project(request, labels, params, node_id):
    generic_create_related(Person, Project, 'projects', request, labels, params, node_id)


@command(':Person', 'create', 'roles')
def create_person_role(request, labels, params, node_id):
    generic_create_related(Person, Role, 'roles', request, labels, params, node_id)


@command(':Person', 'update')
def update_person(request, labels, params, node_id):
    generic_update_node(Person, request, labels, params, node_id)


@command(':Project', 'delete')
def delete_project(request, labels, params, node_id):
    generic_delete(Project, request, labels, params, node_id)


@command(':Project', 'update')
def update_project(request, labels, params, node_id):
    generic_update_node(Project, request, labels, params, node_id)


@command(':Project', 'create', 'notes')
def create_project_note(request, labels, params, node_id):
    generic_create_related(Project, Note, 'notes', request, labels, params, node_id)


@command(':Project', 'create', 'topics')
def create_project_topic(request, labels, params, node_id):
    generic_create_related(Project, Topic, 'topics', request, labels, params, node_id)


@command(':Project', 'link', 'topics')
def link_project_topic(request, labels, params, node_id):
    generic_link_related(Project, Topic, 'topics', request, labels, params, node_id)


@command(':Project', 'unlink', 'topics')
def unlink_project_topic(request, labels, params, node_id):
    generic_unlink_related(Project, Topic, 'topics', request, labels, params, node_id)


@command(':Project', 'delete')
def delete_project(request, labels, params, node_id):
    generic_delete(Project, request, labels, params, node_id)


@command(':Role', 'create', 'companies')
def create_role_company(request, labels, params, node_id):
    generic_create_related(Role, Company, 'companies', request, labels, params, node_id)


@command(':Role', 'link', 'companies')
def link_role_company(request, labels, params, node_id):
    generic_link_related(Role, Company, 'companies', request, labels, params, node_id)


@command(':Role', 'unlink', 'companies')
def unlink_role_company(request, labels, params, node_id):
    generic_unlink_related(Role, Company, 'companies', request, labels, params, node_id)


@command(':Role', 'delete')
def delete_role(request, labels, params, node_id):
    generic_delete(Role, request, labels, params, node_id)


@command(':Role', 'create', 'via_roles')
def create_role_via_role(request, labels, params, node_id):
    role, via_role = generic_create_related(Role, Role, 'via_roles', request, labels, params, node_id)
    for person in role.people:
        via_role.people.connect(person)


@command(':Role', 'link', 'via_roles')
def link_role_via_role(request, labels, params, node_id):
    generic_link_related(Role, Role, 'via_roles', request, labels, params, node_id)


@command(':Role', 'unlink', 'via_roles')
def unlink_role_via_role(request, labels, params, node_id):
    generic_unlink_related(Role, Role, 'via_roles', request, labels, params, node_id)


@command(':Role', 'update')
def update_role(request, labels, params, node_id):
    generic_update_node(Role, request, labels, params, node_id)


@command(':Role', 'create', 'notes')
def create_role_note(request, labels, params, node_id):
    generic_create_related(Role, Note, 'notes', request, labels, params, node_id)


@command('(:Person)-[:PERFORMED]->(:Role)', 'update')
def update_performed(request, labels, params, node_id):
    generic_update_rel(PerformedRel, request, labels, params, node_id)


@command(':Topic', 'delete')
def delete_topic(request, labels, params, node_id):
    generic_delete(Topic, request, labels, params, node_id)


@command(':Topic', 'create', 'notes')
def create_topic_note(request, labels, params, node_id):
    generic_create_related(Topic, Note, 'notes', request, labels, params, node_id)


@command(':Topic', 'create', 'topics')
def create_topic_other_topic(request, labels, params, node_id):
    generic_create_related(Topic, Topic, 'topics', request, labels, params, node_id)


@command(':Topic', 'link', 'topics')
def link_topic_other_topic(request, labels, params, node_id):
    generic_link_related(Topic, Topic, 'topics', request, labels, params, node_id)


@command(':Topic', 'unlink', 'topics')
def unlink_topic_other_topic(request, labels, params, node_id):
    generic_unlink_related(Topic, Topic, 'topics', request, labels, params, node_id)


@command(':Topic', 'update')
def update_topic(request, labels, params, node_id):
    generic_update_node(Topic, request, labels, params, node_id)
