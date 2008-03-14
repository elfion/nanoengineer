# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
SelectChunks_Command.py 

The 'Command' part of the Select Chunks Mode (SelectChunks_basicCommand and 
SelectChunks_basicGraphicsMode are the two split classes of the old 
selectMolsMode)  It provides the command object for its GraphicsMode class. 
The Command class defines anything related to the 'command half' of the mode -- 
For example: 
- Anything related to its current Property Manager, its settings or state
- The model operations the command does (unless those are so simple
  that the mouse event bindings in the _GM half can do them directly
  and the code is still clean, *and* no command-half subclass needs
  to override them).

@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.


TODO:
- Items mentioned in Select_GraphicsMode.py 
- Other items listed in Select_Command.py

History:
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from 
                          the old class selectMolsMode and moved the 
                          Command related methods into this class from 
                          selectMolsMode.py

"""
from commands.Select.Select_Command import Select_basicCommand
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from command_support.GraphicsMode_API import GraphicsMode_API

from model.chem import Atom
from model.chunk import Chunk
from model.bonds import Bond

class SelectChunks_basicCommand(Select_basicCommand):
    """
    The 'Command' part of the Select Chunks Mode (SelectChunks_basicCommand and 
    SelectChunks_basicGraphicsMode are the two split classes of the old 
    selectMolsMode)  It provides the command object for its GraphicsMode class. 
    The Command class defines anything related to the 'command half' of the 
    mode -- 
    For example: 
    - Anything related to its current Property Manager, its settings or state
    - The model operations the command does (unless those are so simple
      that the mouse event bindings in the _GM half can do them directly
      and the code is still clean, *and* no command-half subclass needs
      to override them).
    """
    commandName = 'SELECTMOLS'
    default_mode_status_text = "Mode: Select Chunks"
    featurename = "Select Chunks Mode"

    hover_highlighting_enabled = True
    
    def __init__(self, commandSequencer):
        """
        ...
        """
        Select_basicCommand.__init__(self, commandSequencer)
        return
    
    def Enter(self): 
        Select_basicCommand.Enter(self)           
        self.hover_highlighting_enabled = True

    def init_gui(self):
        """
        """
        self.w.toolsSelectMoleculesAction.setChecked(True)
 
    def restore_gui(self):
        """
        """
        self.w.toolsSelectMoleculesAction.setChecked(False)
    
    # moved here from modifyMode.  mark 060303.
    call_makeMenus_for_each_event = True
    #bruce 050914 enable dynamic context menus
    # [fixes an unreported bug analogous to 971]
    def makeMenus(self): # mark 060303.

        self.Menu_spec = []
        selobj = self.glpane.selobj
        highlightedChunk = None
        if isinstance(selobj, Chunk):
            highlightedChunk = selobj
        if isinstance(selobj, Atom):
            highlightedChunk = selobj.molecule
        elif isinstance(selobj, Bond):
            chunk1 = selobj.atom1.molecule
            chunk2 = selobj.atom2.molecule
            if chunk1 is chunk2 and chunk1 is not None:
                highlightedChunk = chunk1

        if highlightedChunk is not None:
            highlightedChunk.make_glpane_context_menu_items(self.Menu_spec,
                                                     command = self)
            

        if self.o.assy.selmols:
            # Menu items added when there are selected chunks.
            
            contextMenuList = [
                # These are marked for removal (toolbar commands now available).
                # --Mark 2008-03-10
                #@('Change Color of Selected Chunks...', 
                #@ self.w.dispObjectColor),
                #@('Reset Color of Selected Chunks', 
                #@ self.w.dispResetChunkColor),
                ('Reset Atoms Display of Selected Chunks', 
                 self.w.dispResetAtomsDisplay),
                ('Show Invisible Atoms of Selected Chunks', 
                 self.w.dispShowInvisAtoms),
                ('Hide Selected Chunks', self.o.assy.Hide),
            ]
            
            self.Menu_spec.extend(contextMenuList)

        # Enable/Disable Jig Selection.
        # This is duplicated in depositMode.makeMenus().
        if self.o.jigSelectionEnabled:
            self.Menu_spec.extend( [('Enable Jig Selection',  
                                     self.graphicsMode.toggleJigSelection, 
                                     'checked')])
        else:
            self.Menu_spec.extend( [('Enable Jig Selection',  
                                     self.graphicsMode.toggleJigSelection, 
                                     'unchecked')])

        self.Menu_spec.extend( [
            # mark 060303. added the following:
            None,
            ('Change Background Color...', self.w.changeBackgroundColor),
        ])

        self.debug_Menu_spec = [
            ('debug: invalidate selection', self.invalidate_selection),
            ('debug: update selection', self.update_selection),
        ]

    # moved here from modifyMode.  mark 060303.
    def invalidate_selection(self): #bruce 041115 (debugging method)
        """
        [debugging method] invalidate all aspects of selected atoms or mols
        """
        for mol in self.o.assy.selmols:
            print "already valid in mol %r: %r" % (mol, mol.invalid_attrs())
            mol.invalidate_everything()
        for atm in self.o.assy.selatoms.values():
            atm.invalidate_everything()

    # moved here from modifyMode.  mark 060303.
    def update_selection(self): #bruce 041115 (debugging method)
        """
        [debugging method] update all aspects of selected atoms or mols;
        no effect expected unless you invalidate them first
        """
        for atm in self.o.assy.selatoms.values():
            atm.update_everything()
        for mol in self.o.assy.selmols:
            mol.update_everything()
        return

class SelectChunks_Command(SelectChunks_basicCommand):
    """
    @see: B{SelectChunks_basicCommand}
    @see: cad/doc/splitting_a_mode.py
    """
    GraphicsMode_class = SelectChunks_GraphicsMode
    
    def __init__(self, commandSequencer):
        SelectChunks_basicCommand.__init__(self, commandSequencer)
        self._create_GraphicsMode()
        self._post_init_modify_GraphicsMode()
        return
        
    def _create_GraphicsMode(self):
        GM_class = self.GraphicsMode_class
        assert issubclass(GM_class, GraphicsMode_API)
        args = [self] 
        kws = {} 
        self.graphicsMode = GM_class(*args, **kws)

    def _post_init_modify_GraphicsMode(self):
        pass
    
