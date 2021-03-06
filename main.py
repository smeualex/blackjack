import os
import logging
import datetime

from blackjack.deck import Deck
from blackjack.player import Dealer
from blackjack.game import Game

PLAYERS_FILE = 'ListaParticipanti.txt'

log = logging.getLogger("blackjack")
cwd = os.path.dirname(os.path.realpath(__file__))
players_file = os.path.join(cwd, 'assets', PLAYERS_FILE)


def init():
    # set up logging
    now = datetime.datetime.now()
    str_now = now.strftime('%Y%m%d_%H%M%S')

    log_file_name = 'blackjack_' + str_now + '.log'
    log_file = os.path.join(cwd, 'logs', log_file_name)
    logging.basicConfig(
            handlers=[logging.FileHandler(log_file, 'w', 'utf-8')],
            level=logging.DEBUG,
            format='%(asctime)s | %(levelname)5.5s | %(name)10s | %(message)s')
    # we are going
    log.info('')
    log.info('-' * 80)
    log.info('-- Program started')


def log_and_print(msg, log_f=logging.info, end='\n'):
    log_f(msg)
    print(msg, end=end)


def main():
    init()

    game = Game(players_file)
    while game.players_in_game() > 0 and game.new_round():
        game.run()

    if game.players_in_game() == 0:
        log_and_print('No more players. Game stops!')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_and_print('Well that\'s sad. Please come again!')
