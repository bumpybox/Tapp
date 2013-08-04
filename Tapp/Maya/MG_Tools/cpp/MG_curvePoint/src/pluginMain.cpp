#include <maya/MGlobal.h>
#include <maya/MFnPlugin.h>

#include "MG_curvePoint.h"


// init
MStatus initializePlugin( MObject obj )
{ 
	MStatus   status;
	MFnPlugin plugin( obj );
    status = plugin.registerNode( "MG_curvePoint", MG_curvePoint::typeId, MG_curvePoint::creator,
        MG_curvePoint::initialize);

	return status;
}

MStatus uninitializePlugin( MObject obj)
{
	MStatus   status;
	MFnPlugin plugin( obj );

    status = plugin.deregisterNode( MG_curvePoint::typeId );

	return status;
}