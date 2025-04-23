import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_ITALIC(self):
        node = TextNode("another", TextType.ITALIC)
        node2 = TextNode("Random string", TextType.ITALIC)
        self.assertEqual(node, node2)

if __name__ == "__main__":
    unittest.main()