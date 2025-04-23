import re
import os
from textnode import TextType, TextNode
from htmlnode import *

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for old_node in old_nodes:
        # If the node isn't a text node, we don't need to process it
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        # Split the text by the delimiter
        parts = old_node.text.split(delimiter)
        
        # If there's an even number of parts, that means we have unmatched delimiters
        # (think about it: text`code`more text -> 3 parts, which is odd)
        if len(parts) % 2 == 0:
            raise Exception(f"Invalid markdown syntax: unmatched delimiter {delimiter}")
        
        # Process each part
        for i in range(len(parts)):
            # Skip empty parts, but only if they're regular text
            if parts[i] == "" and i % 2 == 0:
                continue
                
            # Even indices are regular text (outside delimiters)
            if i % 2 == 0:
                new_nodes.append(TextNode(parts[i], TextType.TEXT))
            # Odd indices are the special text type (between delimiters)
            else:
                new_nodes.append(TextNode(parts[i], text_type))
    
    return new_nodes

def extract_markdown_images(text):
    pattern = r'!\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, text)
    return matches

def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        matches = extract_markdown_links(text)

        if not matches:
            new_nodes.append(node)
            continue

        i = 0
        for anchor, url in matches:
            link_md = f"[{anchor}]({url})"
            start = text.find(link_md, i)

            if start > i:
                new_nodes.append(TextNode(text[i:start], TextType.TEXT))
            new_nodes.append(TextNode(anchor, TextType.LINK, url))

            i = start + len(link_md)

        if i < len(text):
            new_nodes.append(TextNode(text[i:], TextType.TEXT))

    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        matches = extract_markdown_images(text)

        if not matches:
            new_nodes.append(node)
            continue

        i = 0
        for alt, url in matches:
            img_md = f"![{alt}]({url})"
            start = text.find(img_md, i)

            if start > i:
                new_nodes.append(TextNode(text[i:start], TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))

            i = start + len(img_md)

        if i < len(text):
            new_nodes.append(TextNode(text[i:], TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes

def markdown_to_blocks(markdown):

    md_filter = markdown.split("\n\n")
    cleaned_blocks = []

    for block in md_filter:
        if block.strip():  # Check if block has content after stripping
            # Split by newlines, strip each line, then rejoin
            lines = block.strip().split("\n")
            cleaned_lines = [line.strip() for line in lines]
            cleaned_block = "\n".join(cleaned_lines)
            cleaned_blocks.append(cleaned_block)

    return cleaned_blocks

def extract_title(markdown):
    head_split = markdown.split("\n")
    for title in head_split:
        result = title.strip()
        if result.startswith("# "):
            return result[2:]
    raise Exception ("No title found")

def generate_page(from_path, template_path, dest_path, basepath):
    from blocktype import markdown_to_html_node
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path) as file:
        md_content = file.read()
        print("Markdown content:", md_content)
        md_file = markdown_to_html_node(md_content).to_html() # converts markdown to HTML
        final = extract_title(md_content) # Extracts the title from the markdown file

    with open(template_path) as file:
        template = file.read() # extracts my template
        new_template = template.replace('{{ Title }}', final).replace('{{ Content }}', md_file)
        new_template = new_template.replace('href="/', f'href="{basepath}')
        new_template = new_template.replace('src="/', f'src="{basepath}')

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'w') as outfile:
        #print("Generated template:", new_template)
        outfile.write(new_template)


    
    
