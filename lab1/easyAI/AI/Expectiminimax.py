import pickle

LOWERBOUND, EXACT, UPPERBOUND = -1, 0, 1
inf = float("infinity")


def expectiminimax(game, depth, origDepth, scoring, alpha=+inf, beta=-inf, tt=None):
    
    alphaOrig = alpha

    # Is there a transposition table and is this game in it ?
    lookup = None if (tt is None) else tt.lookup(game)

    if lookup is not None:
        # The game has been visited in the past

        if lookup["depth"] >= depth:
            flag, value = lookup["flag"], lookup["value"]
            if flag == EXACT:
                if depth == origDepth:
                    game.ai_move = lookup["move"]
                return value
            elif flag == LOWERBOUND:
                alpha = max(alpha, value)
            elif flag == UPPERBOUND:
                beta = min(beta, value)

            if alpha >= beta:
                if depth == origDepth:
                    game.ai_move = lookup["move"]
                return value
    
    if (depth == 0) or game.is_over():
        # NOTE: the "depth" variable represents the depth left to recurse into,
        # so the smaller it is, the deeper we are in the negamax recursion.
        # Here we add 0.001 as a bonus to signify that victories in less turns
        # have more value than victories in many turns (and conversely, defeats
        # after many turns are preferred over defeats in less turns)
        return scoring(game) * (1 + 0.001 * depth)

    if lookup is not None:
        # Put the supposedly best move first in the list
        possible_moves = game.possible_moves()
        possible_moves.remove(lookup["move"])
        possible_moves = [lookup["move"]] + possible_moves

    else:

        possible_moves = game.possible_moves()

    state = game
    best_move = possible_moves[0]
    if depth == origDepth:
        state.ai_move = possible_moves[0]

    bestValue = -inf
    unmake_move = hasattr(state, "unmake_move")

    for move in possible_moves:

        if not unmake_move:
            game = state.copy()  # re-initialize move


        if not game.deterministic:
            probability = 0.1

            # Try normal move
            game.make_move(move)
            game.switch_player()
            move_alpha = -expectiminimax(game, depth - 1, origDepth, scoring, -beta, -alpha, tt)
            game.switch_player()
            game.unmake_move(move)
            expectedValue = move_alpha * (1-probability)

            # Try backfired move
            pile, count = move.split(',')
            count = str(int(count) - 1)
            backfired_move = f"{pile},{count}"
            game.make_move(backfired_move)
            game.switch_player()
            backfired_move_alpha = -expectiminimax(game, depth - 1, origDepth, scoring, -beta, -alpha, tt)
            game.switch_player()
            game.unmake_move(backfired_move)
            expectedValue += backfired_move_alpha * (probability)
        else:
            game.make_move(move)
            game.switch_player()
            move_alpha = -expectiminimax(game, depth - 1, origDepth, scoring, -beta, -alpha, tt)
            game.switch_player()
            game.unmake_move(move)
            expectedValue = move_alpha

        # bestValue = max( bestValue,  move_alpha )
        if bestValue < expectedValue:
            bestValue = expectedValue
            best_move = move

        if alpha < expectedValue:
            alpha = expectedValue
            # best_move = move
            if depth == origDepth:
                state.ai_move = move
            if alpha >= beta:
                break

    if tt is not None:

        assert best_move in possible_moves
        tt.store(
            game=state,
            depth=depth,
            value=bestValue,
            move=best_move,
            flag=UPPERBOUND
            if (bestValue <= alphaOrig)
            else (LOWERBOUND if (bestValue >= beta) else EXACT),
        )

    return bestValue


class Expectiminimax:
    """
    Expectiminimax is a modification of the Minimax algorithm, which is used in turn-based games.
    It is used to find the optimal move for a player, assuming that the opponent plays optimally.
    It is a recursive algorithm, which is used to evaluate the different positions the game might
    end up in, and then choose the best move for the player.

    Parameters
    -----------

    depth:
      How many moves in advance should the AI think ?
      (2 moves = 1 complete turn)

    scoring:
      A function f(game)-> score. If no scoring is provided
         and the game object has a ``scoring`` method it ill be used.

    win_score:
      Score above which the score means a win. This will be
        used to speed up computations if provided, but the AI will not
        differentiate quick defeats from long-fought ones (see next
        section).

    tt:
      A transposition table (a table storing game states and moves)
      scoring: can be none if the game that the AI will be given has a
      ``scoring`` method.

    Notes
    -----

    The score of a given game is given by

    >>> scoring(current_game) - 0.01*sign*current_depth

    for instance if a lose is -100 points, then losing after 4 moves
    will score -99.96 points but losing after 8 moves will be -99.92
    points. Thus, the AI will chose the move that leads to defeat in
    8 turns, which makes it more difficult for the (human) opponent.
    This will not always work if a ``win_score`` argument is provided.

    """

    def __init__(self, depth, scoring=None, win_score=+inf, tt=None):
        self.scoring = scoring
        self.depth = depth
        self.tt = tt
        self.win_score = win_score

    def __call__(self, game):
        """
        Returns the AI's best move given the current state of the game.
        """

        scoring = (
            self.scoring if self.scoring else (lambda g: g.scoring())
        )  # horrible hack

        self.alpha = expectiminimax(
            game,
            self.depth,
            self.depth,
            scoring,
            -self.win_score,
            +self.win_score,
            self.tt,
        )
        return game.ai_move
