package cz.cvut.fel.pjv.impl;

import cz.cvut.fel.pjv.Lab01;

import java.util.Scanner;

public class Lab01Impl implements Lab01 {
    @Override
    public void homework() {
        String operation = "+";
        String message1 = "scitanec", message2 = "scitanec";
        Scanner scanner = new Scanner(System.in);

        System.out.println("Vyber operaci (1-soucet, 2-rozdil, 3-soucin, 4-podil):");
        Number choice = readInput(scanner, true);

        if (choice == null || choice.intValue() > 4 || choice.intValue() < 0) {
            System.out.println("Chybna volba!");
            return;
        }

        switch (choice.intValue()) {
            case 2:
                message1 = "mensenec";
                message2 = "mensitel";
                break;
            case 3:
                message1 = message2 = "cinitel";
                break;
            case 4:
                message1 = "delenec";
                message2 = "delitel";
                break;
            default:
        }

        System.out.println("Zadej " + message1 + ": ");
        Number operand1 = readInput(scanner, false);
        if (operand1 == null) {
            System.out.println("Chybna volba!");
            return;
        }

        System.out.println("Zadej " + message2 + ": ");
        Number operand2 = readInput(scanner, false);
        if (operand2 == null) {
            System.out.println("Chybna volba!");
            return;
        }

        if (choice.intValue() == 4 && operand2.doubleValue() == 0) {
            System.out.println("Pokus o deleni nulou!");
            return;
        }

        System.out.println("Zadej pocet desetinnych mist: ");
        Number precision = readInput(scanner, true);

        if (precision == null) {
            System.out.println("Chybna volba!");
            return;
        } else if (precision.intValue() < 0) {
            System.out.println("Chyba - musi byt zadane kladne cislo!");
            return;
        }

        double num1 = operand1.doubleValue();
        double num2 = operand2.doubleValue();
        int order = precision.intValue();

        double result = 0;
        switch (choice.intValue()) {
            case 1:
                result = num1 + num2;
                break;
            case 2:
                operation = "-";
                result = num1 - num2;
                break;
            case 3:
                operation = "*";
                result = num1 * num2;
                break;
            case 4:
                operation = "/";
                result = num1 / num2;
                break;
        }

        System.out.printf("%." + order + "f %s %." + order + "f = %." + order + "f\n",
                num1, operation, num2, result);
    }

    private Number readInput(Scanner scanner, boolean integer) {
        if (integer) {
            if (scanner.hasNextInt()) {
                return scanner.nextInt();
            }
        } else {
            if (scanner.hasNextDouble()) {
                return scanner.nextDouble();
            }
        }
        scanner.next(); // důležité – vyčistí nevalidní vstup
        return null;
    }
}
