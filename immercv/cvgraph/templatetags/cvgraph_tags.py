from django import template

from immercv.cvgraph.forms import form_for_node_properties
from immercv.cvgraph.models import label_string

register = template.Library()


@register.inclusion_tag('cvgraph/tags/cvgraph_node_creator.html')
def cvgraph_node_creator(node, relationship_name, *property_names):
    relationship = getattr(node, relationship_name)
    other_node_class = relationship.definition['node_class']
    form = form_for_node_properties(other_node_class, property_names)
    return {
        'labels': label_string(node.labels()),
        'form': form,
        'node_id': node._id,
        'relationship_name': relationship_name,
    }


@register.inclusion_tag('cvgraph/tags/cvgraph_node_deleter.html')
def cvgraph_node_deleter(node):
    return {
        'labels': label_string(node.labels()),
        'node_id': node._id,
    }


@register.inclusion_tag('cvgraph/tags/cvgraph_prop_editor.html')
def cvgraph_prop_editor(node, *property_names):
    form = form_for_node_properties(node, property_names)
    return {
        'labels': label_string(node.labels()),
        'form': form,
        'node_id': node._id,
    }
