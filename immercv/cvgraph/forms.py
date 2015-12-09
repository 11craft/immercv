from django import forms
from neomodel import DateProperty, IntegerProperty, StringProperty


PROPERTY_TYPE_FIELDS = {
    # property-type: form-field-type,
    DateProperty: forms.DateField,
    IntegerProperty: forms.IntegerField,
    StringProperty: forms.CharField,
}


def field_for_node_property(node_or_class, property_name, **kwargs):
    if isinstance(node_or_class, type):
        node_class = node_or_class
    else:
        node_class = node_or_class.__class__
    property = getattr(node_class, property_name)
    property_type = type(property)
    kwargs['required'] = kwargs.pop('required', property.required)
    return PROPERTY_TYPE_FIELDS[property_type](**kwargs)


def form_for_node_properties(node_or_class, property_names, data=None):
    if isinstance(node_or_class, type):
        current_values = {}
    else:
        current_values = {
            property_name: getattr(node_or_class, property_name)
            for property_name in property_names
        }
    class NodeForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super(NodeForm, self).__init__(*args, **kwargs)
            # Create fields in the order given in `property_names`.
            for property_name in property_names:
                field = field_for_node_property(node_or_class, property_name)
                self.fields[property_name] = field
    return NodeForm(initial=current_values, data=data)
