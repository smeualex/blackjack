import logging
import time

from deck import Deck
from player import Dealer
from util import delay
from game_outcome import game_outcome
from registered_players import Players

log = logging.getLogger("game")


def log_and_print(msg, log_f=logging.info, end='\n'):
    log_f(msg)
    print(msg, end=end)


class Game:
    def __init__(self):
        """
        A new game
            - registered players are taken from input file
            - dealer gets 1000
            - a new fresh deck
            - deck is shuffled
        """
        self.players = Players()
        # self.self.losers = []
        self.dealer = Dealer(1000)
        self.deck = Deck()
        self.deck.log()
        self.deck.shuffle()
        self.deck.log()
        self.rounds_played = 0
        self.total_bets = 0
        self.__outcome = game_outcome(self)

    def run(self):
        """
        Game main
        """
        # set the bets
        self.__set_bets()
        # deal cards
        self.__deal_first_hand()
        # log current game state
        self.log()
        # ask each player - (h)it or (s)tand?
        self.__players()
        # dealer's turn
        self.__dealer()
        # game's outcome
        self.__outcome.get()
        # see who's broke
        self.__check_players_for_money()
        # show the round's results
        self.__show_outcome()
        # reset for a new game
        self.__reset()

    def __deal_first_hand(self):
        """
        Deals the first hand:
            - player 1, 2, 3, 4 first card
            - dealer           only card
            - player 1, 2, 3, 4 second card
        """
        log_and_print('')
        log_and_print(" > Dealing cards", end='')
        # players first card
        for player in self.players.players:
            delay()
            player.draw_card(self.deck.draw_card())

        # dealer
        delay()
        self.dealer.draw_card(self.deck.draw_card())

        # players second card
        for player in self.players.players:
            delay()
            player.draw_card(self.deck.draw_card())
        log_and_print('')

    def __set_bets(self):
        """
        Ask all the players to place their bets
        """
        log.debug('Setting bets...')
        for player in self.players.players:
            self.total_bets += player.bet()

    def hit(self, player):
        card = self.deck.draw_card()
        player.draw_card(card)

        log_and_print('\t\t>> %s drew a card - [%s]' %
                      (player.nume, str(card)))

        if(player.get_cards_sum() == 21):
            log_and_print('\t\t>> %s ' % (player.display_name()))

        if(player.get_cards_sum() > 21):
            player.lost = True
            log_and_print('\t\t>> %s is done' % (player.display_name()))
            return -1

        return 0

    def stand(self, player):
        log_and_print('\t\t>> %s stands [sum=%d]' %
                      (player.display_name(), player.get_cards_sum()))
        log_and_print('-' * 80)

    def players_in_game(self):
        return len(self.players.get())

    def new_round(self):
        answer = ' '
        while answer != 'y' and answer != 'n':
            if self.rounds_played > 0:
                msg = "Fancy another round? (Y)es or (N)o: "
            else:
                msg = "Shall we begin a game?  (Y)es or (N)o: "
            answer = input(msg).lower()
        if answer == 'y':
            self.rounds_played += 1
            # check if we need a new deck
            self.__new_deck()

        return answer == 'y'

    def log(self):
        """
        Log current game state
        """
        # header
        log_and_print('')
        log.debug('-' * 80)
        log.debug('-- GAME STATE')
        log.debug('')

        # deck
        self.deck.log()
        log.debug('')

        fmt = ' %12s[%4d$] : %24s'

        # dealer
        log_and_print(fmt %
                      (self.dealer.nume, self.dealer.jetoane,
                       self.dealer.get_cards_str()))
        # players
        for player in self.players.players:
            log_and_print(fmt %
                          (player.nume, player.jetoane,
                           player.get_cards_str()))
        # bankrupts
        if len(self.players.broke_players) > 0:
            log_and_print('')
            log_and_print('Went bankrupt: ')
            for player in self.players.broke_players:
                log_and_print(fmt %
                              (player.nume, player.jetoane,
                               player.get_cards_str()))

        # footer
        log.debug('-' * 80)
        log_and_print('')

    def __everyone_lost(self):
        """
        Return True if everyone lost :(
        """
        return (self.dealer.lost and
                len(self.players.get_losers()) == len(self.players.get()))

    def __all_players_lost(self):
        """
        Return True if all players lost lost :(
        """
        return (len(self.players.get_losers()) == len(self.players.get()))

    def __show_outcome(self):
        """
        Log current round's status
        """
        # header
        log_and_print('')
        log.debug('-' * 80)
        log.debug('-- ROUND RESULT')
        log.debug('')

        # deck
        self.deck.log()
        log.debug('')

        # print format
        # ' name[money] : cards list | cards sum - [WON/LOST] bet_value
        fmt = ' %12s[%4d$] : %24s | %2d | %5s %4s$'
        fmt_l = ' %12s[%4d$] LOST'
        fmt_b = ' %12s[%4d$]'

        # all lost
        if self.__everyone_lost():
            # dealer
            log_and_print(fmt_l %
                          (self.dealer.nume, self.dealer.jetoane))
            # players
            for player in self.players.players:
                log_and_print(fmt_l %
                              (player.nume, player.jetoane))
        else:
            # dealer
            log_and_print(fmt %
                          (self.dealer.nume, self.dealer.jetoane,
                           self.dealer.get_cards_str(),
                           self.dealer.get_cards_sum(),
                           "LOSES" if self.dealer.lost else "WINS",
                           ''))
            # players
            for player in self.players.players:
                log_and_print(fmt %
                              (player.nume, player.jetoane,
                               player.get_cards_str(),
                               player.get_cards_sum(),
                               "LOSES" if player.lost else "WINS",
                               str(player.bet_value)))

        # bankrupts
        if len(self.players.broke_players) > 0:
            log_and_print('')
            log_and_print('Went bankrupt: ')
            for player in self.players.broke_players:
                log_and_print(fmt_b %
                              (player.nume, player.jetoane))

    def __new_deck(self):
        """
        Use a fresh shuffled pack of cards if there aren't enough cards left

        `Enough cards` are defined randomly when each player plus the dealer
        can get 5 cards 5*(np + 1)
        """
        if len(self.deck.card_deck) < (len(self.players.players) + 1) * 5:
            self.deck.__init__()
            self.deck.shuffle()
            self.deck.log()

    def __dealer(self):
        """
        The dealer's turn at the game
        """
        # stop if already won
        if self.__all_players_lost():
            log.debug("Dealer already won! [stands... and drops the mic]")
            self.stand(self.dealer)
            return

        while True:
            time.sleep(0.1)
            s = self.dealer.get_cards_sum()
            # stop only if more than 17
            if s > 17:
                self.stand(self.dealer)
                break
            # hit the dealer
            self.hit(self.dealer)

    def __players(self):
        """
        Ask each player if they want another card or not
        """
        for player in self.players.players:
            log.debug('     player %s turn' % player.nume)
            while True:
                answer = ' '
                while answer != 'h' and answer != 's':
                    answer = input('%s : (h)it or (s)tand? ' %
                                   player.display_name()).lower()
                # hit
                if answer == 'h':
                    if self.hit(player) == -1:
                        break
                    continue
                # stand
                if answer == 's':
                    self.stand(player)
                    break

    def __check_players_for_money(self):
        """
        Remove from the game players with no money left
        """
        for player in self.players.get():
            if player.jetoane == 0:
                self.players.broke(player)
        self.players.remove_broke_players_from_game()

    def __reset(self):
        """
        Reset internal objects state for a new round
        """
        self.players.reset_for_new_game()
        self.dealer.reset_for_new_game()
