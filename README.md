ls mcpat-hotspot-parser
====================

Parser that converts log files from McPAT tool to Hotspot ptrace

Usage:
$python mcpat-hotspot-parser power.log

Output:
power.ptrace
A file ("power.ptrace") with Cores and L2s (so far) power values in the hotspot format


Usage:
$build-logs.py logfile0.log logfile1.log tracefile.ptrace

It accepts as many log files as demanded.
Note: The number of L2s is always one (1). Increase the number of L2s should be hard coded.

Output:
tracefile.ptrace
A file ("tracefile.ptrace") with Cores and L2s (so far) power values of the excited cores of each simulation ("core_0") put together
