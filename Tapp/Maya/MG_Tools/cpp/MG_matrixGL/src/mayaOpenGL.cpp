#include "mayaOpenGL.h"


void mayaOpenGL::drawArrow( MVector vec  ,  MVector upVec , double arrowSizeV ,  MPoint startPointV )
 {
	
	vec.normalize();
	upVec.normalize();

	
	double tipX , tipY , tipZ, 
	      corner1X ,corner1Y ,corner1Z ,
	      corner2X ,corner2Y ,corner2Z ,
	      corner3X ,corner3Y ,corner3Z ,
	      corner4X ,corner4Y ,corner4Z ;
	
	double dot = vec*upVec;
	if (dot >= 0.99 )
	{
	  tipX=(0.0)+startPointV.x;
	  tipY=(1.0*arrowSizeV)+startPointV.y;
	  tipZ=(0.0)+startPointV.z;
	  
	  
	  corner1Y=(0.9*arrowSizeV)+startPointV.y;
	  corner1X=(0.05*arrowSizeV)+startPointV.x ;
	  corner1Z=(-0.05*arrowSizeV)+startPointV.z;
	  
	  
	  corner2Y=(0.9*arrowSizeV)+startPointV.y;
	  corner2X=(0.05*arrowSizeV)+startPointV.x;
	  corner2Z=(0.05*arrowSizeV)+startPointV.z;
	  
	  
	  corner3Y=(0.9*arrowSizeV)+startPointV.y;
	  corner3X=(-0.05*arrowSizeV)+startPointV.x;
	  corner3Z=(0.05*arrowSizeV)+startPointV.z;
	  
	  corner4Y=(0.9*arrowSizeV)+startPointV.y;
	  corner4X=(-0.05*arrowSizeV)+startPointV.x;
	  corner4Z=(-0.05*arrowSizeV)+startPointV.z;
	  
	  
	}//end if (dot >= 0.99 )
 	
 	else if (dot <= -0.99)
	{
	  tipX=(0.0)+startPointV.x;
	  tipY=(1.0*arrowSizeV*-1)+startPointV.y;
	  tipZ=(0.0)+startPointV.z;
	  
	  
	  corner1Y=(0.9*arrowSizeV*-1)+startPointV.y;
	  corner1X=(0.05*arrowSizeV)+startPointV.x ;
	  corner1Z=(-0.05*arrowSizeV)+startPointV.z;
	  
	  
	  corner2Y=(0.9*arrowSizeV*-1)+startPointV.y;
	  corner2X=(0.05*arrowSizeV)+startPointV.x;
	  corner2Z=(0.05*arrowSizeV)+startPointV.z;
	  
	  
	  corner3Y=(0.9*arrowSizeV*-1)+startPointV.y;
	  corner3X=(-0.05*arrowSizeV)+startPointV.x;
	  corner3Z=(0.05*arrowSizeV)+startPointV.z;
	  
	  corner4Y=(0.9*arrowSizeV*-1)+startPointV.y;
	  corner4X=(-0.05*arrowSizeV)+startPointV.x;
	  corner4Z=(-0.05*arrowSizeV)+startPointV.z;
	  
	  
	  
	}//else if (dot <= -0.99)
	
	else
	{
	  
	   MVector cross1Pos = vec^upVec;
	   cross1Pos.normalize();
	   MVector cross2Pos = cross1Pos^vec;
	   
	   MVector vecScaled = vec*0.9;
	   MVector corner1 = (((cross1Pos*0.07)+vecScaled)*arrowSizeV)+startPointV;
	   MVector corner2 = (((cross2Pos*0.07)+vecScaled)*arrowSizeV)+startPointV;
	   MVector corner3 = (((cross1Pos*0.07*-1)+vecScaled)*arrowSizeV)+startPointV;
	   MVector corner4 = (((cross2Pos*0.07*-1)+vecScaled)*arrowSizeV)+startPointV;
	   
	   corner1X = corner1.x;
	   corner1Y = corner1.y;
	   corner1Z = corner1.z;
	   
	   corner2X = corner2.x;
	   corner2Y = corner2.y;
	   corner2Z = corner2.z;
	   
	   corner3X = corner3.x;
	   corner3Y = corner3.y;
	   corner3Z = corner3.z;
	   
	   corner4X = corner4.x;
	   corner4Y = corner4.y;
	   corner4Z = corner4.z;
	   
	   tipX = (vec.x*arrowSizeV) +startPointV.x;
	   tipY = (vec.y*arrowSizeV)+startPointV.y;
	   tipZ = (vec.z*arrowSizeV)+startPointV.z;
	}// end else
	  
 	
	glBegin(GL_LINES);
		//draw the reader 
		glVertex3d(0+startPointV.x,0+startPointV.y,0+startPointV.z);
		glVertex3d(tipX,tipY,tipZ);
	glEnd();
	glBegin(GL_TRIANGLES);
		glVertex3d(corner1X,corner1Y,corner1Z);
		glVertex3d(corner2X,corner2Y,corner2Z);
		glVertex3d(tipX,tipY,tipZ);

	glEnd();

	glBegin(GL_TRIANGLES);
		glVertex3d(corner3X,corner3Y,corner3Z);
		glVertex3d(corner2X,corner2Y,corner2Z);
		glVertex3d(tipX,tipY,tipZ);

	glEnd();


	glBegin(GL_TRIANGLES);
		glVertex3d(corner3X,corner3Y,corner3Z);
		glVertex3d(corner4X,corner4Y,corner4Z);
		glVertex3d(tipX,tipY,tipZ);

	glEnd();

	glBegin(GL_TRIANGLES);
		glBegin(GL_TRIANGLES);
		glVertex3d(corner1X,corner1Y,corner1Z);
		glVertex3d(corner4X,corner4Y,corner4Z);
		glVertex3d(tipX,tipY,tipZ);

	glEnd();
 }


void    mayaOpenGL::drawText(const MString &text,const double* color, const MPoint &position,M3dView &view){

		glColor4d(color[0],color[1],color[2],1.0f);
		
		view.drawText( text, position, M3dView::kLeft );

}


void mayaOpenGL::drawSphere(const double r, const int lats, const int longs,const MVector position,const double* color)
 {
     int i, j;
        for(i = 0; i <= lats; i++) {
            double lat0 = M_PI * (-0.5 + (double) (i - 1) / lats);
           double z0  = sin(lat0);
           double zr0 =  cos(lat0);
    
           double lat1 = M_PI * (-0.5 + (double) i / lats);
           double z1 = sin(lat1);
           double zr1 = cos(lat1);
		   glColor4d(color[0],color[1],color[2],color[3]);
           glBegin(GL_QUAD_STRIP);
           for(j = 0; j <= longs; j++) {
               double lng = 2 * M_PI * (double) (j - 1) / longs;
               double x = cos(lng);
               double y = sin(lng);
    
			   glNormal3d((x * zr0*r)+position.x,( y * zr0*r)+position.y, (z0*r)+position.z);
               glVertex3d((x * zr0*r)+position.x, (y * zr0*r)+position.y, (z0*r)+position.z);
               glNormal3d((x * zr1*r)+position.x, (y * zr1*r)+position.y, (z1*r)+position.z);
               glVertex3d((x * zr1*r)+position.x, (y * zr1*r)+position.y, (z1*r)+position.z);
           }
           glEnd();
       }
   }

void mayaOpenGL::drawLine  (MPoint p1 ,MPoint p2,const double* color1, const double* color2)
{
		glBegin(GL_LINES);
		glColor4d(color1[0],color1[1],color1[2],1.0f);
		
		//draw the reader 
		glVertex3d(0+p1.x,0+p1.y,0+p1.z);
		
		glColor4d(color2[0],color2[1],color2[2],1.0f);
		glVertex3d(0+p2.x,0+p2.y,0+p2.z);
		glEnd();

}


void mayaOpenGL::stressLine (MPoint p1 ,MPoint p2 , double stress1 , double stress2)
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

	if (stress1>=1)
	{
		if (stress1>=2) 
		{
			glColor4d(red[0],red[1],red[2],1.0f);
		}
		else
		{
			double amount = stress1 - 1;
			glColor4d(red[0]*amount,red[1],red[2],1.0f);


		}
	}
	else
	{	
		if (stress1<=0.15) 
		{
			glColor4d(red[0],red[1],red[2],1.0f);
		}
		else
		{
			double amount = stress1 ;
			glColor4d(blue[0]*amount,blue[1]*amount,blue[2]*amount,1.0f);


		}
	}
	
	glBegin(GL_LINES);

		
	//draw the reader 
	glVertex3d(0+p1.x,0+p1.y,0+p1.z);
		

	if (stress2>=1)
	{
		if (stress2>=2) 
		{
			glColor4d(red[0],red[1],red[2],1.0f);
		}
		else
		{
			double amount = stress2 - 1;
			glColor4d(red[0]*amount,red[1],red[2],1.0f);


		}
	}
	else
	{	
		if (stress2<=0.15) 
		{
			glColor4d(red[0],red[1],red[2],1.0f);
		}
		else
		{
			double amount = stress2;
			glColor4d(blue[0]*amount,blue[1]*amount,blue[2]*amount,1.0f);


		}
	}




	glVertex3d(0+p2.x,0+p2.y,0+p2.z);
	glEnd();
	
}