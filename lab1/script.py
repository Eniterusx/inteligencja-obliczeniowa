from easyAI import TwoPlayerGame, Human_Player, AI_Player, Negamax, solve_with_iterative_deepening
import random

class Nim(TwoPlayerGame):
    def __init__(self, players, piles = [5, 5, 5, 5], deterministic = False):
        self.piles = piles
        self.players = players
        self.nplayer = 1
        self.current_player = 1
        self.deterministic = deterministic
    
    def possible_moves(self):
        moves = ["%d,%d" % (i + 1, j) for i in range(len(self.piles)) for j in range(1, self.piles[i] + 1)]
        return moves
    
    def make_final_move(self, move):
        pile, count = move.split(",")
        extra = 1 if random.randint(1, 10) == 1 and not self.deterministic else 0
        self.piles[int(pile) - 1] -= int(count) - extra
        return extra
    
    def make_move(self, move):
        pile, count = move.split(",")
        self.piles[int(pile) - 1] -= int(count)

    def unmake_move(self, move): # optional method (speeds up the AI)
        pile, count = move.split(",")
        self.piles[int(pile) - 1] += int(count)

    def show(self): print(" ".join(map(str, self.piles)))

    def win(self): return max(self.piles) == 0

    def is_over(self): return self.win()

    def scoring(self): return 100 if self.win() else 0

    def ttentry(self): return tuple(self.piles) #optional, speeds up AI
    

if __name__ == "__main__":
    # w, d, m = solve_with_iterative_deepening(Nim, range(5, 20), win_score = 80)
    ai = Negamax(10, win_score=100)
    ai2 = Negamax(4, win_score=100)
    # game = Nim([Human_Player(), AI_Player(ai)])
    game = Nim([AI_Player(ai), AI_Player(ai2)])
    game.play() # You will always lose this game !
    print("\nplayer %d wins\n" % game.current_player)


# 10% szansy na wziecie jednego mniej w make_final_move.
# Rozdzielenie na make_final_move i make_move. make_final_move zawsze wykonywane jako ostatnie. make_move wykonywane jest przy przeszukiwaniu.
# Pomiar czasu przeszukiwania (ask_move)
# 