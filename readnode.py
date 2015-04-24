import sys, getopt, math, re, csv
import numpy as np
from array import array

#################################
###    QuadEdge Class         ###
################################
class QuadEdge:
 def __init__(self):
  self.rot = 0
  self.e = [Edge(),Edge(),Edge(),Edge()]
  self.curr = self.e[self.rot]
  # self.next = self.e[self.rot].next
  # self.org  = self.e[self.rot].org

 def dest(self):
  return self.curr.dest

 def org(self):
  return self.curr.org
 
 def next(self):
  return self.curr.next

 def Rot(self):
  if (self.rot < 3):
   self.rot += 1 
  else:
   self.rot = 0

 def invRot(self):
  if (self.rot > 0): 
   self.rot -= 1 
  else:
   self.rot = 3

 def Sym(self):
  if (self.rot < 2):
   self.rot += 2 
  else:
   self.rot -= 2

 def setOrg(self, vertex):
  self.e[self.rot].org = vertex;

 def setDest(self, vertex):
  self.e[self.rot].dest = vertex;


###############################
###    Edge Class        ###
################################
class Edge:
 def __init__(self):
  #self.id   = reference
  self.next  = Edge
  self.org   = [None, None]
  self.dest  = [None, None]
  self.rot   = 0

#########################
###    MakeEdge       ###
#########################
def makeEdge():
 a = QuadEdge()

 #Set the points to infinity
 a.e[0].next = a.e[0]
 a.e[1].next = a.e[3]
 a.e[2].next = a.e[2]
 a.e[3].next = a.e[1]

 a.e[0].rot = 0
 a.e[1].rot = 1
 a.e[2].rot = 2
 a.e[3].rot = 3

 return a

#####################
###    Connect    ###
#####################
def Connect(a, b):
 e = makeEdge()
 e.setOrg(a.dest())
 e.setDest(b.org())
 # Splice(e, a.Lnext)


##################
### Run Tests  ###
##################
def runtests():
 b = makeEdge()
 return b









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

 runtests()



if __name__ == "__main__":
  main(sys.argv[1:])