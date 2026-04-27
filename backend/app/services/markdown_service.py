import re


def parse_markdown_document(markdown: str) -> tuple[dict, str]:
    """解析 Markdown 顶部的轻量 YAML 元数据，并返回正文内容。

    当前知识库只需要 title、topic、level、tags 这类简单字段，
    所以这里不引入额外 YAML 依赖，避免后端环境变复杂。
    """
    match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n?", markdown)

    if not match:
        return {}, markdown

    metadata: dict = {}
    raw_metadata = match.group(1)
    content = markdown[match.end() :]

    for line in raw_metadata.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        if key == "tags":
            metadata[key] = _parse_inline_list(value)
        else:
            metadata[key] = value

    return metadata, content


def _parse_inline_list(value: str) -> list[str]:
    value = value.strip()

    if not value.startswith("[") or not value.endswith("]"):
        return [value] if value else []

    inner = value[1:-1].strip()
    if not inner:
        return []

    return [item.strip().strip("\"'") for item in inner.split(",") if item.strip()]
