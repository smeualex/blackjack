import random
import logging

from blackjack.util import delay

log = logging.getLogger("deck")


def log_and_print(msg, log_f=logging.info, end='\n'):
    log_f(msg)
    print(msg, end=end)


class Card:
    def __init__(self, type, suite, value):
        """
        Create a Card object
        """
        self.type = type
        self.suite = suite
        self.display_str = self.type + self.suite
        self.value = value

    def __str__(self):
        return self.display_str


class Deck:
    ace_card = " A"
    ace = Card(" A", "♠", [1, 11])
    two = Card(" 2", "♠", 2)
    king = Card(" K", "♠", 10)
    card_names = [
        (" 2", 2),  (" 3", 3),       (" 4", 4),  (" 5", 5),
        (" 6", 6),  (" 7", 7),       (" 8", 8),  (" 9", 9),
        ("10", 10), (" A", [1, 11]), (" J", 10), (" Q", 10),
        (" K", 10)
    ]
    card_suites = ["♠", "♡", "♢", "♣"]

    def __init__(self):
        """
        Create a deck of 52 standard cards
        """
        log_and_print(' > Got a new fresh deck...')
        self.card_deck = [Card(card[0], suite, card[1])
                          for card in self.card_names
                          for suite in self.card_suites]

    def log(self):
        """
        Log the deck in its current state
        """
        log.debug("Deck: [%d cards]" % len(self.card_deck))

        GROUP_CARDS = 16
        for idx in range(0, len(self.card_deck) + 1, GROUP_CARDS):
            tmp = [self.card_deck[i]
                   for i in range(0 + idx,
                                  min(len(self.card_deck), GROUP_CARDS+idx))]
            log.debug(' '.join(map(str, tmp)))

    def shuffle(self):
        """
        Shuffle the deck for a random number of times
        """
        log_and_print('')
        log_and_print(' > Shuffling the cards', end='')
        random.seed()

        number_of_shuffles = random.randrange(10, 50)

        log.debug("Shuffling the deck %d times" % number_of_shuffles)
        for i in range(0, number_of_shuffles):
            delay(random.randrange(30, 70, 5))
            random.shuffle(self.card_deck)

        log_and_print('')
        log_and_print("Shuffled deck")

    def draw_card(self):
        """
        Get the first card from the pack
        The card is removed from the pack
        """
        return self.card_deck.pop(0)
