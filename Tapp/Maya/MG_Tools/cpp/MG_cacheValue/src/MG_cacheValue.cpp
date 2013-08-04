/** \brief let s you cache a value 
*/



#include "MG_cacheValue.h"

#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MGlobal.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MVector.h>
#include <maya/MDoubleArray.h>
 
MObject MG_cacheValue::toCacheValue ;
MObject MG_cacheValue::iterationStored;
MObject MG_cacheValue::outValue;
MObject MG_cacheValue::cache;
MObject MG_cacheValue::pastIterationOutIndex;
MObject MG_cacheValue::startFrame;
MObject MG_cacheValue::startFrameValue;
MObject MG_cacheValue::time;
MObject MG_cacheValue::timeDriven;
MObject MG_cacheValue::timeStored;

MTypeId MG_cacheValue::typeId( 0x80010 );


void* MG_cacheValue::creator()
{

	return new MG_cacheValue();
}

MStatus MG_cacheValue::initialize()
	{ 
	  MFnNumericAttribute numFn;
	  
	  
	toCacheValue = numFn.create("toCacheValue","tcv",MFnNumericData::kDouble,0);
	numFn.setStorable(true);
	numFn.setKeyable(true);
	addAttribute(toCacheValue);
	
	
	cache = numFn.create("cache","ca",MFnNumericData::kDouble,0);
	numFn.setStorable(true);
	numFn.setKeyable(true);
	numFn.setArray(true);
	addAttribute(cache);	
	
	
	iterationStored = numFn.create("iterationStored","is",MFnNumericData::kLong,0);
	numFn.setStorable(true);
	numFn.setKeyable(true);
	addAttribute(iterationStored);	
	
	pastIterationOutIndex = numFn.create("pastIterationOutIndex","pii",MFnNumericData::kLong,1);
	numFn.setStorable(true);
	numFn.setKeyable(true);
	addAttribute(pastIterationOutIndex);	

	startFrame = numFn.create("startFrame","sf",MFnNumericData::kInt,0);
	numFn.setStorable(true);
	numFn.setKeyable(true);
	addAttribute(startFrame);	

	startFrameValue = numFn.create("startFrameValue","sfv",MFnNumericData::kDouble,0);
	numFn.setStorable(true);
	numFn.setKeyable(true);
	addAttribute(startFrameValue);

	time = numFn.create("time","ti",MFnNumericData::kInt,0);
	numFn.setStorable(true);
	numFn.setKeyable(true);
	addAttribute(time);	

	timeDriven = numFn.create("timeDriven","tid",MFnNumericData::kBoolean,0);
	numFn.setStorable(true);
	numFn.setKeyable(true);
	addAttribute(timeDriven);

	timeStored = numFn.create("timeStored","tis",MFnNumericData::kInt,0);
	numFn.setStorable(true);
	addAttribute(timeStored);

		  
	outValue = numFn.create("outValue","out",MFnNumericData::kDouble,0);
	numFn.setStorable(false);
	numFn.setKeyable(false);
	numFn.setWritable(false);
	addAttribute(outValue);	    


	attributeAffects (toCacheValue ,outValue);
	attributeAffects (iterationStored ,outValue);
	attributeAffects (iterationStored ,cache);
	attributeAffects (pastIterationOutIndex ,outValue);
	attributeAffects (startFrameValue ,outValue);
	attributeAffects (startFrame ,outValue);
	attributeAffects (time ,outValue);
	attributeAffects (timeDriven ,outValue);


	
		return MS::kSuccess;
	}

MStatus MG_cacheValue::compute(const MPlug& plug,MDataBlock& dataBlock)
	{

		int iterationStoredV = dataBlock.inputValue(iterationStored).asInt();
		MArrayDataHandle cacheH = dataBlock.inputValue(cache);
		int cacheSize = cacheH.elementCount ();
		double toCacheValueV =  dataBlock.inputValue(toCacheValue).asDouble();
		int pastIterationOutIndexV = dataBlock.inputValue(pastIterationOutIndex).asInt();
		MPlug cacheP(thisMObject(),cache);
		int timeV = dataBlock.inputValue(time).asInt();
		bool timeDrivenV = dataBlock.inputValue(timeDriven).asBool();
		int timeStoredV = dataBlock.inputValue(timeStored).asInt();
		int startFrameV = dataBlock.inputValue(startFrame).asInt();

		if (timeDrivenV == 1 )
		{
			if (timeStoredV == timeV)
			{
			//No time change
				return MS::kSuccess;
			
			}
			else 
			{
				//Check if time is == to start frame
				if ( timeV == startFrameV)
				{
					//Delete the cache
					double startFrameValueV = dataBlock.inputValue(startFrameValue).asDouble();
					MArrayDataHandle cacheH = dataBlock.outputArrayValue(cache);
					cacheH.jumpToArrayElement(0);
					for (int i = 0 ; i < cacheH.elementCount() ; i++ , cacheH.next())
					{
						MDataHandle outH = cacheH.outputValue();
						outH.set(startFrameValueV);
					
					}
				dataBlock.outputValue(timeStored).set(timeV);
				dataBlock.outputValue(outValue).set(startFrameValueV);
				dataBlock.outputValue(outValue).setClean();
				return MS::kSuccess;



				}
				
			}


		}

		//Loop based on the needed amount so to create the needed array indexs
		if (cacheSize<(iterationStoredV+1))
		{
		  for(int i=0;i<(iterationStoredV+1);++i)
		  {
			  
		    cacheP.selectAncestorLogicalIndex(i,cache);
		    MDataHandle pointHandle;
		    cacheP.getValue(pointHandle);
		    
		  }
		  
		}
		
		MDoubleArray cacheDouble , finalCache ;
		cacheDouble.setLength(iterationStoredV);
		finalCache.setLength(iterationStoredV);
		cacheH.jumpToArrayElement(0);
		//Reade back up the cache
		for (unsigned int i = 0 ; i < cacheH.elementCount(); i++ ,cacheH.next())
		{

		    
		  MDataHandle inH = cacheH.inputValue();
		  double cacheV = inH.asDouble();
		  
		  cacheDouble[i] = cacheV;
		  
		}
		
		cacheH.jumpToArrayElement(0);
		


		//Compute new cache
		MArrayDataHandle cacheOutH = dataBlock.outputValue(cache);
		cacheOutH.jumpToArrayElement(0);
		for (int i = 0 ; i <= iterationStoredV ; i++ ,cacheOutH.next())
		{
		    
		    if ( i != 0)
		    {
		      
		      finalCache[i] = cacheDouble[i-1];
		      
		      MDataHandle outH = cacheOutH.outputValue();
		      outH.set(finalCache[i]);
	
		    }else{
		      finalCache[0] = toCacheValueV;
		      
		      MDataHandle outH = cacheOutH.outputValue();
		      outH.set(finalCache[0]);
		      
		    }
		     	    
		    
		}
		if ( (pastIterationOutIndexV > 0 ) && (pastIterationOutIndexV < cacheSize) )
		{
		  
		  dataBlock.outputValue(outValue).set(finalCache[pastIterationOutIndexV]);
		}else{
		dataBlock.outputValue(outValue).set(finalCache[1]);
		}
		
	      dataBlock.outputValue(outValue).setClean();
			
			return MS::kSuccess;
	}

