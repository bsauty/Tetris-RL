# Tetris-RL
A reinforcment learning project to train an AI to play Tetris

Files are :
 - environment_full.py : an environment for the full tetris game (20x10 grid and 7 different shapes)
 - environment_reduced.py : an easier environment to train on (6x9 grid with 3 different shapes)
 - agent.py : the deep Q learning agent that will learn to play
 
Necessary packages :
 - Keras
 - Pygame
 - Numpy

We use an epsilon greedy policy to train the neural network with a stochastic gradient descent optimizer.
We use as input the position of the highest pieces of each column and the position of the falling shape.
