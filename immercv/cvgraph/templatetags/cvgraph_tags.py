from django import template

from immercv.cvgraph.forms import form_for_node_properties
from immercv.cvgraph.models import label_string

register = template.Library()


@register.inclusion_tag('cvgraph/tags/cvgraph_prop_editor.html')
def cvgraph_prop_editor(node, *property_names):
    form = form_for_node_properties(node, property_names)
    return {
        'labels': label_string(node.labels()),
        'form': form,
        'node_id': node._id,
    }
