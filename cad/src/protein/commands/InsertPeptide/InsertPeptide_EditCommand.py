# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Piotr, Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
2008-07-24: Created

"""

from utilities.Log  import greenmsg
from command_support.EditCommand import EditCommand
from protein.commands.InsertPeptide.PeptideGenerator import PeptideGenerator
from utilities.constants import gensym
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from protein.temporary_commands.PeptideLine_GraphicsMode import PeptideLine_GraphicsMode
from utilities.debug import print_compact_stack, print_compact_traceback

import foundation.env as env
from utilities.prefs_constants import cursorTextColor_prefs_key

from protein.commands.BuildProtein.BuildProtein_Command import BuildProtein_Command
from protein.commands.InsertPeptide.InsertPeptide_PropertyManager import InsertPeptide_PropertyManager

_superclass = EditCommand
class InsertPeptide_EditCommand(EditCommand):

    PM_class = InsertPeptide_PropertyManager
    
    cmd              =  greenmsg("Insert Peptide: ")
    prefix           =  'Peptide'   # used for gensym
    cmdname          = 'Insert Peptide'

    commandName      = 'INSERT_PEPTIDE'
    featurename      = "Insert Peptide"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_PROTEIN'

    create_name_from_prefix  =  True 
    
    GraphicsMode_class = PeptideLine_GraphicsMode
    #required by PeptideLine_GraphicsMode
    mouseClickPoints = []
    
    structGenerator = PeptideGenerator()
    
    command_should_resume_prevMode = True
    command_has_its_own_PM = True

    def __init__(self, commandSequencer):
        """
        Constructor for InsertPeptide_EditCommand
        """
        _superclass.__init__(self, commandSequencer)        
        #Maintain a list of peptides created while this command is running. 
        self._peptideList = []
        return
        
    def command_entered(self):
        """
        Extends superclass method. 
        @see: basecommand.command_entered() for documentation
        """
        _superclass.command_entered(self)
        #NOTE: Following code was copied from self.init_gui() that existed 
        #in old command API -- Ninad 2008-09-18
        if isinstance(self.graphicsMode, PeptideLine_GraphicsMode):            
            self._setParamsForPeptideLineGraphicsMode()
            self.mouseClickPoints = []
        #Clear the peptideList as it may still be maintaining a list of peptides
        #from the previous run of the command. 
        self._peptideList = []                    
        ss_idx, self.phi, self.psi, aa_type = self._gatherParameters()
        return
        
    def command_will_exit(self):
        """
        Extends superclass method. 
        @see: basecommand.command_will_exit() for documentation
        """
        if isinstance(self.graphicsMode, PeptideLine_GraphicsMode):
                self.mouseClickPoints = []    
        self.graphicsMode.resetVariables()   
        self._peptideList = []
        
        _superclass.command_will_exit(self)
        return
    
    def _getFlyoutToolBarActionAndParentCommand(self):
        """
        See superclass for documentation.
        @see: self.command_update_flyout()
        """
        flyoutActionToCheck = 'buildPeptideAction'
        parentCommandName = 'BUILD_PROTEIN'
        return flyoutActionToCheck, parentCommandName
                
    def keep_empty_group(self, group):
        """
        Returns True if the empty group should not be automatically deleted. 
        otherwise returns False. The default implementation always returns 
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True. 
        (and as of 2008-03-06, it is proposed that cnt_updater calls this method
        when needed. 
        @see: Command.keep_empty_group() which is overridden here. 
        """

        bool_keep = _superclass.keep_empty_group(self, group)
        return bool_keep
        
    def _gatherParameters(self):
        """
        Return the parameters from the property manager.
        """
        return self.propMgr.getParameters()  
    
    def runCommand(self):
        """
        Overrides EditCommand.runCommand
        """
        self.struct = None
        return
    
    def _createStructure(self):        
        """
        Build a peptide from the parameters in the Property Manager.
        """
        
        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix, self.win.assy) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name
            
        self.secondary, self.phi, self.psi, aa_type = self._gatherParameters()
        
        #
        self.win.assy.part.ensure_toplevel_group()
        """
        struct = self.structGenerator.make(self.win.assy,
                                           name, 
                                           params, 
                                           -self.win.glpane.pov)
        """                                   
        from geometry.VQT import V
        pos1 = V(self.mouseClickPoints[0][0], \
                 self.mouseClickPoints[0][1], \
                 self.mouseClickPoints[0][2])
        pos2 = V(self.mouseClickPoints[1][0], \
                 self.mouseClickPoints[1][1], \
                 self.mouseClickPoints[1][2])
        struct = self.structGenerator.make_aligned(self.win.assy, 
                                                   name, 
                                                   aa_type, 
                                                   self.phi, 
                                                   self.psi, 
                                                   pos1, 
                                                   pos2, 
                                                   fake_chain = False, 
                                                   secondary = self.secondary)
        
        self.win.assy.part.topnode.addmember(struct)
        self.win.win_update()
        return struct
    
    def _modifyStructure(self, params):
        """
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. 
        See more comments in this method.
        """
        
        #@NOTE: Unlike editcommands such as Plane_EditCommand or 
        #DnaSegment_EditCommand this  actually removes the structure and
        #creates a new one when its modified. 
        #TODO: Change this implementation to make it similar to whats done 
        #iin DnaSegment resize. (see DnaSegment_EditCommand)
        self._removeStructure()

        self.previousParams = params

        self.struct = self._createStructure()
        return
    
    def cancelStructure(self):
        """
        Overrides Editcommand.cancelStructure. Calls _removePeptides which 
        deletes all the peptides created while this command was running.
        @see: B{EditCommand.cancelStructure}
        """
        _superclass.cancelStructure(self)
        self._removePeptides()
        return

    def _removePeptides(self):
        """
        Deletes all the peptides created while this command was running
        @see: L{self.cancelStructure}
        """
        peptideList = self._peptideList

        #for peptide in peptideList: 
            #can peptide be None?  Lets add this condition to be on the safer 
            #side.
        #    if peptide is not None: 
        #        peptide.kill_with_contents()
        #    self._revertNumber()

        self._peptideList = []	
        self.win.win_update()
        return
    
    def createStructure(self):
        """
        Overrides superclass method. Creates the structure 

        """        
        assert self.propMgr is not None

        if self.struct is not None:
            self.struct = None

        self.win.assy.part.ensure_toplevel_group()
        self.propMgr.endPoint1 = self.mouseClickPoints[0]
        self.propMgr.endPoint2 = self.mouseClickPoints[1]
        
        #ntLength = vlen(self.mouseClickPoints[0] - self.mouseClickPoints[1])

        self.preview_or_finalize_structure(previewing = True)

        #Now append this peptide to self._peptideList 
        self._peptideList.append(self.struct)

        #clear the mouseClickPoints list
        self.mouseClickPoints = [] 
        self.graphicsMode.resetVariables()    
        return
    
    def _finalizeStructure(self):
        """
        Finalize the structure. This is a step just before calling Done method.
        to exit out of this command. Subclasses may overide this method
        @see: EditCommand_PM.ok_btn_clicked
        """
        
        if len(self.mouseClickPoints) == 1:
            return
        else:
            _superclass._finalizeStructure(self)
        return
    
            
    def _getStructureType(self):
        """
        Subclasses override this method to define their own structure type. 
        Returns the type of the structure this editCommand supports. 
        This is used in isinstance test. 
        @see: EditCommand._getStructureType() (overridden here)
        """

        return self.win.assy.Chunk

    def _setParamsForPeptideLineGraphicsMode(self):
        #"""
        #Needed for PeptideLine_GraphicsMode (NanotubeLine_GM). The method names need to
        #be revised (e.g. callback_xxx. The prefix callback_ was for the earlier 
        #implementation of CntLine mode where it just used to supply some 
        #parameters to the previous mode using the callbacks from the 
        #previous mode. 
        #"""
        self.mouseClickLimit = None
        self.jigList = self.win.assy.getSelectedJigs()
        self.callbackMethodForCursorTextString = self.getCursorText
        self.callbackForSnapEnabled = self.isRubberbandLineSnapEnabled
        self.callback_rubberbandLineDisplay = self.getDisplayStyleForNtRubberbandLine
        return
    
    def getCursorText(self, endPoint1, endPoint2):
        """
        This is used as a callback method in PeptideLineLine mode 
        @see: PeptideLine_GraphicsMode.setParams, PeptideLine_GraphicsMode.Draw
        """
        
        text = ''
        textColor = env.prefs[cursorTextColor_prefs_key]
        
        if endPoint1 is None or endPoint2 is None:
            return text, textColor
        
        vec = endPoint2 - endPoint1
        from geometry.VQT import vlen
        peptideLength = vlen(vec)
        ss_idx, phi, psi, aa_type = self._gatherParameters()
        peptideLength = self.structGenerator.get_number_of_res(endPoint1, endPoint2, phi, psi)
        lengthString = self._getCursorText_length(peptideLength)
        
        thetaString = ''
        #Urmi 20080804: not sure if angle will be required later
        theta = self.glpane.get_angle_made_with_screen_right(vec)
        thetaString = '%5.2f deg'%theta
                        
        commaString = ", "
        
        text = lengthString

        if text and thetaString:
            text += commaString

        text += thetaString
        
        return text, textColor
    
    
    def _getCursorText_length(self, peptideLength):
        """
        Returns a string that gives the length of the Peptide for the cursor 
        text.
        
        @param peptideLength: length of the peptide (number of amino acids)
        @type peptideLength: int
        """

        # This should be moved to more appropriate place. piotr 081308
        self.secondary, self.phi, self.psi, aa_type = self._gatherParameters()
        
        peptideLengthString = ''
        
        lengthUnitString = 'AA'
        #change the unit of length to nanometers if the length is > 10A
        #fixes part of bug 2856
        
        peptideLengthString = "%d%s"%(peptideLength, lengthUnitString)
    
        return peptideLengthString
    
    def getDisplayStyleForNtRubberbandLine(self):
        """
        This is used as a callback method in peptideLine mode. 
        @return: The current display style for the rubberband line. 
        @rtype: string
        @note: Placeholder for now
        """
        return 'Ladder'
    
    def isRubberbandLineSnapEnabled(self):
        """
        This returns True or False based on the checkbox state in the PM.

        This is used as a callback method in CntLine mode (NanotubeLine_GM)
        @see: NanotubeLine_GM.snapLineEndPoint where the boolean value returned from
              this method is used
        @return: Checked state of the linesnapCheckBox in the PM
        @rtype: boolean
        @note: placeholder for now
        """
        return True
        
