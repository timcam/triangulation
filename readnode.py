import sys, getopt, math, re, csv
import numpy as np
from array import array

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
  self.org   = [None, None]
  self.dest  = [None, None]
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
# returns eRot, q is unchanged
def Rot(a,q):
 if (a.rot < 3):
  return q.e[a.rot+1]
 else:
  return q.e[0]

#### Inv Rotate ######
#returns eRot-1, q is unchanged
def invRot(a,q):
 if (a.rot > 0):
  return q.e[a.rot-1]
 else:
  return q.e[3]

###### sym #########
#returns eSym, q is unchanged
def Sym(a,q):
 if (a.rot > 1):
  return q.e[a.rot-2]
 else:
  return q.e[a.rot+2]

###### Onext ########
#returns eOnext and qOnext
def Onext(a):
 return (a.next, quadlist[a.next.qid])

###### Lnext ########
#returns eLnext and qLnext
def Lnext(a,q):
 tmp = invRot(a,q)
 tmp, qtmp = Onext(tmp)
 return (Rot(tmp,qtmp), qtmp)

###### Rnext ########
#returns eRnext and qRnext
def Lnext(a,q):
 tmp = Rot(a,q)
 tmp, qtmp = Onext(tmp)
 return (Rot(tmp,qtmp), qtmp)

###### Dnext ########
#returns eRnext and qRnext
def Lnext(a,q):
 tmp = Sym(a,q)
 tmp, qtmp = Onext(tmp)
 return (Sym(tmp,qtmp), qtmp)


###### Oprev ########
#returns eOprev and qOprev
def Oprev(a,q):
 tmp = Rot(a,q) 
 tmp, qtmp = Onext(tmp)
 return (Rot(tmp,qtmp), qtmp)

###### Lprev ########
#returns eLprev and qLprev
def Lprev(a,q):
 tmp, qtmp = Onext(a)
 return (Sym(tmp,qtmp), qtmp)

###### Rprev ########
#returns eRprev and qRprev
def Rprev(a,q):
 tmp, qtmp = Sym(a,q)
 return (Onext(tmp), qtmp)

###### Dprev ########
#returns eDprev and qDprev
def Dprev(a,q):
 tmp = invRot(a,q)
 tmp, qtmp = Onext(tmp)
 return (invRot(tmp), qtmp)


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
 e.setOrg(a.dest())
 e.setDest(b.org())
 # Splice(e, a.Lnext)

#####################
###    Splice     ###
#####################




###################
### Parse File ###
###################
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

 parsefile(filename)

 #Set the global values first




if __name__ == "__main__":
  main(sys.argv[1:])


