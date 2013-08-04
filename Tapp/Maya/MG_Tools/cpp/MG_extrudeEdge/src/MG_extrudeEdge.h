/** \brief lets create a loft nurbs out of a edge by using normals as direction
*/

/**
* @author Marco Giordano
* @date  03/13/2013
* @version latest version : V1
* @version changeload versions : \n
*			V1 : \n
*				- initial release \n				
*
*
* node name : MG_extrudeEdge.
* 
* details : This node lets you create a loft nurbs out of a mesh edge defined by vertex
*
*			
* example create node : (MEL) createNode MG_extrudeEdge.
*
*
*
*		  
* 
*/

#include <maya/MPxNode.h>
#include <maya/MTypeId.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MDagPath.h>
#include <maya/MPlug.h>
#include <maya/MPoint.h>
#include <maya/MVector.h>

class MG_extrudeEdge : public MPxNode 

{

   public:


      static void *creator();
      static MStatus initialize();
      virtual MStatus compute(const MPlug &plug, MDataBlock &data);
	  /**
		* The node id
		*/
      static MTypeId typeId;
      /**
		* This is the input mesh value 
		*/
      static MObject inputMesh;
	  /**
		* This is the size of the normals
		*/
      static MObject normalSize;
	  /**
		* This is vertex array used to create the loft
		*/
      static MObject vtxArray;
	  /**
		* This is the extruded surface as output 
		*/
      static MObject outSurface;
	  /**
		* This is the world matrix of the mesh used to multipy the normal
		*/
	  static MObject meshParentMatrix;
	  /**
		* This is the world matrix of the mesh used to multipy the normal
		*/
	  static MObject tiltMatrix;
	  	 /**
		* This is matrix is the matrix that defines the overall motion of the object , example if your are extruding a edge of the 
		* eyeLid the overal motion of the eyelid and sorrounding will come from the head so plug here the matrix that describe this overall
		* movement , during the test of the node what I did was placing a locator under the head control and pluggi the world matrix of this 
		* locator.
		* Then inside the node what happen is I multiply the normal for the inverse of the given matrix in order to restor the normal to 
		* initial position , then I perfomr the tilt and finally I multiply again for the counter matrix to puth the normal back to its right
		*position
		*/
	  static MObject counterMatrix;
	  /**
	  * This attribute sets whether to use or not the tilt matrix
	  */
	  static MObject useTiltMatrix;
	  /**
	  * This attribute sets whether to use or not the custom source
	  */
	  static MObject useCustomSource;
	  /**
	  * This attribute sets how to read the customSource attribute data, possible option : point or attribute
	  */
	  static MObject customSourceAs;
	  /**
	  * This is the X component of the customSource attribute
	  */
	  static MObject customSourceX;
	  /**
	 * This is the Y component of the customSource attribute
	  */
	  static MObject customSourceY;
	  /**
	  * This is the Z component of the customSource attribute
	  */
	  static MObject customSourceZ;
	  /**
	  * This attribute holds the custom source , values : -Point , if in point mode the normal of the vertex will be compute from this point to the vertex itself
	  *                                                   -Vector , If in vector mode the value will be used as normal of the verticies
	  */
	  static MObject customSource;

};

