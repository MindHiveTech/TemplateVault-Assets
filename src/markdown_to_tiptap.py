"""
Markdown to TipTap Converter

Converts Markdown to Circle API v2 TipTap JSON format (ProseMirror).
"""

from markdown_it import MarkdownIt
from markdown_it.token import Token


def markdown_to_tiptap(markdown: str) -> dict:
    """
    Convert markdown to TipTap JSON format.

    Args:
        markdown: Markdown string

    Returns:
        TipTap JSON document (dict with type="doc")
    """
    md = MarkdownIt()
    tokens = md.parse(markdown)

    content = []
    i = 0
    while i < len(tokens):
        node = _convert_token(tokens, i)
        if node:
            content.append(node)
            i = node.get("_skip_to", i + 1)
        else:
            i += 1

    return {"type": "doc", "content": content}


def _convert_token(tokens: list[Token], index: int) -> dict | None:
    """
    Convert a markdown-it token to TipTap node.

    Args:
        tokens: List of all tokens
        index: Current token index

    Returns:
        TipTap node dict or None if token should be skipped
    """
    token = tokens[index]

    # Heading
    if token.type == "heading_open":
        level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
        inline_token = tokens[index + 1]
        content = _convert_inline(inline_token)
        node = {"type": "heading", "attrs": {"level": level}, "content": content}
        node["_skip_to"] = index + 3  # Skip heading_open, inline, heading_close
        return node

    # Paragraph
    if token.type == "paragraph_open":
        inline_token = tokens[index + 1]
        content = _convert_inline(inline_token)
        node = {"type": "paragraph", "content": content}
        node["_skip_to"] = index + 3  # Skip paragraph_open, inline, paragraph_close
        return node

    # Bullet list
    if token.type == "bullet_list_open":
        items, end_index = _convert_list(tokens, index, "bullet")
        node = {"type": "bulletList", "content": items}
        node["_skip_to"] = end_index + 1
        return node

    # Ordered list
    if token.type == "ordered_list_open":
        items, end_index = _convert_list(tokens, index, "ordered")
        node = {"type": "orderedList", "content": items}
        node["_skip_to"] = end_index + 1
        return node

    # Blockquote
    if token.type == "blockquote_open":
        content, end_index = _convert_blockquote(tokens, index)
        node = {"type": "blockquote", "content": content}
        node["_skip_to"] = end_index + 1
        return node

    # Code block
    if token.type == "fence" or token.type == "code_block":
        language = token.info or None
        code_attrs = {}
        if language:
            code_attrs["language"] = language
        node = {
            "type": "codeBlock",
            "attrs": code_attrs if code_attrs else {},
            "content": [{"type": "text", "text": token.content}],
        }
        return node

    # Horizontal rule
    if token.type == "hr":
        return {"type": "horizontalRule"}

    # Skip close tokens and other non-content tokens
    return None


def _convert_inline(token: Token) -> list:
    """
    Convert inline token to TipTap inline content.

    Args:
        token: Inline token from markdown-it

    Returns:
        List of TipTap inline nodes
    """
    if not token.children:
        return []

    content = []
    i = 0
    while i < len(token.children):
        child = token.children[i]

        # Text
        if child.type == "text":
            text_node = {"type": "text", "text": child.content}
            content.append(text_node)
            i += 1

        # Strong (bold)
        elif child.type == "strong_open":
            text_content, end_index = _collect_text_until(token.children, i + 1, "strong_close")
            if text_content:
                content.append({"type": "text", "marks": [{"type": "bold"}], "text": text_content})
            i = end_index + 1

        # Emphasis (italic)
        elif child.type == "em_open":
            text_content, end_index = _collect_text_until(token.children, i + 1, "em_close")
            if text_content:
                content.append(
                    {"type": "text", "marks": [{"type": "italic"}], "text": text_content}
                )
            i = end_index + 1

        # Link
        elif child.type == "link_open":
            href = child.attrGet("href") or ""
            text_content, end_index = _collect_text_until(token.children, i + 1, "link_close")
            if text_content:
                content.append(
                    {
                        "type": "text",
                        "marks": [{"type": "link", "attrs": {"href": href}}],
                        "text": text_content,
                    }
                )
            i = end_index + 1

        # Code (inline)
        # NOTE: Circle has issues with inline code marks, so we render as plain text
        elif child.type == "code_inline":
            content.append({"type": "text", "text": child.content})
            i += 1

        # Softbreak / hardbreak
        elif child.type == "softbreak" or child.type == "hardbreak":
            # Softbreaks are usually spaces in TipTap paragraphs
            content.append({"type": "text", "text": " "})
            i += 1

        else:
            i += 1

    return content


def _collect_text_until(children: list[Token], start: int, end_type: str) -> tuple[str, int]:
    """
    Collect text content until a specific token type.

    Args:
        children: List of inline tokens
        start: Start index
        end_type: Token type to stop at

    Returns:
        Tuple of (collected text, end index)
    """
    text = ""
    i = start
    while i < len(children):
        if children[i].type == end_type:
            return text, i
        if children[i].type == "text" or children[i].type == "code_inline":
            text += children[i].content
        i += 1
    return text, i


def _convert_list(tokens: list[Token], start_index: int, list_type: str) -> tuple[list, int]:
    """
    Convert a list (bullet or ordered) to TipTap format.

    Args:
        tokens: All tokens
        start_index: Index of list_open token
        list_type: "bullet" or "ordered"

    Returns:
        Tuple of (list items, end index)
    """
    items = []
    i = start_index + 1
    close_type = "bullet_list_close" if list_type == "bullet" else "ordered_list_close"

    while i < len(tokens) and tokens[i].type != close_type:
        if tokens[i].type == "list_item_open":
            # Find corresponding list_item_close
            item_content = []
            i += 1
            depth = 1
            while i < len(tokens) and depth > 0:
                if tokens[i].type == "list_item_open":
                    depth += 1
                elif tokens[i].type == "list_item_close":
                    depth -= 1
                    if depth == 0:
                        break

                # Convert item content
                if tokens[i].type == "paragraph_open":
                    inline_token = tokens[i + 1]
                    content = _convert_inline(inline_token)
                    item_content.append({"type": "paragraph", "content": content})
                    i += 3  # Skip paragraph_open, inline, paragraph_close
                else:
                    i += 1

            items.append({"type": "listItem", "content": item_content})
        i += 1

    return items, i


def _convert_blockquote(tokens: list[Token], start_index: int) -> tuple[list, int]:
    """
    Convert a blockquote to TipTap format.

    Args:
        tokens: All tokens
        start_index: Index of blockquote_open token

    Returns:
        Tuple of (blockquote content, end index)
    """
    content = []
    i = start_index + 1

    while i < len(tokens) and tokens[i].type != "blockquote_close":
        if tokens[i].type == "paragraph_open":
            inline_token = tokens[i + 1]
            paragraph_content = _convert_inline(inline_token)
            content.append({"type": "paragraph", "content": paragraph_content})
            i += 3  # Skip paragraph_open, inline, paragraph_close
        else:
            i += 1

    return content, i
