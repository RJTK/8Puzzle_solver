from random import shuffle
from multiprocessing import Process, Pipe
from copy import deepcopy
from ds_heap import Heap
from time import time

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
  #The reason the puzzles are passed through pipes is that I was thinking about
  #running a bunch of solvers in parallel, but I decided not to spend the
  #time to implement that.  It is fast enough with just a sequential
  #implementation.  Although there is obviously huge room for improvement
  #in my implementation, I am mostly interested in the number of nodes that
  #need to be explored.
  num_puzzles = 15
  heuristics = [h1, h2, h4]
  Pipes = []
  for h in heuristics:
    Pipes.append(Pipe())
  
  for i in range(num_puzzles):
    P = gen_random_puzzle()
    while not is_solvable(P):
      P = gen_random_puzzle()
    for here, there in Pipes:
      there.send(P)

  for here, there in Pipes:
    there.send(None)

  for hi, h in enumerate(heuristics):
    solve(P_goal, Pipes[hi], h, p_id)

  for hi, h in enumerate(heuristics):
    here, there = Pipes[hi]
    average_nodes = 0
    average_time = 0
    for i in range(num_puzzles):
      nodes, path_len, time = here.recv()
      average_nodes = average_nodes + nodes
      average_time = average_time + time
    average_nodes = average_nodes/float(num_puzzles)
    average_time = average_time/float(num_puzzles)
    print 'Heuristic %d solved %d puzzles with %f average nodes explored, ' \
      'and %f average time' %(hi, num_puzzles, average_nodes, average_time)

  return

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
def h1(P):
  '''
  Heuristic number 1.  Checks the number of misplaced tiles.
  '''
  h = 0
  for i, row in enumerate(P_goal[0:3]):
    for j, v in enumerate(row):
      if P[i][j] != v and v != 0:
        h = h + 1
  return h + P[3]

#--------------------------------------------------------------------------------
def h2(P):
  '''
  Heuristic number 2.  Checks the sum of distances out of place.
  '''
  h = 0
  for i, row in enumerate(P[0:3]):
    for j, v in enumerate(row):
      if v != 0:
        for i_goal, row_goal in enumerate(P_goal[0:3]):
          try:
            j_goal = row_goal.index(v)
            h = h + abs(i - i_goal) + abs(j - j_goal)
            break
          except ValueError:
            continue
  return h + P[3]

#--------------------------------------------------------------------------------
def h3(P):
  '''
  Heuristic number 3.  Checks the number of direct reversals.
  This heuristic sucks when used alone.
  '''
  h = 0
  p = list(P[0:3]) #P[3] messes this up.  deepcopy() not necessary.
  for i, row in enumerate(p):
    for j, v in enumerate(row):
      if v != 0:
        try:
          if p[i + 1][j] == P_goal[i][j] and p[i][j] == P_goal[i + 1][j]:
            h = h + 1
        except IndexError:
          pass

        try:
          if p[i - 1][j] == P_goal[i][j] and p[i][j] == P_goal[i - 1][j]:
            h = h + 1
        except IndexError:
          pass

        try:
          if p[i][j + 1] == P_goal[i][j] and p[i][j] == P_goal[i][j + 1]:
            h = h + 1
        except IndexError:
          pass

        try:
          if p[i][j - 1] == P_goal[i][j] and p[i][j] == P_goal[i][j - 1]:
            h = h + 1
        except IndexError:
          pass
        
  return h + P[3]

#--------------------------------------------------------------------------------
def h4(P):
  '''
  The 4th heuristic.  The third plus the second.
  '''
  return h3(P) + h2(P)

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

#--------------------------------------------------------------------------------
def solve(P_goal, pipe, h, p_id):
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
  here, there = pipe
  P = here.recv()
  print 'Received', P
  while P:
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
        there.send((n_explored, path_len, time() - start_time))
        #path_len is the min path
        print 'Solved in %d explorations, with a min path len %d' % (n_explored,
                                                                     path_len)
        #Get a new puzzle if one is available
        P = here.recv()
        print 'Received', P
        break
      
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
  there.send(None)
  return

#Entry point
#--------------------------------------------------------------------------------
if __name__ == '__main__':
  main()
