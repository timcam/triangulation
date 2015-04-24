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

 def next(self):
  return self.e[self.rot].next

 def current(self):
  return self.e[self.rot]


###############################
###    Edge Class        ###
################################
class Edge:
 def __init__(self):
  #self.id   = reference
  self.next  = [Edge]
  self.org   = [None, None]
  self.dest  = [0, 0]
  self.rot   = 0

#########################
###    MakeEdge       ###
#########################
def makeEdge():
 a = QuadEdge()

 #Set the points to infinity
 a.e[0].next = a.e[3]
 a.e[1].next = a.e[2]
 a.e[2].next = a.e[1]
 a.e[3].next = a.e[0]

 a.e[0].rot = 0
 a.e[1].rot = 1
 a.e[2].rot = 2
 a.e[3].rot = 3

 return a

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