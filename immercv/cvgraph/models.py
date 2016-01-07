from django.core.urlresolvers import reverse
from django.utils.text import slugify
from neomodel import IntegerProperty, StructuredNode, StringProperty, db, DateProperty, RelationshipFrom, \
    RelationshipTo, StructuredRel, Relationship

EDITABLE_PROPERTIES = {
    # labels: {property-name, ...},

    # Nodes
    ':Company': ['name'],
    ':CV': ['name', 'date', 'spec'],
    ':Experience': ['title', 'date', 'publish_date', 'summary', 'body'],
    ':Link': ['title', 'url', 'publish_date', 'summary'],
    ':Note': ['text', 'publish_date'],
    ':Person': ['name'],
    ':Project': ['name', 'description'],
    ':Role': ['name', 'description'],
    ':Topic': ['name', 'description'],

    # Relationships
    '(:Person)-[:CONTRIBUTED_TO]->(:Project)': ['start_date', 'end_date'],
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


class DateRangeRel(StructuredRel):

    start_date = DateProperty()
    end_date = DateProperty()


class ContributedToRel(DateRangeRel):

    def labels(self):
        return ['CONTRIBUTED_TO']


class PerformedRel(DateRangeRel):

    def labels(self):
        return ['PERFORMED']


class Company(StructuredNode):

    name = StringProperty(required=True)

    experiences = RelationshipFrom('Experience', 'WITH')
    links = RelationshipFrom('Link', 'ABOUT')
    notes = RelationshipFrom('Note', 'ABOUT')
    roles = RelationshipFrom('Role', 'WITH')
    topics = RelationshipFrom('Topic', 'RELATED_TO')

    def __str__(self):
        return self.name


class CV(StructuredNode):

    name = StringProperty(required=True)
    date = DateProperty()
    spec = StringProperty()

    people = RelationshipFrom('Person', 'PREPARED')

    def __str__(self):
        return self.name


class Experience(StructuredNode):

    title = StringProperty(required=True)
    date = DateProperty()
    publish_date = DateProperty()
    summary = StringProperty()
    body = StringProperty()

    links = RelationshipFrom('Link', 'ABOUT')
    notes = RelationshipFrom('Note', 'ABOUT')
    projects = RelationshipTo('Project', 'WITH')
    roles = RelationshipTo('Role', 'WITH')
    topics = RelationshipFrom('Topic', 'RELATED_TO')

    def __str__(self):
        return self.title

    def canonical_url(self):
        return reverse('cvgraph:experience_detail',
                       kwargs=dict(id=self._id, slug=slugify(self.title)))


class Link(StructuredNode):

    title = StringProperty(required=True)
    url = StringProperty(required=True)
    publish_date = DateProperty()
    summary = StringProperty()

    def __str__(self):
        return self.title


class Note(StructuredNode):

    text = StringProperty(required=True)
    publish_date = DateProperty()

    def __str__(self):
        return u'Note'


class Person(StructuredNode):

    django_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(required=True)

    cvs = RelationshipTo('CV', 'PREPARED')
    links = RelationshipFrom('Link', 'ABOUT')
    notes = RelationshipFrom('Note', 'ABOUT')
    projects = RelationshipTo('Project', 'CONTRIBUTED_TO', model=ContributedToRel)
    roles = RelationshipTo('Role', 'PERFORMED', model=PerformedRel)
    topics = RelationshipFrom('Topic', 'RELATED_TO')

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

    def published_experiences(self):
        results = db.cypher_query(
            """
            MATCH (n:Experience)-[:WITH]->()<-[*]-(p:Person)
            WHERE ID(p)={id} AND n.publish_date IS NOT NULL
            RETURN DISTINCT n
            """,
            dict(id=self._id)
        )
        return [
            Experience.inflate(result['n'])
            for result in results[0]
        ]

    def published_notes(self):
        results = db.cypher_query(
            """
            MATCH (n:Note)-[:ABOUT]->()<-[*]-(p:Person)
            WHERE ID(p)={id} AND n.publish_date IS NOT NULL
            RETURN DISTINCT n
            """,
            dict(id=self._id)
        )
        return [
            Note.inflate(result['n'])
            for result in results[0]
        ]

    def published_links(self):
        results = db.cypher_query(
            """
            MATCH (n:Link)-[:ABOUT]->()<-[*]-(p:Person)
            WHERE ID(p)={id} AND n.publish_date IS NOT NULL
            RETURN DISTINCT n
            """,
            dict(id=self._id)
        )
        return [
            Link.inflate(result['n'])
            for result in results[0]
        ]


class Project(StructuredNode):

    name = StringProperty(required=True)
    description = StringProperty()

    experiences = RelationshipFrom('Experience', 'WITH')
    links = RelationshipFrom('Link', 'ABOUT')
    notes = RelationshipFrom('Note', 'ABOUT')
    people = RelationshipFrom('Person', 'CONTRIBUTED_TO', model=ContributedToRel)
    roles = RelationshipFrom('Role', 'WORKED_ON')
    topics = RelationshipFrom('Topic', 'RELATED_TO')

    def __str__(self):
        return self.name


class Role(StructuredNode):

    name = StringProperty(required=True)
    description = StringProperty()

    companies = RelationshipTo('Company', 'WITH')
    experiences = RelationshipFrom('Experience', 'WITH')
    links = RelationshipFrom('Link', 'ABOUT')
    notes = RelationshipFrom('Note', 'ABOUT')
    people = RelationshipFrom('Person', 'PERFORMED', model=PerformedRel)
    projects = RelationshipTo('Project', 'WORKED_ON')
    topics = RelationshipFrom('Topic', 'RELATED_TO')
    via_roles = RelationshipTo('Role', 'VIA')

    def __str__(self):
        if len(self.companies) == 0:
            return self.name
        else:
            company = self.companies.single()
            return '{} at {}'.format(self.name, company.name)


class Topic(StructuredNode):

    name = StringProperty(required=True)
    description = StringProperty()

    experiences = RelationshipFrom('Experience', 'WITH')
    links = RelationshipFrom('Link', 'ABOUT')
    notes = RelationshipFrom('Note', 'ABOUT')
    topics = Relationship('Topic', 'RELATED_TO')

    def __str__(self):
        return self.name
