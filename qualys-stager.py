#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
qualys-stager.py
v0.3
Updated on Fri Aug 17 12:39:18 EDT 2018

Written and tested using: Python 2.7.15, macOS 10.13.6 (17G65), Darwin 17.7.0

This file moves through a directory of Qualys scans,
removes the header from each file, and then concatenates
them into a single file. There is basic error checking and exception
handling. The purpose of this file is to prepare multiple .csv files
from Qualys for upload to a tool like Splunk.

input: .csv files of Qualys scans from current working directory
output: .csv file of combined scans to current working directory

The script can be modified to change the location of input or output files.
By default, they are the same, namely the current working directory. This
is useful when invoking the script as a commandline alias.

System exit calls have been commented out. This prevents the script from
restarting the Python kernel when running in an IDE. To use standalone from
the commandline, uncommenting these lines will help ensure the program
exits gracefully when terminated.

@author: andrew kulak
"""

# Libraries
import os # To allow interaction with the file structure
import time # For naming new files to avoid collision

# Global variables
inDirectory = os.getcwd() # Uses current working directory
outDirectory = os.getcwd() # Recommend creating a new directory and updating

# Main script
numFiles = 0
filenames = []
for filename in os.listdir(inDirectory):
    if filename.endswith('.csv') and not filename.startswith('combined-scans-'):
        filenames.append(filename)
        numFiles += 1

if numFiles == 0:
    print '[-] No .csv files were found in %s' % (inDirectory)
    print '[-] Please use a different directory and try again'
    #exit (0)

else:
    print '[+] %d .csv file was found in %s' % (numFiles, inDirectory) if (numFiles == 1) else '[+] %d .csv files were found in %s' % (numFiles, inDirectory)
    validation = raw_input ('[*] Headers will be removed and all scan data will be combined into a single .csv file. Continue? Y/N: ')
    if validation.lower() == 'y':
        print '[+] Removing Qualys headers from files...'
        references = [] # unique scan reference IDs for duplicate checking
        dataHeaders = [] # data headers, which should all be the same
        noHeaders = [] # the actual data without any header info
        # This block is capturing data from the files
        try:
            for filename in filenames:
                with open(filename,'r') as file:
                    lines = file.readlines()
                ref = ''
                for i in range(0, len(lines)):
                    if '"Reference"' in lines[i]:
                        refIndex = lines[i].split('Reference"')[0].count(',')
                        ref = lines[i+1].split(',')[refIndex].strip('"').strip()
                        if ref.startswith('scan/'):
                            references.append(ref)
                        break
                # This is a basic check for a standard Qualys .csv file
                if not ref:
                    raise Exception ('Nonstandard filetype detected')
                dataHeaders.append(lines[7])
                del lines[0:8]
                noHeaders.append(lines)
        except Exception as e:
            print '[-] Something\'s not quite right. Details:'
            print str(e)
            print '[-] Exiting...'
            #exit(1)
        # Checking for duplicates or other possible unusual situations
        try:
            # Check that all lists are equal in length, which they should be
            if not len(references) == len(dataHeaders) == len(noHeaders):
                raise Exception ('Complete information was not captured for all files')
            # Check that all data fields are the same, which they should be
            testCase = dataHeaders[0]
            for header in dataHeaders:
                if not testCase == header:
                    raise Exception ('Data fields not the same for each file')
            dataHeader = testCase
            # Check for duplicate scans and ask to write only unique scans to output file
            if len(references) != len(set(references)):
                print '[-] Duplicate scans detected, attempting to resolve...'
                seen = set()
                uniq = [x for x in references if x not in seen and not seen.add(x)]
                referencesSorted = sorted(references)
                print '[+] There are %d files, and %d appear unique' % (numFiles, len(uniq))
                validation = raw_input ('[*] View scan IDs for all scans? Y/N: ')
                if validation.lower() == 'y':
                    print '[+] All scans:'
                    for k in range (0, len(referencesSorted)-1):
                        print '%d\t%s\t' % (k+1, str(referencesSorted[k])) if (referencesSorted[k] != referencesSorted[k+1]) else '%d\t%s\t< Duplicated scan' % (k+1, str(referencesSorted[k]))
                    print '%d\t%s\t' % (len(referencesSorted), str(referencesSorted[len(referencesSorted)-1])) 
                validation = raw_input ('[*] View the scan IDs for only duplicate scans? Y/N: ')
                if validation.lower() == 'y':
                    print '[+] Duplicated scans:'
                    numDups = 1
                    for k in range(0,len(referencesSorted)-1):
                        if referencesSorted[k] == referencesSorted[k+1]:
                            print str(numDups) + '\t' + referencesSorted[k]
                            numDups += 1
                validation = raw_input ('[*] Remove the duplicate scans? Y/N: ')
                if validation.lower() == 'y':
                    print '[+] Removing duplicate scans...'
                    noHeadersNoDups = []
                    for scan in uniq:
                        for j in range (0, len(references)):
                            if scan == references[j]:
                                noHeadersNoDups.append(noHeaders[j])
                                break
                    print '[+] Combining scans...'
                    combinedFile = 'combined-scans-' + str(time.time()) + '.csv'
                    with open(outDirectory + '/' + combinedFile,'w+') as file:
                        file.write(dataHeader)
                        for scan in noHeadersNoDups:
                            for vuln in scan:
                                file.write(vuln)
                    print '[+] Combined scan file %s written to %s' % (combinedFile, outDirectory)
                else:
                    print '[+] Exiting based on user input...'
                    print '[+] Please review scan files and try again'
                    #exit(0)
            # Case for if all error checks have been passed
            else:
                print '[+] Combining scans...'
                combinedFile = 'combined-scans-' + str(time.time()) + '.csv'
                with open(outDirectory + '/' + combinedFile,'w+') as file:
                    file.write(dataHeader)
                    for scan in noHeaders:
                        for vuln in scan:
                            file.write(vuln)
                print '[+] Combined scan file %s written to %s' % (combinedFile, outDirectory)
        except Exception as e:
            print '[-] Something\'s not quite right...'
            print str(e)
            print '[-] Exiting...'
            #exit(1)
    else:
        print '[+] Exiting based on user input...'
        #exit(0)

print '[+] All finished!'
#exit (0)
