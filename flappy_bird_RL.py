'''
TERCER OBJETIVO: QUE UNA IA JUEGUE A FLAPPY BIRD POR REINFORCEMENT LEARNING

Las variables de entrada para la IA en el juego Flappy Bird son las siguientes:
    - La posición actual del jugador (posición del pájaro).
    - La velocidad actual del jugador (velocidad del pájaro).
    - La altura de los dos tubos que aparecen en la pantalla.
    - La posición de la cereza en la pantalla, si está presente.
    - La posición del fantasma en la pantalla, si está presente.
    - La puntuación actual del jugador.

Las variables de salida para la IA en el juego Flappy Bird son las siguientes:
    - Eventos del teclado: la tecla de espacio para hacer que el pájaro salte.
'''

import pygame, sys, time, random
from pygame.locals import *
import math
import numpy as np
import pickle

class FlappyBirdEnv:
    def __init__(self):
        pygame.init()
        self.width = 500
        self.height = 700
        self.play_surface = pygame.display.set_mode((self.width, self.height))
        self.background_image = pygame.image.load("back.png").convert()
        self.bird_image = pygame.image.load("bird.png").convert_alpha()
        self.top_pipe = pygame.image.load("pipe_top.png").convert_alpha()
        self.bot_pipe = pygame.image.load("pipe_bot.png").convert_alpha()
        self.fps = pygame.time.Clock()

        self.reset()

    def reset(self):
        print("Resetting game...")  # Added print statement
        self.score = 0
        self.player_pos = [100, 550]
        self.gravity = 1
        self.speed = 0
        self.jump = -30
        self.speed_increase = 1
        self.pipe_pos = 500
        self.pipe_width = 50
        self.pipe_height = self.pipe_random_height()

        state = self.get_state()
        print("Initial state:", state)  # Added print statement
        return state

    def step(self, action):
        print("Step:", action)  # Added print statement

        if action == 1:
            self.speed = self.jump

        self.speed += self.speed_increase
        self.speed += self.gravity
        self.speed *= 0.95
        self.player_pos[1] += self.speed

        if self.pipe_pos >= -20:
            self.pipe_pos -= 10
        else:
            self.pipe_pos = 500
            self.pipe_height = self.pipe_random_height()

        passed_pipe = False
        if self.player_pos[0] == self.pipe_pos + self.pipe_width:
            passed_pipe = True
            self.score += 10

        reward = 0
        if self.player_pos[1] >= self.height or self.player_pos[1] <= 0 or \
                (self.player_pos[0] in list(range(self.pipe_pos, self.pipe_pos + self.pipe_width)) and 
                (self.player_pos[1] <= (-self.pipe_height[0] + 500) or self.player_pos[1] >= self.pipe_height[1])):
                reward = -15
        elif passed_pipe:
            reward = 10
        else:
            reward = 5

        done = False
        if self.player_pos[1] >= self.height or self.player_pos[1] <= 0 or \
                (self.player_pos[0] in list(range(self.pipe_pos, self.pipe_pos + self.pipe_width)) and 
                (self.player_pos[1] <= (-self.pipe_height[0] + 500) or self.player_pos[1] >= self.pipe_height[1])):
            done = True

        state = self.get_state()
        print("New state:", state, "Reward:", reward, "Done:", done)  # Added print statement
        return state, reward, done

    def render(self):
        print("Rendering...")  # Added print statement
        self.play_surface.blit(self.background_image, [0, 0])
        self.play_surface.blit(self.top_pipe, (self.pipe_pos, -self.pipe_height[0]))
        self.play_surface.blit(self.bot_pipe, (self.pipe_pos, self.pipe_height[1]))
        self.play_surface.blit(self.bird_image, (int(self.player_pos[0]), int(self.player_pos[1])))

        font = pygame.font.Font(None, 40)
        text = font.render(f"{self.score}", 1, (255, 255, 255))
        self.play_surface.blit(text, (250, 10))

        pygame.display.flip()
        self.fps.tick(25)
        return

    def human_play(self):
        state = self.reset()
        print("Game reset:", state)  # Added print statement
        game_states = []
        actions = []
        done = False

        while not done:
            self.render()
            action = 0
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_SPACE:
                    action = 1

            print("Action:", action)  # Added print statement
            game_states.append(self.get_state())
            actions.append(action)

            state, reward, done = self.step(action)
            print("New state:", state, "Reward:", reward, "Done:", done)  # Added print statement

        return game_states, actions

    def get_state(self):
        # Calcular la distancia horizontal desde el pájaro hasta el tubo más cercano
        horizontal_distance = self.pipe_pos - self.player_pos[0]

        # Calcular la distancia vertical desde el pájaro hasta el centro del orificio de las tuberías
        hole_center = (-self.pipe_height[0] + 500) + (self.pipe_height[1] - (-self.pipe_height[0] + 500)) / 2
        vertical_distance = self.player_pos[1] - hole_center

        state = (horizontal_distance, vertical_distance)
        print("Current state:", state)  # Added print statement
        return state


    def pipe_random_height(self):
        pipe_h = [random.randint(200, (self.height / 2) - 20), random.randint((self.height / 2) + 20, self.height - 200)]
        print("Random pipe height:", pipe_h)  # Added print statement
        return pipe_h

class QLearningAgent:
    def __init__(self, env, learning_rate=0.9, discount_factor=0.1, exploration_rate=0.8, exploration_decay_rate=0.001):
        self.env = env
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay_rate = exploration_decay_rate

        self.q_table = self.build_q_table()

    def discretize_state(self, state):
        horizontal_distance, vertical_distance = state
        horizontal_distance = min(20, max(0, int(horizontal_distance / 25)))
        vertical_distance = min(20, max(0, int((vertical_distance + 250) / 25)))  # Ajusta el factor de discretización aquí si es necesario
        return (horizontal_distance, vertical_distance)

    def build_q_table(self):
        state_space_size = (21, 21)  # (horizontal_distance, vertical_distance)
        action_space_size = 2
        q_table = np.zeros(state_space_size + (action_space_size,))
        return q_table

    def choose_action(self, state):
        state = self.discretize_state(state)
        if np.random.uniform(0, 1) < self.exploration_rate:
            return np.random.choice([0, 1])  # Explore: choose a random action
        else:
            return np.argmax(self.q_table[state])  # Exploit: choose the action with the highest Q value

    def train(self, num_episodes):
        for episode in range(num_episodes):
            state = self.env.reset()
            done = False

            while not done:
                action = self.choose_action(state)
                next_state, reward, done = self.env.step(action)
                next_state_disc = self.discretize_state(next_state)

                # Update the Q table
                state_disc = self.discretize_state(state)
                old_value = self.q_table[state_disc][action]
                next_max = np.max(self.q_table[next_state_disc])

                new_value = (1 - self.learning_rate) * old_value + self.learning_rate * (reward + self.discount_factor * next_max)
                self.q_table[state_disc][action] = new_value

                state = next_state

                self.exploration_rate *= (1 - self.exploration_decay_rate)

                if done:
                    break

            self.env.render()
    
    def supervised_learning(self, game_states, actions, num_epochs=1000):
        for _ in range(num_epochs):
            for state, action in zip(game_states, actions):
                state_disc = self.discretize_state(state)
                old_value = self.q_table[state_disc][action]
                next_state, reward, done = self.env.step(action)
                next_state_disc = self.discretize_state(next_state)
                next_max = np.max(self.q_table[next_state_disc])

                new_value = (1 - self.learning_rate) * old_value + self.learning_rate * (reward + self.discount_factor * next_max)
                self.q_table[state_disc][action] = new_value
    
    def save_q_table(self, file_path):
        with open(file_path, 'wb') as file:
            pickle.dump(self.q_table, file)

    def load_q_table(self, file_path):
        with open(file_path, 'rb') as file:
            self.q_table = pickle.load(file)

### PARA LA PRIMERA VEZ QUE SE CORRE EL CÓDIGO ###

# Crear el entorno del juego
env = FlappyBirdEnv()

# Crear el agente Q-Learning
agent = QLearningAgent(env)

# Jugar una partida como humano y obtener los estados y acciones
game_states, actions = env.human_play()

# Entrenar al agente con aprendizaje supervisado utilizando los estados y acciones recopilados durante la partida humana
agent.supervised_learning(game_states, actions)

# Entrenar al agente con Q-Learning para que mejore su rendimiento jugando solo
num_episodes = 1000  # Número de episodios para entrenar al agente
agent.train(num_episodes)

# Guardar la tabla Q final para su uso futuro
agent.save_q_table("q_table.pickle")

# ### PARA SEGUIR ENTRENANDO LA IA ###

# # Crear el entorno del juego
# env = FlappyBirdEnv()

# # Crear el agente Q-Learning
# agent = QLearningAgent(env)

# # Cargar la tabla Q previamente guardada
# agent.load_q_table("q_table.pickle")

# # Ajustar los parámetros de aprendizaje si es necesario
# agent.learning_rate = 0.9
# agent.discount_factor = 0.1
# agent.exploration_rate = 0.7
# agent.exploration_decay_rate = 0.0005

# # Entrenar al agente con Q-Learning para que siga mejorando su rendimiento jugando solo
# for i in range(1000):
#     num_additional_episodes = 1000
#     agent.train(num_additional_episodes)
#     agent.save_q_table("q_table_updated.pickle")
#     print('Epoch ', i+1, ' completed!')