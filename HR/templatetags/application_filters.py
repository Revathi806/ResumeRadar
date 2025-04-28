# HR/templatetags/application_filters.py
from django import template

register = template.Library()

@register.filter
def filter_status(applications, status):
    return [app for app in applications if app.status == status]

@register.filter
def status_count(applications, status):
    return len([app for app in applications if app.status == status])