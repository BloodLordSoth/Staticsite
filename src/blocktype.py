from enum import Enum
from textnode import TextType, TextNode
from codefile import text_to_textnodes, markdown_to_blocks
from htmlnode import HTMLNode, ParentNode, LeafNode, text_node_to_html_node

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(markdown):
    if markdown.startswith('#'):
        parts = markdown.split(' ', 1)
        if parts[0].strip() == '#' * len(parts[0].strip()) and 1 <= len(parts[0].strip()) <= 6: # Check if the first part only contains # characters (1-6 of them)
            if len(parts) > 1:
                return BlockType.HEADING

    if markdown.startswith('```') and markdown.endswith("```"):
        return BlockType.CODE
    lines = markdown.split('\n')

    is_quote = all(line.startswith('>') for line in lines)
    if is_quote:
        return BlockType.QUOTE

    lines = markdown.split('\n')
    is_unordered_list = all(line.startswith('- ') for line in lines)
    if is_unordered_list:
        return BlockType.UNORDERED_LIST

    lines = markdown.split('\n')
    is_ordered_list = True

    for i, line in enumerate(lines):
        expected_prefix = f"{i+1}. "
        if not line.startswith(expected_prefix):
            is_ordered_list = False
            break

    if is_ordered_list:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_list = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        html_list.append(html_node)
    return html_list

def process_header_block(block_text):
    heading_level = 0
    for char in block_text:
        if char == '#':
            heading_level += 1
        else:
            break

    if heading_level > 6:
        heading_level = 6

    text_content = block_text[heading_level:].lstrip()
    children = text_to_children(text_content)
    header_node = ParentNode(f"h{heading_level}", children)

    return header_node

def process_quote_block(block_text):
    lines = block_text.split("\n")
    clean_lines = []
    for line in lines:
        if line.startswith(">"):
            clean_line = line[1:].lstrip(" ")
            clean_lines.append(clean_line)
    clean_text = "\n".join(clean_lines)
    children = text_to_children(clean_text)
    return ParentNode("blockquote", children)


def process_code_block(block_text):
    # Split into lines and strip each line
    lines = [line.strip() for line in block_text.strip().split("\n")]
    
    # Find start and end of code block
    start_idx = -1
    end_idx = -1
    
    for i, line in enumerate(lines):
        if line.startswith("```") and start_idx == -1:
            start_idx = i
        elif line.startswith("```") and start_idx != -1:
            end_idx = i
            break
    
    # Extract code content
    if start_idx != -1 and end_idx != -1:
        content_lines = lines[start_idx+1:end_idx]
    else:
        # Fallback - just remove backticks from first and last lines
        content_lines = lines[1:-1] if len(lines) > 2 else []
    
    # Join lines with newlines
    code_content = "\n".join(content_lines) + "\n"
    
    # Create the nodes
    code_node = LeafNode("code", code_content)
    pre_node = ParentNode("pre", [code_node])
    
    return pre_node

def process_ul_block(block_text):
    line_split = block_text.split("\n")
    clean_lines = []
    for char in line_split:
        line_strip = char.strip()
        if line_strip.startswith("-") or line_strip.startswith("* "):
            content = char[2:].strip(" ")
            item_children = text_to_children(content)
            li_node = ParentNode("li", item_children)
            clean_lines.append(li_node)

    return ParentNode("ul", clean_lines)

def process_ol_block(block_text):
    line_split = block_text.split("\n")
    child_tag = []
    for char in line_split:
        line_strip = char.strip()
        if line_strip and line_strip[0].isdigit() and ". " in line_strip:
            marker_end = line_strip.find(". ") + 2
            content = line_strip[marker_end:]
            item_children = text_to_children(content)
            li_node = ParentNode("li", item_children)
            child_tag.append(li_node)
    return ParentNode("ol", child_tag)


def markdown_to_html_node(markdown):
    parent_node = ParentNode("div", [])
    blocks = markdown_to_blocks(markdown)

    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.QUOTE:
            quote_node = process_quote_block(block)
            parent_node.children.append(quote_node)

        elif block_type == BlockType.CODE:
             code_node = process_code_block(block)
             parent_node.children.append(code_node)

        elif block_type == BlockType.HEADING:
            head_node = process_header_block(block)
            parent_node.children.append(head_node)

        elif block_type == BlockType.UNORDERED_LIST:
            ul_block = process_ul_block(block)
            parent_node.children.append(ul_block)

        elif block_type == BlockType.ORDERED_LIST:
            ol_block = process_ol_block(block)
            parent_node.children.append(ol_block)

        else:
            paragraph_text = " ".join([line.strip() for line in block.strip().split("\n")])
            para_text = ParentNode("p", text_to_children(paragraph_text))
            parent_node.children.append(para_text)

    return parent_node