package cz.cvut.fel.pjv.impl;

import cz.cvut.fel.pjv.Node;
import cz.cvut.fel.pjv.Tree;

public class TreeImpl implements Tree {
    NodeImpl root;

    /**
     * TreeImpl has to have noarg constructor
     */
    public TreeImpl() {}

    @Override
    public void setTree(int[] values) {
        if (values == null || values.length == 0) {
            root = null;
            return;
        }

        root = treeRecur(values, 0, values.length, 0);
    }

    private NodeImpl treeRecur(int[] arr, int start, int end, int depth) {
        if (start >= end) {
            return null;
        }

        int middle = start + (end - start) / 2;

        NodeImpl node = new NodeImpl(arr[middle]);
        node.depth = depth;

        node.left = treeRecur(arr, start, middle, depth + 1);
        node.right = treeRecur(arr, middle + 1, end, depth + 1);

        return node;
    }

    @Override
    public Node getRoot() {
        return root;
    }

    @Override
    public String toString() {
        return toString(root, 0);
    }

    public String toString(NodeImpl node, int depth) {
        if (node == null) {
            return "";
        }

        StringBuilder ret = new StringBuilder();

        for (int i = 0; i < depth; i++) {
            ret.append(" ");
        }
        ret.append("- ");
        ret.append(node.getValue());
        ret.append("\n");

        ret.append(toString(node.left, depth + 1));
        ret.append(toString(node.right, depth + 1));

        return ret.toString();
    }

}
