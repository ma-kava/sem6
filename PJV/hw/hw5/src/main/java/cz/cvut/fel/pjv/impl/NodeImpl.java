package cz.cvut.fel.pjv.impl;

import cz.cvut.fel.pjv.Node;

public class NodeImpl implements Node {
    public NodeImpl left;
    public NodeImpl right;
    private int value;
    public int depth;

    NodeImpl(int value) {
        this.value = value;
    }

    @Override
    public Node getLeft() {
        return this.left;
    }

    @Override
    public Node getRight() {
        return this.right;
    }

    @Override
    public int getValue() {
        return this.value;
    }
}
