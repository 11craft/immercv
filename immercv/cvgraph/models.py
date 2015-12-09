from neomodel import IntegerProperty, StructuredNode, StringProperty, db


def get_by_id(cls, id):
    labels = ''.join(':' + label for label in cls.inherited_labels())
    results = db.cypher_query(
        'MATCH (n{}) WHERE ID(n)={{id}} RETURN n'.format(labels),
        dict(id=int(id))
    )
    if len(results) == 0:
        raise cls.DoesNotExist('No node found with given ID')
    return cls.inflate(results[0][0]['n'])


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
