// HEADER FILES:
#include "MG_curvePoint.h"
#include <maya/MIOStream.h>
#include <maya/MMatrix.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnMesh.h>
#include <maya/MPointArray.h>
#include <maya/MIntArray.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MVectorArray.h>
#include <maya/MDoubleArray.h>
#include <cmath>
#include <maya/MFnEnumAttribute.h>
#include <maya/MGlobal.h>



//Needed variables
MObject MG_curvePoint::inputCurve;
MObject MG_curvePoint::firstUpVec;
MObject MG_curvePoint::firstUpVecX;
MObject MG_curvePoint::firstUpVecY;
MObject MG_curvePoint::firstUpVecZ;
MObject MG_curvePoint::outputTranslateX;
MObject MG_curvePoint::outputTranslateY;
MObject MG_curvePoint::outputTranslateZ;
MObject MG_curvePoint::outputTranslate;
MObject MG_curvePoint::outputRotateX;
MObject MG_curvePoint::outputRotateY;
MObject MG_curvePoint::outputRotateZ;
MObject MG_curvePoint::outputRotate;
MObject MG_curvePoint::numberOfSamples;
MObject MG_curvePoint::param;
MObject MG_curvePoint::paramAs;
MObject MG_curvePoint::normalAs;
MObject MG_curvePoint::outputTangentX;
MObject MG_curvePoint::outputTangentY;
MObject MG_curvePoint::outputTangentZ;
MObject MG_curvePoint::outputTangent;
MObject MG_curvePoint::outputNormalX;
MObject MG_curvePoint::outputNormalY;
MObject MG_curvePoint::outputNormalZ;
MObject MG_curvePoint::outputNormal;




MTypeId MG_curvePoint::typeId( 0x800019 );

// FOR CREATING AN INSTANCE OF THIS NODE:
void *MG_curvePoint::creator()
{
   return new MG_curvePoint();
}

//The node template
MString curvePointTemplateNode ( MString () + "global proc AEMG_curvePointTemplate( string $nodeName )\n" +
						" { editorTemplate -beginScrollLayout;\n" +
 
							
							"editorTemplate -beginLayout \"Parallel Frame Options\" -collapse 0;\n"+
								
								"editorTemplate -addControl \"firstUpVec\";\n" +
								"editorTemplate -addControl \"numberOfSamples\";\n" +
							
							
						
							
							"editorTemplate -addExtraControls;\n"+
					"editorTemplate -endScrollLayout;\n}"  );


// INITIALIZES THE NODE BY CREATING ITS ATTRIBUTES:
MStatus MG_curvePoint::initialize()
{
    MFnTypedAttribute typedFn;
    MFnCompoundAttribute compund;
    MFnNumericAttribute numFn;
    MFnMatrixAttribute    matrixFn;
    MFnUnitAttribute    uAttr;
    MFnEnumAttribute    eAttr;
    
    
    inputCurve  = typedFn.create( "inputCurve", "ic", MFnData::kNurbsCurve );
    addAttribute(inputCurve);
    
    
    numberOfSamples = numFn.create("numberOfSamples","nos",MFnNumericData::kInt,1);
    numFn.setMin(1);
    numFn.setStorable(true);
    numFn.setKeyable(true);
    addAttribute(numberOfSamples);
    
    firstUpVecX = numFn.create("firstUpVecX","fux",MFnNumericData::kDouble,0);
    numFn.setStorable(true);
    numFn.setKeyable(true);
    addAttribute(firstUpVecX);

    firstUpVecY = numFn.create("firstUpVecY","fuy",MFnNumericData::kDouble,1);
    numFn.setStorable(true);
    numFn.setKeyable(true);
    addAttribute(firstUpVecY);
    

    firstUpVecZ = numFn.create("firstUpVecZ","fuz",MFnNumericData::kDouble,0);
    numFn.setStorable(true);
    numFn.setKeyable(true);
    addAttribute(firstUpVecZ);

    
    firstUpVec= compund.create("firstUpVec","fu");
    compund.addChild(firstUpVecX);
    compund.addChild(firstUpVecY); 
    compund.addChild(firstUpVecZ);
    addAttribute(firstUpVec);    
    

	param = numFn.create("param","pr",MFnNumericData::kDouble,1);
    numFn.setStorable(true);
    numFn.setKeyable(true);
    addAttribute(param);

	paramAs = eAttr.create("paramAs" , "pras" ,0);
	eAttr.addField("u", 0);
	eAttr.addField("len" , 1);
	eAttr.setKeyable(true);
	eAttr.setStorable(true);
	addAttribute(paramAs);

	normalAs = eAttr.create("normalAs" , "nas" ,0);
	eAttr.addField("mayaAPI",0);
	eAttr.addField("parallelFrame" , 1);
	eAttr.setKeyable(true);
	eAttr.setStorable(true);
	addAttribute(normalAs);
  
    outputTranslateX = numFn.create("outputTranslateX","otx",MFnNumericData::kDouble,0);
    numFn.setStorable(false);
    numFn.setKeyable(false);
    numFn.setWritable(false);
    addAttribute(outputTranslateX);

    outputTranslateY = numFn.create("outputTranslateY","oty",MFnNumericData::kDouble,0);
    numFn.setStorable(false);
    numFn.setWritable(false);
    numFn.setKeyable(false);
    addAttribute(outputTranslateY);
    

    outputTranslateZ = numFn.create("outputTranslateZ","otz",MFnNumericData::kDouble,0);
    numFn.setStorable(false);
    numFn.setKeyable(false);
    numFn.setWritable(false);
    addAttribute(outputTranslateZ);

    
    outputTranslate= compund.create("outputTranslate","ot");
    compund.addChild(outputTranslateX);
    compund.addChild(outputTranslateY); 
    compund.addChild(outputTranslateZ);
    compund.setStorable(false);
    compund.setKeyable(false);
    compund.setWritable(false);

    addAttribute(outputTranslate);
    
    
    outputRotateX = uAttr.create("outputRotateX","orx",MFnUnitAttribute::kAngle,0.0);
    numFn.setStorable(false);
    numFn.setWritable(false);
    numFn.setKeyable(false);
    addAttribute(outputRotateX);

    outputRotateY = uAttr.create("outputRotateY","ory",MFnUnitAttribute::kAngle,0.0);
    numFn.setStorable(false);
    numFn.setKeyable(false);
    numFn.setWritable(false);

    addAttribute(outputRotateY);
    

    outputRotateZ = uAttr.create("outputRotateZ","orz",MFnUnitAttribute::kAngle,0.0);
    numFn.setStorable(false);
    numFn.setKeyable(false);
    numFn.setWritable(false);
    
    addAttribute(outputRotateZ);

    
    outputRotate= compund.create("outputRotate","or");
    compund.addChild(outputRotateX);
    compund.addChild(outputRotateY); 
    compund.addChild(outputRotateZ);
    compund.setStorable(false);
    compund.setKeyable(false);
    compund.setWritable(false);
    addAttribute(outputRotate);
  

	outputNormalX = numFn.create("outputNormalX","onx",MFnNumericData::kDouble,0);
	numFn.setStorable(false);
	numFn.setKeyable(false);
	numFn.setWritable(false);
	addAttribute(outputNormalX);

	outputNormalY = numFn.create("outputNormalY","ony",MFnNumericData::kDouble,0);
	numFn.setStorable(false);
	numFn.setWritable(false);
	numFn.setKeyable(false);
	addAttribute(outputNormalY);
    

	outputNormalZ = numFn.create("outputNormalZ","onz",MFnNumericData::kDouble,0);
	numFn.setStorable(false);
	numFn.setKeyable(false);
	numFn.setWritable(false);
	addAttribute(outputNormalZ);

    
	outputNormal= compund.create("outputNormal","on");
	compund.addChild(outputNormalX);
	compund.addChild(outputNormalY); 
	compund.addChild(outputNormalZ);
	compund.setStorable(false);
	compund.setKeyable(false);
	compund.setWritable(false);

	addAttribute(outputNormal);

	outputTangentX = numFn.create("outputTangentX","otax",MFnNumericData::kDouble,0);
	numFn.setStorable(false);
	numFn.setKeyable(false);
	numFn.setWritable(false);
	addAttribute(outputTangentX);

	outputTangentY = numFn.create("outputTangentY","otay",MFnNumericData::kDouble,0);
	numFn.setStorable(false);
	numFn.setWritable(false);
	numFn.setKeyable(false);
	addAttribute(outputTangentY);
    

	outputTangentZ = numFn.create("outputTangentZ","otaz",MFnNumericData::kDouble,0);
	numFn.setStorable(false);
	numFn.setKeyable(false);
	numFn.setWritable(false);
	addAttribute(outputTangentZ);

    
	outputTangent= compund.create("outputTangent","otan");
	compund.addChild(outputTangentX);
	compund.addChild(outputTangentY); 
	compund.addChild(outputTangentZ);
	compund.setStorable(false);
	compund.setKeyable(false);
	compund.setWritable(false);

	addAttribute(outputTangent);

    attributeAffects (inputCurve , outputTranslate);
    attributeAffects (inputCurve , outputRotate);
	attributeAffects (inputCurve , outputTangent);
	attributeAffects (inputCurve , outputNormal);

        
    attributeAffects (firstUpVec , outputTranslate);
    attributeAffects (firstUpVec , outputRotate);
	attributeAffects (firstUpVec , outputTangent);
	attributeAffects (firstUpVec , outputNormal);
    
    attributeAffects (numberOfSamples , outputTranslate);
    attributeAffects (numberOfSamples , outputRotate);
	attributeAffects (numberOfSamples , outputTangent);
	attributeAffects (numberOfSamples , outputNormal);

	attributeAffects (param , outputTranslate);
    attributeAffects (param , outputRotate);
	attributeAffects (param , outputTangent);
	attributeAffects (param , outputNormal);

	attributeAffects (paramAs , outputTranslate);
    attributeAffects (paramAs , outputRotate);
	attributeAffects (paramAs , outputTangent);
	attributeAffects (paramAs , outputNormal);


	attributeAffects (normalAs , outputTranslate);
    attributeAffects (normalAs , outputRotate);
	attributeAffects (normalAs , outputTangent);
	attributeAffects (normalAs , outputNormal);
    
	MGlobal::executeCommand(curvePointTemplateNode);
       
   return MS::kSuccess;
}


// COMPUTE METHOD'S DEFINITION:
MStatus MG_curvePoint::compute(const MPlug &plug, MDataBlock &data)
{
    //Get the data
    
	/*
	if ((plug == outputTranslate ) || (plug == outputRotate) || (plug == outputTangent) || (plug == outputNormal))
	{
	*/

    MObject inputCurveV = data.inputValue (inputCurve).asNurbsCurve();
    MVector firstUpVecV = data.inputValue(firstUpVec).asVector();
    firstUpVecV.normalize();
    int numberOfSamplesV = data.inputValue(numberOfSamples).asInt();
	double paramV = data.inputValue(param).asDouble();
	
	//Do some checks on the data
	//Create a MFnNurbsCurve to work with
	MFnNurbsCurve curveFn(inputCurveV);
	double length = curveFn.length();
	int paramAsV = data.inputValue(paramAs).asShort();

	//Clamp the param value if gets out of the  length
	if (paramV < 0)
	{
	
	paramV = 0;
	}
	if ((paramV >length ) && (paramAsV == 1))

	{
		paramV = paramV;
	}
	
	double paramVStored = double(paramV);
	
	int normalAsV = data.inputValue(normalAs).asShort();



	//Check if there is a curve connected

	MPlug inputCurvePlug( thisMObject(), inputCurve );
	if (inputCurvePlug.isConnected() == false)
	{	
	    return MS::kNotImplemented;
	}

	

	//Fist check if we deal with length or U value
	if ( paramAsV == 1 )
	{
		 
		paramV = curveFn.findParamFromLength(paramV);
	
	} 

	//Declare out rotation and traslation attribute
	MPoint outP ;
	double outR[3];
	outR[0] = 0; 
	outR[1] = 0;
	outR[2] = 0;

	//Get the out position
	curveFn.getPointAtParam(paramV , outP , MSpace::kWorld );

	
	//Compute out rotation
	MVector  normal , tangent , third ;

	if ( normalAsV == 0 )
	{
		//compute the orientation using maya api normal

		tangent = curveFn.tangent(paramV , MSpace::kWorld );
		normal  = curveFn.normal(paramV , MSpace::kWorld);
		third =  tangent ^ normal;
		normal  = third ^ tangent  ;
	}

	else 
	{

		//Compute the orientation by using the parallel frame transportation method 
		
		//Based on the length and the number of sample lets calculate the segment that we multiply
		// for each iteration
		
		double subvidsSample = length/double(numberOfSamplesV)  ;

		//The array where we will store all the params
		MDoubleArray paramValues;
		paramValues.setLength(numberOfSamplesV);


		//First sample the curve
		//We calculate the normals by using the parallel frame transportation method
		MVectorArray normals;
		normals.setLength(numberOfSamplesV);
   
		MVector currentNormal = firstUpVecV;

		for ( int i = 0 ; i < numberOfSamplesV ; i++)
		{
      
		  double paramTemp = curveFn.findParamFromLength(i*subvidsSample);
		  MVector tan = curveFn.tangent(paramTemp , MSpace::kObject);
		  paramValues[i] = paramTemp;
		  tan.normalize();
		  MVector cross1 = currentNormal^tan;
		  cross1.normalize() ;
		  MVector cross2 =  tan^cross1;
		  cross2.normalize();
		  currentNormal = cross2 ;
		  normals[i] = cross2;


		}



		//Now lets calculate the orientation on the curve using the previously calculated normals
		//Find which normal to use 
		if ( paramAsV == 0 ) 
		{	
			for ( unsigned int i = 0 ; i < paramValues.length() ; i++ )
			{
				if( paramV < paramValues[i])
				{
					normal = normals[i];
					break;
				}//end if( paramV < paramValues[i])
			}// end for ( int i = 0 ; i < paramValues.length() ; i++ )
		}//end if ( paramAsV == 0 ) 


		else
		{

			int subDiv = int (paramVStored/subvidsSample);
			if (subDiv <= (numberOfSamplesV - 1))
			{
			 
			 normal = normals[subDiv];
			 }//end if (subDiv <= (numberOfSamplesV - 1))

		}//end else

		tangent = curveFn.tangent(paramV , MSpace::kWorld );
		third =  tangent ^ normal;
		normal  = third ^ tangent  ;
	
	}//end else of if ( normalAsV == 0 )


	//Build a matrix and extract euler rotation
	double myMatrix[4][4]={	{ tangent.x, tangent.y , tangent.z, 0},
						{ normal.x, normal.y , normal.z, 0},
						{third.x, third.y , third.z, 0},
						{ 0, 0, 0, 1}};

	MMatrix rotMatrix (myMatrix);		
	MTransformationMatrix matrixFn(rotMatrix);
	MTransformationMatrix::RotationOrder rotOrder;
	rotOrder =MTransformationMatrix::kXYZ;
	matrixFn.getRotation(outR,rotOrder,MSpace::kObject );


	//Set the out data
	//Out translate
	data.outputValue(outputTranslate).setMVector(MVector(outP)); 
	data.outputValue(outputTranslate).setClean();

	//Out rotate
	data.outputValue(outputRotate).set(outR[0] ,outR[1],outR[2]);
	data.outputValue(outputRotate).setClean();

	//Out normal
	data.outputValue(outputNormal).set(normal[0] ,normal[1],normal[2]);
	data.outputValue(outputNormal).setClean();

	//Out tangent
	data.outputValue(outputTangent).set(tangent[0] ,tangent[1],tangent[2]);
	data.outputValue(outputTangent).setClean();

   return MS::kSuccess;
}


















