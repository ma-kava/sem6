package cz.cvut.fel.pjv.impl;

import cz.cvut.fel.pjv.Queue;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * Implementation of the {@link Queue} backed by fixed size array.
 */
public class CircularArrayQueue implements Queue {
    private final String[] array;
    private final int max_capacity;

    private int size = 0;
    private int first_idx = 0;
    private int last_idx = 0;

    /**
     * Creates the queue with capacity set to the value of 5.
     */
    public CircularArrayQueue() {
        array = new String[5];
        max_capacity = 5;
    }

    /**
     * Creates the queue with given {@code capacity}. The capacity represents maximal number of elements that the
     * queue is able to store.
     * @param capacity of the queue
     */
    public CircularArrayQueue(int capacity) {
        array = new String[capacity];
        max_capacity = capacity;
    }

    @Override
    public int size() {
        return size;
    }

    @Override
    public boolean isEmpty() {
        return size == 0;
    }

    @Override
    public boolean isFull() {
        return size == max_capacity;
    }

    @Override
    public boolean enqueue(String obj) {
        if (size < max_capacity && obj != null) {
            size += 1;
            array[last_idx] = obj;
            last_idx = (last_idx + 1) % max_capacity;
            return true;
        }
        return false;

    }

    @Override
    public String dequeue() {
        if (size > 0) {
            size -= 1;
            String ret = array[first_idx];
            array[first_idx] = "";
            first_idx = (first_idx + 1) % max_capacity;
            return ret;
        }
        return null;
    }

    @Override
    public Collection<String> getElements() {
        List<String> list = new ArrayList<>(size);
        for (int i = 0; i < size; i++) {
            list.add(array[(first_idx + i) % max_capacity]);
        }
        return list;
    }

    @Override
    public void printAllElements() {
        int idx = first_idx;
        for (int i = 0; i < size; i++) {
            System.out.println(array[idx]);
            idx = (idx + 1) % max_capacity;
        }
    }

}
