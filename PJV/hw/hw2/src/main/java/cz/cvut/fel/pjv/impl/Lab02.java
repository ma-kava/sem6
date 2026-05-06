package cz.cvut.fel.pjv.impl;

import java.util.Scanner;

public class Lab02 {
    public static void main(String[] args) {
        Stats stats = new Stats();
        Scanner reader = new Scanner(System.in);
        int lines = 0;

        while (reader.hasNextLine()) {
            lines++;
            String text = reader.nextLine();
            Scanner lineChecker = new Scanner(text);

            if (lineChecker.hasNextDouble()) {
                double num = lineChecker.nextDouble();
                stats.addNumber(num);
            } else {
                System.err.println(String.format(
                        "A number has not been parsed from line %d", lines));
            }
        }

        System.err.println("End of input detected!");

        if (stats.getCount() > 0) {
            String formatted = stats.getFormattedStatistics();
            System.out.println(formatted);
        }
    }
}