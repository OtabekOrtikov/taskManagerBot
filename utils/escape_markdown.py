import re

def escape_markdown_v2(text: str) -> str:
    # List of Markdown special characters that need to be escaped
    escape_chars = r'\.*_`[]()~>#+-=|{}!'
    # Escape each special character with a preceding backslash
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)