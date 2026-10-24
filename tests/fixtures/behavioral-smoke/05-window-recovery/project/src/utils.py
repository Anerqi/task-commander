import re

def slugify(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r'[\s_]+', '-', re.sub(r'[^\w\s-]', '', text))
