"""Example usage script

import sim
s = sim.Simulator()
s.ToMinimize = 1
s.DumpAsText = 1
s.read("tests/rigid_organics/test_C6H10.mmp")
s.everythingElse()
"""

cdef extern from "simhelp.c":
    ctypedef struct SimArgs:
        char *printPotential
        double printPotentialInitial
        double printPotentialIncrement
        double printPotentialLimit
        int printPotentialEnergy
        char *ofilename
        char *tfilename
        char *filename
    # stuff from globals.c
    int debug_flags
    int Iteration
    int ToMinimize
    int IterPerFrame
    int NumFrames
    int DumpAsText
    int DumpIntermediateText
    int PrintFrameNums
    int OutputFormat
    int KeyRecordInterval
    int DirectEvaluate
    char *IDKey
    char *baseFilename
    double Dt
    double Dx
    double Dmass
    double Temperature
    # end of globals.c stuff
    SimArgs myArgs
    int initsimhelp()
    void readPart()
    void dumpPart()
    void everythingElse()
    cdef char *structCompareHelp()

class Simulator:
    """Pyrex permits access to doc strings"""

    def __getattr__(self, key):
        """Access to simulator's command line options and globals.c
        goodies
        """
        if key == "debug_flags":
            return debug_flags
        elif key == "Iteration":
            return Iteration
        elif key == "ToMinimize":
            return ToMinimize
        elif key == "IterPerFrame":
            return IterPerFrame
        elif key == "NumFrames":
            return NumFrames
        elif key == "DumpAsText":
            return DumpAsText
        elif key == "DumpIntermediateText":
            return DumpIntermediateText
        elif key == "PrintFrameNums":
            return PrintFrameNums
        elif key == "OutputFormat":
            return OutputFormat
        elif key == "KeyRecordInterval":
            return KeyRecordInterval
        elif key == "DirectEvaluate":
            return DirectEvaluate
        elif key == "IDKey":
            return IDKey
        elif key == "baseFilename":
            return baseFilename
        elif key == "Dt":
            return Dt
        elif key == "Dx":
            return Dx
        elif key == "Dmass":
            return Dmass
        elif key == "Temperature":
            return Temperature

    def __setattr__(self, key, value):
        """Access to simulator's command line options and globals.c
        goodies
        """
        if key == "debug_flags":
            global debug_flags
            debug_flags = value
        elif key == "Iteration":
            global Iteration
            Iteration = value
        elif key == "ToMinimize":
            global ToMinimize
            ToMinimize = value
        elif key == "IterPerFrame":
            global IterPerFrame
            IterPerFrame = value
        elif key == "NumFrames":
            global NumFrames
            NumFrames = value
        elif key == "DumpAsText":
            global DumpAsText
            DumpAsText = value
        elif key == "DumpIntermediateText":
            global DumpIntermediateText
            DumpIntermediateText = value
        elif key == "PrintFrameNums":
            global PrintFrameNums
            PrintFrameNums = value
        elif key == "OutputFormat":
            global OutputFormat
            OutputFormat = value
        elif key == "KeyRecordInterval":
            global KeyRecordInterval
            KeyRecordInterval = value
        elif key == "DirectEvaluate":
            global DirectEvaluate
            DirectEvaluate = value
        elif key == "IDKey":
            global IDKey
            IDKey = value
        elif key == "baseFilename":
            global baseFilename
            baseFilename = value
        elif key == "Dt":
            global Dt
            Dt = value
        elif key == "Dx":
            global Dx
            Dx = value
        elif key == "Dmass":
            global Dmass
            Dmass = value
        elif key == "Temperature":
            global Temperature
            Temperature = value

    def everythingElse(self):
        everythingElse()

    def read(self, filename,
             printPotentialInitial=1, # pm
             printPotentialIncrement=1, # pm
             printPotentialLimit=200, # pm
             printPotentialEnergy=0,
             printPotential="",
             ofilename="",
             tfilename=""):

        if not filename:
            raise Exception("Need a filename (probably MMP)")

        myArgs.printPotential = printPotential
        myArgs.printPotentialInitial = printPotentialInitial
        myArgs.printPotentialIncrement = printPotentialIncrement
        myArgs.printPotentialLimit = printPotentialLimit
        myArgs.printPotentialEnergy = printPotentialEnergy
        myArgs.printPotential = printPotential
        myArgs.ofilename = ofilename
        myArgs.tfilename = tfilename
        myArgs.filename = filename

        if initsimhelp():
            raise Exception, "please only run initsim() once!"
        readPart()

    def structCompare(self):
        r = structCompareHelp()
        if r:
            raise Exception, r
