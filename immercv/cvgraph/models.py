import datetime

from django.core.urlresolvers import reverse
from django.utils.text import slugify
from neomodel import IntegerProperty, StructuredNode, StringProperty, db, DateProperty, RelationshipFrom, \
    RelationshipTo, StructuredRel, Relationship, BooleanProperty

EDITABLE_PROPERTIES = {
    # labels: {property-name, ...},

    # Nodes
    ':Company': ['name'],
    ':CV': ['name', 'date', 'spec'],
    ':Experience': ['title', 'date', 'publish_date', 'summary', 'body'],
    ':Link': ['title', 'url', 'publish_date', 'summary'],
    ':Note': ['text', 'publish_date'],
    ':Person': ['name', 'contact_info', 'image_url'],
    ':Project': ['name', 'description'],
    ':Role': ['name', 'description', 'hidden'],
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


def parse8601(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


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
    contact_info = StringProperty()
    image_url = StringProperty()

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

    def all_roles_and_dates(self):
        results = db.cypher_query(
            """
            MATCH
                (person:Person)-[rel:PERFORMED]->(role:Role)
            WHERE
                id(person) = {id}
            RETURN
                role,
                rel.start_date as start_date,
                rel.end_date as end_date
            ORDER BY
                rel.start_date DESC, rel.end_date DESC
            """,
            dict(id=self._id)
        )
        return [
            (
                Role.inflate(result['role']),
                parse8601(result['start_date']) if result['start_date'] else datetime.date.today(),
                parse8601(result['end_date']) if result['end_date'] else datetime.date.today(),
            )
            for result in results[0]
        ]

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
    hidden = BooleanProperty()

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
    projects = RelationshipTo('Project', 'RELATED_TO')
    roles = RelationshipTo('Role', 'RELATED_TO')
    topics = Relationship('Topic', 'RELATED_TO')

    def __str__(self):
        return self.name

    def all_experiences(self):
        # There is a quirk in that a topic could be related to an experience,
        # or an experience could be with a topic. We want to find all such
        # experiences.
        results = db.cypher_query(
            """
            MATCH (e:Experience), (t:Topic)
            WHERE ID(t) = {id}
              AND ((e)-[:WITH]->(t) OR (t)-[:RELATED_TO*1..]->(e))
            RETURN e
            """,
            dict(id=self._id)
        )
        return [
            Experience.inflate(result['e'])
            for result in results[0]
        ]

    def all_projects(self):
        results = db.cypher_query(
            """
            MATCH (p:Project), (t:Topic)
            WHERE ID(t) = {id}
              AND (t)-[:RELATED_TO*1..]->(p)
            RETURN p
            """,
            dict(id=self._id)
        )
        return [
            Project.inflate(result['p'])
            for result in results[0]
        ]

    def all_roles(self):
        results = db.cypher_query(
            """
            MATCH (r:Role), (t:Topic)
            WHERE ID(t) = {id}
              AND (t)-[:RELATED_TO*1..]->(r)
            RETURN r
            """,
            dict(id=self._id)
        )
        return [
            Role.inflate(result['r'])
            for result in results[0]
        ]
