import re


def tokenize_text(text: str) -> set[str]:
    """第一版先用轻量分词占位，后续可替换为真实 Embedding。"""
    normalized = text.lower()
    ascii_terms = re.findall(r"[a-z0-9_+#.]{2,}", normalized)
    chinese_terms = re.findall(r"[\u4e00-\u9fff]{2,}", normalized)

    tokens = set(ascii_terms)
    for term in chinese_terms:
        tokens.add(term)
        for index in range(len(term) - 1):
            tokens.add(term[index : index + 2])

    return tokens
