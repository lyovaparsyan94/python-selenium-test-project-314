def build_xpath_by_text(tag: str, text: str) -> str:
    """Return an XPath expression that matches elements by their normalized text."""
    normalized_tag = tag or "*"

    if "'" not in text:
        return f"//{normalized_tag}[normalize-space()='{text}']"

    if '"' not in text:
        return f'//{normalized_tag}[normalize-space()="{text}"]'

    parts = text.split("'")
    concat_args = []
    for index, part in enumerate(parts):
        if part:
            concat_args.append(f"'{part}'")
        if index != len(parts) - 1:
            concat_args.append('"\'"')

    joined = ", ".join(concat_args)
    return f"//{normalized_tag}[normalize-space()=concat({joined})]"

