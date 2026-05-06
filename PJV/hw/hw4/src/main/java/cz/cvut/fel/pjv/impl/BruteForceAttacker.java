package cz.cvut.fel.pjv.impl;

import cz.cvut.fel.pjv.Thief;

public class BruteForceAttacker extends Thief {
    @Override
    public void breakPassword(int sizeOfPassword) {
        char[] alphabet = getCharacters();
        char[] attempt = new char[sizeOfPassword];

        bruteForce(attempt, alphabet, 0);
    }

    private void bruteForce(char[] attempt, char[] alphabet, int position) {
        if (position == attempt.length) {
            if (tryOpen(attempt)) {
                return;
            }
            return;
        }

        for (char c : alphabet) {
            attempt[position] = c;
            bruteForce(attempt, alphabet, position + 1);
            if (isOpened()) return;
        }
    }
}
