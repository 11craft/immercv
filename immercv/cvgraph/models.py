from neomodel import IntegerProperty, StructuredNode, StringProperty, db, DateProperty, RelationshipFrom, \
    RelationshipTo

EDITABLE_PROPERTIES = {
    # labels: {property-name, ...},
    ':Note': {'text', 'date'},
    ':Person': {'name'},
    ':Project': {'name', 'description'},
}


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


def editable_params(params, label):
    return {
        k: v
        for k, v in params.items()
        if k in EDITABLE_PROPERTIES[label]
        }


class Note(StructuredNode):

    text = StringProperty(required=True)
    date = DateProperty()


class Person(StructuredNode):

    django_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(required=True)

    notes = RelationshipFrom('Note', 'ABOUT')
    projects = RelationshipTo('Project', 'CONTRIBUTED_TO')

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


class Project(StructuredNode):

    name = StringProperty(required=True)
    description = StringProperty()
