# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_commands.py - UI commands offered directly by the dna updater.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from debug import register_debug_menu_command

from chem import _changed_structure_Atoms # but it's private! refactor sometime

import env

from utilities.Log import greenmsg

# ==

def initialize_commands():
    _register_our_debug_menu_commands()
    return

# ==

def rescan_atoms_in_current_part(assy, only_selected = False):
    oldlen = len(_changed_structure_Atoms)
    for mol in assy.molecules:
        for atom in mol.atoms.itervalues():
            if not only_selected or atom.picked or \
               (atom.is_singlet() and atom.singlet_neighbor().picked):
                _changed_structure_Atoms[atom.key] = atom
    newlen = len(_changed_structure_Atoms)
    msg = "len(_changed_structure_Atoms) %d -> %d" % (oldlen, newlen)
    env.history.message(greenmsg( "DNA debug command:") + " " + msg)
    return

def rescan_all_atoms(glpane):
    rescan_atoms_in_current_part( glpane.assy)

def rescan_selected_atoms(glpane):
    rescan_atoms_in_current_part( glpane.assy, only_selected = True)

def _register_our_debug_menu_commands():
    register_debug_menu_command( "DNA: rescan all atoms", rescan_all_atoms )
    register_debug_menu_command( "DNA: rescan selected atoms", rescan_selected_atoms )

# end