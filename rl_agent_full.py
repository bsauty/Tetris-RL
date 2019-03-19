'''This is the working RL agent for the full environment

Just run to initiate training.
Feel free to mess with the hyperparameters to compare convergence speed (epsilon, gamma, alpha)




/!\/!\ : There is an occasionnal bug when clearing lines that happens when using the agent but not when playing manually

'''



from pygame.constants import K_UP, K_LEFT, K_RIGHT, K_SPACE
import numpy as np
import pygame
import copy
import math


from environment_full import m,n, play




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

class clever_agent():

    def __init__(self):
        self.reward = 0.

        # Parameters
        self.epsilon = 0.8 # probability of doing a random move
        self.epsilon_decay = 0.01
        self.epsilon_end = 0.05

        self.gamma = 0.95     # discounted future rewarddq
        self.alpha = 0.01

        self.weights = [-5, -5, -5, -30]     # initial weight vector, pretty random


    #we get the current state of the game
    def get_state(self, locked_pos = {}):

        # we get the list of locked spots, regardless of the color
        from environment_full import locked_positions

        if locked_pos == {} :
            locked_pos = locked_positions

        full_spots = list(locked_pos.keys())

        # maximum height in each column
        heights =  [m for i in range(n)]
        for (i, j) in full_spots:
            if (0 <= i < n) and (j < heights[i]):
                heights[i] = j
        # the lowest row is m and highest 0 so we change that
        for i in range(n):
            heights[i] = m - heights[i]

        # sum of all heights
        height_sum = sum(heights)

        # difference in heights
        height_diff = [heights[i+1] - heights[i] for i in range(n-1)]
        diff_sum = 0
        for diff in height_diff:
            diff_sum += abs(diff)
        # maximum height
        max_height = max(heights)

        # number of holes
        holes = 0
        #print(full_spots)
        for j in range(m):
            # we use a flag for each line to know if there is something on it
            occupied_row = 0
            for i in range(n):
                if (i,j) in full_spots :
                    occupied_row = 1
            for i in range(n):
                if (i,j) not in full_spots and occupied_row == 1 :
                    holes += 1

        return height_sum, diff_sum, max_height, holes

    def get_expected_score(self, locked_pos):
        # here we evaluate the score for a given grid with a given set of weights
        height_sum, diff_sum, max_height, holes = self.get_state(locked_pos)
        A,B,C,D = self.weights
        evaluated_score = float(A * height_sum + B * diff_sum + C * max_height + D * holes)
        return evaluated_score

    def try_move(self, action):
        # here we calculate the reward of the present action if the piece was brought down after the action

        from environment_full import grid, current_piece, valid_space, locked_positions,\
            convert_shape_format, clear_rows

        test_piece = copy.copy(current_piece)
        reference_height = self.get_state()[0]

        rot, sideways = action

        test_piece.x += sideways
        test_piece.rotation = test_piece.rotation + rot % len(test_piece.shape)

        if not valid_space(test_piece, grid) :
            return None

        # move shape at the bottom
        while valid_space(test_piece, grid):
            test_piece.y += 1
        test_piece.y -= 1

        test_locked = copy.copy(locked_positions)
        test_grid = copy.copy(grid)
        shape_pos = convert_shape_format(test_piece)
        for pos in shape_pos:
            p = (pos[0], pos[1])
            # we update position
            test_locked[p] = current_piece.color

        # increment score with number of rows cleared at once
        test_inc = clear_rows(test_grid, test_locked)
        height_sum, diff_sum, max_height, holes = self.get_state(test_locked)

        one_step_reward = 5 * ( 2 * test_inc) - (height_sum - reference_height)
        #print(one_step_reward)
        return test_locked, one_step_reward

    def make_move(self, action):
        rot, sideways = action
        actions = []
        for i in range(rot):
            actions.append(pygame.event.Event(pygame.KEYDOWN, {"key" : K_UP}))
        if sideways >= 0 :
            for i in range(sideways):
                actions.append(pygame.event.Event(pygame.KEYDOWN, {"key" : K_RIGHT}))
        else :
            for i in range(abs(sideways)):
                actions.append(pygame.event.Event(pygame.KEYDOWN, {"key" : K_LEFT}))

        return actions

    def find_next_move(self):

        from environment_full import current_piece
        # we find the best action to take
        moves = []
        scores = []

        for rot in range(len(current_piece.shape)):
            for sideways in range(-n // 2, n // 2):
                action = [rot, sideways]
                test_board = self.try_move(action)
                if test_board is not None:
                    moves.append(action)
                    test_score = self.get_expected_score(test_board[0])
                    scores.append(test_score)

        if np.random.rand() > self.epsilon :
            best_score = max(scores)
            best_move = moves[scores.index(best_score)]

        else:
            i = np.random.randint(0, len(moves))
            best_move = moves[i]

        #print(self.epsilon)
        return best_move


    '''def gradient_descent(self):
        action = find_next_move()
        old_state = get_state()
        test_board = try_move(action)

        if test_board is not None:
            new_state = get_state(test_board[0])
            one_step_reward = test_board[1]

        for i in range(len(self.weights)):
            weights[i] += alpha * weights[i] * (one_step_reward - old_state[i] + gamma * new_state[i])

        normalization = abs(sum(weights))
        for i in range(len(self.weights)):
            weights[i] = 100 * weights[i] / normalization
            weights[i] = math.floor(1e4 * weights[i]) / 1e4  # Rounds the weights

        return action'''

    #we get the reward from last action and train the nn accordingly
    def new_episode(self, *args, **kwargs):


        if self.epsilon > self.epsilon_end:
            self.epsilon -= self.epsilon_decay
            #print(self.epsilon)

        action = self.find_next_move()
        old_state = self.get_state()
        test_board = self.try_move(action)

        if test_board is not None:
            new_state = self.get_state(test_board[0])
            one_step_reward = test_board[1]

        for i in range(len(self.weights)):
            self.weights[i] += self.alpha * self.weights[i] * (one_step_reward - old_state[i]
                                                          + self.gamma * new_state[i])

        normalization = abs(sum(self.weights))
        for i in range(len(self.weights)):
            self.weights[i] = 100 * self.weights[i] / normalization
            self.weights[i] = math.floor(1e4 * self.weights[i]) / 1e4  # Rounds the weights

        actions = self.make_move(action)
        #print(self.weights)
        #print(self.epsilon)
        return actions


    #we launch the game
    def start(self):

        pygame.event.get = function_intercept(pygame.event.get, self.new_episode)
        # specify as an argument the number of games we want to train on
        play(250000)
        self.playing = True

    def stop(self):
        self.playing = False


if __name__ == "__main__":
    player = clever_agent()
    player.start()
