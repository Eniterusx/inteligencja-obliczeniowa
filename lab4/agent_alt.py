import torch
import random
import numpy as np
from collections import deque
from game_logic_ai import TankGame, Direction, Utils, PIXEL_SIZE, BLOCK_SIZE
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 10_000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.98 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(5, 512, 5)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game: TankGame):
        # tank_location = [game.game_state.tank1.x, game.game_state.tank1.y]
        # find closest bot, give relative cords
        closest_bot = Utils.find_closest_bot(game.game_state)
        bot_location = [(game.game_state.tank1.x-closest_bot.x)/100, (game.game_state.tank1.y-closest_bot.y)/100]
        rotation = [np.sign(game.game_state.tank1.direction[0]), np.sign(game.game_state.tank1.direction[1])]
        # iterate through all game objects, check if they are next to the tank in 4 main directions
        nearby_objects = Utils.check_nearby_objects(game.game_state.tank1, game.game_state.tank_bots + game.game_state.map)
        nearby_bullets = [i/100 for i in Utils.check_nearby_bullets(game.game_state.tank1, game.game_state.bullets)]
        reload_time = 1 if game.game_state.tank1.reload_time > 0 else 0
        # state = bot_location + rotation + nearby_objects + nearby_bullets + [reload_time]
        state = [reload_time] + nearby_objects
        return np.array(state, dtype=int)


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY reached


    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        


    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)


    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - 40*self.n_games
        final_move = [0,0,0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 4)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0) # this calls the forward function from Linear_Qnet
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = TankGame("lab4/survival.txt", FPS=600000)
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        if state_old[1] == 1:
            reward -= 1
        if state_old[2] == 1:
            reward -= 1
        if state_old[3] == 1:
            reward -= 1
        if state_old[4] == 1:
            reward -= 1
        print(reward)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            
            if score > record:
                record = score
                agent.model.save()
            
            print('Game', agent.n_games, 'Score', score, 'Record', record)
            
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()