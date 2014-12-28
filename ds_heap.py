#ds_heap.py
'''
My implementation of a heap datastructure.  Capable of storing any type that
fits in a python list. A key() function must be provided.
'''

#--------------------------------------------------------------------------------
class Heap(object):
  '''
  My implementation of a heap datastructure.  Capable of storing any type that
  fits in a python list. A key() function must be provided.  This implements
  a min-heap.  To create a max heap, the key() function may simply invert
  it's output.
  '''
  #------------------------------------------------------------------------------
  def __init__(self, key, item_id = id, init_list = None):
    '''
    '''
    if not hasattr(key, '__call__'):
      raise TypeError('key must be callable')
    if not hasattr(item_id, '__call__'):
      raise TypeError('item_id must be callable')
    self._key = key #function for comparison
    self._item_id = item_id #function for identifying an item
    self._heap = [None,] #the list storing items in the heap
    self._heap_dict = {} #a dictionary that maps item_id to heap index
    return

  #------------------------------------------------------------------------------
  def __len__(self):
    return len(self._heap) - 1

  #------------------------------------------------------------------------------
  def __contains__(self, x):
    return self._item_id(x) in self._heap_dict

  #------------------------------------------------------------------------------
  def is_empty(self):
    '''
    Returns True if the heap is empty
    '''
    if len(self._heap) == 1:
      return True

  #------------------------------------------------------------------------------
  def push(self, item):
    '''
    '''
    i = len(self._heap)
    self._heap.append(item)
    self._heap_dict[self._item_id(item)] = i
    self._bubble_up(i)
    assert self._heap[0] == None
    return
    
  #------------------------------------------------------------------------------
  def pop(self):
    '''
    Pops off the top of the heap.  This is the min element according to the
    ordering imposed by key()
    '''
    N = len(self._heap) - 1
    if N == 0:
      return None
    self._swap(1, N)
    min_element = self._heap.pop(N)
    del self._heap_dict[self._item_id(min_element)]
    self._bubble_down(1)
    return min_element

  #------------------------------------------------------------------------------
  def peek(self):
    '''
    Peeks at the minimum element of the heap.  This is the min element
    according to the ordering imposed by key()
    '''
    return self._heap[1]
    return

  #------------------------------------------------------------------------------
  def remove(self, x):
    '''
    Removes the item x from the heap.  It is found using the _item_dict hash
    table.  The table is indexed with the given key function on x.  that is,
    self.key(x).
    '''
    N = len(self._heap)
    i = self._heap_dict[self._item_id(x)]
    self._swap(i, N - 1)
    self._heap.pop(N - 1)
    del self._heap_dict[self._item_id(x)]
    if i != 1 and self._compare(i/2, i):
      self._bubble_up(i)
    if self._compare(i, 2*i) or self._compare(i, 2*i + 1):
      self._bubble_down(i)
    
    assert self._heap[0] == None
    return

  #------------------------------------------------------------------------------
  def _bubble_up(self, i):
    while i != 1 and self._compare(i/2, i):
      self._swap(i, i/2)
      i = i/2
    return

  #------------------------------------------------------------------------------
  def _bubble_down(self, i):
    while self._compare(i, 2*i) or self._compare(i, 2*i + 1):
      if self._compare(2*i, 2*i + 1):
        self._swap(i, 2*i + 1)
        i = 2*i + 1
      else:
        self._swap(i, 2*i)
        i = 2*i
    assert self._heap[0] == None

  #------------------------------------------------------------------------------
  def _compare(self, i, j):
    '''
    Compares the keys of the elements at positions i and j,
    returns key(_heap[i]) >= key(_heap[j]).  If either of i or j raise IndexErrors
    False is returned.
    '''
    try:
      i_val = self._key(self._heap[i])
    except IndexError:
      return False
      
    try:
      j_val = self._key(self._heap[j])
    except IndexError:
      return False

    return i_val >= j_val

  #------------------------------------------------------------------------------
  def _swap(self, i, j):
    '''
    Swaps the elements in index i and j and maintains the dictionary.
    '''
    self._heap_dict[self._item_id(self._heap[i])] = j
    self._heap_dict[self._item_id(self._heap[j])] = i

    temp_val = self._heap[j]
    self._heap[j] = self._heap[i]

    self._heap[i] = temp_val
    return
