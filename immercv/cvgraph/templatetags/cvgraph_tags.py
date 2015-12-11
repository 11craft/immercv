from django import template

from immercv.cvgraph.forms import form_for_node_properties
from immercv.cvgraph.models import label_string, EDITABLE_PROPERTIES

register = template.Library()


@register.filter
def node_id(node):
    return node._id


@register.filter
def relationship(relationship_manager, other):
    return relationship_manager.relationship(other)


@register.inclusion_tag('cvgraph/tags/cvgraph_node_creator.html')
def cvgraph_node_creator(node, relationship_name, *property_names):
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


@register.inclusion_tag('cvgraph/tags/cvgraph_node_deleter.html')
def cvgraph_node_deleter(node):
    labels = label_string(node.labels())
    return {
        'labels': labels,
        'node_id': node._id,
    }


@register.inclusion_tag('cvgraph/tags/cvgraph_node_editor.html')
def cvgraph_node_editor(node, *property_names):
    labels = label_string(node.labels())
    if len(property_names) == 0:
        property_names = EDITABLE_PROPERTIES[labels]
    form = form_for_node_properties(node, property_names)
    return {
        'labels': labels,
        'form': form,
        'node_id': node._id,
    }


@register.inclusion_tag('cvgraph/tags/cvgraph_rel_editor.html')
def cvgraph_rel_editor(rel, *property_names):
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
