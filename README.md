# qualys-stager
A simple Python script to validate and compile scans from Qualys in CSV format 

## Summary
This file moves through a directory of Qualys scans, removes the header from each file, and then concatenates them into a single file. There is basic error checking and exception handling. The purpose of this file is to prepare multiple .csv files from Qualys for upload to a tool like Splunk.

input: .csv files of Qualys scans from current working directory

output: .csv file of combined scans to current working directory

The script can be modified to change the location of input or output files. By default, they are the same, namely the current working directory. This is useful when invoking the script as a commandline alias.

System exit calls have been commented out. This prevents the script from restarting the Python kernel when running in an IDE. To use standalone from the commandline, uncommenting these lines will help ensure the program exits gracefully when terminated.
