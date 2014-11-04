# coding=utf-8
import jinja2

JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(['templates']))


def render(template, template_vars=None):
    if template_vars is None:
        template_vars = {}

    return JINJA_ENV.get_template(template).render(template_vars)
