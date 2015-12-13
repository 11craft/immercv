from neomodel import IntegerProperty, StructuredNode, StringProperty, db, DateProperty, RelationshipFrom, \
    RelationshipTo, StructuredRel

EDITABLE_PROPERTIES = {
    # labels: {property-name, ...},

    # Nodes
    ':Company': ['name'],
    ':Note': ['text', 'date'],
    ':Person': ['name'],
    ':Project': ['name', 'description'],
    ':Role': ['name'],

    # Relationships
    '(:Person)-[:PERFORMED]->(:Role)': ['start_date', 'end_date'],
}


def get_node_by_id(cls, id):
    labels = ''.join(label_string(cls.inherited_labels()))
    results = db.cypher_query(
        'MATCH (n{}) WHERE ID(n)={{id}} RETURN n'.format(labels),
        dict(id=id)
    )
    if len(results[0]) == 0:
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


class Company(StructuredNode):

    name = StringProperty(required=True)

    notes = RelationshipFrom('Note', 'ABOUT')

    def __str__(self):
        return self.name


class Note(StructuredNode):

    text = StringProperty(required=True)
    date = DateProperty()

    def __str__(self):
        return u'Note'


class PerformedRel(StructuredRel):

    start_date = DateProperty()
    end_date = DateProperty()

    def labels(self):
        return ['PERFORMED']


class Person(StructuredNode):

    django_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(required=True)

    notes = RelationshipFrom('Note', 'ABOUT')
    projects = RelationshipTo('Project', 'CONTRIBUTED_TO')
    roles = RelationshipTo('Role', 'PERFORMED', model=PerformedRel)

    def __str__(self):
        return self.name

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

    notes = RelationshipFrom('Note', 'ABOUT')

    def __str__(self):
        return self.name


class Role(StructuredNode):

    name = StringProperty(required=True)

    companies = RelationshipTo('Company', 'WITH')
    notes = RelationshipFrom('Note', 'ABOUT')
    people = RelationshipFrom('Person', 'PERFORMED', model=PerformedRel)
    via_roles = RelationshipTo('Role', 'VIA')

    def __str__(self):
        if len(self.companies) == 0:
            return self.name
        else:
            company = self.companies.single()
            return '{} at {}'.format(self.name, company.name)
