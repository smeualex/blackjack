import os
import logging
import deck
import random

log = logging.getLogger("player")


def log_and_print(msg, log_f=logging.info, end='\n'):
    log_f(msg)
    print(msg, end=end)


class IPlayer:
    """
    Common properties for all players and the dealer
    """
    def __init__(self, nume, jetoane):
        self.nume = nume
        self.jetoane = jetoane
        self.current_hand = []
        self.lost = False

    def __str__(self):
        return "nume=%s; jetoane=%s;" % (self.nume, self.jetoane)

    def draw_card(self, card):
        """
        Get a card from the deck and add it to the current_hand
        """
        self.current_hand.append(card)

    def __add_aces(self, s, aces_in_deck):
        """
        Handle the aces in our hand
            - 1 at most can be added with the value of `11`
            - the rest, if any, will be added as `1`
            - if needed the `11` will be turned into a `1`

        Return: integer - the new sum including the aces
        """

        def can_we_change_ace():
            """
            Helper internal method
            Returns true if we can change an ace from 11 to 1
            """
            return s + deck.Deck.ace.value[0] > 21 and added_ace_11 is True

        added_ace_11 = False
        for i in range(0, aces_in_deck):
            if s + deck.Deck.ace.value[1] <= 21:
                # we can safely add the ace as an 11
                s += deck.Deck.ace.value[1]
            else:
                # if we have only one ace add it as a 1
                if aces_in_deck == 1:
                    s += deck.Deck.ace.value[0]
                    added_ace_11 = True
                else:
                    # we have more than 1 ace in the deck
                    # and adding the final as `1` we will go over 21
                    # one of the previous ones must have been added
                    # as an `11` so we subtract 10 to turn it into a `1`
                    if can_we_change_ace() and i > 0:
                        s -= 10
                    # add the ace as a `1`
                    s += deck.Deck.ace.value[0]
        return s

    def get_cards_sum(self):
        """
        Get the sum of all the cards in the player's hand
        Return: integer - sum of cards
        """
        # sum the non-aces first
        s = sum([card.value for card in self.current_hand
                 if card.type != deck.Deck.ace_card])
        # find the number of aces in the deck
        aces_in_deck = sum([1 for card in self.current_hand
                           if card.type == deck.Deck.ace_card])
        # we now have to add `aces_in_deck` aces to
        # the total sum of the cards
        s = self.__add_aces(s, aces_in_deck)

        return s

    def get_cards_str(self):
        return ' '.join(map(str, self.current_hand))

    def display_name(self):
        """
        Return a display string for the player
            - 'name'                        before the player has any cards
            - 'name [cards list] - sum'     after the game has begun
        Return: str
        """
        if len(self.current_hand) == 0:
            return self.nume
        else:
            card_sum = self.get_cards_sum()
            blackjack = ''
            if card_sum == 21:
                blackjack = 'BLACKJACK !!!'
            return ('%s [%s] - %d' %
                    (self.nume, self.get_cards_str(), card_sum)) + blackjack

    def reset_hand(self):
        self.current_hand = []


class Dealer(IPlayer):
    def __init__(self, jetoane=2000):
        super().__init__("dealer", jetoane)

    def bet_won(self, amount):
        self.jetoane += amount

    def reset_for_new_game(self):
        self.current_hand = []
        self.lost = False


class Player(IPlayer):
    """
    One player
    """
    def __init__(self, nume, prenume, varsta, nationalitate, jetoane):
        super().__init__(nume, jetoane)
        self.prenume = prenume
        self.nationalitate = nationalitate
        self.varsta = varsta
        self.bet_value = 0

    def __str__(self):
        s = ('nume=%s; prenume=%s; nationalitate=%s;'
             ' varsta=%d; jetoane=%d; [bet=%d]') % (
            self.nume, self.prenume, self.nationalitate,
            self.varsta, self.jetoane, self.bet_value)
        return s

    def bet(self, bet_val):
        self.bet_value = bet_val
        self.jetoane -= bet_val

    def reset_bet(self):
        self.bet_value = 0

    def bet_won(self):
        self.jetoane += (2 * self.bet_value)
