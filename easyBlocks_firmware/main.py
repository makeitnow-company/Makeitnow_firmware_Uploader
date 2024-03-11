from Makeitnow_function import mPrint
import sys
import utime

mPrint("1.0.0",dataType = "version")
utime.sleep(0.2)

try:
    import makeitnow
except Exception as e:
    if len(e.args) > 1:
        mPrint(e.args[0], status="error", message=e.args[1])
    else:
        mPrint(e.args[0], status="error")
