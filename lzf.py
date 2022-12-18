# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AVcNjlCnRIwC6ZlJJQSu1EwXIUF3oq24
"""

import numpy as np
import heapq as hq
from collections import deque
import matplotlib.pyplot as plt
from pylab import *
import numpy as np
from tensorflow.keras import models, layers
# Similar code to queue search lecture notebook
# Only part you need to change is in the queue_search method below

class SearchNode(object):
    def __init__(self, problem, state, parent=None, action=None, step_cost=0, depth=0):
        self.problem = problem
        self.state = state
        self.parent = parent
        self.action = action
        self.step_cost = step_cost
        self.path_cost = step_cost + (0 if parent is None else parent.path_cost)
        self.path_risk = self.path_cost + problem.heuristic(state)
        # print("heu", problem.heuristic(state))
        self.depth = depth
        self.child_list = []
    def is_goal(self):
        return self.problem.is_goal(self.state)
    def children(self):
        if len(self.child_list) > 0: return self.child_list
        domain = self.problem.domain
        for action, step_cost in domain.valid_actions(self.state):
            new_state = domain.perform_action(self.state, action)
            self.child_list.append(
                SearchNode(self.problem, new_state, self, action, step_cost, depth=self.depth+1))
        return self.child_list
    def path(self):
        if self.parent == None: return []
        return self.parent.path() + [self.action]

class SearchProblem(object):
    def __init__(self, domain, initial_state, is_goal = None):
        if is_goal is None: is_goal = lambda s: False
        self.domain = domain
        self.initial_state = initial_state
        self.is_goal = is_goal
        self.heuristic = lambda s: 0
    def root_node(self):
        return SearchNode(self, self.initial_state)

class FIFOFrontier:
    def __init__(self):
        self.queue_nodes = deque()
        self.queue_states = set()
    def __len__(self):
        return len(self.queue_states)
    def push(self, node):
        if node.state not in self.queue_states:
            self.queue_nodes.append(node)
            self.queue_states.add(node.state)
    def pop(self):
        node = self.queue_nodes.popleft()
        self.queue_states.remove(node.state)
        return node
    def is_not_empty(self):
        return len(self.queue_nodes) > 0

class PriorityHeapFIFOFrontier(object):
    """
    Implementation using heapq
    https://docs.python.org/3/library/heapq.html
    """
    def __init__(self):
        self.heap = []
        self.state_lookup = {}
        self.count = 0

    def push(self, node):
        if node.state in self.state_lookup:
            entry = self.state_lookup[node.state] # = [risk, count, node, removed]
            if entry[0] <= node.path_risk: return
            entry[-1] = True # mark removed
        new_entry = [node.path_risk, self.count, node, False]
        hq.heappush(self.heap, new_entry)
        self.state_lookup[node.state] = new_entry
        self.count += 1

    def pop(self):
        while len(self.heap) > 0:
            risk, count, node, already_removed = hq.heappop(self.heap)
            if not already_removed:
                self.state_lookup.pop(node.state)
                return node

    def is_not_empty(self):
        return len(self.heap) > 0

    def states(self):
        return list(self.state_lookup.keys())

def queue_search(frontier, problem):

    # This is the total number of nodes popped off the frontier during the search
    count = 0  # new
    explored = set()
    root = problem.root_node()
    frontier.push(root)
    cost=[]
    risk=[]
    guess=[]
    while frontier.is_not_empty():
        print('pop')
        print(count)
        node = frontier.pop() # need to count how many times this happens
        count += 1
        cost.append(node.path_cost)
        risk.append(node.path_risk)
        guess.append(node.path_risk-node.path_cost)
        if count==200:
            # encoding=utf-8
            #mpl.rcParams['font.sans-serif'] = ['SimHei']

            x = range(200)
            y1 = guess
            y2=risk
            y3=cost
            #y1 = [0.86, 0.85, 0.853, 0.849, 0.83]
            # plt.plot(x, y, 'ro-')
            # plt.plot(x, y1, 'bo-')

            plt.plot(x, y1, marker='o', mec='r', mfc='w', label=u'heuristic')
            plt.plot(x, y2, marker='*', ms=10, label=u'total risk')
            plt.plot(x, y3, marker='.', mec='r', mfc='w', label=u'path cost')
            plt.legend()  # 让图例生效
            #plt.xticks(x, names, rotation=45)
            plt.margins(0)
            plt.subplots_adjust(bottom=0.15)
            plt.xlabel(u"search time")
            plt.ylabel("costs")
            plt.title("Heuristic during A* search with neural Network")

            plt.show()
        # print(node.path_risk)
        # print(node.path_cost)
        # print(node.path_risk-node.path_cost)

        if node.is_goal(): break
        explored.add(node.state)
        for child in node.children():
            if child.state in explored: continue
            frontier.push(child)
        # print(len(frontier.heap))
              # new
    plan = node.path() if node.is_goal() else []

    # Second return value should be node count, not 0
    return plan, count

def breadth_first_search(problem):
    return queue_search(FIFOFrontier(), problem)

def a_star_search(problem, heuristic):
    # print("in-astar")
    problem.heuristic = heuristic
    print('search_begin')
    return queue_search(PriorityHeapFIFOFrontier(), problem)

from time import perf_counter
import numpy as np
import random as rd
import matplotlib.pyplot as pt
from matplotlib import animation
from matplotlib import rc
rc('animation', html='jshtml')

WALL, MOVING, CHARGER, CLEAN, DIRTY, ROOMBA = list(range(6))
SIZE = 7

class RoombaDomain:
    def __init__(self):

        # deterministic grid world
        num_rows, num_cols = SIZE, SIZE
        grid = CLEAN * np.ones((num_rows, num_cols), dtype=int)
        grid[SIZE // 2, 2:SIZE - 2] = WALL
        grid[2:SIZE // 2, SIZE // 2] = WALL

        # Randomize moving initial point
        moving_count = 1
        for _ in range(moving_count):
            x = rd.randrange(SIZE)
            y = rd.randrange(SIZE)
            if grid[x, y] == CLEAN:
                grid[x, y] = MOVING

        grid[0, 0] = CHARGER
        grid[0, -1] = CHARGER
        grid[-1, SIZE // 2] = CHARGER
        max_power = 2 * SIZE + 1

        self.grid = grid
        self.max_power = max_power

    def pack(self, g, r, c, p):
        return (g.tobytes(), r, c, p)

    def unpack(self, state):
        grid, r, c, p = state
        grid = np.frombuffer(grid, dtype=int).reshape(self.grid.shape).copy()
        return grid, r, c, p

    def initial_state(self, roomba_position, dirty_positions):
        r, c = roomba_position
        grid = self.grid.copy()
        for dr, dc in dirty_positions: grid[dr, dc] = DIRTY
        return self.pack(grid, r, c, self.max_power)

    def render(self, ax, state, x=0, y=0):
        grid, r, c, p = self.unpack(state)
        num_rows, num_cols = grid.shape
        ax.imshow(grid, cmap='gray', vmin=0, vmax=4, extent=(x - .5, x + num_cols - .5, y + num_rows - .5, y - .5))
        for col in range(num_cols + 1): pt.plot([x + col - .5, x + col - .5], [y + -.5, y + num_rows - .5], 'k-')
        for row in range(num_rows + 1): pt.plot([x + -.5, x + num_cols - .5], [y + row - .5, y + row - .5], 'k-')
        pt.text(c - .25, r + .25, str(p), fontsize=24)
        pt.tick_params(which='both', bottom=False, left=False, labelbottom=False, labelleft=False)

    def valid_actions(self, state):

        # r, c is the current row and column of the roomba
        # p is the current power level of the roomba
        # grid[i,j] is WALL, CHARGER, CLEAN or DIRTY to indicate status at row i, column j.
        grid, r, c, p = self.unpack(state)
        num_rows, num_cols = grid.shape
        actions = []

        # actions[k] should have the form ((dr, dc), step_cost) for the kth valid action
        # where dr, dc are the change to roomba's row and column position
        if p != 0:
            if r != 0:
                actions.append(((-1, 0), 1))
            if r != SIZE - 1:
                actions.append(((1, 0), 1))
            if c != 0:
                actions.append(((0, -1), 1))
            if c != SIZE - 1:
                actions.append(((0, 1), 1))
            if r != SIZE - 1 and c != SIZE - 1:
                actions.append(((1, 1), 1))
            if r != SIZE - 1 and c != 0:
                actions.append(((1, -1), 1))
            if r != 0 and c != SIZE - 1:
                actions.append(((-1, 1), 1))
            if r != 0 and c != 0:
                actions.append(((-1, -1), 1))
        actions.append(((0, 0), 1))

        return actions

    def perform_action(self, state, action):
        grid, r, c, p = self.unpack(state)
        dr, dc = action

        if dr == 0 and dc == 0:  # staying put
            if grid[r][c] == DIRTY and p != 0:  # if spot is dirty and has enough power
                grid[r][c] = CLEAN  # clean
                p -= 1  # decrease power level
            elif grid[r][c] == CHARGER and p != 2 * SIZE + 1:
                p += 1  # on charger and stay then charge +1
        elif p != 0:  # moving and has enough power
            p -= 1  # decrease power level
            r += dr
            c += dc

            if grid[r][c] == WALL:  # runs into wall then undo previous step
                r -= dr
                c -= dc
                p += 1
            elif grid[r][c] == MOVING:  # runs into moving then undo previous step
                r -= dr
                c -= dc
                p += 1

        new_state = self.pack(grid, r, c, p)
        return new_state

    def is_goal(self, state):
        grid, r, c, p = self.unpack(state)

        # In a goal state, no grid cell should be dirty
        result = (grid != DIRTY).all()

        ### TODO: Implement additional requirement that roomba is back at a charger
        result = result and grid[r][c] == CHARGER

        return result

    def better_heuristic(self, state):

        # "Better" means more memory-efficient (fewer popped nodes during A* search)

        grid, r, c, p = self.unpack(state)
        dirty = list(zip(*np.nonzero(grid == DIRTY)))
        if len(dirty) == 0:
            return 0

        dist = 0
        curr_r = r
        curr_c = c
        seen = set()
        seen.add((r, c))
        for i in dirty:
            min_dist = float('inf')
            min_r = -1
            min_c = -1
            for (dr, dc) in dirty:
                if not (dr, dc) in seen:
                    curr_dist = ((dr - curr_r) ** 2 + (dc - curr_c) ** 2) ** (1 / 2)  # distance
                    if curr_dist < min_dist:
                        min_dist = curr_dist
                        min_r = curr_r
                        min_c = curr_c
            if min_r != -1:
                dist += min_dist
                seen.add((min_r, min_c))
        return dist

    def update_state(self, roomba_position, grid, power):
        r, c = roomba_position
        new_grid = grid.copy()
        return self.pack(new_grid, r, c, power)


def main(show_animation, index, heuristic_function, size, dirty_count):
    if size != None:
        global SIZE
        SIZE = size

    def A_star(problem):
        start = perf_counter()
        if heuristic_function == None:
          plan, node_count = a_star_search(problem, domain.better_heuristic)
        else:
          plan, node_count = a_star_search(problem, heuristic_function)
        astar_time = perf_counter() - start
        # print("better heuristic:")
        # print("astar_time", astar_time)
        # print("node count", node_count)
        return plan, node_count

    # set up initial state by making five random open positions dirty
    domain = RoombaDomain()

    # randomize roomba starting position
    # roomba_init_r = rd.randrange(SIZE)
    # roomba_init_c = rd.randrange(SIZE)

    # print(np.random.permutation(list(zip(*np.nonzero(domain.grid == CLEAN))))[:1])
    # roomba_init = np.random.permutation(list(zip(*np.nonzero(domain.grid == CLEAN))))[:1]
    # roomba_init_r, roomba_init_c = np.array(roomba_init)
    # print(type(roomba_init))

    found = False
    while not found:
        x = rd.randrange(size)
        y = rd.randrange(size)
        if grid[x, y] == CLEAN:
            roomba_init_r, roomba_init_c = x, y
            found = True


    init = domain.initial_state(
        
        

    # roomba_position=(0, 0),
    roomba_position=(roomba_init_r, roomba_init_c),

    # dirty_positions=np.random.permutation(list(zip(*np.nonzero(domain.grid == CLEAN))))[:4])
    dirty_positions=np.random.permutation(list(zip(*np.nonzero(domain.grid == CLEAN))))[:dirty_count])

    problem = SearchProblem(domain, init, domain.is_goal)

    start = perf_counter()

    # record initial state
    init_g, init_r, init_c, init_p = problem.initial_state
    init_g = np.frombuffer(init_g, dtype=int).reshape([SIZE, SIZE]).copy()
    # print("Initial State:\n", repr(init_g), init_r, init_c, init_p)

    overall_node_count = 0

    # print("pre-astar")
    # plan, node_count = a_star_search(problem, domain.better_heuristic)
    if heuristic_function == None:
      plan, node_count = a_star_search(problem, domain.better_heuristic)
    else:
      plan, node_count = a_star_search(problem, heuristic_function)
    # print("post-astar")

    overall_node_count += node_count

    astar_time = perf_counter() - start
    # print("better heuristic:")
    # print("astar_time", astar_time)
    # print("node count", node_count)

    # reconstruct the intermediate states along the plan
    states = [problem.initial_state]

    a = 0
    b = 0
    while bool(len(plan)):
        a = a + 1
        states_len=0
        last_state = states[-1]
        if a % 4 == 0:
            b = b + 1

            c_grid, c_r, c_c, c_p = domain.unpack(current_state)

            indices = np.where(c_grid == MOVING)
            xs, ys = indices
            for i in range(len(xs)):
                m_r = xs[i]
                m_c = ys[i]

                valid_actions = []
                if m_r > 0:
                    valid_actions.append((-1, 0))
                if m_r < SIZE - 1:
                    valid_actions.append((1, 0))
                if m_c > 0:
                    valid_actions.append((0, -1))
                if m_c < SIZE - 1:
                    valid_actions.append((0, 1))
                next_action = rd.randint(1, len(valid_actions))
                action = valid_actions[next_action - 1]
                if c_grid[m_r + action[0], m_c + action[1]] != WALL and \
                        (m_r + action[0], m_c + action[1]) != (c_r, c_c) and \
                        c_grid[m_r + action[0], m_c + action[1]] != CHARGER and \
                        c_grid[m_r + action[0], m_c + action[1]] != DIRTY:
                    c_grid[m_r, m_c] = CLEAN
                    c_grid[m_r + action[0], m_c + action[1]] = MOVING

            update = domain.update_state((c_r, c_c), c_grid, c_p)
            new_problem = SearchProblem(domain, update, domain.is_goal)
            new_plan, node_count = A_star(new_problem)

            overall_node_count += node_count

            plan = new_plan
            last_state = update

        current_state = domain.perform_action(last_state, plan[0])
        
        states.append(current_state)
        #state_len=state_len+1
        if len(states)>50: 
          break
        del plan[0]

    # Animate the plan
    fig = pt.figure(figsize=(8, 8))

    print("\nOverall node count:", overall_node_count)
    print("Overall step count:", len(states))

    def drawframe(n):
        pt.cla()
        domain.render(pt.gca(), states[n])

    # blit=True re-draws only the parts that have changed.
    anim = animation.FuncAnimation(fig, drawframe, frames=len(states), interval=500, blit=False)
    if show_animation:
      pt.show()
    else:
      pt.close()

    print("index:", index, "\n")

    return init_g, len(states), roomba_init_r, roomba_init_c, anim


def generate_training_data(index):    
    domain = RoombaDomain()

    roomba_init_r = rd.randrange(SIZE)
    roomba_init_c = rd.randrange(SIZE)

    init = domain.initial_state(
      roomba_position=(roomba_init_r, roomba_init_c),
      dirty_positions=np.random.permutation(list(zip(*np.nonzero(domain.grid == CLEAN))))[:rd.randrange(1,5)])

    problem = SearchProblem(domain, init, domain.is_goal)

    init_g, init_r, init_c, init_p = problem.initial_state
    init_g = np.frombuffer(init_g, dtype=int).reshape([SIZE, SIZE]).copy()
    print("index:", index)
    return init_g, roomba_init_r, roomba_init_c


generate_training_data('test_data')

grids = []
steps = []

for i in range(200):
    # grid, step, roomba_init_r, roomba_init_c = main(False, i, None)

    # grid[roomba_init_r][roomba_init_c] = ROOMBA
    grid, roomba_init_r, roomba_init_c = generate_training_data(i)
    
    domain = RoombaDomain()
    steps.append(domain.better_heuristic((grid, roomba_init_r, roomba_init_c, rd.randrange(2 * SIZE + 1))))
    grid[roomba_init_r][roomba_init_c] = ROOMBA
    
    grids.append(grid)
    # steps.append(step)

y = np.array(steps)

grids = np.array(grids)
steps = np.array(steps)
print(grids.shape)
print(steps.shape)

import numpy as np
import tensorflow as tf



swaped_grids=np.swapaxes(grids,0,2)
print(swaped_grids.shape)
print(steps.shape)



# # Define the input shape
# input_shape = (7, 7, 1)
#
# # Create an input layer with the specified shape
# inputs = tf.keras.layers.Input(shape=input_shape)
#
# # Add a convolutional layer with 32 filters and a kernel size of 3x3
# x = tf.keras.layers.Conv2D(32, kernel_size=(4, 4), activation='relu')(inputs)
#
# # Add a max pooling layer with a pool size of 2x2
# x = tf.keras.layers.MaxPooling2D(pool_size=(1, 1))(x)
#
# # Add a dense layer with 32 units and ReLU activation
# x = tf.keras.layers.Dense(32, activation='linear')(x)
#
# # Add an output layer with a single unit and linear activation
# outputs = tf.keras.layers.Dense(1, activation='linear')(x)
#
# # Create a model from the input and output layers
# model = tf.keras.Model(inputs=inputs, outputs=outputs)
#
# # Compile the model with mean squared error loss and Adam optimization
# model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])





###################################################################################
# #zli
#
# input_shape = (7, 7, 1)
#
#
# inputs = tf.keras.layers.Input(shape=input_shape)
#
# x = tf.keras.layers.Conv2D(32, kernel_size=(2,2), activation='relu')(inputs)
# x = tf.keras.layers.MaxPooling2D(pool_size=(1, 1))(x)
# x = tf.keras.layers.Dense(36, activation='relu')(x)
# x = tf.keras.layers.Dense(6, activation='relu')(x)
#
# outputs = tf.keras.layers.Dense(1, activation='relu')(x)
# model = tf.keras.Model(inputs=inputs, outputs=outputs)
# model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])

# zli2
model = models.Sequential()
model.add(layers.Conv2D(32, kernel_size=(2,2), input_shape=(7,7,1), activation='relu'))
model.add(layers.Dense(36, activation='relu'))
model.add(layers.Dense(6, activation='relu'))
model.add(layers.Dense(1))
model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])










# Import the necessary libraries
import numpy as np
from tensorflow.keras import models, layers

# Define the neural network architecture
# model = models.Sequential()
# model.add(layers.Dense(128, input_shape=(None,7,7), activation='relu'))
# model.add(layers.Dense(64, activation='relu'))
# model.add(layers.Dense(32, activation='relu'))
# model.add(layers.Dense(1))

# # leo
# model = models.Sequential()
# model.add(layers.Conv2D(32, kernel_size=(7, 7), input_shape=(7,7,1), activation='linear'))
# # tf.keras.layers.MaxPooling2D(pool_size=(1, 1))(x)
# # model.add(layers.Dense(1024, input_shape=(7,7), activation='linear'))
# # model.add(layers.Dense(1024, activation='linear'))
# model.add(layers.Dense(128, activation='linear'))
# model.add(layers.Dense(32, activation='linear'))
# model.add(layers.Dense(16, activation='linear'))
# model.add(layers.Dense(1))
#
# # Compile the model
# model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])

# Train the model on a dataset of paths and their corresponding costs
# X = grids
X = np.expand_dims(grids, 3)

y = steps

# X = np.array([
#       [[5, 3, 3, 1, 3, 3, 2],
#        [3, 1, 3, 3, 3, 4, 3],
#        [3, 3, 3, 0, 3, 3, 3],
#        [3, 3, 0, 0, 0, 3, 3],
#        [1, 3, 3, 3, 3, 3, 4],
#        [3, 3, 3, 3, 4, 3, 3],
#        [3, 3, 4, 2, 3, 3, 3]],

#       [[5, 3, 4, 1, 3, 3, 2],
#        [3, 1, 3, 3, 3, 3, 3],
#        [3, 3, 3, 0, 4, 3, 3],
#        [3, 3, 0, 0, 0, 3, 3],
#        [1, 3, 3, 3, 3, 3, 3],
#        [3, 3, 4, 3, 3, 3, 3],
#        [4, 3, 3, 2, 3, 3, 3]]
#      ])
# y = np.array([20, 22])
model.fit(grids.tolist(), steps.tolist(), epochs=500)
def heuristic(point):
  
  grid, r, c, p = point
  # grid = np.array(grid).reshape((7,7))
  grid = np.frombuffer(grid, dtype=int).reshape((1,7,7)).copy()
  grid[0][r][c] = ROOMBA
  # print(grid)
  
  # print(np.expand_dims(np.expand_dims(grid, 0),0).shape)
  # return model.predict(grid, verbose=0)[0][0][0][0]
  return model.predict(grid, verbose=0)[0][0][0][0]

grid, step, r, c, anim = main(True, i, heuristic,7,4)
#anim
# print(grid, step, r, c)

#grid, step = main(True, 0, heuristic,7,4)

def heuristic(point):
  
  grid, r, c, p = point
  # grid = np.array(grid).reshape((7,7))
  grid = np.frombuffer(grid, dtype=int).reshape((7,7)).copy()
  grid[r][c] = ROOMBA
  print(grid)
  
  # print(np.expand_dims(np.expand_dims(grid, 0),0).shape)
  return model.predict(grid, verbose=0)