from easyAI import TwoPlayerGame, Human_Player, AI_Player, Negamax, solve_with_iterative_deepening
import random
from tqdm import tqdm

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
    
def launch_game_negamax(depth_1: int,
                depth_2: int,
                deterministic: bool,
                piles: list = [5, 5, 5, 5]):
    
    # ai = Negamax(depth_1)
    ai2 = Negamax(depth_2)
    # game = Nim([AI_Player(ai), AI_Player(ai2)], deterministic=deterministic)
    game = Nim(players=[Human_Player(), AI_Player(ai2)],
               deterministic=deterministic,
               piles=piles)
    game.play() # You will always lose this game !
    print("\nplayer %d wins\n" % game.current_player)    
    x = game.current_player
    return x



if __name__ == "__main__":
    ai = Negamax(10)
    ai2 = Negamax(10)
    game = Nim([AI_Player(ai), Human_Player()])
    # game = Nim([AI_Player(ai), AI_Player(ai2)])
    x = game.play() # You will always lose this game !
    print("\nplayer %d wins\n" % game.current_player)
    print(x)

    # Win tracking dict
    # results = {}

    # depths = [3, 10]
    # deterministic = [True, False]
    # game_amount = 10

    # for d1, d2 in tqdm([(d1, d2) for d1 in depths for d2 in depths], desc="Processing depths"):
    #     for det in tqdm(deterministic, desc="Processing deterministic"):
    #         # print(f"depth1: {d1}, depth2: {d2} deterministic: {det}")
            
    #         # Play 10 games and track the results
    #         p1_wins = 0
    #         p2_wins = 0
    #         p1_avg_time = 0
    #         p2_avg_time = 0

    #         for x in tqdm(range(game_amount), desc="Playing games"):
    #             ai = Negamax(d1)
    #             ai2 = Negamax(d2)
    #             game = Nim(players=[AI_Player(ai), AI_Player(ai2)],
    #                     deterministic=det,
    #                     piles=[5,5,5,5])
    #             p1_time, p2_time = game.play(verbose=False)
    #             p1_avg_time += p1_time
    #             p2_avg_time += p2_time
    #             print("\nplayer %d wins\n" % game.current_player)
    #             if game.current_player == 1:
    #                 p1_wins += 1
    #             else:
    #                 p2_wins += 1 

    #         p1_avg_time /= game_amount
    #         p2_avg_time /= game_amount
    #         results[(d1, d2, det)] = {"p1_wins": p1_wins,
    #                                   "p2_wins": p2_wins,
    #                                   "p1_average_game_time": p1_avg_time,
    #                                   "p2_average_game_time": p2_avg_time} # Update the results

    # print(results)

# 10% szansy na wziecie jednego mniej w make_final_move.
# Rozdzielenie na make_final_move i make_move. make_final_move zawsze wykonywane jako ostatnie. make_move wykonywane jest przy przeszukiwaniu.
# Pomiar czasu przeszukiwania (ask_move)
# game.play() zwraca sredni czas na ruch obu graczy



# TODO: dodac zapisywanie rezultatow do pliku, nazwa pliku to nazwa uzytego algorytmu (albo walic, sam se przekopiuje)
# jakis expecti-minmax obsrany zrobic
