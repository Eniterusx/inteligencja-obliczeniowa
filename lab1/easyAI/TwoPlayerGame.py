from abc import ABC, abstractclassmethod
from copy import deepcopy
from timeit import default_timer as timer
import numpy as np


class TwoPlayerGame(ABC):
    """
    Base class for... wait for it... two-players games !

    To define a new game, make a subclass of TwoPlayerGame, and define
    the following methods:

    - ``__init__(self, players, ...)`` : initialization of the game
    - ``possible_moves(self)`` : returns of all moves allowed
    - ``make_move(self, move)``: transforms the game according to the move
    - ``is_over(self)``: check whether the game has ended

    The following methods are optional:

    - ``show(self)`` : prints/displays the game
    - ``scoring``: gives a score to the current game (for the AI)
    - ``unmake_move(self, move)``: how to unmake a move (speeds up the AI)
    - ``ttentry(self)``: returns a string/tuple describing the game.
    - ``ttrestore(self, entry)``: use string/tuple from ttentry to restore a game.

    The __init__ method *must* do the following actions:

    - Store ``players`` (which must be a list of two Players) into
      self.players
    - Tell which player plays first with ``self.current_player = 1 # or 2``

    When defining ``possible_moves``, you must keep in mind that you
    are in the scope of the *current player*. More precisely, a
    subclass of TwoPlayerGame has the following attributes that
    indicate whose turn it is. These methods can be used but should not
    be overwritten:

    - ``self.player`` : the current player (e.g. ``Human_Player``)
    - ``self.opponent`` : the current Player's opponent (Player).
    - ``self.current_player``: the number (1 or 2) of the current player.
    - ``self.opponent_index``: the number (1 or 2) of the opponent.
    - ``self.nmove``: How many moves have been played so far ?

    For more, see the examples in the dedicated folder.

    Examples:
    ----------

    ::

        from easyAI import TwoPlayerGame, Human_Player

        class Sticks( TwoPlayerGame ):
            ''' In turn, the players remove one, two or three sticks from
                a pile. The player who removes the last stick loses '''

            def __init__(self, players):
                self.players = players
                self.pile = 20 # start with 20 sticks
                self.current_player = 1 # player 1 starts
            def possible_moves(self): return ['1','2','3']
            def make_move(self,move): self.pile -= int(move)
            def is_over(self): return self.pile <= 0

        p
        game = Sticks( [Human_Player(), Human_Player() ] )
        game.play()


    """

    @abstractclassmethod
    def possible_moves(self):
        pass

    @abstractclassmethod
    def make_move(self, move):
        pass

    @abstractclassmethod
    def is_over(self):
        pass

    def play(self, nmoves=1000, verbose=True):
        """
        Method for starting the play of a game to completion. If one of the
        players is a Human_Player, then the interaction with the human is via
        the text terminal.

        Parameters
        -----------

        nmoves:
          The limit of how many moves (plies) to play unless the game ends on
          it's own first.

        verbose:
          Setting verbose=True displays additional text messages.
        """

        history = []
        p1_think_time_arr = []
        p2_think_time_arr = []

        if verbose:
            self.show()

        thinking_time = 0
        for self.nmove in range(1, nmoves + 1):

            if self.is_over():
                break

            start_time = timer()
            move = self.player.ask_move(self)
            end_time = timer()

            thinking_time = end_time - start_time
            
            history.append((deepcopy(self), move))
            # self.make_move(move) # this is the original line
            miss = self.make_final_move(move) # we need to replace it with our method to add the 10% chance of making a mistake
            mistake = "was not successful" if miss else "was successful"
            if verbose:
                print("-" * 30)
                print(f"\nMove #{self.nmove}: player {self.current_player} plays ({move}) and it {mistake}:")
                print(f"Took {(thinking_time):.5f} seconds to make a move.")
                self.show()
                print()

            if self.current_player == 1:
                p1_think_time_arr.append(thinking_time)
            else:
                p2_think_time_arr.append(thinking_time)

            self.switch_player()

        history.append(deepcopy(self))

        p1_think_time = np.mean(p1_think_time_arr)
        p2_think_time = np.mean(p2_think_time_arr)
        # return history
        return p1_think_time, p2_think_time

    @property
    def opponent_index(self):
        return 2 if (self.current_player == 1) else 1

    @property
    def player(self):
        return self.players[self.current_player - 1]

    @property
    def opponent(self):
        return self.players[self.opponent_index - 1]

    def switch_player(self):
        self.current_player = self.opponent_index

    def copy(self):
        return deepcopy(self)

    def get_move(self):
        """
        Method for getting a move from the current player. If the player is an
        AI_Player, then this method will invoke the AI algorithm to choose the
        move. If the player is a Human_Player, then the interaction with the
        human is via the text terminal.
        """
        return self.player.ask_move(self)

    def play_move(self, move):
        """
        Method for playing one move with the current player. After making the move,
        the current player will change to the next player.

        Parameters
        -----------

        move:
          The move to be played. ``move`` should match an entry in the ``.possibles_moves()`` list.
        """
        result = self.make_move(move)
        self.switch_player()
        return result
