/** \brief lets you draw a matrix and its component in maya viewport
*/
/**
* @author Marco Giordano
* @date  02/11/2013
* @version latest version : V1
* @version changeload versions : \n
*			V1 : \n
*				- initial release \n		
*			V1.5 : \n
*				- Added drawing text attributes \n
*
*
* node name : MG_matrixGL.
* 
* details : This node lets you draw a matrix and its component in maya viewport,
*			usefull when you need to debug transformations , just plug a matrix
*			in the inputMatrix attribute ,if you have refresh problem , connect 
*			something to the fake output attributr
*			
* example create node : (MEL) createNode MG_matrixGL.
*
* 
*		  
* 
*/

#ifndef MG_matrixGL_H
#define MG_matrixGL_H



#include <maya/MTypeId.h>
#include <maya/MPxLocatorNode.h>
#include <mayaOpenGL.h>



class MG_matrixGL : public MPxLocatorNode
{
public:

	virtual MStatus		compute( const MPlug& plug, MDataBlock& data );

    virtual void draw( M3dView&,
						const MDagPath&,
						M3dView::DisplayStyle,
						M3dView::DisplayStatus);

    virtual bool	isBounded() const;

	static  void*		creator();
	static  MStatus		initialize();


public:
	/**
	* The node id
	*/
	static	MTypeId		typeId;
	/**
	* The X component of the upVec used to draw the arrows
	*/
  	static MObject upVecX ;
	/**
	* The Y component of the upVec used to draw the arrows
	*/
	static MObject upVecY ;
	/**
	* The Z component of the upVec used to draw the arrows
	*/
	static MObject upVecZ ;
	/**
	* The  upVec used to draw the arrows
	*/
	static MObject upVec ;
	/**
	* This attribute sets the size of the ball showing the point
	*/
	static MObject ballSize ;
	/**
	* This attribute is used to force the recompute
	*/
	static MObject fakeOut ;
	/**
	* This attribute holds the matrix that has to be drawn
	*/
	static MObject inputMatrix ;
	/**
	* This attribute sets whether or not to draw the arrows
	*/
	static MObject drawIt;
	/**
	* This attribute sets the arrow size
	*/
	static MObject arrowSize;
	/**
	* This attribute sets if to draw the debug text or not
	*/
	static MObject drawText;
	/**
	* This attribute sets if to draw the debug text relative to the vectors , works only if drawText is on
	*/
	static MObject drawTextVec;

	/**
	* This attribute sets if to draw the debug text relative to the position , works only if drawText is on
	*/
	static MObject drawTextPos;

	


};

#endif
