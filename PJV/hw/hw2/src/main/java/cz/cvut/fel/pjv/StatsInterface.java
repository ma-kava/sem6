package cz.cvut.fel.pjv;

public interface StatsInterface {
    /**
     * Add number to the sequence. If this is a 10th number, print the statistics
     * via {@link #getFormattedStatistics()} and reset the statistics
     *
     * @param number to be added
     */
    void addNumber(double number);

    /**
     * Calculates average from values saved within the instance.
     *
     * @return average value
     */
    double getAverage();

    /**
     * Calculates standard deviation from values saved within the instance.
     * Use
     *
     * @return standard deviation
     */
    double getStandardDeviation();

    /**
     * Get count of numbers from which the statistics is calculated.
     *
     * @return count of numbers
     */
    int getCount();

    String getFormattedStatistics();
}
