from neomodel import IntegerProperty, StructuredNode, StringProperty, db


UPDATE_FUNCTIONS = {
    # (labels, operation): update-function,
}

VALID_PROPERTIES = {
    # labels: {property-name, ...},
    ':Person': {'name'},
}


def apply_change(request, properties):
    labels = properties.pop('_labels')[0]
    operation = properties.pop('_operation')[0]
    node_id = properties.pop('_id', [None])[0]
    fn = UPDATE_FUNCTIONS.get((labels, operation))
    if callable(fn):
        fn(request, properties, node_id)


def changer(labels, operation):
    def updater_decorator(fn):
        UPDATE_FUNCTIONS[(labels, operation)] = fn
        return fn
    return updater_decorator


def get_by_id(cls, id):
    labels = ''.join(label_string(cls.inherited_labels()))
    results = db.cypher_query(
        'MATCH (n{}) WHERE ID(n)={{id}} RETURN n'.format(labels),
        dict(id=int(id))
    )
    if len(results) == 0:
        raise cls.DoesNotExist('No node found with given ID')
    return cls.inflate(results[0][0]['n'])


def label_string(labels):
    return ''.join(':' + label for label in labels)


def set_node_properties_from_params(node, params):
    for k, v in params.items():
        setattr(node, k, v) #!


def valid_params(params, label):
    return {
        k: v
        for k, v in params.items()
        if k in VALID_PROPERTIES[label]
    }


@changer(':Person', 'update')
def update_person(request, params, node_id):
    params = valid_params(params, ':Person')
    node = get_by_id(Person, node_id)
    set_node_properties_from_params(node, params) #!
    node.save()


class Person(StructuredNode):

    django_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(required=True)

    @classmethod
    def for_user(cls, user):
        if not user.is_authenticated():
            raise cls.DoesNotExist('User is not authenticated')
        else:
            return cls.nodes.get(django_id=user.id)

    @classmethod
    def create_for_user(cls, user):
        return cls(
            django_id=user.id,
            name=user.name if len(user.name) > 0 else user.username,
        ).save()
