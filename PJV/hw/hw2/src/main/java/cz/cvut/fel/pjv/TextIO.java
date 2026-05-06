package cz.cvut.fel.pjv;

import java.util.Scanner;

public final class TextIO {
    private final Scanner scanner;

    public TextIO() {
        this.scanner = new Scanner(System.in);
    }

    /**
     * Get next line from stdin
     *
     * @return text from stdin, or "" if no line is present
     */
    public String getLine() {
        return scanner.hasNext() ? scanner.nextLine() : "";
    }

    /**
     * Check if the provided string is a valid integer
     *
     * @param s string to be checked
     * @return true if valid integer, false otherwise
     */
    public static boolean isInteger(String s) {
        boolean ret = true;
        try {
            Integer.parseInt(s);
        } catch (NumberFormatException e) {
            ret = false;

        }
        return ret;
    }

    /**
     * Check if the provided string is a valid double
     *
     * @param s string to be checked
     * @return true if valid double, false otherwise
     */
    public static boolean isDouble(String s) {
        boolean ret = true;
        try {
            Double.parseDouble(s);
        } catch (NumberFormatException e) {
            ret = false;
        }
        return ret;
    }
} 
