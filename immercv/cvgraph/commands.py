from immercv.cvgraph.forms import form_for_node_properties
from immercv.cvgraph.models import editable_params, get_by_id, Person, Note


COMMAND_FUNCTIONS = {
    # Created via application of `command` decorator.
    #
    # (labels, operation): update-function,
}


def apply_command(request, properties):
    labels = properties.pop('_labels')[0]
    operation = properties.pop('_operation')[0]
    node_id = properties.pop('_id', [None])[0]
    fn = COMMAND_FUNCTIONS.get((labels, operation))
    if callable(fn):
        fn(request, properties, node_id)


def command(labels, operation):
    def command_decorator(fn):
        COMMAND_FUNCTIONS[(labels, operation)] = fn
        return fn
    return command_decorator


def set_node_properties_from_params(node, params):
    for k, v in params.items():
        property = getattr(node.__class__, k)
        if not property.required and v == '':
            v = None
        setattr(node, k, v)


@command(':Note', 'update')
def update_note(request, params, node_id):
    node = get_by_id(Note, node_id)
    params = editable_params(params, ':Note')
    form = form_for_node_properties(node, params.keys(), params)
    if form.is_valid():
        set_node_properties_from_params(node, form.cleaned_data)
        node.save()


@command(':Person', 'update')
def update_person(request, params, node_id):
    params = editable_params(params, ':Person')
    node = get_by_id(Person, node_id)
    set_node_properties_from_params(node, params)
    node.save()
