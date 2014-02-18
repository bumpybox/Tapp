#
#    ngSkinTools
#    Copyright (c) 2009-2013 Viktoras Makauskas. 
#    All rights reserved.
#    
#    Get more information at 
#        http://www.ngskintools.com
#        http://www.neglostyti.com
#    
#    --------------------------------------------------------------------------
#
#    The coded instructions, statements, computer programs, and/or related
#    material (collectively the "Data") in these files are subject to the terms 
#    and conditions defined by
#    Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License:
#        http://creativecommons.org/licenses/by-nc-nd/3.0/
#        http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode
#        http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode.txt
#         
#    A copy of the license can be found in file 'LICENSE.txt', which is part 
#    of this source code package.
#    

from ngSkinTools.mllInterface import MllInterface
from ngSkinTools.utils import MessageException
from ngSkinTools.log import LoggerFactory
from ngSkinTools.layerUtils import LayerUtils

log = LoggerFactory.getLogger("WeightsClipboard")
class WeightsClipboard:
    def __init__(self,mllInterface):
        self.copiedWeights = None
        self.mll = mllInterface
        self.layer = None
        self.influence = None
    

    def withCurrentLayerAndInfluence(self):
        self.layer = self.mll.getCurrentLayer()
        log.debug("weights clipboard setting current layer to %r" % self.layer)
        self.influence = self.mll.getCurrentPaintTarget()
        log.debug("weights clipboard setting current influence to %r" % self.influence)
        return self
    
    def getPaintTargetWeights(self,paintTarget):
        if paintTarget==LayerUtils.PAINT_TARGET_MASK:
            return self.mll.getLayerMask(self.layer)
        else:
            return self.mll.getInfluenceWeights(self.layer,paintTarget)

    def copy(self):
        self.copiedWeights = self.getPaintTargetWeights(self.influence)
        
        log.debug("copied weights: %r" % self.copiedWeights)
        if len(self.copiedWeights)==0:
            self.copiedWeights = None
            raise MessageException("Nothing copied")
    
    def cut(self):
        self.copy()
        self.mll.setInfluenceWeights(self.layer, self.influence, [0.0]*len(self.copiedWeights))
        
    
    def paste(self,replace):
        if self.copiedWeights == None:
            raise MessageException("Nothing to paste")
        
        if self.mll.getVertCount()!=len(self.copiedWeights):
            raise MessageException("Could not paste weights - vertex count does not match")
        
        newWeights =self.copiedWeights
        if not replace: 
            prevWeights = self.getPaintTargetWeights(self.influence)
            newWeights = [a+b for a,b in zip(newWeights,prevWeights)]
        
        if self.influence==LayerUtils.PAINT_TARGET_MASK:
            self.mll.setLayerMask(self.layer, newWeights)
        else:
            self.mll.setInfluenceWeights(self.layer, self.influence, newWeights)
        
