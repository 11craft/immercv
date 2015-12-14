from django import template
from neomodel import db

from immercv.cvgraph.forms import form_for_node_properties, \
    form_for_node_link
from immercv.cvgraph.models import label_string, EDITABLE_PROPERTIES, Topic

register = template.Library()


@register.filter
def cvgraph_deep_topics(node):
    query = """
        START n=node({self})
        MATCH n-[*0..]->()<-[:RELATED_TO*1..]-(topics:Topic)
        RETURN DISTINCT topics
    """
    params = {'self': node._id}
    results, meta = db.cypher_query(query, params)
    return [Topic.inflate(row[0]) for row in results]


@register.filter
def node_id(node):
    return node._id


@register.filter
def relationship(relationship_manager, other):
    return relationship_manager.relationship(other)


@register.inclusion_tag('cvgraph/tags/cvgraph_node_create_related.html')
def cvgraph_node_create_related(node, relationship_name, *property_names):
    labels = label_string(node.labels())
    rel = getattr(node, relationship_name)
    other_node_class = rel.definition['node_class']
    if len(property_names) == 0:
        other_labels = label_string(other_node_class.inherited_labels())
        property_names = EDITABLE_PROPERTIES[other_labels]
    form = form_for_node_properties(other_node_class, property_names)
    return {
        'labels': labels,
        'form': form,
        'node_id': node._id,
        'relationship_name': relationship_name,
    }


@register.inclusion_tag('cvgraph/tags/cvgraph_node_link_related.html')
def cvgraph_node_link_related(node, relationship_name, *property_names):
    labels = label_string(node.labels())
    rel = getattr(node, relationship_name)
    other_node_class = rel.definition['node_class']
    form = form_for_node_link(other_node_class)
    return {
        'form': form,
        'labels': labels,
        'node_id': node._id,
        'relationship_name': relationship_name,
    }


@register.inclusion_tag('cvgraph/tags/cvgraph_node_delete.html')
def cvgraph_node_delete(node):
    labels = label_string(node.labels())
    return {
        'labels': labels,
        'node_id': node._id,
    }


@register.inclusion_tag('cvgraph/tags/cvgraph_node_unlink.html')
def cvgraph_node_unlink(node, relationship_name, other_node):
    labels = label_string(node.labels())
    other_labels = label_string(other_node.labels())
    return {
        'labels': labels,
        'node_id': node._id,
        'relationship_name': relationship_name,
        'other_node_id': other_node._id,
        'other_labels': other_labels,
    }


@register.inclusion_tag('cvgraph/tags/cvgraph_node_edit_properties.html')
def cvgraph_node_edit_properties(node, *property_names):
    labels = label_string(node.labels())
    if len(property_names) == 0:
        property_names = EDITABLE_PROPERTIES[labels]
    form = form_for_node_properties(node, property_names)
    return {
        'labels': labels,
        'form': form,
        'node_id': node._id,
    }


@register.inclusion_tag('cvgraph/tags/cvgraph_rel_edit_properties.html')
def cvgraph_rel_edit_properties(rel, *property_names):
    labels = '({})-[{}]->({})'.format(
        label_string(rel.start_node().labels()),
        label_string(rel.labels()),
        label_string(rel.end_node().labels()),
    )
    if len(property_names) == 0:
        property_names = EDITABLE_PROPERTIES[labels]
    form = form_for_node_properties(rel, property_names)
    return {
        'labels': labels,
        'form': form,
        'node_id': rel._id,
        'rel': rel,
    }
