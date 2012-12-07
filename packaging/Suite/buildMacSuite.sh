#!/bin/sh -x

# Usage: Run ./buildWinSuite.sh from the Suite directory in packaging.


# Set control variable to build packages if they are not build already
# This will probably be removed later as it was only added for testing
BUILD_IF_UNBUILT=1

# Set up path variables
PKNG_DIR=`pwd`
cd ../..
TOP_LEVEL=`pwd`

# set up a directory to store pre-built stuff
if [ ! -e ~/MacOSX_Installers ]
then
  mkdir ~/MacOSX_Installers
fi

# set up package version information
if [ -x $PKNG_DIR/ver_info.sh ]
then
  . $PKNG_DIR/ver_info.sh
  VERSION_NUM=$NE1_VERSION
  GROMACS_VERSION=$GMX_VERSION
  QUTEMOLX_VERSION=$QMX_VERSION
  PREF_VER=$PREF_VERSION
else
  VERSION_NUM="1.1.1"
  GROMACS_VERSION="3.3.3"
  QUTEMOLX_VERSION="0.5.1"
  PREF_VER="0.0.2"
fi
RC_NUMBER="0"

DATECODE=`date "+%B %d, %Y"`

# Do a basic check for sanity in the build area.
if [ ! -e "$TOP_LEVEL/cad/src" ]
then
  echo "The build directories are not valid"
  exit 1
fi

# Check to see if the smaller packages are built

# Start with Pref_Mod since it's easy to build
cd $TOP_LEVEL
# this check is to see if we've already run Pref_Mod for this tree
if [ ! -e ~/MacOSX_Installers/pref_modifier.pkg ]
then
  if [ $BUILD_IF_UNBUILT -ne 0 ]
  then
#   All clear to do the build
    cd packaging/Pref_Mod
    ./buildMac.sh $PREF_VER || exit 1
  else
    echo "Build Pref_Mod before continuing"
    exit 1
  fi
fi


# Build section for QuteMolX

if [ ! -e ~/MacOSX_Installers/QuteMolX_$QUTEMOLX_VERSION.pkg ]
then
  if [ $BUILD_IF_UNBUILT -ne 0 ]
  then
    cd $TOP_LEVEL/cad/plugins/QuteMol/packaging
    ./buildMac.sh $QUTEMOLX_VERSION
    if [ "$?" != "0" ]
    then
      echo "Error in the QuteMolX build, investigate."
      exit 1
    fi
  fi
fi
# The build will normally handle this, but if the files used are pre-builds,
# the build does not store the readme and license.  (Needed for Suite)
#cp $TOP_LEVEL/cad/plugins/QuteMol/packaging/Win32/License.txt /c/QMX_Install || exit 1
#cp $TOP_LEVEL/cad/plugins/QuteMol/packaging/ReadMe.html /c/QMX_Install || exit 1

# End of build section for QuteMolX

cd $TOP_LEVEL

# Build section for GROMACS

if [ ! -e ~/MacOSX_Installers/GROMACS_$GROMACS_VERSION.pkg ]
then
  if [ $BUILD_IF_UNBUILT -ne 0 ]
  then
    cd $TOP_LEVEL/cad/plugins/GROMACS/gromacs-$GROMACS_VERSION/packaging
    ./buildMac.sh $GROMACS_VERSION
    if [ "$?" != "0" ]
    then
      echo "Error in the GROMACS build, investigate."
      exit 1
    fi
  fi
fi
# The build will normally handle this, but if the files used are pre-builds,
# the build does not store the readme and license.  (Needed for Suite)
#cp $TOP_LEVEL/cad/plugins/GROMACS/gromacs-$GROMACS_VERSION/packaging/Win32/License.txt /c/GMX_Install
#cp $TOP_LEVEL/cad/plugins/GROMACS/gromacs-$GROMACS_VERSION/packaging/ReadMe.html /c/GMX_Install

# End of GROMACS build section

cd $TOP_LEVEL

# Build section for NE1

#Check for an NE1 build
cd $TOP_LEVEL
if [ ! -e ~/MacOSX_Installers/NanoEngineer-1_v$VERSION_NUM.pkg ]
then
  if [ $BUILD_IF_UNBUILT -ne 0 ]
  then
#   Set version information for NE1
    cat packaging/buildMac.sh | sed -e "s:^VERSION_NUM=.*:VERSION_NUM=\\\"$VERSION_NUM\\\":" | sed -e "s:^RC_NUMBER=.*:RC_NUMBER=\\\"$RC_NUMBER\\\":" > packaging/buildMac.sh.tmp
    mv packaging/buildMac.sh.tmp packaging/buildMac.sh || exit 1
    cd packaging
#   Set up the environment variables for the build 
    export CPPFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include -I/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/include"
    export CFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include -I/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/include"
    export LDFLAGS="-Wl,-syslibroot,/Developer/SDKs/MacOSX10.4u.sdk -isysroot /Developer/SDKs/MacOSX10.4u.sdk -L/usr/local/lib -L/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/lib"
    export CXXFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include -I/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/include"
    export FFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include -I/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/include"
    export MACOSX_DEPLOYMENT_TARGET=10.3
    chmod 755 ./buildMac.sh
    ./buildMac.sh
    if [ "$?" != "0" ]
    then
      echo "Error in the NE1 Build, investigate"
      exit 1
    fi
  else
    echo "Build NE1 before continuing"
    exit 1
  fi
fi  

cd $TOP_LEVEL

# Made it this far, continue building the suite.  Mod the suite installer files
cd $PKNG_DIR
cd MacOSX
# create a blank metapackages directory directory for the build
sudo rm -rf metapackage
mkdir metapackage || exit 1
mkdir metapackage/packages || exit 1
mkdir metapackage/extras || exit 1
# grab the packages that make up the build and rename them to what the build 
# expects them to be.  Basically stripping off version numbers
if [ -e ~/MacOSX_Installers ]
then
# use the versions in the pre-built area if possible
  cd metapackage/packages || exit 1
  sudo cp -R ~/MacOSX_Installers/NanoEngineer-1_v$VERSION_NUM.pkg . || exit 1
  sudo mv NanoEngineer-1_v$VERSION_NUM.pkg NanoEngineer-1.pkg || exit 1
  sudo cp -R ~/MacOSX_Installers/GROMACS_$GROMACS_VERSION.pkg . || exit 1
  sudo mv GROMACS_$GROMACS_VERSION.pkg GROMACS.pkg || exit 1
  sudo cp -R ~/MacOSX_Installers/QuteMolX_$QUTEMOLX_VERSION.pkg . || exit 1
  sudo mv QuteMolX_$QUTEMOLX_VERSION.pkg QuteMolX.pkg || exit 1
  sudo cp -R ~/MacOSX_Installers/pref_modifier.pkg . || exit 1
else
# To be replaced later with something that searches for the pkg files
  echo "Couldn't find pre-build packages"
  exit 1
fi

cd $PKNG_DIR/MacOSX
sudo rm -rf NanoEngineer-1_Suite build rec
# create the build directory area
sudo mkdir build
sudo mkdir build/NanoEngineer-1_Suite
# remove any old version of the doc used by package make to build the distro
sudo rm -rf NE1_Suite.pmdoc
# expand the doc we need to build the distro
tar -xzvf NE1_Suite.pmdoc.tar.gz
# insert the gromacs version into the default install directory
cd NE1_Suite.pmdoc
GROM_FILE=`ls *gromacs.xml`
cat $GROM_FILE | sed -e "s:/Applications/GROMACS:/Applications/GROMACS_$GROMACS_VERSION:" > $GROM_FILE.tmp
mv $GROM_FILE.tmp $GROM_FILE || exit 1
QMX_FILE=`ls *qutemolx.xml`
cat $QMX_FILE | sed -e "s:/Applications/Nanorex/QuteMolX:/Applications/Nanorex/QuteMolX $QUTEMOLX_VERSION:" > $QMX_FILE.tmp
mv $QMX_FILE.tmp $QMX_FILE
#cat index.xml | sed -e "s:/Applications/Nanorex/QuteMolX:/Applications/Nanorex/QuteMolX $QUTEMOLX_VERSION:" | sed -e "s:/Applications/GROMACS:/Applications/GROMACS_$GROMACS_VERSION:" | sed -e "s:/Applications/Nanorex/NanoEngineer-1:/Applications/Nanorex/NanoEngineer-1_v$VERSION_NUM:" > index.xml.tmp
cat index.xml | sed -e "s:/Applications/Nanorex/QuteMolX:/Applications/Nanorex/QuteMolX $QUTEMOLX_VERSION:" | sed -e "s:/Applications/GROMACS:/Applications/GROMACS_$GROMACS_VERSION:" > index.xml.tmp
mv index.xml.tmp index.xml
cd ..

# create and populate the resources directory
mkdir rec
cp background.jpg rec
# make a welcome file for the installer
cat Welcome_template.rtf | sed -e "s:VERSION_GOES_HERE:$VERSION_NUM:g" | sed -e "s:DATE_GOES_HERE:$DATECODE:g" > Welcome.rtf
cp Welcome.rtf rec
cp License.txt rec
# copy in the post install scripts
cp post_*.sh rec

# Run the package builder
sudo /Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker -v -o build/NanoEngineer-1_Suite/NanoEngineer-1_Suite_v$VERSION_NUM.mpkg -d NE1_Suite.pmdoc || exit 1

# Code added to get around the race condition that seems to be a problem where
# hdiutil doesn't see the srcfolder unless the drive has been completely 
# sync'd up
sleep 10
sudo sync
sleep 10

# Create the distribution dmg file
sudo hdiutil create -srcfolder build/NanoEngineer-1_Suite -fs HFS+ -format UDZO build/NanoEngineer-1_Suite_v$VERSION_NUM.dmg || exit 1

# Store the installers for use later or for upload
if [ -e ~/MacOSX_Installers ]
then
  cd build/NanoEngineer-1_Suite
  sudo cp -R NanoEngineer-1_Suite_v$VERSION_NUM.mpkg ~/MacOSX_Installers
  cd ..
  sudo cp NanoEngineer-1_Suite_v$VERSION_NUM.dmg ~/MacOSX_Installers
fi
