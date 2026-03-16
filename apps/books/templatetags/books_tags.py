from django import template


register = template.Library()
TAG_TONE_COUNT = 6


@register.filter
def tag_tone(value):
    text = str(value or "").strip()
    if not text:
        return 0
    score = sum((index + 1) * ord(char) for index, char in enumerate(text))
    return score % TAG_TONE_COUNT
