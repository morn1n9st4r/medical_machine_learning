from django import template

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