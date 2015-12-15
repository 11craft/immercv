from neomodel import db

from immercv.cvgraph.forms import form_for_node_properties, \
    form_for_node_link
from immercv.cvgraph.models import editable_params, get_node_by_id, Person, Note, \
    Project, Role, PerformedRel, Company, Topic, label_string, \
    ContributedToRel, Experience

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


def register_create_link_unlink(node_class, other_node_class, rel_name):
    node_labels = label_string(node_class.inherited_labels())
    @command(node_labels, 'create', rel_name)
    def create(request, labels, params, node_id):
        generic_create_related(node_class, other_node_class, rel_name, request, labels, params, node_id)
    @command(node_labels, 'link', rel_name)
    def link(request, labels, params, node_id):
        generic_link_related(node_class, other_node_class, rel_name, request, labels, params, node_id)
    @command(node_labels, 'unlink', rel_name)
    def unlink(request, labels, params, node_id):
        generic_unlink_related(node_class, other_node_class, rel_name, request, labels, params, node_id)


def register_create_notes(node_class):
    node_labels = label_string(node_class.inherited_labels())
    @command(node_labels, 'create', 'notes')
    def create(request, labels, params, node_id):
        generic_create_related(node_class, Note, 'notes', request, labels, params, node_id)


def register_create_experiences(node_class):
    node_labels = label_string(node_class.inherited_labels())
    @command(node_labels, 'create', 'experiences')
    def create(request, labels, params, node_id):
        generic_create_related(node_class, Experience, 'experiences', request, labels, params, node_id)


def register_delete_update(node_class):
    node_labels = label_string(node_class.inherited_labels())
    @command(node_labels, 'delete')
    def delete(request, labels, params, node_id):
        generic_delete(node_class, request, labels, params, node_id)
    @command(node_labels, 'update')
    def update(request, labels, params, node_id):
        generic_update_node(node_class, request, labels, params, node_id)


# -- COMPANY --

register_delete_update(Company)
register_create_notes(Company)
register_create_experiences(Company)
register_create_link_unlink(Company, Topic, 'topics')


# -- EXPERIENCE --

register_delete_update(Experience)
register_create_notes(Experience)


# -- NOTE --

register_delete_update(Note)


# -- PERSON --

register_delete_update(Person)
register_create_notes(Person)
register_create_experiences(Person)
register_create_link_unlink(Person, Project, 'projects')
register_create_link_unlink(Person, Role, 'roles')


# -- PROJECT --

register_delete_update(Project)
register_create_notes(Project)
register_create_experiences(Project)
register_create_link_unlink(Project, Role, 'roles')
register_create_link_unlink(Project, Topic, 'topics')

@command('(:Person)-[:CONTRIBUTED_TO]->(:Project)', 'update')
def update_contributed_to(request, labels, params, node_id):
    generic_update_rel(ContributedToRel, request, labels, params, node_id)


# -- ROLE --

register_delete_update(Role)
register_create_notes(Role)
register_create_experiences(Role)
register_create_link_unlink(Role, Company, 'companies')
register_create_link_unlink(Role, Project, 'projects')
register_create_link_unlink(Role, Role, 'via_roles')
register_create_link_unlink(Role, Topic, 'topics')

@command(':Role', 'create', 'projects')
def create_role_project(request, labels, params, node_id):
    role, project = generic_create_related(Role, Project, 'projects', request, labels, params, node_id)
    for person in role.people:
        project.people.connect(person)

@command(':Role', 'create', 'via_roles')
def create_role_via_role(request, labels, params, node_id):
    role, via_role = generic_create_related(Role, Role, 'via_roles', request, labels, params, node_id)
    for person in role.people:
        via_role.people.connect(person)

@command('(:Person)-[:PERFORMED]->(:Role)', 'update')
def update_performed(request, labels, params, node_id):
    generic_update_rel(PerformedRel, request, labels, params, node_id)


# -- TOPIC --

register_delete_update(Topic)
register_create_notes(Topic)
register_create_experiences(Topic)
register_create_link_unlink(Topic, Topic, 'topics')
