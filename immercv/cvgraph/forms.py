from django import forms
from neomodel import DateProperty, IntegerProperty, StringProperty


PROPERTY_TYPE_FIELDS = {
    # property-type: form-field-type,
    DateProperty: forms.DateField,
    IntegerProperty: forms.IntegerField,
    StringProperty: forms.CharField,
}


def field_for_node_property(node, property_name, **kwargs):
    property = getattr(node.__class__, property_name)
    property_type = type(property)
    kwargs['required'] = kwargs.pop('required', property.required)
    return PROPERTY_TYPE_FIELDS[property_type](**kwargs)


def form_for_node_properties(node, property_names, data=None):
    current_values = {
        property_name: getattr(node, property_name)
        for property_name in property_names
    }
    class NodeForm(forms.Form):
        def __init__(self, node, *args, **kwargs):
            super(NodeForm, self).__init__(*args, **kwargs)
            # Create fields in the order they're specified in `property_names`.
            for property_name in property_names:
                self.fields[property_name] = field_for_node_property(node, property_name)
    return NodeForm(node, initial=current_values, data=data)
