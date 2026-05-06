package cz.cvut.fel.pjv;

import java.util.Collection;

public interface Queue {

    /**
     * It will count number of elements in CircularArrayQueue, not a size of the structure
     * @return the number of elements in CircularArrayQueue (int)
     */
    int size();

    /**
     * It will check if CircularArrayQueue is empty
     * @return <code>true</code> if the CircularArrayQueue is empty and contains no elements
    <code>false</code> otherwise (CircularArrayQueue contains atleast one element).
     */
    boolean isEmpty();

    /**
     * It will check if CircularArrayQueue is full
     * @return <code>true</code> if the CircularArrayQueue is full
    <code>false</code> otherwise.
     */
    boolean isFull();

    /**
     * This method will enqueue the String to CircularArrayQueue
     * @param obj the String object that we want add to CircularArrayQueue
     * @return <code>true</code> if the obj param is added to CircularArrayQueue
    <code>false</code> otherwise (if CircularArrayQueue is full or if obj param is null).
     */
    boolean enqueue(String obj);

    /**
     * This method will dequeue the first String from CircularArrayQueue
     * @return <code>String value</code> if the CircularArrayQueue is not empty
    <code>null</code> otherwise (if CircularArrayQueue is empty).
     */
    String dequeue();

    /**
     * This method will return all non-null elements from CircularArrayQueue
     * @return <code>Collection<String></code> of non-null elements
     */
    Collection<String> getElements();

    /**
     * It will print all non-null elements from CircularArrayQueue
     */
    void printAllElements();
}
