// HEADER FILES:
#include "MG_extrudeEdge.h"
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
#include <maya/MQuaternion.h>
#include <maya/MRampAttribute.h>
#include <maya/MGlobal.h>
#include <maya/MFloatArray.h>
#include <maya/MFnNurbsCurveData.h>
#include <maya/MFnNurbsSurface.h>
#include <maya/MFnNurbsSurfaceData.h>
#include <maya/MFnEnumAttribute.h>


MObject MG_extrudeEdge::inputMesh;
MObject MG_extrudeEdge::normalSize;
MObject MG_extrudeEdge::vtxArray;
MObject MG_extrudeEdge::outSurface;
MObject MG_extrudeEdge::meshParentMatrix;
MObject MG_extrudeEdge::tiltMatrix;
MObject MG_extrudeEdge::counterMatrix;								
MObject MG_extrudeEdge::useTiltMatrix;		
MObject MG_extrudeEdge::useCustomSource;	
MObject MG_extrudeEdge::customSourceAs;	
MObject MG_extrudeEdge::customSourceX;	
MObject MG_extrudeEdge::customSourceY;	
MObject MG_extrudeEdge::customSourceZ;	
MObject MG_extrudeEdge::customSource;	


MTypeId MG_extrudeEdge::typeId( 0x800018 );

MString templateNode ( MString () + "global proc AEMG_extrudeEdgeTemplate( string $nodeName )\n" +
						" { editorTemplate -beginScrollLayout;\n" +
 
							
							"editorTemplate -beginLayout \"Tilt Attributes\" -collapse 0;\n"+
								"editorTemplate -addControl \"useTiltMatrix\";\n" +
								"editorTemplate -addControl \"tiltMatrix\";\n" +
								"editorTemplate -addControl \"counterMatrix\";\n" +
							"editorTemplate -endLayout;\n" + 
							
							"editorTemplate -beginLayout \"Custom Source\" -collapse 0;\n"+
								"editorTemplate -addControl \"useCustomSource\";\n" +
								"editorTemplate -addControl \"customSourceAs\";\n" +
								"editorTemplate -addControl \"customSource\";\n" +
							"editorTemplate -endLayout;\n" +
								
							"editorTemplate -addExtraControls;\n"+
					"editorTemplate -endScrollLayout;\n}"  );



// FOR CREATING AN INSTANCE OF THIS NODE:
void *MG_extrudeEdge::creator() 
{
   return new MG_extrudeEdge();
}


// INITIALIZES THE NODE BY CREATING ITS ATTRIBUTES:
MStatus MG_extrudeEdge::initialize()
{
    MFnTypedAttribute typedFn;
    MFnCompoundAttribute compund;
    MFnNumericAttribute numFn;
    MFnMatrixAttribute    matrixFn;
    MFnUnitAttribute    uAttr;
	MFnEnumAttribute    eAttr;

    
	vtxArray = numFn.create("vtxArray","vtxa",MFnNumericData::kInt,0);
    numFn.setStorable(true);
    numFn.setKeyable(true);
	numFn.setArray(true);
    addAttribute(vtxArray);

	normalSize = numFn.create("normalSize","ns",MFnNumericData::kDouble,1);
    numFn.setStorable(true);
    numFn.setKeyable(true);
    addAttribute(normalSize);
    
	inputMesh  = typedFn.create( "inputMesh", "im", MFnData::kMesh );
    addAttribute(inputMesh);

	outSurface  = typedFn.create( "outSurface", "os", MFnData::kNurbsSurface );
	typedFn.setStorable(false);
	typedFn.setKeyable(false);
	typedFn.setWritable(false);
    addAttribute(outSurface);

	
	meshParentMatrix= matrixFn.create("meshParentMatrix","mpm");
	addAttribute(meshParentMatrix);

	useTiltMatrix = numFn.create("useTiltMatrix","utm",MFnNumericData::kBoolean, 0);
    numFn.setStorable(true);
    numFn.setKeyable(true);
    addAttribute(useTiltMatrix);

	tiltMatrix= matrixFn.create("tiltMatrix","tlm");
	addAttribute(tiltMatrix);

	counterMatrix= matrixFn.create("counterMatrix","cnm");
	addAttribute(counterMatrix);

	//custom normal
	useCustomSource = numFn.create("useCustomSource","ucs",MFnNumericData::kBoolean, 0);
    numFn.setStorable(true);
    numFn.setKeyable(true);
    addAttribute(useCustomSource);


	customSourceAs = eAttr.create("customSourceAs" , "csa" , 0);
	eAttr.addField("Point" , 0);
	eAttr.addField("Vector" , 1);
	eAttr.setStorable(true);
    eAttr.setKeyable(true);
    eAttr.setWritable(true);
	addAttribute(customSourceAs);

	customSourceX = numFn.create("customSourceX","csx",MFnNumericData::kDouble,0.0);
    numFn.setStorable(true);
    numFn.setWritable(true);
    numFn.setKeyable(true);
    addAttribute(customSourceX);

    customSourceY = numFn.create("customSourceY","csy",MFnNumericData::kDouble,1.0);
    numFn.setStorable(true);
    numFn.setKeyable(true);
    numFn.setWritable(true);

    addAttribute(customSourceY);
    

    customSourceZ = numFn.create("customSourceZ","csz",MFnNumericData::kDouble,0.0);
    numFn.setStorable(true);
    numFn.setKeyable(true);
    numFn.setWritable(true);
    
    addAttribute(customSourceZ);

    
    customSource= compund.create("customSource","cs");
    compund.addChild(customSourceX);
    compund.addChild(customSourceY); 
    compund.addChild(customSourceZ);
    compund.setStorable(true);
    compund.setKeyable(true);
    compund.setWritable(true);
    addAttribute(customSource);

	attributeAffects(vtxArray, outSurface);
	attributeAffects(inputMesh, outSurface);
	attributeAffects(normalSize, outSurface);
	attributeAffects(meshParentMatrix, outSurface);
	attributeAffects(useTiltMatrix, outSurface);
	attributeAffects(counterMatrix, outSurface);
	attributeAffects(tiltMatrix, outSurface);
	attributeAffects(useCustomSource, outSurface);
	attributeAffects(customSourceAs, outSurface);
	attributeAffects(customSource, outSurface);


	MGlobal::executeCommand(templateNode);


	return MS::kSuccess;
}


// COMPUTE METHOD'S DEFINITION:
MStatus MG_extrudeEdge::compute(const MPlug &plug, MDataBlock &data)
{
    //Get the data
    
	MPlug inputMeshPlug( thisMObject(), inputMesh );
	    
	if (inputMeshPlug.isConnected() == false)
	{	
	    return MS::kNotImplemented;
	}


	MObject inputMeshV = data.inputValue(inputMesh).asMeshTransformed();
	MFnMesh meshFn (inputMeshV);
	
	double normalSizeV = data.inputValue(normalSize).asDouble();
	MArrayDataHandle  vtxArrayV = data.inputArrayValue(vtxArray);
	MMatrix meshParentMatrixV = data.inputValue(meshParentMatrix).asMatrix();
	MMatrix tiltMatrixV = data.inputValue(tiltMatrix).asMatrix();
	MMatrix counterMatrixV = data.inputValue(counterMatrix).asMatrix();
	bool useTiltMatrixV = data.inputValue(useTiltMatrix).asBool();
	bool useCustomSourceV = data.inputValue(useCustomSource).asBool();
	int  customSourceAsV = data.inputValue(customSourceAs).asInt();

	if((useTiltMatrixV == 1) && (useCustomSourceV == 1))
	{
		MGlobal::displayError("Is not possible to use both useTiltMatrix and useCustomSource mode at the same time");
		return MS::kNotImplemented;
	}

	vtxArrayV.jumpToElement(0);
	int arraySize = vtxArrayV.elementCount();
	MPointArray points ;
	MPointArray shiftedPoints;
	points.setLength(arraySize);
	shiftedPoints.setLength (arraySize);
	MVector normal;
	for ( int i = 0 ; i < arraySize ; i++ , vtxArrayV.next())
	{

		//Get points 
		MPoint pos;
		int neededVtx =vtxArrayV.inputValue().asInt();
		meshFn.getPoint(neededVtx , pos , MSpace::kWorld);
		points[i] = pos;
		//GetNormal
		
		if(useCustomSourceV== 0)
		{

		meshFn.getVertexNormal(neededVtx ,0,normal ,MSpace::kWorld);
		
		normal = normal*meshParentMatrixV;
		}
		else
		{

			MVector customSourceV = data.inputValue(customSource).asVector();

			if (customSourceAsV==0)
			{	

				normal = ( pos - customSourceV );
				normal.normalize();
			}
			else
			{
			
				normal = customSourceV;
				normal.normalize();

			}

		}
		if (useTiltMatrixV == 1)
		{
		normal = normal*counterMatrixV.inverse();
		normal = normal*tiltMatrixV;
		normal = normal*counterMatrixV;
		}

		

		//Shift the point
		MPoint shiftPos = pos+ (normal*normalSizeV);
		shiftedPoints.append(shiftPos);
		
		points.append(shiftPos);
	}
	
	
    // create knot vectors for U and V 

	
    MDoubleArray ku, kv;
	
	kv.append(0);
	kv.append(1);
	
    for (int i = 0 ; i < arraySize;i++)
	{
		ku.append(i/double(arraySize));

		
	
	}


	MStatus stat;

	MFnNurbsSurface surfFn;
	MFnNurbsSurfaceData dataCreator;
    MObject newSurfData = dataCreator.create(  );
	surfFn.create(
                points, kv,ku , 1, 1,
                MFnNurbsSurface::kOpen, 
				MFnNurbsSurface::kOpen,
                false, newSurfData ,&stat );
	
	MDataHandle outputH = data.outputValue(outSurface);
	outputH.set(newSurfData);
	outputH.setClean();

   return MS::kSuccess;
}














