import sys, getopt, math, re, csv
import numpy as np
from array import array
from predicates import orient2d, incircle

#set global variables
quadID = 0
edgeID = 0
quadlist = []

#####################################################
########   Delauney Trianulation       ##############
#####################################################
def Delaunay(s):
 #takes a list of tuples as points

 #Base case with two points
 if len(s) == 2:
  a = MakeEdge()
  #select edge object
  a[0].org  = s[0]
  a[0].dest = s[1]

  print 'returning from base 2'
  return (a, Sym(a))
 
 #base case with three (3) points
 elif (len(s) == 3):
  a = MakeEdge(); b = MakeEdge()
  Splice(Sym(a),b)

  a[0].org = s[0]; a[0].dest = s[1]
  b[0].org = s[1]; b[0].dest = s[2]

  if CCW(s[0],s[1],s[2]):
   c = Connect(b,a)
   print 'returning from base 3 case 1'
   return (a, Sym(b))

  elif CCW(s[0],s[2],s[1]):
   c = Connect(b,a)
   print 'returning from base 3 case 2'
   return (Sym(c), c)

  else:
   print 'returning from base 3 case 3'
   return (a, Sym(b))

  #case with 4 or more points
  #split the set again and then zip together
 else:
  left, right = HalfSet(s)

  ldo, ldi = Delaunay(left);
  rdi, rdo = Delaunay(right);

  print 'ldo.org:', ldo[0].org, 'ldo.dest:', ldo[0].dest
  print 'ldi.org:', ldi[0].org, 'ldi.dest:', ldi[0].dest
  print 'rdi.org:', rdi[0].org, 'rdi.dest:', rdi[0].dest
  print 'rdo.org:', rdo[0].org, 'rdo.dest:', rdo[0].dest

  while True:
   if LeftOf(rdi[0].org, ldi):
    ldi = Lnext(ldi)
   elif RightOf(ldi[0].org, rdi):
    rdi = Rprev(rdi)
   else:
     print 'break'
     break

  #create the base edge  
  basel = Connect(Sym(rdi), ldi)
  ldi[0].org
  print 'Connect ldi.org and ldo.org:', ldi[0].org, ldo[0].org
  if ldi[0].org == ldo[0].org:
   ldo = Sym(basel) 
  if rdi[0].org == rdo[0].org:
   rdo = basel

  #this is the merge loop
  while True:
   lcand = Onext(Sym(basel))
   print 'lcand.org: ' + str(lcand[0].org)
   print 'lcand.dest: '+ str(lcand[0].dest)
   if Valid(lcand, basel):
    while InCircle(basel[0].dest, basel[0].org, lcand[0].dest, Onext(lcand)[0].dest):
     t = Onext(lcand); DeleteEdge(lcand); lcand = t

   # symmetrically locate first R point to hit and delete R edges
   rcand = Oprev(basel)
   if Valid(rcand, basel):
    while InCircle(basel[0].dest, basel[0].org, lcand[0].dest, Oprev(lcand)[0].dest):
     t = Oprev(rcand); DeleteEdge(rcand); rcand = t

   # if both lcand and rcand are invalid then basel L is tanget
   if not Valid(lcand, basel) and not Valid(rcand, basel):
    break

   # if both are valid then choose the right edge with incircle
   if not Valid(lcand, basel) or (Valid(rcand, basel) and InCircle(lcand[0].dest, lcand[0].org, rcand[0].org, rcand[0].dest)):
    # add cross edge basel from rcand to basel.dest
    basel = Connect(rcand, Sym(basel))
   else:
    basel = Connect(Sym(basel), Sym(lcand))

  return (ldo, rdo)


#map(tuple,x)



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
  q.e[a.rot-2].org  = a.dest
  q.e[a.rot-2].dest = a.org
  return (q.e[a.rot-2], q)
 else:
  q.e[a.rot+2].org  = a.dest
  q.e[a.rot+2].dest = a.org
  return (q.e[a.rot+2], q)

###### Onext ########
def Onext(t):
 a = t[0]
 return (a.next, quadlist[a.next.qid])

###### Lnext ########
def Lnext(t):
 a = Rot( Onext( invRot(t)))
 a[0].org = t[0].dest
 return a

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
 a = Onext( Sym(t))
 a[0].org = t[0].dest
 print 'Rprev: a.org', a[0].org, 'a.dest', a[0].dest 
 return a

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
 e = MakeEdge()

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
#takes a tuple x and quadedge e
def RightOf(x, e):
 print 'RightOf: x:', x, 'e.dest:', e[0].dest, 'e.org:', e[0].org
 return CCW(x, e[0].dest, e[0].org)

###### Left OF ########
#takes a tuple x and quadedge e
def LeftOf(x, e):
 print 'LeftOf: x:', x, 'e.org:', e[0].org, 'e.dest:', e[0].dest
 return CCW(x, e[0].org, e[0].dest) 

###### Counter Clockwise ########
# takes three points as tuples
def CCW(a, b, c):
# a = tuple(a); b = tuple(b); c = tuple(c);

 print 'CCW: a:', a, 'b:', b,'c:', c 
 return True if (orient2d(a,b,c) > 0) else False

###### In Circle ########
# takes four points as tuples
def InCircle(a, b, c, d):
 #a = tuple(a); b = tuple(b); c = tuple(c); d = tuple(d)
 return True if (incircle(a, b, c, d) > 0) else False

###### In Circle ########
def Valid(e, base):
 return CCW(e[0].dest, base[0].dest, base[0].org)


###############################################
###########  Splitting Sets     ################
###############################################

#######################
###    quickselect  ###
#######################
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

 

 # # for odd number of points split an even set and add right side
 # if ((len(s) % 2) > 0):

 #  left, right = np.vsplit(s[0:-1],2)
 #  #add the extra to right side
 #  right = np.vstack([right,x[-1,:]])

 #  return left, right 

 # else:
  left  = s[:len(s)/2]
  right = s[len(s)/2:]
  #left, right = np.vsplit(s,2)
  return left, right

 #median = quickSelect(s,(len(s) // 2))


###############################################
###########  File Handling     ################
###############################################

def ParseFile(filename):
 # Read the file and header
 f = open(filename, "r")
 header = f.readline()
 print header

 # Parse the header
 head = re.split('  ', header)
 numVert = int(head[0])

 # Make an array that is (rotber of Vertices x 3)
 #v = np.zeros([numVert,2], dtype = float)
 v = []

 # fill the array
 for i in xrange(numVert): 

  l = f.readline().strip('\n')
  l = re.split(' ',l)
  l = filter(lambda a: a != '', l)
  line  = map(float, l)
  #splits by the spaces and converts to floats 
  # line = map(float, re.split('  ', f.readline().strip('\n')))
  #drops the vertex numbe
  #v[i] = line[-2:]
  v.append(tuple(line[-2:]))

 # sort the list
 #q = v.tolist()
 #q.sort()
 v.sort()
 #v = np.array(q)

 print v

 f.close()

 return v



 #when I need a tuple of the vertex
 #tuple(vertices[1,:].tolist())


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

 vertices = ParseFile(filename)
 print filename



if __name__ == "__main__":
  main(sys.argv[1:])


