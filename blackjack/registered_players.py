import os
import random
import logging

from blackjack.player import Player

log = logging.getLogger("players")


def log_and_print(msg, log_f=logging.info, end='\n'):
    log_f(msg)
    print(msg, end=end)


class Players:
    """
    Registered players to play the game
    Wrapper around player list
    """
    def __init__(self, players_file):
        """
        Load the players file
        """
        PLAYERS_FILE = 'ListaParticipanti.txt'
        self.players = []
        self.broke_players = []
        self.__load_players_from_file(players_file)
        self.__check_number_of_players()

    def broke(self, player):
        log_and_print(' >> %s is broke! :(' % player.display_name())
        self.broke_players.append(player)

    def remove_broke_players_from_game(self):
        for player in self.broke_players:
            if player in self.players:
                self.players.remove(player)

    def reset_for_new_game(self):
        for player in self.players:
            player.reset_for_new_game()

    def get(self, all=True, losers=False):
        """
        Return the players list
            all     = True  - return all the players
                    = False - filters the list based on `losers`
            losers  = True  - return only players who lost
                    = False - return only players who won
        """
        if all:
            return self.players
        else:
            return [p for p in self.players if p.lost == losers]

    def get_winners(self):
        """
        Return the winners list
        """
        return self.get(all=False, losers=False)

    def get_losers(self):
        """
        Return the losers list
        """
        return self.get(all=False, losers=True)

    def __check_number_of_players(self):
        """
        Check if we have max 4 players
        If there are more, 4 players are randomly selected
        """
        # number of registered players
        registered_players = len(self.players)
        if registered_players > 4:
            log_and_print(' >> We have %d registered players' %
                          registered_players)
            log_and_print(' >> Max is 4')
            log_and_print(' >> %d random players will leave' %
                          (registered_players - 4))
            # choosing 4 random players
            self.players = random.sample(self.players, 4)

        # log the list
        log.debug('')
        log.debug('Player object list: ')
        for player in self.players:
            log.debug(player)

    def __load_players_from_file(self, player_file):
        """
        Load the players from file `player_file`
        """
        try:
            with open(player_file) as f:
                for line in f:
                    [nume, prenume,
                     varsta, tara,
                     jetoane] = line.replace('\n', '').split('\t')
                    tmp = Player(nume, prenume,
                                 int(varsta), tara,
                                 int(jetoane))
                    self.players.append(tmp)
        except FileNotFoundError as err:
            log_and_print("FATAL ERROR - File %s not found" % player_file,
                          log_f=logging.error)
            log_and_print(err, log_f=logging.error)
            exit(1)
        except TypeError as err:
            log.error("FATAL ERROR - File %s is not properly formatted" %
                      player_file)
            log.error(err)
            exit(1)

    def log(self):
        """
        Log the registered players in a more or less nice formatted table
        """
        if len(self.players) == 0:
            return
        T_SEP = '%s|%s|%s|%s|%s|%s' % ('-' * 7, '-' * 13, '-' * 12,
                                       '-' * 5, '-' * 16, '-' * 8)
        log.info('')
        log.info('Registered players:')
        # table header
        log.info('\t%s' % T_SEP)
        log.info("\t  %3s  |  %10.10s | %10.10s | %3.3s | %4s" %
                 ('IDX', 'NUME', 'PRENUME', 'N', 'JETOANE')
                 )
        log.info('\t%s' % T_SEP)
        # table data
        player_index = 1
        for player in self.players['jucatori']:
            log.info("\t  %3d  |  %10.10s | %10.10s | %3.3s | %-4d" %
                     (player_index,
                      player['nume'],          player['prenume'],
                      player['nationalitate'],
                      player['jetoane'])
                     )
            player_index += 1
        # table end
        log.info('\t%s' % T_SEP)
