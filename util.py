"""
What's the world without an `util` module?
Everything you need for a game of blackjack
"""
import time


def delay(time_ms=100):
    time.sleep(100 / 1000)
    print('.', end='')
