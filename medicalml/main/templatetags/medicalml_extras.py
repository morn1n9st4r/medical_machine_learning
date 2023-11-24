from django import template


from ..choices import *

register = template.Library()


@register.filter(name='instanceof')
def isinstanceof(value, class_str):
    try:
        model_class = eval(class_str)
        return isinstance(value, model_class)
    except (NameError, TypeError):
        return False

@register.filter(name='variable_type')
def variable_type(value):
    return type(value).__name__

@register.filter(name='tag_definition')
def tag_definition(value):
    dictionary = list(set().union(GENDER_CHOICES, TAGS_CHOICES, SEVERITY_CHOICES, FORM_CHOICES, FREQUENCY_CHOICES))
    return dict(dictionary).get(value, value)

@register.filter(name='split_examinations')
def split_examinations(value):
    return value.split(', ')