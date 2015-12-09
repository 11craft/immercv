from immercv.cvgraph.forms import form_for_node_properties
from immercv.cvgraph.models import editable_params, get_by_id, Person, Note


COMMAND_FUNCTIONS = {
    # Created via application of `command` decorator.
    #
    # (labels, operation, relationship_name): update-function,
}


def apply_command(request, properties):
    labels = properties.pop('_labels')[0]
    node_id = properties.pop('_id', [None])[0]
    operation = properties.pop('_operation')[0]
    relationship_name = properties.pop('_relationship_name', [None])[0]
    key = (labels, operation, relationship_name)
    print(key)
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


@command(':Note', 'update')
def update_note(request, params, node_id):
    note = get_by_id(Note, node_id)
    params = editable_params(params, ':Note')
    form = form_for_node_properties(note, params.keys(), params)
    if form.is_valid():
        set_node_properties_from_params(note, form.cleaned_data)
        note.save()


@command(':Person', 'create', 'notes')
def create_person_note(request, params, node_id):
    person = get_by_id(Person, node_id)
    params = editable_params(params, ':Note')
    form = form_for_node_properties(Note, params.keys(), params)
    if form.is_valid():
        note = create_node_from_params(Note, params)
        person.notes.connect(note)


@command(':Person', 'update')
def update_person(request, params, node_id):
    params = editable_params(params, ':Person')
    person = get_by_id(Person, node_id)
    set_node_properties_from_params(person, params)
    person.save()
