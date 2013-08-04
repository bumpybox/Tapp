#ifndef mayaOpenGL_H
#define mayaOpenGL_H

#include <maya/MVector.h>
#include <maya/MPoint.h>
#include <gl/GL.h>
#include <maya/M3dView.h>
class mayaOpenGL {


public :
	void drawArrow ( const MVector vec = MVector(1,0,0) ,
			 const MVector upVec = MVector(0,1,0),
			 const double arrowSizeV = 1 ,  const 
			 MPoint startPointV = MPoint(0,0,0));

	void drawText(const MString &text,const double* color, const MPoint &position,M3dView &view);
	
	void drawSphere(const double r, const int lats, const int longs,const MVector position,const double* color);

	void drawLine  (MPoint p1 ,MPoint p2,const double* color1, const double* color2);

	void stressLine (MPoint p1 ,MPoint p2 , double stress1 , double stress2);
};

#endif