import sys, getopt, math, re, csv
import numpy as np
from array import array
from predicates import orient2d, incircle

#set global variables
quadID = 0
edgeID = 0
qlist = []
#edgelist = []

#####################################################
########   Delauney Trianulation       ##############
#####################################################
def Delaunay(s):
 #takes a list of tuples as points

 #Base case with two points
 if len(s) == 2:
  a = MakeEdge()
  #select edge object
  a.setOrg(s[0])
  a.setDest(s[1])

  print 'returning from base 2'
  return (a, a.Sym)

 #base case with three (3) points
 elif (len(s) == 3):
  a = MakeEdge(); b = MakeEdge()
  Splice(a.Sym, b)

  a.setOrg(s[0]); a.setDest(s[1])
  b.setOrg(s[1]); b.setDest(s[2])

  if CCW(s[0],s[1],s[2]):
   print 'cond A'
   c = Connect(b,a)
   print 'returning from base 3 case 1'
   return (a, b.Sym)

  elif CCW(s[0],s[2],s[1]):
   print 'cond B'
   c = Connect(b,a)
   print 'returning from base 3 case 2'
   return (c.Sym, c)

  else:
   print 'returning from base 3 case 3'
   return (a, b.Sym)

  #case with 4 or more points
  #split the set again and then zip together
 else:
  left, right = HalfSet(s)

  ldo, ldi = Delaunay(left);
  rdi, rdo = Delaunay(right);

  print 'ldo.org:', ldo.Org, 'ldo.dest:', ldo.Dest
  print 'ldi.org:', ldi.Org, 'ldi.dest:', ldi.Dest
  print 'rdi.org:', rdi.Org, 'rdi.dest:', rdi.Dest
  print 'rdo.org:', rdo.Org, 'rdo.dest:', rdo.Dest

  while True:
   if LeftOf(rdi.Org, ldi):
    ldi = ldi.Lnext
    print 'New ldi(id):', ldi.qid, 'ldi.Org:', ldi.Org, 'ldi.Dest:', ldi.Dest

   elif RightOf(ldi.Org, rdi):
    rdi = rdi.Rprev
    print 'New rdi(id):', rdi.qid, 'rdi.Org:', rdi.Org, 'rdi.Dest:', rdi.Dest

   else:
    print 'break'
    break

  #create the base edge  
  print 'Connecting rdi.Sym and ldi:', rdi.Sym.Org, ldi.Org
  basel = Connect(rdi.Sym, ldi)


  if ldi.Org == ldo.Org:
   ldo = basel.Sym
  if rdi.Org == rdo.Org:
   rdo = basel

  #this is the merge loop
  while True:
   lcand = basel.Sym.Onext

   print 'lcand.org:',  lcand.Org
   print 'lcand.dest:', lcand.Dest

   if Valid(lcand, basel):
    while InCircle(basel.Dest, basel.Org, lcand.Dest, lcand.Onext.Dest):
     print 'Resetting lcand to lcand.Onext (org) (dest):', lcand.Onext.Org, lcand.Onext.Dest
     t = lcand.Onext
     DeleteEdge(lcand)
     lcand = t

   # symmetrically locate first R point to hit and delete R edges
   rcand = basel.Oprev
   if Valid(rcand, basel):
    while InCircle(basel.Dest, basel.Org, rcand.Dest, rcand.Oprev.Dest):
     print 'Resetting rcand to rcand.OPrev (org) (dest):', rcand.Oprev.Org, rcand.Oprev.Dest
     t = rcand.Oprev
     DeleteEdge(rcand)
     rcand = t

   # if both lcand and rcand are invalid then basel L is tanget
   if (not Valid(lcand, basel)) and (not Valid(rcand, basel)):
    print 'Both lcand and rcand are invalid, exiting loop'
    break

   # if both are valid then choose the right edge with incircle
   if (not Valid(lcand, basel)) or (Valid(rcand, basel) and InCircle(lcand.Dest, lcand.Org, rcand.Org, rcand.Dest)):
    # add cross edge basel from rcand to basel.dest
    print 'Connecting rcand to basel.Sym'
    basel = Connect(rcand, basel.Sym)
   else:
    print 'Connecting basel.Sym to lcand.Sym'
    basel = Connect(basel.Sym, lcand.Sym)

  return (ldo, rdo)

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
  self.qid = quadID
  print 'Creating quadedge num:', quadID
  quadID += 1

  # add quadEdge to List for reference
  global quadlist
  qlist.append(self)

  #initialize list of edges
  self.e = [Handle(),Handle(),Handle(),Handle()]

  #initialize next
  self.next = [Handle, Handle, Handle, Handle]

  #initialize Org
  self.org = [(None, None), (None, None), (None, None), (None, None)]

  #set the orientations of each edge
  self.e[0].ort = 0
  self.e[1].ort = 1
  self.e[2].ort = 2
  self.e[3].ort = 3

  #Set the next pointers to infinity
  self.next[0] = self.e[0] #correct
  self.next[1] = self.e[3]
  self.next[2] = self.e[2]
  self.next[3] = self.e[1]

  # set the quadedge ID in each of the edges
  for i in xrange(3): 
   self.e[i].qid = self.qid


#############################
###    Edge Class        ###
#############################
class Handle:
 def __init__(self):
  #self.id   = reference
  self.ort = 0      # orientation in quadedge 
  self.qid = 0      # quadedge identification
  self.vis = False  #used for output searching

  # edge identification
  global edgeID
  self.id = edgeID  
  edgeID += 1

  # #added edge to edgelist
  # global edgelist
  # edgelist.append(self)

 #############################################
 #########  Edge Algebra Methods  ############
 #############################################
 @property
 def Org(self):
  return qlist[self.qid].org[self.ort]

 @property
 def Dest(self):
  return self.Sym.Org

 def setOrg(self, vertex):
  qlist[self.qid].org[self.ort] = vertex

 def setDest(self, vertex):
  self.Sym.setOrg(vertex)

 def setNext(self, edge):
  qlist[self.qid].next[self.ort] = edge

 ####### Rotate ########
 @property
 def Rot(self):
  #look up the parent quadedge and return the CCW edge
  if (self.ort < 3):
   return qlist[self.qid].e[self.ort+1]
  else:
   return qlist[self.qid].e[0]

 #### Inv Rotate ######
 @property
 def invRot(self):
  if (self.ort > 0):
   return qlist[self.qid].e[self.ort-1]
  else:
   return qlist[self.qid].e[3]

 ###### sym #########
 @property
 def Sym(self):
  if self.ort < 2 :
   return qlist[self.qid].e[self.ort +2]
  else:
   return qlist[self.qid].e[self.ort -2]

 ###### Onext ########
 @property
 def Onext(self):
  return qlist[self.qid].next[self.ort]

 ###### Lnext ########
 @property
 def Lnext(self):
  return self.invRot.Onext.Rot

 ###### Rnext ########
 @property
 def Rnext(self):
  return self.Rot.Onext.invRot

 ###### Dnext ########
 @property
 def Dnext(self):
  return self.Sym.Onext.Sym

 ###### Oprev ########
 @property
 def Oprev(self):
  return self.Rot.Onext.Rot

 ###### Lprev ########
 @property
 def Lprev(self):
  return self.Onext.Sym
 
 ###### Rprev ########
 @property
 def Rprev(self):
  return self.Sym.Onext

 ###### Dprev ########
 @property
 def Dprev(self):
  return self.invRot.Onext.invRot

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
 return a

#####################
###    Connect    ###
#####################
def Connect(a, b): 
 e = MakeEdge()

 e.setOrg(a.Dest)
 e.setDest(b.Org)

 print 'Connect: splicing e and a.Lnext: (org) (dest)', a.Lnext.Org, a.Lnext.Dest
 Splice(e, a.Lnext)
 print 'Connect: splicing e.Sym (org) (dest) and b: ', e.Sym.Org, a.Sym.Dest
 Splice(e.Sym, b)

 return e


#####################
###    Splice     ###
#####################
def Splice(a, b):
 #holders for edges
 alpha = a.Onext.Rot
 beta  = b.Onext.Rot

 # assign temp edge variables
 # the [0] is the edge element
 p = b.Onext
 q = a.Onext
 r = beta.Onext
 s = alpha.Onext

 # reassign the next values
 a.setNext = p
 b.setNext = q

 #reassign their 
 a.Onext.Rot.setNext = r
 b.Onext.Rot.setNext = s

#####################
###    Delete     ###
#####################
def DeleteEdge(e):
 Splice(e, e.Oprev)
 Splice(e.Sym, e.Sym.Oprev)

##################################################
###########  Orientation Tests    ################
##################################################

###### Right Of ########
#takes a tuple x and quadedge e
def RightOf(x, e):
 print 'RightOf: x:', x, 'e.Dest:', e.Dest, 'e.Org:', e.Org
 return CCW(x, e.Dest, e.Org)

###### Left OF ########
#takes a tuple x and quadedge e
def LeftOf(x, e):
 print 'LeftOf: x:', x, 'e.org:', e.Org, 'e.dest:', e.Dest
 return CCW(x, e.Org, e.Dest) 

###### Valid ########
def Valid(e, basel):
 return CCW(e.Dest, basel.Dest, basel.Org)

###### Counter Clockwise ########
# takes three points as tuples
def CCW(a, b, c):
 return True if (orient2d(a,b,c) > 0) else False

###### In Circle ########
# takes four points as tuples
def InCircle(a, b, c, d):
 return True if (incircle(a, b, c, d) > 0) else False

###############################################
###########  Splitting Sets     ################
###############################################

######    quickselect  ##########
#http://stackoverflow.com/questions/19258457/python-quickselect-function-finding-the-median
def QuickSelect(seq,k):
 k = len(seq) // 2
 # this part is the same as quick sort
 len_seq = len(seq)
 if len_seq < 2: return seq

 ipivot = len_seq // 2
 pivot = seq[ipivot]

 smallerList = [x for i,x in enumerate(seq) if x <= pivot and  i != ipivot]
 largerList = [x for i,x in enumerate(seq) if x > pivot and  i != ipivot]

 # here starts the different part
 m = len(smallerList)
 if k == m:
  return pivot
 elif k < m:
  return quickSelect(smallerList, k)
 else:
  return quickSelect(largerList, k-m-1)

#######################
###    halfSet  ###
#######################
def HalfSet(s):
 left  = s[:len(s)/2]
 right = s[len(s)/2:]

 # a = np.array(s)
 # m = np.median(a[:,0])
 # x = a[:,0].tolist()
 # i = x.index(m)

 # left = s[:i+1]
 # right = s[i+1:]
 print len(left), len(right)
 return left, right


###############################################
#####  Triangles from QuadEdge    #############
###############################################
def WriteFile(l):
 triangles = []
 count = 0

 count, triangles = MakeFaces(l, count, triangles)

 return triangles

def Report(l):
  print 'l.Org', l.Org
  print 'l.Dest', l.Dest
  print 'l.Onext.Dest', l.Onext.Dest
  print 'l.Lnext.Dest', l.Lnext.Dest
  print 'l.Rprev.Dest', l.Rprev.Dest
  print 'l.Oprev.Dest', l.Oprev.Dest


def MakeFaces(a, count, triangles):
 tri = []
 # go arount the triangle
 b = a.Lnext; c = b.Lnext
 print 'a.id:', a.id, 'b.id', b.id, 'c.id', c.id
 #print 'a.Org:', a.Org, 'b.Org', b.Org, 'c.Org', c.Org

 if edgelist[a.id][1]:
  #already visited, base case
  print 'in loop base'
  return count, triangles

 # elif (b.Dest == a.Org): 
 #  #looping face, set visited 
 #  #edgelist[b.id][1] = True
 #  return count, triangles

 # elif (a.id == c.id):
 #  #another looping face
 #  edgelist[b.id][1] = True
 #  edgelist[c.id][1] = True
 #  return count, triangles

 else:

  #record the unique triangle
  tri.append(count)
  count += 1


  #record vertices
  tri.append(a.Org); tri.append(b.Org); tri.append(c.Org)
  print 
  'Recorded Triangle:', tri
  triangles.append(tuple(tri))

  # set edges in current triangle as visited
  edgelist[a.id][1] = True; edgelist[b.id][1] = True; edgelist[c.id][1] = True

  #recurse on each of the Sym edges
  print 'a.sym', a.Sym.id, 'b.sym', b.Sym.id, 'c.sym', c.Sym.id
  count, triangles = MakeFaces(a.Sym, count, triangles)
  count, triangles = MakeFaces(b.Sym, count, triangles)
  count, triangles = MakeFaces(c.Sym, count, triangles)

  return count, triangles



###############################################
###########  File Handling     ################
###############################################

def ParseFile(filename):
 # Read the file and header
 f = open(filename, "r")
 header = f.readline().strip('\n')
 print header

 # Parse the header
 head = re.split(' ', header)
 head = filter(lambda a: a != '', head)
 head = map(int,head)
 numVert = int(head[0])
 v = []

 # fill the array
 for i in xrange(numVert): 
  l = f.readline().strip('\n')
  l = re.split(' ',l)
  l = filter(lambda a: a != '', l)
  line  = map(float, l)
  v.append(tuple(line[-2:]))

 edgelist = []
 quadlist = []



 v.sort()
 print v
 f.close()
 return v


################################
### Main Arguments Statement ###
################################

def main(argv):

 print 'Read Node File v 1.0'
 print 'press -h for help'

 filename = 'test/4.node'

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

 vertices = ParseFile(filename)
 print filename



if __name__ == "__main__":
  main(sys.argv[1:])


