#include "MG_matrixGL.h"

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
MTypeId MG_matrixGL::typeId( 0x80016 );

//Needed attributes


MObject MG_matrixGL::upVecX;
MObject MG_matrixGL::upVecY;
MObject MG_matrixGL::upVecZ;
MObject MG_matrixGL::upVec;
MObject MG_matrixGL::inputMatrix;
MObject MG_matrixGL::fakeOut;
MObject MG_matrixGL::drawIt;
MObject MG_matrixGL::ballSize;
MObject MG_matrixGL::arrowSize;
MObject MG_matrixGL::drawText;
MObject MG_matrixGL::drawTextVec;
MObject MG_matrixGL::drawTextPos;

//Class


void* MG_matrixGL::creator()
{

	return new MG_matrixGL();
}

MStatus MG_matrixGL::initialize()
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
  
  

    drawText =numFn.create("drawText","drt",MFnNumericData::kBoolean,1);
  numFn.setKeyable(true);
  numFn.setStorable(true);
  addAttribute(drawText);

  drawTextVec =numFn.create("drawTextVec","drtv",MFnNumericData::kBoolean,0);
  numFn.setKeyable(true);
  numFn.setStorable(true);
  addAttribute(drawTextVec);

  drawTextPos =numFn.create("drawTextPos","drtp",MFnNumericData::kBoolean,0);
  numFn.setKeyable(true);
  numFn.setStorable(true);
  addAttribute(drawTextPos);


  arrowSize =numFn.create("arrowSize","as",MFnNumericData::kDouble,1);
  numFn.setKeyable(true);
  numFn.setStorable(true);
  addAttribute(arrowSize);
  
  ballSize =numFn.create("ballSize","bs",MFnNumericData::kDouble,0.2);
  numFn.setKeyable(true);
  numFn.setStorable(true);
  addAttribute(ballSize);

  inputMatrix =matrixFn.create("inputMatrix","inm");
  addAttribute(inputMatrix);

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
  
  
  attributeAffects(arrowSize , fakeOut);
  attributeAffects(ballSize , fakeOut);
  attributeAffects(upVec , fakeOut);
  attributeAffects(drawIt , fakeOut);
  attributeAffects(inputMatrix , fakeOut);
  
  return MS::kSuccess;
	

}

bool MG_matrixGL::isBounded() const
{ 
	return false ;
}

MStatus MG_matrixGL::compute(const MPlug& plug,MDataBlock& dataBlock)
	{
		
		dataBlock.outputValue(fakeOut).setDouble(0);
		dataBlock.outputValue(fakeOut).setClean();

		return MS::kSuccess;
	}








void MG_matrixGL::draw( M3dView & view, const MDagPath & path, 
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
	MPlug drawTextP (thisMObject(),drawText);
	bool drawTextV;
	drawTextP.getValue(drawTextV);
	
	MPlug inputMatrixP (thisMObject(),inputMatrix);
	MObject inputMatrixData;
	inputMatrixP.getValue(inputMatrixData);
	MFnMatrixData matrixFn(inputMatrixData);
	MMatrix inputMatrixV =matrixFn.matrix();


	MPlug arrowSizeP (thisMObject(),arrowSize);
	double arrowSizeV;
	arrowSizeP.getValue(arrowSizeV);

	MPlug ballSizeP (thisMObject(),ballSize);
	double ballSizeV;
	ballSizeP.getValue(ballSizeV);
	
	MPlug upVecP (thisMObject(),upVec);
	MVector upVecV;
	upVecP.child(0).getValue(upVecV.x);
	upVecP.child(1).getValue(upVecV.y);
	upVecP.child(2).getValue(upVecV.z);
	
	


	
	MPoint currentPoint (inputMatrixV[3][0] , inputMatrixV[3][1] ,inputMatrixV[3][2]);
	MVector currentPointVec (currentPoint);
	MVector xAxis (inputMatrixV[0][0] , inputMatrixV[0][1] ,inputMatrixV[0][2]);
	MVector yAxis (inputMatrixV[1][0] , inputMatrixV[1][1] ,inputMatrixV[1][2]);
	MVector zAxis (inputMatrixV[2][0] , inputMatrixV[2][1] ,inputMatrixV[2][2]);

	// Draw it 
	view.beginGL();
	glPushAttrib( GL_ALL_ATTRIB_BITS );
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
	glLineWidth(2);

	glColor4f(1.0,0.0,0.0,1.0f);
	
	mayaOpenGL moGL;

	moGL.drawArrow(xAxis , upVecV , arrowSizeV , currentPoint);
	
	glColor4f(0.0,1.0,0.0,1.0f);
	moGL.drawArrow(yAxis , upVecV , arrowSizeV , currentPoint);
	glColor4f(0.0,0.0,1.0,1.0f);
	moGL.drawArrow(zAxis , upVecV , arrowSizeV , currentPoint);
	
	double * yellow;
	yellow = new double[4];
	yellow[0]=1;
	yellow[1]=1;
	yellow[2]=0.2;
	yellow[3]=0.3;

	moGL.drawSphere(ballSizeV, 20, 20 ,currentPointVec ,yellow);
		

	if ( drawTextV == 1 )

	{


		MPlug drawTextVecP (thisMObject(),drawTextVec);
		bool drawTextVecV;
		drawTextVecP.getValue(drawTextVecV);

		MPlug drawTextPosP (thisMObject(),drawTextPos);
		bool drawTextPosV;
		drawTextPosP.getValue(drawTextPosV);

		if (drawTextVecV == 1)

		{

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

		//X AXIS
		MPoint textX =  MPoint(currentPoint);
		textX+= (xAxis*1.4*arrowSizeV);
		textX.y += arrowSizeV/3;

		MString StextXx = MString() + xAxis.x;
		moGL.drawText( StextXx ,red ,textX , view);

		textX.y -= arrowSizeV/3;

		MString StextXy = MString() + xAxis.y;
		moGL.drawText( StextXy ,red ,textX , view);

		textX.y -= arrowSizeV/3;

		MString StextXz = MString() + xAxis.z;
		moGL.drawText( StextXz ,red ,textX , view);


		//Y AXIS
		MPoint textY =  MPoint(currentPoint);
		textY+= (yAxis*1.4*arrowSizeV);
		textY.y += arrowSizeV/3;

		MString StextYx = MString() + yAxis.x;
		moGL.drawText( StextYx ,green ,textY , view);

		textY.y -= arrowSizeV/3;

		MString StextYy = MString() + yAxis.y;
		moGL.drawText( StextYy ,green ,textY , view);

		textY.y -= arrowSizeV/3;

		MString StextYz = MString() + yAxis.z;
		moGL.drawText( StextYz ,green ,textY , view);


		//Z AXIS
		MPoint textZ =  MPoint(currentPoint);
		textZ+= (zAxis*1.4*arrowSizeV);
		textZ.y += arrowSizeV/3;

		MString StextZx = MString() + zAxis.x;
		moGL.drawText( StextZx ,blue ,textZ , view);

		textZ.y -= arrowSizeV/3;

		MString StextZy = MString() + zAxis.y;
		moGL.drawText( StextZy ,blue ,textZ , view);

		textZ.y -= arrowSizeV/3;

		MString StextZz = MString() + zAxis.z;
		moGL.drawText( StextZz ,blue ,textZ , view);
		}

		if (drawTextPosV == 1)
		{

		//Pos
		MPoint text =  MPoint(currentPoint);
		text+= (yAxis*-1*1.4*arrowSizeV);
		text.y += arrowSizeV/3;

		MString Stextx = MString() + currentPoint.x;
		moGL.drawText( Stextx ,yellow ,text , view);

		text.y -= arrowSizeV/3;

		MString Stexty = MString() + currentPoint.y;
		moGL.drawText( Stexty ,yellow ,text , view);

		text.y -= arrowSizeV/3;

		MString Stextz = MString() + currentPoint.z;
		moGL.drawText( Stextz ,yellow ,text , view);
		}

	}


	glDisable(GL_BLEND);
	glPopAttrib();



}




 
