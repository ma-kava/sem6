package cz.cvut.fel.pjv;

/**
 * Interface Node represents one node of binary tree. It contains integer value.
 */
public interface Node {
	
	/**
	 * @return left child of this node, or null
	 */
	Node getLeft();
	
	/**
	 * @return right child of this node, or null
	 */
	Node getRight();
	
	/**
	 * @return value of this node
	 */
	int getValue();
}
