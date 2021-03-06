#include <stdlib.h>
#include <iostream.h>
#include "Basic.H"
#include "quadedge.H"
#include "stuff.H"

////////////////////////////////////////////////////////////////////////
// This code is a modified version of the Delaunay triangulator
// written by Dani Lischinski
// in Graphics Gems IV
////////////////////////////////////////////////////////////////////////


/*********************** Basic Topological Operators ************************/

Edge* MakeEdge()
{
	QuadEdge *ql = new QuadEdge;
	return ql->e;
}

void Splice(Edge* a, Edge* b)
// This operator affects the two edge rings around the origins of a and b,
// and, independently, the two edge rings around the left faces of a and b.
// In each case, (i) if the two rings are distinct, Splice will combine
// them into one; (ii) if the two are the same ring, Splice will break it
// into two separate pieces. 
// Thus, Splice can be used both to attach the two edges together, and
// to break them apart. See Guibas and Stolfi (1985) p.96 for more details
// and illustrations.
{
	Edge* alpha = a->Onext()->Rot();
	Edge* beta  = b->Onext()->Rot();

	Edge* t1 = b->Onext();
	Edge* t2 = a->Onext();
	Edge* t3 = beta->Onext();
	Edge* t4 = alpha->Onext();

	a->next = t1;
	b->next = t2;
	alpha->next = t3;
	beta->next = t4;
}

void DeleteEdge(Edge* e)
{
	Splice(e, e->Oprev());
	Splice(e->Sym(), e->Sym()->Oprev());
	delete e->Qedge();
}

/************* Topological Operations for Delaunay Diagrams *****************/

void Subdivision::init(const Point2d& a, const Point2d& b,
		       const Point2d& c, const Point2d& d)
// Initialize a subdivision to the rectangle defined by the points a, b, c, d.
{
	Point2d *da, *db, *dc, *dd;
	da = new Point2d(a), db = new Point2d(b);
	dc = new Point2d(c), dd = new Point2d(d);

	Edge* ea = MakeEdge();
	ea->EndPoints(da, db);
	Edge* eb = MakeEdge();
	Splice(ea->Sym(), eb);
	eb->EndPoints(db, dc);
	Edge* ec = MakeEdge();
	Splice(eb->Sym(), ec);
	ec->EndPoints(dc, dd);
	Edge *ed = MakeEdge();
	Splice(ec->Sym(), ed);
	ed->EndPoints(dd, da);
	Splice(ed->Sym(), ea);
	startingEdge = ea;

	Edge *diag = MakeEdge();
	Splice(ed->Sym(),diag);
	Splice(eb->Sym(),diag->Sym());
	diag->EndPoints(da,dc);

	first_face = NULL;

	Triangle *f1 = make_face(ea->Sym());
	Triangle *f2 = make_face(ec->Sym());
}

Edge* Connect(Edge* a, Edge* b)
// Add a new edge e connecting the destination of a to the
// origin of b, in such a way that all three have the same
// left face after the connection is complete.
// Additionally, the data pointers of the new edge are set.
{
	Edge* e = MakeEdge();
	Splice(e, a->Lnext());
	Splice(e->Sym(), b);
	e->EndPoints(a->Dest(), b->Org());

	return e;
}

// These two variables track what faces InsertSite would like to recycle.
// And, yes, this is rather loathsome.
//
// Faces are recycled to optimize heap operations, so that we can recycle
// and update heap entries instead of deleting and then inserting.
// It also saves on destruction and construction of Triangles, but that's
// a much smaller cost.
static Triangle *recycle1 = NULL;
static Triangle *recycle2 = NULL;


void Subdivision::rebuild_face(Edge *e)
{
    Triangle *f;
    if( recycle1 ) {
	f = recycle1;
	f->reanchor(e);
	f->attach_face();
	recycle1 = NULL;
    } else if( recycle2 ) {
	f = recycle2;
	f->reanchor(e);
	f->attach_face();
	recycle2 = NULL;
    } else
	f = make_face(e);
	    // this call creates a new Triangle with null heap index,
	    // among other things
}


void Swap(Edge* e)
// Essentially turns edge e counterclockwise inside its enclosing
// quadrilateral. The data pointers are modified accordingly.
{
    Triangle *f1 = e->Lface();
    Triangle *f2 = e->Sym()->Lface();

	Edge* a = e->Oprev();
	Edge* b = e->Sym()->Oprev();
	Splice(e, a);
	Splice(e->Sym(), b);
	Splice(e, a->Lnext());
	Splice(e->Sym(), b->Lnext());
	e->EndPoints(a->Dest(), b->Dest());

    f1->reanchor(e);
    f2->reanchor(e->Sym());
    f1->attach_face();
    f2->attach_face();
}

/*************** Geometric Predicates for Delaunay Diagrams *****************/

int InCircle(const Point2d& a, const Point2d& b,
			 const Point2d& c, const Point2d& d)
// Returns TRUE if the point d is inside the circle defined by the
// points a, b, c. See Guibas and Stolfi (1985) p.107.
{
	return (a.x*a.x + a.y*a.y) * TriArea(b, c, d) -
	       (b.x*b.x + b.y*b.y) * TriArea(a, c, d) +
	       (c.x*c.x + c.y*c.y) * TriArea(a, b, d) -
	       (d.x*d.x + d.y*d.y) * TriArea(a, b, c) > 0;
}

int ccw(const Point2d& a, const Point2d& b, const Point2d& c)
// Returns TRUE if the points a, b, c are in a counterclockwise order
{
	return (TriArea(a, b, c) > 0);
}

int RightOf(const Point2d& x, Edge* e)
{
	return ccw(x, e->Dest2d(), e->Org2d());
}

int LeftOf(const Point2d& x, Edge* e)
{
	return ccw(x, e->Org2d(), e->Dest2d());
}

int Edge::CcwPerim()
{
	return !RightOf(Oprev()->Dest2d(), this);
}

int OnEdge(const Point2d& x, Edge* e)
// A predicate that determines if the point x is on the edge e.
// The point is considered on if it is in the EPS-neighborhood
// of the edge.
{
	Real t1, t2, t3;
	t1 = (x - e->Org2d()).norm();
	t2 = (x - e->Dest2d()).norm();
	if (t1 < EPS || t2 < EPS)
	    return TRUE;
	t3 = (e->Org2d() - e->Dest2d()).norm();
	if (t1 > t3 || t2 > t3)
	    return FALSE;
	Line line(e->Org2d(), e->Dest2d());
	return (fabs(line.eval(x)) < EPS);
}

/************* An Incremental Algorithm for the Construction of *************/
/************************ Delaunay Diagrams *********************************/

Edge *Subdivision::Locate(const Point2d& x, Edge *hintedge)
// Returns an edge e, s.t. the triangle to the left of e is interior to the
// subdivision and either x is on e (inclusive of endpoints) or x lies in the
// interior of the triangle to the left of e.
// The search starts from either hintedge, if it is not NULL, else
// startingEdge, and proceeds in the general direction of x.
//
// Algorithm is a variant of Green and Sibson's walking method for
// point location, as described by Guibas and Stolfi (ACM Trans. on Graphics,
// Apr. 1985, p.121), but modified in three ways:
//	* Randomness added to avoid infinite loops.
//	* Supports queries on perimeter of subdivision,
//	  provided perimeter is convex.
//	* Uses two area computations per step, not three.
{
    Edge* e = hintedge ? hintedge : startingEdge, *eo, *ed;
    Real t, to, td;

    t = TriArea(x, e->Dest2d(), e->Org2d());
    if (t>0) {			// x is to the right of edge e
	t = -t;
	e = e->Sym();
    }

    // x is on e or to the left of e

    // edges e, eo, ed point upward in the diagram below:
    //
    //         /|
    //     ed / |
    //       /  |
    //      /   |
    //     /    |
    //     \    | e
    //      \   |
    //       \  |
    //     eo \ |
    //         \|

    while (TRUE) {
	eo = e->Onext();
	to = TriArea(x, eo->Dest2d(), eo->Org2d());
	ed = e->Dprev();
	td = TriArea(x, ed->Dest2d(), ed->Org2d());
	if (td>0)			// x is below ed
	    if (to>0 || to==0 && t==0) {// x is interior, or origin endpoint
		startingEdge = e;
		return e;
	    }
	    else {			// x is below ed, below eo
		t = to;
		e = eo;
	    }
	else				// x is on or above ed
	    if (to>0)			// x is above eo
		if (td==0 && t==0) {	// x is destination endpoint
		    startingEdge = e;
		    return e;
		}
		else {			// x is on or above ed and above eo
		    t = td;
		    e = ed;
		}
	    else			// x is on or below eo
		if (t==0 && !LeftOf(eo->Dest2d(), e))
					// x on e but subdiv. is to right
		    e = e->Sym();
		else if (random()&1) {	// x is on or above ed and
		    t = to;		// on or below eo; step randomly
		    e = eo;
		}
		else {
		    t = td;
		    e = ed;
		}
    }
}

Edge *Subdivision::Spoke(const Point2d& x, Triangle *tri)
// Inserts a new point x into triangle tri of a subdivision and
// adds "spokes" connecting the point to the vertices of the surrounding
// polygon.  Returns a pointer to one of the inward-pointing spokes.
//
// --- Tri can be NULL
{
    // Point x is inside the triangle tri or on its boundary.
    // To make sure boundary cases are handled properly, we call Locate.
    Edge* e = Locate(x, tri?tri->get_anchor():NULL);

    if ( (x == e->Org2d()) || (x == e->Dest2d()) ) {
	// point is already in the mesh
	cout << "already in mesh: (" << x.x << "," << x.y << ")" << endl;
	assert(0);
    }

    Edge *pedge = 0;
    if (OnEdge(x, e)) {
	if (e->CcwPerim()) {
	    // if point x lies on a perimeter edge then add spokes
	    // before deleting it
	    recycle1 = e->Lface();
	    recycle1->dont_anchor(e);
	    pedge = e;		// save pointer to old perimeter edge
	}
	else {
	    // point is on an edge -- delete 2 faces
	    // unless the edge is a border edge and has no outer face
	    recycle1 = e->Lface();
	    recycle1->dont_anchor(e);
	    recycle2 = e->Sym()->Lface();
	    recycle2->dont_anchor(e->Sym());
	    e = e->Oprev();
	    DeleteEdge(e->Onext());
	}
    } else {
	// point is in triangle, delete that face only
	recycle1 = e->Lface();
	recycle1->dont_anchor(e);
    }

    // Add spokes: connect the new point to the vertices of the containing
    // triangle (or quadrilateral, if the new point fell on an
    // existing edge.)
    Edge* base = MakeEdge();
    base->EndPoints(e->Org(), new Point2d(x));
    Splice(base, e);
    startingEdge = base;
    do {
	base = Connect(e, base->Sym());
	e = base->Oprev();
    } while (e->Lnext() != startingEdge);
    if (pedge)		// delete old perimeter edge and mark new ones
	DeleteEdge(pedge);

    // Update all the faces in our new spoked polygon.
    // If point x on perimeter, then don't add an exterior face
    base = pedge ? startingEdge->Rprev() : startingEdge->Sym();
    do {
	rebuild_face(base);
	base = base->Onext();
    } while( base!=startingEdge->Sym() );

    return startingEdge;
}

int Subdivision::is_interior(Edge *e)
//
// Tests whether e is an interior edge.
// 
// WARNING: This topological test will not work if the boundary is
//          a triangle.  This is not a problem in scape; the boundary is
//          always a rectangle.  But if you try to adapt this code, please
//          keep this in mind.
{
    return (e->Lnext()->Lnext()->Lnext() == e &&
            e->Rnext()->Rnext()->Rnext() == e );
}


Edge *Subdivision::InsertSite(const Point2d& x, Triangle *tri)
// Inserts a new point x into triangle tri of a subdivision representing
// a Delaunay triangulation, and fixes the affected edges so that the result
// is still a Delaunay triangulation. This is based on the
// pseudocode from Guibas and Stolfi (1985) p.120, with slight
// modifications and a bug fix.
// Returns a pointer to an outward-pointing spoke.
//
// --- Tri can be NULL
{
    Edge *startspoke = Spoke(x, tri);

    //
    // Reorient the spoke so that it points away from the insertion site.
    // This is what our caller expects to get back, and I prefer to think
    // of the spokes this way.
    startspoke = startspoke->Sym();
    Edge *s = startspoke;

    do {
      Edge *e = s->Lnext();
      Edge *t = e->Oprev();

      if( is_interior(e) && InCircle(e->Org2d(), t->Dest2d(), e->Dest2d(), x))
          Swap(e);
      else {
          s = s->Onext();
          if( s == startspoke )
              break;
      }
    } while( TRUE );

    return startspoke;
}


/*****************************************************************************/

static unsigned int timestamp = 0;

void Subdivision::OverEdges(edge_callback f,void *closure)
{
    if (++timestamp == 0) 
	timestamp = 1;
    startingEdge->OverEdges(timestamp,f,closure);
}

void Edge::OverEdges(unsigned int stamp,edge_callback f,void *closure)
{
    if( Qedge()->TimeStamp(stamp) ) {
	(*f)(this,closure);

	// Recurse to neighbors
	Onext()->OverEdges(stamp,f,closure);
	Oprev()->OverEdges(stamp,f,closure);
	Dnext()->OverEdges(stamp,f,closure);
	Dprev()->OverEdges(stamp,f,closure);
    }
}


void Subdivision::OverFaces(face_callback f,void *closure)
{
    Triangle *t = first_face;

    while( t ) {
	(*f)(t,closure);
	t = t->next;
    }
}


UpdateRegion::UpdateRegion(Edge *e)
{
    start = e;
}

Triangle *UpdateRegion::first()
{
    current = start;
    if (current->Lface()) return current->Lface();
	// in case p is on perimeter and one of faces is null
    current = current->Onext();
    return current->Lface();
	// no need to check, can't have two null faces
}

Triangle *UpdateRegion::next()
{
    current = current->Onext();
    if (current==start) return NULL;
    if (current->Lface()) return current->Lface();
	// in case p is on perimeter and one of faces is null
    current = current->Onext();
    if (current==start) return NULL;
    return current->Lface();
	// no need to check, can't have two null faces
}

void Triangle::attach_face()
{
    anchor->set_Lface(this);
    anchor->Lnext()->set_Lface(this);
    anchor->Lprev()->set_Lface(this);
}

void Triangle::dont_anchor(Edge *e) {
    if( anchor == e ) {
	if( e->Lnext()->Lface() == this )
	    anchor = e->Lnext();
	else if( e->Lprev()->Lface() == this )
	    anchor = e->Lprev();
	else assert( NULL );
    }
}

void intersect(const Line &k, const Line &l, Point2d &p)
// intersect: point of intersection p of two lines k, l
{
    Real den = k.a*l.b-k.b*l.a;
    assert(den!=0);
    p.x = (k.b*l.c-k.c*l.b)/den;
    p.y = (k.c*l.a-k.a*l.c)/den;
}


// routines to compute the number of edges, vertices, and faces

static int vert_degree(Edge *e) {
    // returns number of triangles adjacent to vertex at e->Org
    // (counts only interior faces, not exterior faces)
    Edge *e0 = e;
    int deg = 0;
    do {
	deg += e->Lface() != 0;
	e = e->Onext();
    } while (e!=e0);
    return deg;
}

static int edge_degree(Edge *e) {
    // returns number of triangles adjacent to edge e
    return (e->Lface() != 0) + (e->Sym()->Lface() != 0);
}

static double dv, de;
static int df;

static void count_vef(Triangle *tri, void *) {
    Edge *e1 = tri->get_anchor();
    Edge *e2 = e1->Lnext();
    Edge *e3 = e2->Lnext();
    dv += 1./vert_degree(e1) + 1./vert_degree(e2) + 1./vert_degree(e3);
    de += 1./edge_degree(e1) + 1./edge_degree(e2) + 1./edge_degree(e3);
    df++;
}

void Subdivision::vef(int &nv, int &ne, int &nf) {
    // returns number of vertices, edges, and faces in subdivision
    dv = de = 0;
    df = 0;
    OverFaces(count_vef, 0);
    nv = (int)(dv+.5);		// round, in case of roundoff error
    ne = (int)(de+.5);
    nf = df;
}
