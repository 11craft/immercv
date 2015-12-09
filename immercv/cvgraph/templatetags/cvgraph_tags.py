from django import template

from immercv.cvgraph.forms import form_for_node_properties
from immercv.cvgraph.models import label_string, EDITABLE_PROPERTIES

register = template.Library()


@register.inclusion_tag('cvgraph/tags/cvgraph_node_creator.html')
def cvgraph_node_creator(node, relationship_name, *property_names):
    labels = label_string(node.labels())
    relationship = getattr(node, relationship_name)
    other_node_class = relationship.definition['node_class']
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


@register.inclusion_tag('cvgraph/tags/cvgraph_prop_editor.html')
def cvgraph_prop_editor(node, *property_names):
    labels = label_string(node.labels())
    if len(property_names) == 0:
        property_names = EDITABLE_PROPERTIES[labels]
    form = form_for_node_properties(node, property_names)
    return {
        'labels': labels,
        'form': form,
        'node_id': node._id,
    }
