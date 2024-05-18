import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
import numpy as np
from model import Linear_QNet, QTrainer
from game_logic_ai import TankGame, Direction, Utils, PIXEL_SIZE, BLOCK_SIZE
from helper import plot

# Constants
MAX_MEMORY = 100_000
BATCH_SIZE = 64
LR = 0.001
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 200  # Decay parameter for epsilon

class Agent:
    def __init__(self, state_size, action_size):
        self.n_games = 0
        self.state_size = state_size
        self.action_size = action_size
        self.epsilon = EPS_START
        self.gamma = 0.98
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(state_size, 512, action_size)
        self.target_model = Linear_QNet(state_size, 512, action_size)
        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval()
        self.optimizer = optim.Adam(self.model.parameters(), lr=LR)
        self.criterion = nn.SmoothL1Loss()

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
        state = bot_location + rotation + nearby_objects + nearby_bullets + [reload_time]
        # state = [reload_time] + nearby_objects 
        return np.array(state, dtype=int)

    def get_action(self, state):
        if np.random.rand() <= self.epsilon:
            action = random.randrange(self.action_size)
            return action
        else:
            with torch.no_grad():
                state = torch.tensor(state, dtype=torch.float).unsqueeze(0)
                action = self.model(state).max(1)[1].item()
                return action

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train(self):
        if len(self.memory) < BATCH_SIZE:
            return
        batch = random.sample(self.memory, BATCH_SIZE)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.tensor(states, dtype=torch.float)
        actions = torch.tensor(actions, dtype=torch.long).view(-1, 1)
        rewards = torch.tensor(rewards, dtype=torch.float).view(-1, 1)
        next_states = torch.tensor(next_states, dtype=torch.float)
        dones = torch.tensor(dones, dtype=torch.bool).view(-1, 1)

        current_q_values = self.model(states).gather(1, actions)

        next_q_values = torch.zeros(BATCH_SIZE, dtype=torch.float)
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, next_states)), dtype=torch.bool)
        non_final_next_states = next_states[non_final_mask]
        with torch.no_grad():
            next_q_values[non_final_mask] = self.target_model(non_final_next_states).max(1)[0]

        expected_q_values = rewards + (self.gamma * next_q_values.unsqueeze(1))

        loss = self.criterion(current_q_values, expected_q_values)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def decay_epsilon(self):
        self.epsilon = EPS_END + (EPS_START - EPS_END) * np.exp(-1. * self.n_games / EPS_DECAY)


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    agent = Agent(state_size=13, action_size=5)
    total_score = 0
    record = 0
    game = TankGame("lab4/survival.txt", FPS=600000)
    for episode in range(1000):  # Adjust the number of episodes as needed
        # Run episode
        done = False
        score = 0
        total_reward = 0
        # Initialize your game environment here
        while not done:
            state = agent.get_state(game) 
            action = agent.get_action(state)
            final_move = [0] * 5
            final_move[action] = 1
            reward, done, score = game.play_step(final_move)
            next_state = agent.get_state(game)


            agent.remember(state, action, reward, next_state, done)
            agent.train()
            agent.update_target_model()

            total_reward += reward

        # Logging
        game.reset()
        agent.n_games += 1
        agent.decay_epsilon()
        if agent.n_games % 1 == 0:
            print(f'Episode: {episode}, Total Episode Reward: {total_reward}')
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