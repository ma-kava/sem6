package cz.cvut.fel.pjv.impl;

import cz.cvut.fel.pjv.StatsInterface;

import java.util.ArrayList;

public class Stats implements StatsInterface {
    private ArrayList<Number> number_list = new ArrayList<>();

    @Override
    public void addNumber(double number) {
        if (getCount() == 10) {
            printStatistics();
            number_list.clear();
        }
        number_list.add(number);
    }

    @Override
    public double getAverage() {
        double sum = 0.0;
        for (Number number : number_list) {
            sum += number.doubleValue();
        }
        return sum / getCount();
    }

    @Override
    public double getStandardDeviation() {
        double result = 0;
        double average = getAverage();
        for (Number number : number_list) {
            double deviation = average - number.doubleValue();
            result += deviation * deviation;
        }
        return Math.sqrt(result / getCount());
    }

    @Override
    public int getCount() {
        return (int) number_list.stream().count();
    }

    @Override
    public String getFormattedStatistics() {
        return String.format("%2d %.3f %.3f", getCount(), getAverage(), getStandardDeviation());
    }

    public void printStatistics() {
        System.out.println(getFormattedStatistics());
    }
}
