'''
A program that solves 8 puzzles (with multiple processes) using A* search.
It isn't very efficient, just trying stuff out with multiprocessing
'''

from random import shuffle
from multiprocessing import Process, Queue
from copy import deepcopy
from ds_heap import Heap
from time import time
from os import getpid

from heuristics import h1, h2, h4

#The 8-puzzle will be represented as a 2D list of integers.  This is the most
#obvious representation.  I also store the distance from the start in the
#Puzzles like so:
#[[3,2,5],
# [1,6,7],
# [4,8,0],
# 22] <- This is the distance from the start.  Heuristics need this value

#This is the goal state
P_goal = [[1,2,3],
          [4,0,5],
          [6,7,8]]

#--------------------------------------------------------------------------------
def main():
  '''
  Effective program entry point
  '''
  num_puzzles = 1
  num_threads = 0
  heuristics = [h1, h2, h4]
  QUEUE_SIZE = num_puzzles*len(heuristics) + num_threads + 1
  total_expected_results = num_puzzles*len(heuristics)
  Q_puzzles = Queue(maxsize = QUEUE_SIZE)
  Q_results = Queue(maxsize = QUEUE_SIZE)

  for i in range(num_puzzles):
    P = gen_random_puzzle()
    while not is_solvable(P):
      P = gen_random_puzzle()
    for hi, h in enumerate(heuristics):
      Q_puzzles.put((P, hi, h))
  for i in range(num_threads):
    Q_puzzles.put((None, None, None))
    #Since Queue.empty() is unreliable, this is an "end" delimiter

  if num_threads == 0:
    Q_puzzles.put((None, None, None))
    solve(P_goal, p_id, Q_puzzles, Q_results)

  else:
    Processes = []
    for ti, t in enumerate(range(num_threads)):
      P = Process(target = solve, args = (P_goal, p_id, Q_puzzles, Q_results))
      Processes.append(P)
      P.start()

  #H_results = {h_num : [average_nodes, average_time]}
  H_results = {}
  while total_expected_results:
    n_explored, path_len, T, h_num = Q_results.get(block = True, timeout = None)
    total_expected_results -= 1
    try:
      H_results[h_num][0] += n_explored
      H_results[h_num][1] += T
    except KeyError:
      H_results[h_num] = [n_explored, T]

  for h_num in range(len(heuristics)):
    average_nodes = H_results[h_num][0]/float(num_puzzles)
    average_time = H_results[h_num][1]/float(num_puzzles)
    print 'Heuristic %d solved %d puzzles with %f average nodes explored, '\
      'and %f average time' %(h_num, num_puzzles, average_nodes, average_time)
  if num_threads > 0:
    for p in Processes:
      p.join()
  return

#--------------------------------------------------------------------------------
def solve(P_goal, p_id, Q_puzzles, Q_results):
  '''
  Solves the 8 puzzle starting at a puzzle sent through the pipe
  heading towards P_goal.
  
  h is the heuristic function. p_id is a function that uniquely identifies
  a puzzle configuration and distance from start.

  pipe is a multiprocessing.Pipe used to get puzzles to solve, and to return
  the results.  The total number of states explored, and the minimum path
  distance to the goal and running time are returned through the pipe in a tuple 
  (n_explored, path_length, time).
  '''
  my_pid = getpid()

  P, h_num, h = Q_puzzles.get(block = True)
  if P == None:
    print 'Process %d exiting.' % my_pid
    return #Done

  print '%d Puzzles left in the Queue' % Q_puzzles.qsize()

  while True:
    start_time = time()
    n_explored = 0

    #A priority queue, ordered based on the heuristic
    fringe = Heap(h, item_id = p_id)
    fringe.push(P)
    closed = {} #the visited states.  A hash table (dictionary)
    
    #Start the search
    while not fringe.is_empty():
      x = fringe.pop()
      n_explored = n_explored + 1
      path_len = x[3] #We store the min path length in the puzzle itself
      if x[0:3] == P_goal[0:3]:
        Q_results.put((n_explored, path_len, time() - start_time, h_num))
        #path_len is the min path

        #Get a new puzzle if one is available

        P, h_num, h = Q_puzzles.get(block = True)
        if P == None:
          print 'Process %d exiting.' % my_pid
          return #Done
        print '%d Puzzles left in the Queue' % Q_puzzles.qsize()

      for child in get_children(x): #Look at all of the current node's children
        if child not in fringe and p_id(child) not in closed:
          fringe.push(child) #A newly discovered state

        elif child in fringe:
          if child[3] < fringe._heap[fringe._heap_dict[p_id(child)]][3]:
            fringe.remove(child) #I didn't implement editing items in my heap
            fringe.push(child)

        elif p_id(child) in closed:
          if child[3] < closed[p_id(child)][3]:
            del closed[p_id(child)]
            fringe.push(child)

      #end for
      closed[p_id(x)] = x
      #Go back and get a new state from the fringe.

    #end while
  #end while
  raise AssertionError('Process escaped  while True:')
  return #Should never reach here

#--------------------------------------------------------------------------------
def is_solvable(P):
  '''
  Returns the number of inversions of P versus P_goal if the array is flattened
  and the 0 is ignored
  '''
  p = [i for row in P[0:3] for i in row if i != 0]
  inversions = 0
  for i, v in enumerate(p):
    for j in p[0:i]:
      if j > v:
        inversions = inversions + 1
  if inversions & 1 == 1:
    return False
  return True
  
#--------------------------------------------------------------------------------
def gen_random_puzzle():
  '''
  Generates a random starting configuration for an 8 puzzle.
  '''
  P = range(9) #[0,1,2,3,4,5,6,7,8]
  #There are 9! permutations of a length 9 list, this is far shorter than the
  #period of the random number generator, so shuffling is a safe strategy
  shuffle(P)
  P = zip(*[iter(P)]*3)
  P = [list(p) for p in P]
  P.append(0) #0 starting path length
  return P

#--------------------------------------------------------------------------------
def p_id(P):
  '''
  The puzzle state has the following form

  [[a,b,c],
   [d,e,f],
   [g,h,i],
   l]

  Where a..i are unique numbers from 0 to 8, and l is a positive integer
  representing the path length to reach this state from the start.

  This function returns a unique representation of this state in a single
  number
  '''
  x = P[3]*10
  for row in P[0:-1]:
    for i in row:
      x = x + i
      x = x*10
  return x


#--------------------------------------------------------------------------------
def get_children(x):
  '''
  Returns the children of x.  I couldn't think of a way to do this other than
  hard coding it...
  '''
  #yield makes the function an iterator, and allows it to be reentered at
  #the same point it yielded last
  y = deepcopy(x) #preserve the old state
  y[3] = y[3] + 1 #increment path length
  if 0 in y[0]: #top row
    if y[0][0] == 0:
      new_p = deepcopy(y)
      new_p[0][0] = y[0][1]
      new_p[0][1] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[0][0] = y[1][0]
      new_p[1][0] = 0
      yield new_p

    elif y[0][1] == 0:
      new_p = deepcopy(y)
      new_p[0][1] = y[0][0]
      new_p[0][0] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[0][1] = y[0][2]
      new_p[0][2] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[0][1] = y[1][1]
      new_p[1][1] = 0
      yield new_p

    elif y[0][2] == 0:
      new_p = deepcopy(y)
      new_p[0][2] = y[0][1]
      new_p[0][1] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[0][2] = y[1][2]
      new_p[1][2] = 0
      yield new_p

  elif 0 in y[1]: #middle row
    if y[1][0] == 0:
      new_p = deepcopy(y)
      new_p[1][0] = y[0][0]
      new_p[0][0] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[1][0] = y[1][1]
      new_p[1][1] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[1][0] = y[2][0]
      new_p[2][0] = 0
      yield new_p
      
    elif y[1][1] == 0:
      new_p = deepcopy(y)
      new_p[1][1] = y[0][1]
      new_p[0][1] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[1][1] = y[1][0]
      new_p[1][0] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[1][1] = y[1][2]
      new_p[1][2] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[1][1] = y[2][1]
      new_p[2][1] = 0
      yield new_p

    elif y[1][2] == 0:
      new_p = deepcopy(y)
      new_p[1][2] = y[1][1]
      new_p[1][1] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[1][2] = y[0][2]
      new_p[0][2] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[1][2] = y[2][2]
      new_p[2][2] = 0
      yield new_p

  elif 0 in y[2]: #bottom row
    if y[2][0] == 0:
      new_p = deepcopy(y)
      new_p[2][0] = y[1][0]
      new_p[1][0] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[2][0] = y[2][1]
      new_p[2][1] = 0
      yield new_p
    elif y[2][1] == 0:
      new_p = deepcopy(y)
      new_p[2][1] = y[2][0]
      new_p[2][0] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[2][1] = y[1][1]
      new_p[1][1] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[2][1] = y[2][2]
      new_p[2][2] = 0
      yield new_p
    elif y[2][2] == 0:
      new_p = deepcopy(y)
      new_p[2][2] = y[2][1]
      new_p[2][1] = 0
      yield new_p
      new_p = deepcopy(y)
      new_p[2][2] = y[1][2]
      new_p[1][2] = 0
      yield new_p


#Entry point
#--------------------------------------------------------------------------------
if __name__ == '__main__':
  main()
