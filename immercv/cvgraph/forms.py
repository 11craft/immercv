from django import forms
from neomodel import IntegerProperty, StringProperty


def field_for_node_property(node, property_name, **kwargs):
    property_type = type(getattr(node.__class__, property_name))
    return {
        IntegerProperty: forms.IntegerField,
        StringProperty: forms.CharField,
    }[property_type](**kwargs)


def form_for_node_property(node, property_name):
    current_value = getattr(node, property_name)
    class NodeForm(forms.Form):
        def __init__(self, node, *args, **kwargs):
            super(NodeForm, self).__init__(*args, **kwargs)
            self.fields[property_name] = field_for_node_property(
                node, property_name)
    return NodeForm(node, initial={property_name: current_value})
