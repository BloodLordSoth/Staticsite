import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node
from textnode import TextNode, TextType

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        # Test with multiple properties
        node = HTMLNode(props={"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')
    
    def test_props_to_html_empty(self):
        # Test with empty props
        node = HTMLNode(props={})
        self.assertEqual(node.props_to_html(), "")
        # Test with None props
        node = HTMLNode(props=None)
        self.assertEqual(node.props_to_html(), "")
    
    def test_tag_value_initialization(self):
        # Test tag and value initialization
        node = HTMLNode(tag="p", value="Hello, world!")
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "Hello, world!")
    
    def test_children_initialization(self):
        # Test children initialization
        child1 = HTMLNode(tag="span", value="Child 1")
        child2 = HTMLNode(tag="a", value="Child 2", props={"href": "#"})
        parent = HTMLNode(tag="div", children=[child1, child2])
        
        self.assertEqual(len(parent.children), 2)
        self.assertEqual(parent.children[0].value, "Child 1")
        self.assertEqual(parent.children[1].tag, "a")

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_link(self):
    # The constructor should be: LeafNode(tag, value, props)
    # Props should be a dictionary
        node = LeafNode("a", "Click here to learn!", {"href": "http://www.boot.dev"})
        self.assertEqual(node.to_html(), '<a href="http://www.boot.dev">Click here to learn!</a>')

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
        parent_node.to_html(),
        "<div><span><b>grandchild</b></span></div>",
        )

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

if __name__ == "__main__":
    unittest.main()