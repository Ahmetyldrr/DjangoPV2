from django import template
import markdown

register = template.Library()

@register.filter
def markdown_to_html(value):
    """Markdown metnini HTML'e çevirir"""
    if value:
        return markdown.markdown(value, extensions=['nl2br', 'fenced_code'])
    return value
