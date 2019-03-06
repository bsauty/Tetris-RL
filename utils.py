'''This one is just a visualization tool to see the scores stored in scores.txt'''


import matplotlib.pyplot as plt

scores = open("scores.txt", "r")
num_lines = sum(1 for line in scores)

scores = open("scores.txt", "r")
score, partie = [], []
i = 0

for line in scores :
    partie.append(i)
    score.append(int(line))
    i += 1

plt.plot(partie, score)
plt.show()
