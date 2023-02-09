#Region ;**** Directives created by AutoIt3Wrapper_GUI ****
#AutoIt3Wrapper_Change2CUI=y
#EndRegion ;**** Directives created by AutoIt3Wrapper_GUI ****
#include <ScreenCapture.au3>

$file = $CmdLine[1]
$handle = $CmdLine[2]

; co-ordinates
$c1 = $CmdLine[3]
$c2 = $CmdLine[4]
$c3 = $CmdLine[5]
$c4 = $CmdLine[6]

; Call the function
CaptureWindow()


Func CaptureWindow()
    ; select the mode 4 to active window based on handles
    AutoItSetOption("WinTitleMatchMode", 4)

    ;HWnd function will convert handle from strings to hex
    WinActivate (HWnd($handle))

    ; show the window in fore ground
    GUISetState(@SW_SHOW)

    ;  wait some time for window to appear in fore ground
    Sleep(250)

    ; Sets 24 bit BMP format
    _ScreenCapture_SetBMPFormat(24)

    ; Capture the area for given handle and save it in a file
	_ScreenCapture_CaptureWnd($file, HWnd($handle), $c1, $c2, $c3, $c4)
	;_ScreenCapture_SaveImage($file, $Image, True)
    ;Open the file in picture viewer... useful for testing/development
    ;ShellExecute($file)
EndFunc
