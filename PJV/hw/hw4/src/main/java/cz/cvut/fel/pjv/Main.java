package cz.cvut.fel.pjv;

import cz.cvut.fel.pjv.impl.BruteForceAttacker;

public class Main {
    public static void main(String[] args) {
        final String chars = "ABCDEFGHIJKLMNOPRSTU";
        final String password = "ALFAOMEGA";

        BruteForceAttacker attacker = new BruteForceAttacker();
        attacker.init(chars.toCharArray(), password);
        attacker.breakPassword(password.length());
        System.out.println(attacker.isOpened());
    }
}
