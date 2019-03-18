# Tetris-RL
A reinforcment learning project to train an AI to play Tetris

Files are :
 - environment_full.py : an environment for the full tetris game (20x10 grid and 7 different shapes)
 - environment_reduced.py : an easier environment to train on (6x9 grid with 3 different shapes)
 - DQN_agent.py : the deep Q learning agent that will learn to play (does not work well, probably the rewarding policy that only takes into account the last move)
 - RL_agent_reduced.py : agent that learns the best policy through trial and error with the reduced environment for faster results
 - RL_agent_full.py : same with full environment
 - scores.txt : list of the scores during training
 - utils.py : plot the scores 
 
Necessary packages :
 - Keras
 - Pygame
 - Numpy

We use an epsilon greedy policy to train the neural network with a stochastic gradient descent optimizer.

All the necessary information is inside the project report tetris_RL.pdf
