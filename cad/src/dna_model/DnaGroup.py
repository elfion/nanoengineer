# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaGroup.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_model.Block import Block

from icon_utilities import imagename_to_pixmap

# Following import is disabled. See addSegment method for reason.
## from dna_model.DnaSegment import DnaSegment

class DnaGroup(Block):
    """
    Model object which packages together some Dna Segments, Dna Strands,
    and other objects needed to represent all their PAM atoms and markers.

    The contents are not directly visible to the user in the model tree,
    except for Blocks (fyi, this behavior comes from our Block superclass,
    which is a kind of Group).
    
    But internally, most of the contents are Nodes which can be stored
    in mmp files, copied, and undo-scanned in the usual ways.

    Specific kinds of Group member contents include:
    - DnaStrands (optionally inside Blocks)
    - DnaSegments (ditto)
    - Blocks (a kind of Group)
    - DnaMarkers (a kind of Jig, probably always inside an owning
      DnaStrand or DnaSegment)
    - specialized chunks for holding PAM atoms:
      - DnaAxisChunk (undecided whether these will live inside DnaSegments
        they belong to, but probably they will)
      - DnaStrandChunk (undecided whether these will live inside their
        DnaStrands, but probably they will)

    As other attributes:
    - whatever other properties the user needs to assign, which are not
      covered by the member nodes or superclass attributes.
    """
    
    # The iconPath specifies path(string) of an icon that represents the 
    # objects of this class  
    iconPath = "modeltree/DNA.png"

    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    _mmp_group_classifications = ('DnaGroup',)
    
    # Open/closed state of the Dna Group in the Model Tree --
    # default closed. Note: this is ignored by the Model Tree code
    # (since we inherit from Block), but whether it affects any other code
    # (e.g. a PM display widget) is not yet decided.
    open = False
    
    def node_icon(self, display_prefs):
        """
        Model Tree node icon for the dna group node
        """
        del display_prefs # unused
        return imagename_to_pixmap( self.iconPath)

    def makeStrandOrSegmentForMarker(self, controlling_marker, wholechain): # IMPLEM @@@@
        """
        The given DnaMarker is either newly made to control wholechain,
        or old but newly controlling it; but it has no DnaStrandOrSegment.
        
        Make and return a new DnaStrand or DnaSegment
        (ask wholechain or marker what class to use)
        inside self (review: inside some Block?),
        perhaps making use of info in controlling_marker
        to help decide how to initialize some of its attributes.
        
        (Assume calling code will later move all chunks
        and markers from wholechain into the new object,
        and will store references to it as needed
        into controlling_marker and/or wholechain,
        so don't do those things here.)
        """
        assert 0, "nim"
    
    # Note: some methods below this point are examples or experiments or stubs,
    # and are likely to be revised significantly or replaced.
    # [bruce 080115 comment]
    
    # example method:
    def get_segments(self):
        """
        Return a list of all our DnaSegment objects.
        """
        return self.get_topmost_subnodes_of_class('DnaSegment')
            # note: as of 080115 get_topmost_subnodes_of_class is implemented
            # for class args, but only for a few string args (including 'DnaSegment'),
            # and is untested. String args are useful for avoiding import cycles.

    def addSegment(self, segment):
        """
        Adds a new segment object for this dnaGroup.
        
        @param segment: The DnaSegment to be added to this DnaGroup object
        @type: B{DnaSegment}  
        """
        # importing DnaSegment created an import cycle which throws error. 
        # So this isinstance check is disabled for now.
        ## assert isinstance(segment, DnaSegment)
        
        self.addchild(segment)

    def getProps(self):
        """
	Method to support Dna duplex editing. see Group.__init__ for 
	a comment
        
        THIS IS THE DEFAULT IMPLEMENTATION. TO BE MODIFIED
	"""
        #Should it supply the Dna Segment list (children) and then add 
        #individual segments when setProps is called??
        # [probably not; see B&N email discussion from when this comment was added]
        if self.editCommand:
            props = ()
            return props

    def setProps(self, props):
        """
	Method  to support Dna duplex editing. see Group.__init__ for 
	a comment
        THIS IS THE DEFAULT IMPLEMENTATION. TO BE MODIFIED
	"""
        #Should it accept the Dna Segment list and then add individual segments?
        pass
    
    def edit(self):
        """
        @see: Group.edit()
        """
        commandSequencer = self.assy.w.commandSequencer
        commandSequencer.userEnterCommand('BUILD_DNA')
        currentCommand = commandSequencer.currentCommand
        assert currentCommand.commandName == 'BUILD_DNA'
        currentCommand.editStructure(self)

    pass # end of class DnaGroup

# end
