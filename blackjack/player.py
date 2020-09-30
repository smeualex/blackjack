import os
import logging
import random

from blackjack.deck import Deck

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
            return s + Deck.ace.value[0] > 21 and added_ace_11 is True

        added_ace_11 = False
        for i in range(0, aces_in_deck):
            if s + Deck.ace.value[1] <= 21:
                # we can safely add the ace as an 11
                s += Deck.ace.value[1]
            else:
                # if we have only one ace add it as a 1
                if aces_in_deck == 1:
                    s += Deck.ace.value[0]
                    added_ace_11 = True
                else:
                    # we have more than 1 ace in the deck
                    # and adding the final as `1` we will go over 21
                    # one of the previous ones must have been added
                    # as an `11` so we subtract 10 to turn it into a `1`
                    if can_we_change_ace() and i > 0:
                        s -= 10
                    # add the ace as a `1`
                    s += Deck.ace.value[0]
        return s

    def get_cards_sum(self):
        """
        Get the sum of all the cards in the player's hand
        Return: integer - sum of cards
        """
        # sum the non-aces first
        s = sum([card.value for card in self.current_hand
                 if card.type != Deck.ace_card])
        # find the number of aces in the deck
        aces_in_deck = sum([1 for card in self.current_hand
                           if card.type == Deck.ace_card])
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

    def reset(self):
        self.current_hand = []
        self.lost = False

    def bet_won(self):
        pass

    def bet_lost(self):
        pass

    def draw(self):
        pass


class Dealer(IPlayer):
    def __init__(self, jetoane=2000):
        super().__init__("dealer", jetoane)
        self.balance = 0

    def bet_won(self, amount):
        log.debug('Dealer won %d' % amount)
        self.jetoane += amount
        self.balance += amount

    def bet_lost(self, amount):
        log.debug('Dealer lost %d' % amount)
        self.lost = True
        self.jetoane -= amount
        self.balance -= amount

    def reset_for_new_game(self):
        self.reset()
        self.balance = 0


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

    def bet(self):
        while True:
            try:
                log_and_print('')
                bet_value = int(input(' > %s place your bet: '
                                      % self.nume))
            except ValueError:
                print(' > Please enter only digits for the bet amount')
                continue

            if bet_value > self.jetoane:
                print(' > You\'re not that rich!!!'
                      ' Please enter a bet lower'
                      ' than your total amount [%d] !!!'
                      % self.jetoane)
                continue

            if bet_value < 0:
                print(' > Really?! Try again!')
                continue
            break
        # set the player's bet
        self.bet_value = bet_value
        self.jetoane -= bet_value
        return bet_value

    def reset_for_new_game(self):
        self.reset()
        self.balance = 0

    def bet_won(self):
        log.debug('Player %s won %d' %
                  (self.nume, (2 * self.bet_value)))
        self.jetoane += (2 * self.bet_value)

    def draw(self):
        log.debug('Player %s draw' % self.nume)
        self.jetoane += self.bet_value
