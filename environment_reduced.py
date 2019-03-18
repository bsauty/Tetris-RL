'''This is the reduced environment

To play easy tetris, run play(1)


It is highly modified compared to the full environment in order to be able to interact with the agent

'''





import pygame
import random
import os


pygame.font.init()

# GLOBALS VARS
m,n = 9,6         # size of the grid
s_width = 30*n + 400
s_height = 30*m + 150
play_width = 30*n
play_height = 30*m
block_size = 30
locked_positions = {}  # (x,y):(255,0,0)
score = 0


top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

# SHAPE FORMATS

R = [['.....',
      '.....',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '..00.',
      '...0.',
      '.....'],
     ['.....',
      '.....',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.....',
      '.....']]

I = [['.....',
      '..0..',
      '..0..',
      '.....',
      '.....'],
     ['.....',
      '.00..',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]



shapes = [O, R, I]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255)]


# index 0 - 2 represent shapes


class Piece(object):
    rows = m  # y
    columns = n  # x

    # all the information we need about the shapes
    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # number from 0-3

    # function to send information to the agent in a convenient format
    def info_shape(self):
        # 0 for the square
        index = 0
        # 1,2,3,4 for the R
        if self.shape == R :
            index = 1 + self.rotation % 4
        # 5,6 for the I
        if self.shape == I :
            index = 5 + self.rotation % 2
        return self.x, self.y, index


# define the nxm grid with a 2 dimensionnal list of colors, taking into argument the pieces
# that are already inside the grid
def create_grid(locked_positions={}):
    # empty grid
    grid = [[(0, 0, 0) for x in range(n)] for x in range(m)]

    # we add the locked positions where there are already pieces
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid


# we convert the format of the shapes above into the format we can use to draw the grid
def convert_shape_format(shape):
    positions = []
    # we get the format matching the rotation status
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))
    # we correct the position with an offset (more accurate on screen)
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
    return positions



# check if one Piece is within the grid and in an empty spot
def valid_space(shape, grid):
    accepted_positions = [[(j, i) for j in range(n) if grid[i][j] == (0, 0, 0)] for i in range(m)]
    # we flatten the list
    accepted_positions = [j for sub in accepted_positions for j in sub]
    # we get the formatted version of the shape
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
            else :
                if not (pos[0] in [i for i in range(n)]):
                    return False

    return True


# we check tha all pieces are below the last line
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


# get the next shape that will appear
def get_shape():
    return Piece(n//2, 1, random.choice(shapes))


def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (
    top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() / 2))


# we clear all completed lines
def clear_rows(grid, locked):
    # need to see if row is clear the shift every other row above down one
    inc = 0
    # we check all rows beginning from the bottom
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            # the row is filled with shapes
            inc += 1
            # add positions to remove from locked
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    # we shift all the rows from $inc rows down
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc


# used to fraw the next shape that will come out on the side of the window
def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j * 30, sy + i * 30, 30, 30), 0)

    surface.blit(label, (sx + 10, sy - 30))


def draw_window(surface, score=0):
    surface.fill((0, 0, 0))
    # Tetris Title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j * 30, top_left_y + i * 30, 30, 30), 0)

    # draw grid and border
    sx = top_left_x
    sy = top_left_y
    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * 30),
                         (sx + play_width, sy + i * 30))  # horizontal lines
        for j in range(len(grid[0])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j * 30, sy),
                             (sx + j * 30, sy + play_height))  # vertical lines

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

    # print the score
    font = pygame.font.SysFont('comicsans', 35)
    label = font.render('Score : ' + str(score), 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100

    surface.blit(label, (sx + 20, sy + 150))


def main(win,score):
    global grid
    global inc
    global once
    once = False

    grid = create_grid(locked_positions)

    # we initialize the game
    change_piece = False
    run = True
    # we make the current_piece variable global so that the agent can access it
    global current_piece
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.01
    # we can even make shapes fall faster and faster
    #level_time = 0

    while run:

        grid = create_grid(locked_positions)
        # we add one time interval
        fall_time += clock.get_rawtime()
        #level_time += clock.get_rawtime()
        clock.tick()



        # every 7 seconds we speed up things
        '''if level_time / 1000 > 7:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.004'''

        if fall_time / 1000 >= fall_speed :

            for event in pygame.event.get():

                if not (once):
                    inc = 0
                else :
                    once = False
                    inc = 0

                # end of the game
                if event.type == pygame.QUIT:
                    run = False
                    pygame.display.quit()
                    quit()

                # user input, 4 possible keys
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        # not go out of the grid
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1

                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1

                    elif event.key == pygame.K_UP:
                        # rotate shape, add a modulo to get cyclic rotations
                        if current_piece.shape == I :
                            current_piece.rotation = current_piece.rotation + 1 % 2
                            if not valid_space(current_piece, grid):
                                current_piece.rotation = current_piece.rotation - 1 % 2
                        if current_piece.shape == R :
                            current_piece.rotation = current_piece.rotation + 1 % 4
                            if not valid_space(current_piece, grid):
                                current_piece.rotation = current_piece.rotation - 1 % 4

                    elif event.key == pygame.K_DOWN:
                        # move shape down
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1

                    elif event.key == pygame.K_SPACE:
                        # move shape at the bottom
                        while valid_space(current_piece, grid):
                            current_piece.y += 1
                        current_piece.y -= 1

        if fall_time / 1000 > fall_speed :
            fall_time = 0

            current_piece.y += 1
            if not (valid_space(current_piece, grid)):
                current_piece.y -= 1
                # if we can't move down the piece we go to the next piece
                change_piece = True

        shape_pos = convert_shape_format(current_piece)

        # add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        # the piece is at the bottom so we go to the next one
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                # we update position
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # increment score with number of rows cleared at once
            inc = clear_rows(grid, locked_positions)
            once = True
            score += inc ** 2 * 10

        draw_window(win, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # check if user lost
        if check_lost(locked_positions):
            run = False
            scores = open("scores.txt", "a")
            scores.write(str(score)+"\n")
            print(score)

    # lost message disabled to gain time when training with agent
    #draw_text_middle("You Lost", 40, (255, 255, 255), win)
    #pygame.display.update()
    #pygame.time.delay(100)
    return True


def play(n=100):
    run = True
    i = 0
    if os.path.isfile("scores.txt"):
        os.remove("scores.txt")

    while run and i<n:
        # initiate the pygame display
        win = pygame.display.set_mode((s_width, s_height))
        pygame.display.set_caption('Tetris - RL Project')

        # start game
        run = main(win,score)
        global locked_positions
        locked_positions = {}
        i += 1
        print(str(i))

    return



current_piece = get_shape()
inc = 0
