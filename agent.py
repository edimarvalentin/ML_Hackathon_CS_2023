from arcade import Point
import torch
import random
import numpy as np
from collections import deque
from SpaceGame import Game, Point
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):
        Sship = self.spaceship
        point_l = Point(Sship.x - 20, Sship.y)
        point_r = Point(Sship.x + 20, Sship.y)
        point_u = Point(Sship.x, Sship.y - 20)
        point_d = Point(Sship.x, Sship.y + 20)
        
        dir_l = game.action == 0 #Left direction
        dir_r = game.action == 1 #Right direction
        dir_u = game.action == 2 #Up direction
        dir_d = game.action == 3 #Down direction

        state = [
            # Danger straight
            (dir_r and point_r.collides_with(game.planet.is_green)) or 
            (dir_l and point_l.collides_with(game.planet.is_green)) or 
            (dir_u and point_u.collides_with(game.planet.is_green)) or 
            (dir_d and point_d.collides_with(game.planet.is_green)),

            # Danger right
            (dir_u and point_r.collides_with(game.planet.is_green)) or 
            (dir_d and point_l.collides_with(game.planet.is_green)) or 
            (dir_l and point_u.collides_with(game.planet.is_green)) or 
            (dir_r and point_d.collides_with(game.planet.is_green)),

            # Danger left
            (dir_d and point_r.collides_with(game.planet.is_green)) or 
            (dir_u and point_l.collides_with(game.planet.is_green)) or 
            (dir_r and point_u.collides_with(game.planet.is_green)) or 
            (dir_l and point_d.collides_with(game.planet.is_green)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Green Planet location 
            game.planet.is_green.x < game.Sship.x,  #  Green Planet left
            game.planet.is_green.x > game.Sship.x,  # Green Planet right
            game.planet.is_green.y < game.Sship.y,  # Green Planet up
            game.planet.is_green.y > game.Sship.y  # Green Planet down
            ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, next_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = Game()
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
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

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()