; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "NanoEngineer-1"
!define PRODUCT_VERSION "1.1.1"
!define PRODUCT_PUBLISHER "Nanorex, Inc."
!define PRODUCT_WEB_SITE "http://www.nanoengineer-1.com"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${PRODUCT_NAME}\${PRODUCT_VERSION}"
;!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\babel.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI 1.67 compatible ------
!include "MUI.nsh"
!include "registerExtension.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "install.ico"
!define MUI_UNICON "uninstall.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "install-header.bmp"
!define MUI_HEADERIMAGE_UNBITMAP "install-header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "wizard-sidebar.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "wizard-sidebar.bmp"

InstType "Basic"
InstType "Full"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "..\..\cad\src\dist\Licenses\NanoEngineer-1_License.txt"
; Components page
!insertmacro MUI_PAGE_COMPONENTS
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\program\main.exe"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\ReadMe.html"
;!define MUI_FINISHPAGE_SHOWREADME "http://www.nanoengineer-1.net/mediawiki/index.php?title=Online_Readme"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Name "${PRODUCT_NAME} v${PRODUCT_VERSION}"
OutFile "..\..\cad\src\build\NanoEngineer-1_v${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\Nanorex\NanoEngineer-1 v${PRODUCT_VERSION}"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

SectionGroup /e "NanoEngineer-1"
Section "MainSection" SEC01
  SectionIn 1 2
  SetOutPath "$INSTDIR"
  File "..\..\cad\src\dist\ReadMe.html"
  SetOverwrite try
  SetOutPath "$INSTDIR\bin"
  File /r "..\..\cad\src\dist\bin\*"
  SetOutPath "$INSTDIR\doc"
  File /r "..\..\cad\src\dist\doc\*"
  SetOutPath "$INSTDIR\Licenses"
  File /r "..\..\cad\src\dist\Licenses\*"
  SetOutPath "$INSTDIR\partlib"
  File /r "..\..\cad\src\dist\partlib\*"
  SetOutPath "$INSTDIR\plugins"
  File /r "..\..\cad\src\dist\plugins\*"
  SetOutPath "$INSTDIR\program"
  File /r "..\..\cad\src\dist\program\*"
  SetOutPath "$INSTDIR\src"
  File /r "..\..\cad\src\dist\src\*"

  ; hack
  SetOutPath "$INSTDIR\program"
  File "C:\Qt\4.3.5\bin\QtSvg4.dll"
  
  SetOutPath "$SYSDIR"
  SetOverwrite off
  File "glut32.dll"
  File "gle32.dll"
  CreateDirectory "$SMPROGRAMS\Nanorex\NanoEngineer-1 v${PRODUCT_VERSION}"
  CreateShortCut "$SMPROGRAMS\Nanorex\NanoEngineer-1 v${PRODUCT_VERSION}\NanoEngineer-1.lnk" "$INSTDIR\program\main.exe"
  CreateShortCut "$DESKTOP\NanoEngineer-1.lnk" "$INSTDIR\program\main.exe"
  CreateShortCut "$SMPROGRAMS\Nanorex\NanoEngineer-1 v${PRODUCT_VERSION}\ReadMe.html.lnk" "$INSTDIR\ReadMe.html"
SectionEnd
Section /o "Source" SEC_QMX_SRC
  SectionIn 2
  SetOutPath "$INSTDIR\source"
  SetOverwrite try
  File /r "..\..\cad\src\dist\source\*"
  SetOutPath "$INSTDIR"
SectionEnd
SectionGroupEnd

Section -AdditionalIcons
  SetOutPath $INSTDIR
  CreateShortCut "$SMPROGRAMS\Nanorex\NanoEngineer-1 v${PRODUCT_VERSION}\partlib.lnk" "$INSTDIR\partlib"
  CreateShortCut "$SMPROGRAMS\Nanorex\NanoEngineer-1 v${PRODUCT_VERSION}\Licenses.lnk" "$INSTDIR\Licenses"
  CreateShortCut "$SMPROGRAMS\Nanorex\NanoEngineer-1 v${PRODUCT_VERSION}\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\program\main.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\program\main.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  ${registerExtension} "$INSTDIR\program\main.exe " ".mmp" "NanoEngineer-1 File"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\*"
  RMDir /r "$INSTDIR\src"
  RMDir /r "$INSTDIR\program"
  RMDir /r "$INSTDIR\plugins"
  RMDir /r "$INSTDIR\partlib"
  RMDir /r "$INSTDIR\Licenses"
  RMDir /r "$INSTDIR\doc"
  RMDir /r "$INSTDIR\bin"
  RMDir /r "$INSTDIR\source"
  RMDir "$INSTDIR"
  RMDir "$PROGRAMFILES\Nanorex"

  Delete "$DESKTOP\NanoEngineer-1.lnk"

  RMDir /r "$SMPROGRAMS\Nanorex\NanoEngineer-1 v${PRODUCT_VERSION}"
  RMDir "$SMPROGRAMS\Nanorex"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  ${unregisterExtension} ".mmp" "NanoEngineer-1 File"
  SetAutoClose true
SectionEnd
