from django import forms
from neomodel import DateProperty, IntegerProperty, StringProperty

from immercv.cvgraph.models import Note, Project, Role, Topic, Experience

PROPERTY_TYPE_FIELDS = {
    # property-type: form-field-type,
    DateProperty: forms.DateField,
    IntegerProperty: forms.IntegerField,
    StringProperty: forms.CharField,
}


NODE_CLASS_FIELD_WIDGETS = {
    # node-property: field-widget,
    Experience.body: forms.Textarea,
    Experience.summary: forms.Textarea,
    Note.text: forms.Textarea,
    Project.description: forms.Textarea,
    Role.description: forms.Textarea,
    Topic.description: forms.Textarea,
}


def _node_class_for(node_or_class):
    if isinstance(node_or_class, type):
        return node_or_class
    else:
        return node_or_class.__class__


def field_for_node_link(node_class):
    choices = [
        (node._id, str(node))
        for node in node_class.nodes.all()
    ]
    return forms.ChoiceField(choices)


def field_for_node_property(node_or_class, property_name):
    node_class = _node_class_for(node_or_class)
    property = getattr(node_class, property_name)
    property_type = type(property)
    field_class = PROPERTY_TYPE_FIELDS[property_type]
    return field_class(
        required=property.required,
        widget=NODE_CLASS_FIELD_WIDGETS.get(property),
    )


def form_class_for_node_properties(node_or_class, property_names):
    class Form(forms.Form):
        def __init__(self, *args, **kwargs):
            super(Form, self).__init__(*args, **kwargs)
            # Create fields in the order given in `property_names`.
            for property_name in property_names:
                field = field_for_node_property(node_or_class, property_name)
                self.fields[property_name] = field
    return Form


def form_class_for_node_link(node_class):
    class Form(forms.Form):
        def __init__(self, *args, **kwargs):
            super(Form, self).__init__(*args, **kwargs)
            field = field_for_node_link(node_class)
            self.fields['link_to'] = field
    return Form


def form_for_node_properties(node_or_class, property_names, data=None):
    if isinstance(node_or_class, type):
        current_values = {}
    else:
        current_values = {
            property_name: getattr(node_or_class, property_name)
            for property_name in property_names
        }
    Form = form_class_for_node_properties(node_or_class, property_names)
    return Form(initial=current_values, data=data)


def form_for_node_link(node_class, data=None):
    Form = form_class_for_node_link(node_class)
    return Form(data=data)
