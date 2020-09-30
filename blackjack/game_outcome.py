import logging

log = logging.getLogger("outcome")


def log_and_print(msg, log_f=logging.info, end='\n'):
    log_f(msg)
    print(msg, end=end)


class game_outcome:
    def __init__(self, game):
        self.game = game
        self.sum_dealer = 0

    def __dealer_wins(self, player):
        """
        Dealer has a winner hand against `player`
            - dealer gets the player's bet
            - remove the bet value from the total bets
        """
        self.game.dealer.bet_won(player.bet_value)
        self.game.total_bets -= player.bet_value

    def __player_wins(self, player):
        """
        `player` wins the bet
            - player gets twice its betted amount
            - remove the bet value from the total bets
            - dealer loses the player's bet value
        """
        # player wins - 1:1
        player.bet_won()
        # remove money from the dealer
        self.game.dealer.bet_lost(player.bet_value)
        # remove money from the total bets
        self.game.total_bets -= player.bet_value

    def __draw(self, player):
        """
        It's a draw
        """
        player.draw()
        # remove money from the total bets
        self.game.total_bets -= player.bet_value

    def __all_players_over_21(self):
        """
        All players have results over 21
        """
        log_and_print(' > All players lost')
        # the dealer lost -- should not happen in this case
        if self.sum_dealer > 21:
            log_and_print(' > Dealer lost')
            log_and_print('  --Everybody lost-- ')
            for player in self.game.players.players:
                self.__draw(player)
        # dealer won
        else:
            log_and_print(' > Dealer WINS!!!')
            self.game.dealer.bet_won(self.game.total_bets)
            self.game.total_bets = 0

    def __dealer_lost(self):
        """
        Dealer went over 21
        """
        # self.game.dealer.lost = True
        
        winners = self.game.players.get_winners()
        # we have the winner(s)
        log_and_print('')
        log_and_print('Winners: ')
        for player in winners:
            log_and_print(' > %s     WON %d' % (str(player), player.bet_value))
            self.__player_wins(player)
            # self.game.dealer.bet_lost(player.bet_value)
        # remaining players lost
        for player in self.game.players.get():
            if player not in winners:
                player.lost = True

    def __determine_winner(self):
        """
        All have their score <= 21
        Determine the winner(s)
        """
        for player in self.game.players.get_winners():
            sum_player = player.get_cards_sum()
            # dealer wins
            if sum_player < self.sum_dealer:
                log_and_print(' > Dealer beats %s' % player.nume)
                self.__dealer_wins(player)
                player.lost = True
            # player wins
            elif sum_player > self.sum_dealer:
                log_and_print(' > %s wins %d' %
                              (player.nume, player.bet_value))
                self.__player_wins(player)
            # draw
            else:
                log_and_print(' > draw')
                self.__draw(player)

    def get(self):
        """
        Get the outcome of the game
        """
        self.sum_dealer = self.game.dealer.get_cards_sum()
        losers = self.game.players.get_losers()

        # all players lost
        if len(losers) == len(self.game.players.players):
            self.__all_players_over_21()
        # check for a winner (player(s) or dealer)
        # if dealer lost just pick the highest form the players
        elif self.sum_dealer > 21:
            self.__dealer_lost()
        else:
            self.__determine_winner()

        # any remaining bets go to the dealer
        self.game.dealer.bet_won(self.game.total_bets)
        # update the losers list
        losers = self.game.players.get_losers()
