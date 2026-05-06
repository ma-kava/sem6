package cz.cvut.fel.pjv;

import cz.cvut.fel.pjv.impl.TreeImpl;

public class Main {
    public static void main(String[] argv) {
        Tree tree = new TreeImpl();
        int[] arr = new int[]{1,2,3,4,5,6};
        tree.setTree(arr);
        System.out.println(tree.toString());
        System.out.println(tree.getRoot());
    }
}
