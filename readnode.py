import sys, getopt, math, re, csv
import numpy as np
from array import array
from predicates import orient2d, incircle

#set global variables
quadID = 0
edgeID = 0
quadlist = []

#####################################################
#############    Classes             ################
#####################################################
 
##############################
###    QuadEdge Class      ###
##############################
class QuadEdge:
 def __init__(self):
  # quadedge identification
  global quadID
  self.id = quadID
  quadID += 1

  # add quadEdge to List for reference
  quadlist.append(self)

  #initialize list of edges
  self.e = [Edge(),Edge(),Edge(),Edge()]

  #Set the next pointers to infinity
  self.e[0].next = self.e[0]
  self.e[1].next = self.e[3]
  self.e[2].next = self.e[2]
  self.e[3].next = self.e[1]

  #set the rotations of each edge
  self.e[0].rot = 0
  self.e[1].rot = 1
  self.e[2].rot = 2
  self.e[3].rot = 3

  # set the quadedge ID in each of the edges
  for i in xrange(3): 
   self.e[i].qid = self.id


#############################
###    Edge Class        ###
#############################
class Edge:
 def __init__(self):
  #self.id   = reference
  self.next  = Edge
  self.org   = (None, None)
  self.dest  = (None, None)
  self.rot   = 0   # rotation in quadedge 
  self.qid   = 0   # quadedge identification

  # edge identification
  global edgeID
  self.id = edgeID  
  edgeID += 1


#####################################################
#############    Edge Algebra        ################
#####################################################

####### Rotate ########
def Rot(t):
 a = t[0]; q = t[1]
 if (a.rot < 3):
  return (q.e[a.rot+1], q)
 else:
  return (q.e[0], q)

#### Inv Rotate ######
def invRot(t):
 a = t[0]; q = t[1]
 if (a.rot > 0):
  return (q.e[a.rot-1], q)
 else:
  return (q.e[3], q)

###### sym #########
def Sym(t):
 a = t[0]; q = t[1]
 if (a.rot > 1):
  return (q.e[a.rot-2], q)
 else:
  return (q.e[a.rot+2], q)

###### Onext ########
def Onext(t):
 a = t[0]; 
 return (a.next, quadlist[a.next.qid])

###### Lnext ########
def Lnext(t):
 return Rot( Onext( invRot(t)))

###### Rnext ########
def Rnext(t):
 return invRot( Onext( Rot(t)))

###### Dnext ########
def Dnext(t):
 return Sym( Onext( Sym(t)))

###### Oprev ########
def Oprev(t):
 return Rot( Onext( Rot(t)))

###### Lprev ########
def Lprev(t):
 return Sym( Onext(t))

###### Rprev ########
def Rprev(t):
 return Onext( Sym(t))

###### Dprev ########
def Dprev(t):
 return invRot( Onext( invRot(t)))


#####################################################
###########  Topological Operators   ################
#####################################################


#####################
###    MakeEdge   ###
#####################
def MakeEdge():
 q = QuadEdge()

 #return edge a as e[0], canonical edge in q
 a = q.e[0]
 return (a,q)

#####################
###    Connect    ###
#####################
def Connect(a, b): 
 e = makeEdge()

 e[0].org  = a[0].dest
 e[0].dest = b[0].org

 Splice(e, Lnext(a))
 Splice(Sym(e), b)

 return e


#####################
###    Splice     ###
#####################
def Splice(a, b):
 alpha = Rot( Onext(a))
 beta  = Rot( Onext(b))

 # assign temp edge variables
 # the [0] is the edge element
 p = b[0].next
 q = a[0].next
 r = beta[0].next
 s = alpha[0].next

 # reassign the next values
 a[0].next = p
 b[0].next = q
 alpha[0].next = r
 beta[0].next = s

#####################
###    Delete     ###
#####################
def DeleteEdge(e):
 Splice(e, Oprev(e))
 Splice(Sym(e), Oprev(Sym(e)))

##################################################
###########  Orientation Tests    ################
##################################################

###### Right Of ########
def RightOf(x, e):
 return CCW(x, e[0].dest, e[0].org)

###### Left OF ########
def LeftOf(x, e):
 return CCW(x, e[0].org, e[0].dest) 

###### Counter Clockwise ########
# takes three points as tuples
def CCW(a, b, c):
 return True if (orient2d(a,b,c) > 0) return False

###### In Circle ########
# takes four points as tuples
def InCircle(a, b, c, d):
 return True if (incircle(a, b, c, d) > 0) return False

###### In Circle ########
def Valid(e, base):
 return CCW(e[0].dest, base[0].dest, base[0].org)


###############################################
###########  File Handling     ################
###############################################

def parsefile(filename):
 # Read the file and header
 f = open(filename, "r")
 header = f.readline()
 print header

 # Parse the header
 head = re.split('  ', header)
 rotVert = int(head[0])

 # Make an array that is (rotber of Vertices x 3)
 vertices = np.empty([rotVert, 3], dtype = float)

 # fill the array
 for l in range(0,rotVert): 
  line = re.split('  ', f.readline().strip('\n'))
  vertices[l,:] = map(float,line)

 f.close()

 return vertices


################################
### Main Arguments Statement ###
################################

def main(argv):

 print 'Read Node File v 1.0'
 print 'press -h for help'

 filename = 'test/4.node.txt'

 try: 
  opts, args = getopt.getopt(argv,"f:",["file="])

 except getopt.GetoptError:
  print 'readnode.py -f <file>'
  sys.exit(2)

 for opt, arg in opts:
  if opt == '-h':
   print 'enter the path of the node file to read'
 
  elif opt in ("-f","--file"):
   if isinstance(str(arg),str):
    filename = arg

  else:
   print 'File not valid'
   sys.exit()

 vertices = parsefile(filename)
 print filename



if __name__ == "__main__":
  main(sys.argv[1:])


