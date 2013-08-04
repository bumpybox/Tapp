/** \brief lets you attach an object on a curve and slide it and give you different option to drive it
*/

/**
* @author Marco Giordano
* @date  2/15/2013
* @version latest version : V1
* @version changeload versions : \n
*			V1 : \n
*				- initial release \n				
*
*
* node name : MG_curvePoint.
* 
* details : This node lets you attach an object on a curve and slide it and 
*			give you different option to drive it
*			This node first of all lets you chose if the driving parameter has
*			to be intended as a U param or a length , this can be mostly usefull
*			when you have to stretch the curve and you want the object staying on the same length.
*			You also have two different ways to compute the normals :
*			1) Using the maya api , faster way but les accurate can lead to flips
*			2) Using parallel frame transportation method , this method is a bit heavier but leads
*			   to a way more stable and consistant normals along the curve, the way it worsk is 
*			   pretty simple , you only have to provide a initial up vector , be carefull that this first
*			   up vector is not parellel to the first tangent.
*			   If this requirement is fullfilled then there wont be any normal problem
*	           You also need to set the number of samples , this means how many  times along the curve it will calculate
*	           the normal, the longest the curve is the highest i suggest to set the samples.
*			
*			
* example create node : (MEL) createNode MG_curvePoint.
*
* @todo  add different distribuition mode of the objects on the curve
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

class MG_curvePoint : public MPxNode

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
	  * The curve we want to attach objects on
	  */
      static MObject inputCurve;
	  /**
	  * The X  first up vector used to calculated the first normal
	  */
      static MObject firstUpVec;
	   /**
	  * The X component of the  first up vector used to calculated the first normal
	  */
      static MObject firstUpVecX;
	  /**
	  * The Y component of the  first up vector used to calculated the first normal
	  */
      static MObject firstUpVecY;
	  /**
	  * The Z component of the  first up vector used to calculated the first normal
	  */
      static MObject firstUpVecZ;
	  /**
	  * The X  compound  component  for outputTranslate attribute
	  */
      static MObject outputTranslateX;
	  /**
	  * The Y compound  component  for outputTranslate attribute
	  */
      static MObject outputTranslateY;
	  /**
	  * The Z  compound  component  for outputTranslate attribute
	  */
      static MObject outputTranslateZ;
	  /**
	  * The  outputTranslate attribute
	  */
      static MObject outputTranslate;
	  /**
	  * The X  compound  component  for outputRotate attribute
	  */
      static MObject outputRotateX;
	  /**
	  * The Y  compound  component  for outputRotate attribute
	  */
      static MObject outputRotateY;
	  /**
	  * The Z  compound  component  for outputRotate attribute
	  */
      static MObject outputRotateZ;
	  /**
	  * The outputRotate attribute
	  */
      static MObject outputRotate;
	  /**
	  * The attribute holding the number of samples 
	  */
      static MObject numberOfSamples;
	  /*
	  * This attribute define the position along the curve
	  */
	  static MObject param;
	  /**
	  * This attribute define in which way the param along the curve has to be used
	  */
      static MObject paramAs;
	  /**
	  * The X  compound  component  for outputNormal attribute
	  */
      static MObject outputNormalX;
	  /**
	  * The Y  compound  component  for outputNormal attribute
	  */
      static MObject outputNormalY;
	  /**
	  * The Z  compound  component  for outputNormal attribute
	  */
      static MObject outputNormalZ;
	  /**
	  * The outputNormal attribute
	  */
      static MObject outputNormal;
	  /**
	  * The X  compound  component  for outputTangent attribute
	  */
      static MObject outputTangentX;
	  /**
	  * The Y  compound  component  for outputTangent attribute
	  */
      static MObject outputTangentY;
	  /**
	  * The Z  compound  component  for outputTangent attribute
	  */
      static MObject outputTangentZ;
	  /**
	  * The outputTangent attribute
	  */
      static MObject outputTangent;
	  /*
	  *This attribute define how the normal will be computed
	  */
	  static MObject normalAs;
    
}; 