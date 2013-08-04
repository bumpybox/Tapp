#include "MG_vectorGL.h"
#include <mayaOpenGL.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MGlobal.h>
#include <maya/MFloatVector.h>
#include <maya/MMatrix.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MFloatPoint.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MPlug.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MVector.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnMatrixData.h>
#include <cmath>
#include <maya/MFnMesh.h>
#include <maya/MPointArray.h>
#include <maya/MIntArray.h> 
#include <maya/MFnMeshData.h>
#include <maya/MObjectArray.h>
#include <maya/MFloatPoint.h>


const double PI=3.14159265358979323846264338327950288419716939937510;
const double toDeg = 57.295779513082320876798154814105;
const double toRad = 0.01745329251994329576923690768489;
MTypeId MG_vectorGL::typeId( 0x81006 );

//Needed attributes


MObject MG_vectorGL::upVecX;
MObject MG_vectorGL::upVecY;
MObject MG_vectorGL::upVecZ;
MObject MG_vectorGL::upVec;
MObject MG_vectorGL::vecX;
MObject MG_vectorGL::vecY;
MObject MG_vectorGL::vecZ;
MObject MG_vectorGL::vecs;
MObject MG_vectorGL::fakeOut;
MObject MG_vectorGL::drawIt;
MObject MG_vectorGL::startPointX;
MObject MG_vectorGL::startPointY;
MObject MG_vectorGL::startPointZ;
MObject MG_vectorGL::startPoint;
MObject MG_vectorGL::arrowSize;
MObject MG_vectorGL::drawSingleVec;
MObject MG_vectorGL::drawSingleText;
MObject MG_vectorGL::drawSingleVecText;
MObject MG_vectorGL::inputMatrix1;
MObject MG_vectorGL::inputMatrix2;
//Class



void* MG_vectorGL::creator()
{

	return new MG_vectorGL();
}



MStatus MG_vectorGL::initialize()
{ 
  
  //Declaring all the needed attribute function sets 
  MFnEnumAttribute enumFn;
  MFnMatrixAttribute matrixFn;
  MFnNumericAttribute numFn;
  MFnCompoundAttribute compA;


		
  
  
  drawIt =numFn.create("drawIt","drw",MFnNumericData::kBoolean,1);
  numFn.setKeyable(true);
  numFn.setStorable(true);
  addAttribute(drawIt);
  
  drawSingleVec =numFn.create("drawSingleVec","dsv",MFnNumericData::kBoolean,1);
  numFn.setKeyable(true);
  numFn.setStorable(true);
  addAttribute(drawSingleVec);

  drawSingleText =numFn.create("drawSingleText","dst",MFnNumericData::kBoolean,1);
  numFn.setKeyable(true);
  numFn.setStorable(true);
  addAttribute(drawSingleText);



  drawSingleVecText =numFn.create("drawSingleVecText","dsvt",MFnNumericData::kBoolean,1);
  numFn.setKeyable(true);
  numFn.setStorable(true);
  addAttribute(drawSingleVecText);




  arrowSize =numFn.create("arrowSize","as",MFnNumericData::kDouble,1);
  numFn.setKeyable(true);
  numFn.setStorable(true);
  addAttribute(arrowSize);
  
  
  fakeOut =numFn.create("fakeOut","fo",MFnNumericData::kBoolean,1);
  numFn.setKeyable(false);
  numFn.setStorable(false);
  addAttribute(fakeOut);
    
  
  
  upVecX =numFn.create("upVecX","uvx",MFnNumericData::kDouble,0);

  numFn.setStorable(true);
  addAttribute(upVecX);

  upVecY =numFn.create("upVecY","uvy",MFnNumericData::kDouble,1);

  numFn.setStorable(true);
  addAttribute(upVecY);


  upVecZ =numFn.create("upVecZ","uvz",MFnNumericData::kDouble,0);

  numFn.setStorable(true);
  addAttribute(upVecZ);

  upVec= compA.create("upVec","uv" );
  compA.addChild(upVecX);
  compA.addChild(upVecY);
  compA.addChild(upVecZ);

  addAttribute(upVec);
  
  vecX =numFn.create("vecX","vx",MFnNumericData::kDouble,0);

  numFn.setStorable(true);
  addAttribute(vecX);

  vecY =numFn.create("vecY","vy",MFnNumericData::kDouble,1);

  numFn.setStorable(true);
  addAttribute(vecY);


  vecZ =numFn.create("vecZ","vz",MFnNumericData::kDouble,0);

  numFn.setStorable(true);
  addAttribute(vecZ);

  vecs= compA.create("vecs","vs" );
  compA.addChild(vecX);
  compA.addChild(vecY);
  compA.addChild(vecZ);
  compA.setArray(true);

  addAttribute(vecs);  
  
  
  startPointX =numFn.create("startPointX","spx",MFnNumericData::kDouble,0);

  numFn.setStorable(true);
  addAttribute(startPointX);

  startPointY =numFn.create("startPointY","spy",MFnNumericData::kDouble,0);

  numFn.setStorable(true);
  addAttribute(startPointY);


  startPointZ =numFn.create("startPointZ","spz",MFnNumericData::kDouble,0);

  numFn.setStorable(true);
  addAttribute(startPointZ);

  startPoint= compA.create("startPoints","sp" );
  compA.addChild(startPointX);
  compA.addChild(startPointY);
  compA.addChild(startPointZ);
  compA.setArray(true);

  addAttribute(startPoint); 

  inputMatrix1= matrixFn.create("inputMatrix1","im1");
  addAttribute(inputMatrix1);
  
  inputMatrix2= matrixFn.create("inputMatrix2","im2");
  addAttribute(inputMatrix2);
  
  attributeAffects(drawSingleVecText , fakeOut);
  attributeAffects(drawSingleText , fakeOut);
  attributeAffects(inputMatrix1 , fakeOut);
  attributeAffects(inputMatrix2 , fakeOut);
  attributeAffects(drawSingleVec , fakeOut);
  attributeAffects(arrowSize , fakeOut);
  attributeAffects(startPoint , fakeOut);
  attributeAffects(upVec , fakeOut);
  attributeAffects(drawIt , fakeOut);
  attributeAffects(vecs , fakeOut);
  


  return MS::kSuccess;
	

}

bool MG_vectorGL::isBounded() const
{ 
	return false ;
}

MStatus MG_vectorGL::compute(const MPlug& plug,MDataBlock& dataBlock)
	{
		dataBlock.outputValue(fakeOut).set(0);
		dataBlock.outputValue(fakeOut).setClean();



		return MS::kSuccess;
	}



void MG_vectorGL::draw( M3dView & view, const MDagPath & path, 
							 M3dView::DisplayStyle dispStyle,
							 M3dView::DisplayStatus status )
{ 
   
	MPlug drawItP (thisMObject(),drawIt);
	bool drawItV;
	drawItP.getValue(drawItV);

	if ( drawItV == 0 )
	{
	  return ;
	  
	}

	MPlug drawSingleP (thisMObject(),drawSingleVec);
	bool drawSingleV;
	drawSingleP.getValue(drawSingleV);

	MPlug upVecP (thisMObject(),upVec);
	MVector upVecV;
	upVecP.child(0).getValue(upVecV.x);
	upVecP.child(1).getValue(upVecV.y);
	upVecP.child(2).getValue(upVecV.z);
	

	if (drawSingleV == 0 )
	{
	
		MPlug arrowSizeP (thisMObject(),arrowSize);
		double arrowSizeV;
		arrowSizeP.getValue(arrowSizeV);
	
		MPlug upVecP (thisMObject(),upVec);
		MVector upVecV;
		upVecP.child(0).getValue(upVecV.x);
		upVecP.child(1).getValue(upVecV.y);
		upVecP.child(2).getValue(upVecV.z);
	
		MPlug vecsP (thisMObject(),vecs);
		MPlug startPointP (thisMObject(),startPoint);

	 
		int elemVecs   =  vecsP.numElements();
		int elemPoints =  startPointP.numElements();
	
	
	
		if (elemVecs != elemPoints )
		{
		  return;
	  
		}
	
	
		// Draw it 
		view.beginGL();
		glPushAttrib( GL_ALL_ATTRIB_BITS );
		glEnable(GL_BLEND);
		glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
		glLineWidth(2);
		if(status == M3dView::kLead)
			glColor4f(0.0,1.0,0.0,1.0f);
		else
			glColor4f(1.0,1.0,0.0,1.0f);
	
		for ( unsigned int i = 0 ; i < elemVecs ; i++ )
		{
		   vecsP.selectAncestorLogicalIndex( i , vecs);
		   startPointP.selectAncestorLogicalIndex( i , startPoint);

	
		   MVector currentVec ;
		   MPoint currentPoint;
	  
		  vecsP.child(0).getValue(currentVec.x);
		  vecsP.child(1).getValue(currentVec.y);
		  vecsP.child(2).getValue(currentVec.z);
	  
		  startPointP.child(0).getValue(currentPoint.x);
		  startPointP.child(1).getValue(currentPoint.y);
		  startPointP.child(2).getValue(currentPoint.z);
		
		
		  mayaOpenGL moGL;
		  moGL.drawArrow(currentVec , upVecV , arrowSizeV , currentPoint);
		

		}


		glDisable(GL_BLEND);
		glPopAttrib();

	}
	else
	{

		MPlug drawSingleTextP (thisMObject(),drawSingleText);
		bool drawSingleTextV;
		drawSingleTextP.getValue(drawSingleTextV);


		MPlug drawSingleVecTextP (thisMObject(),drawSingleVecText);
		bool drawSingleVecTextV;
		drawSingleVecTextP.getValue(drawSingleVecTextV);


		MPlug inputMatrix1P (thisMObject(),inputMatrix1);
		MObject inputMatrix1Data;
		inputMatrix1P.getValue(inputMatrix1Data);
		MFnMatrixData matrixFn1(inputMatrix1Data);
		MMatrix inputMatrix1V =matrixFn1.matrix();


		MPlug inputMatrix2P (thisMObject(),inputMatrix2);
		MObject inputMatrix2Data;
		inputMatrix2P.getValue(inputMatrix2Data);
		MFnMatrixData matrixFn2(inputMatrix2Data);
		MMatrix inputMatrix2V =matrixFn2.matrix();

		MVector  point1 ( inputMatrix1V[3][0], inputMatrix1V[3][1], inputMatrix1V[3][2]);
		MVector  point2 ( inputMatrix2V[3][0], inputMatrix2V[3][1], inputMatrix2V[3][2]);

		view.beginGL();
		glPushAttrib( GL_ALL_ATTRIB_BITS );
		glEnable(GL_BLEND);
		glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
		glLineWidth(2);
		if(status == M3dView::kLead)
			glColor4f(0.0,1.0,0.0,1.0f);
		else
			glColor4f(1.0,1.0,0.0,1.0f);


		MVector drawVector = point2 - point1 ;
		
		mayaOpenGL moGL;
		moGL.drawArrow(drawVector , upVecV, drawVector.length() , MPoint(point1));
		
		double * green;
		green = new double[4];
		green[0]=0;
		green[1]=1;
		green[2]=0;
		green[3]=1;
		
		
		double * blue;
		blue = new double[4];
		blue[0]=0;
		blue[1]=0;
		blue[2]=1;
		blue[3]=1;

		double * red;
		red = new double[4];
		red[0]=1;
		red[1]=0;
		red[2]=0.0;
		red[3]=1.0;


		if (drawSingleTextV == 1 )
		{
		MPoint averageP;
		averageP.x= (point1.x + point2.x)/2;
		averageP.y = (point1.y + point2.y)/2;
		averageP.z = (point1.z + point2.z)/2;


		MPoint  averagePLow =  MPoint(averageP);
		averagePLow.y-=  (drawVector.length()/10);

		
		MString text = MString() + drawVector.length();
		moGL.drawText( text ,red ,averagePLow , view);
		moGL.drawText( MString("Magnitude :") ,red ,averageP , view);
		}

		if (drawSingleVecTextV == 1 )
		{

			MPoint point2Text (point2);
			point2Text.x += (drawVector.length()/10);
			point2Text.y += (drawVector.length()/10);

			MString textX = MString("X: ") + drawVector.x ;
			moGL.drawText( textX ,red ,point2Text , view);

			point2Text.y -= (drawVector.length()/10);
			MString textY = MString("Y: ") + drawVector.y ;
			moGL.drawText( textY ,green ,point2Text , view);

			point2Text.y -= (drawVector.length()/10);
			MString textZ = MString("Z: ") + drawVector.z ;
			moGL.drawText( textZ ,blue ,point2Text , view);

		}

		glDisable(GL_BLEND);
		
		glPopAttrib();

	}



} 




 



