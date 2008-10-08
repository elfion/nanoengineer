# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
TestGraphics_Command.py -- command to "Test Graphics Performance"
(for now, available from the debug menu -> 'other' submenu)

@author:    Bruce
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from commands.SelectAtoms.SelectAtoms_GraphicsMode import SelectAtoms_GraphicsMode
from commands.SelectAtoms.SelectAtoms_Command import SelectAtoms_Command
from commands.TestGraphics.TestGraphics_PropertyManager import TestGraphics_PropertyManager

from utilities.debug import register_debug_menu_command

# module imports, for global flag set/get access
import graphics.widgets.GLPane_rendering_methods as GLPane_rendering_methods
import prototype.test_drawing as test_drawing

from prototype.test_drawing import AVAILABLE_TEST_CASES_ITEMS

import foundation.env as env

from utilities.prefs_constants import levelOfDetail_prefs_key


# == GraphicsMode part

class TestGraphics_GraphicsMode(SelectAtoms_GraphicsMode ):
    """
    Graphics mode for TestGraphics command. 
    """
    pass

# == Command part

class TestGraphics_Command(SelectAtoms_Command): 
    """

    """
       
    # class constants
    GraphicsMode_class = TestGraphics_GraphicsMode
    PM_class = TestGraphics_PropertyManager
    
    commandName = 'TEST_GRAPHICS'
    featurename = "Test Graphics"
    from utilities.constants import CL_GLOBAL_PROPERTIES
    command_level = CL_GLOBAL_PROPERTIES
   

    command_should_resume_prevMode = True 
    command_has_its_own_PM = True

    FlyoutToolbar_class = None
        # minor bug, when superclass is Build Atoms: the atoms button in the
        # default flyout remains checked when we enter this command,
        # probably due to command_enter_misc_actions() not being overridden in
        # this command.


    # state methods (which mostly don't use self, except for self.glpane.gl_update)
    
    # note: these use property rather than State since they are providing access
    # to externally stored state. This is ok except that it provides no direct
    # way of usage tracking or change tracking, which means, it's only suitable
    # when only one external thing at a time wants to provide a UI for displaying
    # and perhaps changing this state.

    # bypass_paintgl

    def _get_bypass_paintgl(self):
        print "bypass_paintgl starts out as %r" % (GLPane_rendering_methods.TEST_DRAWING,) #
        return GLPane_rendering_methods.TEST_DRAWING

    def _set_bypass_paintgl(self, enabled):
        print "bypass_paintgl = %r" % (enabled,) #
        GLPane_rendering_methods.TEST_DRAWING = enabled
        if enabled:
            # BUG in test_drawing.py as of 081008
            # on systems with not enough shader constant memory:
            # even in a test case that doesn't use shaders, eg testCase 1,
            # an error in setting up shaders makes the test fail;
            # trying again gets past this somehow. Print warning about this:
            print "\n*** bug workaround: if shader error traceback occurs, disable and reenable to retry ***\n" ###
        self.glpane.gl_update()

    bypass_paintgl = property( _get_bypass_paintgl,
                               _set_bypass_paintgl,
                               doc = "bypass paintGL normal code"
                                     "(draw specific test cases instead)"
                             )

    # redraw_continuously
    
    def _get_redraw_continuously(self):
        return test_drawing.ALWAYS_GL_UPDATE

    def _set_redraw_continuously(self, enabled):
        test_drawing.ALWAYS_GL_UPDATE = enabled
        self.glpane.gl_update()

    redraw_continuously = property( _get_redraw_continuously,
                                    _set_redraw_continuously,
                                    doc = "call paintGL continuously"
                                          "(cpu can get hot!)"
                                  )

    # spin_model
    
    def _get_spin_model(self):
        return test_drawing.SPIN

    def _set_spin_model(self, enabled):
        test_drawing.SPIN = enabled

    spin_model = property( _get_spin_model,
                           _set_spin_model,
                           doc = "spin model whenever it's redrawn"
                         )

    # print_fps
    
    def _get_print_fps(self):
        return test_drawing.printFrames

    def _set_print_fps(self, enabled):
        test_drawing.printFrames = enabled

    print_fps = property( _get_print_fps,
                           _set_print_fps,
                           doc = "print frames-per-second to console every second"
                         )

    # testCaseIndex, testCaseChoicesText
    
    def _get_testCaseIndex(self):
        for testCase, desc in AVAILABLE_TEST_CASES_ITEMS:
            if test_drawing.testCase == testCase:
                return AVAILABLE_TEST_CASES_ITEMS.index((testCase, desc))
        print "bug in _get_testCaseIndex"
        return 0 # fallback to first choice

    def _set_testCaseIndex(self, index): # BUG: doesn't yet work well when done during a test run
        testCase, desc_unused = AVAILABLE_TEST_CASES_ITEMS[index]
        test_drawing.testCase = testCase
        test_drawing.delete_caches()
        self.glpane.gl_update()

    testCaseIndex = property( _get_testCaseIndex,
                             _set_testCaseIndex,
                             doc = "which testCase to run"
                            )

    testCaseChoicesText = []
    for testCase, desc in AVAILABLE_TEST_CASES_ITEMS:
        testCaseChoicesText.append( "%s: %s" % (testCase, desc) ) # fix format

    # nSpheres
    
    def _get_nSpheres(self):
        return test_drawing.nSpheres

    def _set_nSpheres(self, value):
        test_drawing.nSpheres = value
        test_drawing.delete_caches()
        self.glpane.gl_update()

    nSpheres = property( _get_nSpheres,
                           _set_nSpheres,
                           doc = "number on a side of a square of spheres"
                         )

    _NSPHERES_CHOICES = map(str, [1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        
    # detailLevel

    def _get_detailLevel(self):
        # note: this might not agree, initially, with env.prefs[levelOfDetail_prefs_key];
        # doesn't matter for now, since nothing calls this getter
        return test_drawing.DRAWSPHERE_DETAIL_LEVEL

    def _set_detailLevel(self, detailLevel):

        if detailLevel not in (0, 1, 2, -1):
            print "bug: illegal detailLevel", detailLevel
            detailLevel = -1
        
        env.prefs[levelOfDetail_prefs_key] = detailLevel

        if detailLevel != -1:
            ### kluges/bugs:
            # maybe not synced at init;
            # -1 should be disallowed in combobox when test_drawing is used;
            # not known for sure how this works in test_drawing --
            # maybe it doesn't work for all testCases; conceivably it depends on env.prefs too
            test_drawing.DRAWSPHERE_DETAIL_LEVEL = detailLevel

        test_drawing.delete_caches()
        
        self.glpane.gl_update()
        # when not bypassing paintGL:
            # this gl_update is redundant with the prefs change;
            # the redraw this causes will (as of tonight) always recompute the
            # correct drawLevel (in Part._recompute_drawLevel),
            # and chunks will invalidate their display lists as needed to
            # accomodate the change. [bruce 060215]
        # otherwise, explicit gl_update iight be needed.
        return

    detailLevel = property( _get_detailLevel,
                             _set_detailLevel,
                             doc = "detail level of spheres (when made of triangles)"
                            )
        
    pass
    
# == UI for entering this command

def _enter_test_graphics_command(glpane):
    glpane.assy.w.enterOrExitTemporaryCommand('TEST_GRAPHICS')

register_debug_menu_command( "Test Graphics Performance ...", _enter_test_graphics_command )

# or for entering at startup due to debug_pref:

def enter_TestGraphics_Command_at_startup(win):
    """
    Meant to be called only from startup_misc.just_before_event_loop().
    To cause this to be called then (in current code as of 081006),
    set the debug_pref "startup in Test Graphics command (next session)?".
    """
    # set properties the way we want them (from globals in test_drawing module).
    # KLUGE: this has to be done before entering command, so UI in
    # command.propMgr is set up properly.
    from prototype import test_drawing
    cached_command_instance = win.commandSequencer._find_command_instance( 'TEST_GRAPHICS')
    cached_command_instance.bypass_paintgl = True
    cached_command_instance.nSpheres = test_drawing.nSpheres
    
    win.commandSequencer.userEnterCommand('TEST_GRAPHICS')
    currentCommand = win.commandSequencer.currentCommand
    if currentCommand.commandName == 'TEST_GRAPHICS':
        win.update() # try to make sure new PM becomes visible (BUG: doesn't
            # work, requires click to make PM show up; don't know why ###)
        print "\n*** bug workaround: click in GLPane to show Test Graphics PM ***" ###
    else:
        print "bug: tried to startup in %r, but currentCommand.commandName == %r" % \
              ('TEST_GRAPHICS', currentCommand.commandName)
    return

# end