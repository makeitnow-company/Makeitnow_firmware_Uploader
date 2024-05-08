from Makeitnow_function import mPrint
import sys
import utime

for count in range(100):
    utime.sleep_ms(5)

mPrint("1.0.0",dataType = "version")

try:
    import makeitnow
except Exception as e:
    if len(e.args) > 1:
        mPrint(e.args[0], status="error", message=e.args[1])
    else:
        mPrint(e.args[0], status="error")
