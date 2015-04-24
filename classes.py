#################################
###    QuadEdge Class         ###
################################
class QuadEdge:
 def __init__(self, reference, A, B, C, D):
  self.id = reference
  self.a  = A
  self.b  = B
  self.c  = C
  self.d  = D




###############################
###    Edge Class        ###
################################
class Edge:
 def __init__(self, reference, vertex, Next):
  self.id   = reference
  self.data = vertex
  self.next = Next