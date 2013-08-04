#include <maya/MGlobal.h>
#include <maya/MFnPlugin.h>

#include "MG_extrudeEdge.h"


// init
MStatus initializePlugin( MObject obj )
{ 
	MStatus   status;
	MFnPlugin plugin( obj );
    status = plugin.registerNode( "MG_extrudeEdge", MG_extrudeEdge::typeId, MG_extrudeEdge::creator,
        MG_extrudeEdge::initialize);

	return status;
}

MStatus uninitializePlugin( MObject obj)
{
	MStatus   status;
	MFnPlugin plugin( obj );

    status = plugin.deregisterNode( MG_extrudeEdge::typeId );

	return status;
} 