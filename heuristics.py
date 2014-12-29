#This is the goal state
P_goal = [[1,2,3],
          [4,0,5],
          [6,7,8]]

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
