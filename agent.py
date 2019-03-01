from pygame.constants import K_UP, K_LEFT, K_RIGHT, K_SPACE, K_DOWN
import numpy as np
import pygame
from keras.models import Sequential
from keras.layers import Dense


from environment_reduced import m,n, play




def function_intercept(intercepted_func, intercepting_func):
    """
    Intercepts a method call and calls the supplied intercepting_func with the result of it's call and it's arguments
    Example:
        def get_event(result_of_real_event_get, *args, **kwargs):
            # do work
            return result_of_real_event_get
        pygame.event.get = function_intercept(pygame.event.get, get_event)
    :param intercepted_func: The function we are going to intercept
    :param intercepting_func:   The function that will get called after the intercepted func. It is supplied the return
    value of the intercepted_func as the first argument and it's args and kwargs.
    :return: a function that combines the intercepting and intercepted function, should normally be set to the
             intercepted_functions location
    """

    def wrap(*args, **kwargs):
        real_results = intercepted_func(*args, **kwargs)  # call the function we are intercepting and get it's result
        intercepted_results = intercepting_func(real_results, *args, **kwargs)  # call our own function a
        return intercepted_results

    return wrap



'''#Test agent
class random_agent():

    def __init__(self):
        self.score = score

    def start(self):
        pygame.event.get = function_intercept(pygame.event.get, self.test)
        pygame.event.get = function_intercept(pygame.event.get, self.on_event_get)

        play()

    def on_event_get(self, _, *args, **kwargs):
        keys = [K_LEFT, K_RIGHT, K_SPACE, K_UP]
        i = np.random.randint(0, 4)
        event = pygame.event.Event(pygame.KEYDOWN, {"key" : keys[i]})
        return ([event])

    def test(self, _, *args, **kwargs):
        print("coucou")
        return([])'''




class clever_agent():

    def __init__(self):
        self.reward = 0.

    #create decision network
    def initialize_nn(self):
        self.input_size = 28

        self.model = Sequential()
        self.model.add(Dense(20, input_dim=self.input_size, init='uniform', activation='relu'))  # hidden layer after n+8 output
        #self.model.add(Dense(15, init='uniform', activation='relu'))  # hidden layer
        self.model.add(Dense(4, init='uniform', activation='linear'))  # 4 possible actions as output


        self.model.compile(loss='mse', optimizer='SGD', metrics=['accuracy'])


        # Parameters
        self.epsilon = .9         # probability of doing a random move
        self.epsilon_decay = 1/500000
        self.epsilon_end = 0.05

        self.gamma = 0.95     # discounted future reward

        self.mini_batch = 100   # size of data we want to use for stochastic gradient descent
        self.last_events = []   # storing the mini_batch last actions

        self.total_reward = 0.
        self.state = np.zeros((self.input_size,))

    #we get the current state of the game
    def get_state(self):
        # we get the list of locked spots, regardless of the color
        from environment_reduced import locked_positions
        full_spots = list(locked_positions.keys())

        max_height = [m for i in range(n)]
        for (i, j) in full_spots:
            if (0<= i <n) and (j < max_height[i]):
                max_height[i] = j

        # then we get the position of the shape that is falling down
        from environment_reduced import current_piece
        falling_piece = current_piece.info_shape()
        x,y,index = falling_piece

        # here we put the state in the required shape :
        # array([height1,..., heightn, x_piece, y_piece, index_piece]) en mettant les trois derniers sous forme 0-1
        state = np.zeros(self.input_size)
        # the first m pieces of the input are the height of each column
        for i in range(len(max_height)):
            state[i] = max_height[i]
        # then we store n 0-1 with a 1 in the corresponding x for the falling piece
        state[6 + x] = 1
        # same for corresponding y of falling piece
        state[12 + y] = 1
        # same for the index (ie. the shape+rotation state) of the falling piece
        state[21 + index] = 1

        return state

    #we decide which key to press, we return i (the int corresponding to the action) and action (the pygame event)
    def get_action(self):

        #we use epsilon greedy exploration
        if np.random.rand() <= self.epsilon :
            i = np.random.randint(0, 4)
        else:
            Q = self.model.predict(np.array([self.state]))
            i = np.argmax(Q)

        keys = [K_LEFT, K_RIGHT, K_DOWN, K_UP]
        action = pygame.event.Event(pygame.KEYDOWN, {"key": keys[i]})
        self.iteration += 1

        return i, action


    #we get the reward from last action and train the nn accordingly
    def new_episode(self, *args, **kwargs):

        if self.iteration == self.mini_batch:
            #we train the nn on the last mini_batch actions
            #we bring back iteration and last_actions to the initial state
            inputs = np.zeros((self.mini_batch, self.input_size))
            targets = np.zeros((self.mini_batch, 4))

            for i in range(self.mini_batch):
                event = self.last_events[i]
                state = event[0]
                action = event[1]
                reward = event[2]
                state_new = event[3]
                done = event[4]

                #we build Bellman equation for the Q function
                inputs[i:i+1] = np.array([state])
                targets[i] = self.model.predict(np.array([state]))
                Q_sa = self.model.predict(np.array([state_new]))

                if done :
                    targets[i][action] = reward
                else :
                    targets[i][action] = reward + self.gamma * np.max(Q_sa)

                #then we train the network to output the Q function
                self.model.train_on_batch(inputs, targets)

            if self.epsilon > self.epsilon_end:
                self.epsilon -= self.epsilon_decay

            self.last_events =[]
            self.iteration = 0

        # we get the action, the new_state and the reward and add it to the last_events list
        self.reward = 0
        state_new = self.get_state()
        i, action = self.get_action()

        # for the reward, we substract for each difference between two adjacent columns > 2
        # and we add inc² * 10 where inc is the number of cleared lines
        sum_diff = 0
        height_diff = [abs(state_new[i + 1] - state_new[i]) for i in range(n - 1)]
        for diff in height_diff :
            sum_diff += diff
            if diff > 2 :
                self.reward -= 0.01*diff

        from environment_reduced import inc
        self.reward += inc*inc*20

        # we will modify the done thing later
        done = False
        self.total_reward += self.reward

        self.last_events.append((self.state, i, self.reward, state_new, done))
        self.state = state_new
        return [action]


    #we launch the game
    def start(self):
        self.initialize_nn()

        #this is to count until we reach mini_batch and train the nn on the last mini_batch action/rewards
        self.iteration = 0

        pygame.event.get = function_intercept(pygame.event.get, self.new_episode)
        play(250000)
        self.playing = True

    def stop(self):
        pygame.event.get = self._default_event_get
        self.playing = False





if __name__ == "__main__":
    player = clever_agent()
    player.start()