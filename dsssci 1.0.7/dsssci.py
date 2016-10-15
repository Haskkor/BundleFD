#!/usr/bin/python
# -*- coding: utf-8 -*-

# ========================================================================================================================
#
#  File Name      : dsssci
#
#  Author         : GFI  - subcontracted by AIRBUS
#
#  Platform       : Unix / Linux
#
#  Version:
#       1.0.7     2015/05/04   JFA   - Python
#                              GRO   - Adding a number when the file already exists
#       1.0.5     2015/04/22   JFA   - Adding time log
#       1.0.4     2015/04/20   JFA   - Translating n characters to n characters instead of 1 to 1
#                                    - WLCHARBAD and WLCHARREP are now arrays
#       1.0.3     2015/04/14   GRO   - Dealing with "\" in files name
#                              JFA   - Add "\" in WLCHARBAD with "_" in WLCHARREP
#       1.0.2     2015/04/10   PCE   - User SED/Y to translate characters
#                                    - Rename to [dsssci]
#       1.0.1     2015/04/09   PCE   - Script & initialization file renaming
#                                    - Add heading block & comments
#                                    - Make world callable
#                                    - Clean code
#       1.0.0     2015/04/02   JFA   - First version
#
#  Description    : Script to submit and execute a batch-job(s) via LSF for application
#
# ========================================================================================================================

import os
import copy
import time
import sys
import ConfigParser

# --- Forcing unicode encoding

reload(sys)
sys.setdefaultencoding("utf-8")

# --- Get variables from ini file

PWD = os.getcwd()
PATHINI = PWD + "/dsssci.ini"
config = ConfigParser.ConfigParser()
config.read(PATHINI)
CHARGOOD = config.get('SectionOne', 'WLCHARGOOD')
CHARBAD = config.get('SectionOne', 'WLCHARBAD')
CHARREP = config.get('SectionOne', 'WLCHARREP')
WCHARDEFAULT = config.get('SectionOne', 'WCHARDEFAULT')
WLCHARGOOD=CHARGOOD.split(",")
WLCHARBAD=CHARBAD.split(",")
WLCHARREP=CHARREP.split(",")

# --- Print usage

def usage():
        print "Usage: dsssci {{-l|--list}|{-r|--replace}} <root directory>"
        print
        print "-l or --list      List files whose name contain an illegal character."
        print "                  Please provide a path."
        print "-r or --replace   Replace illegal characters in files name."
        print "                  Please provide a path."
        print

# --- List translatable files

def char_list(string,dir,bool):
        result = copy.deepcopy(string)
        change = False
        for i in WLCHARBAD:
                if i in string:
                        change = True
        result = result.decode('utf8')
        for i in result:
                if i not in WLCHARGOOD:
                        change = True
                        print i
        if change:
                if bool:
                        path = dir
                else:
                        path = os.path.join(dir,string)
                if os.path.isdir(path):
                        print "D" + " -- " + path
                else:
                        print "F" + " -- " + path
        return

# --- Checking if the object name already exists

def name_exists(path,number):
        pathNum = path + str(number)
        if os.path.exists(pathNum):
                number += 1
                return name_exists(path,number)
        else:
                return pathNum

# --- Replace bad characters

def char_replace(string,dir,bool):
        result = copy.deepcopy(string)
        change = False
        for i in WLCHARBAD:
                if i in string:
                        change = True
                        result = string.replace(i, WLCHARREP[WLCHARBAD.index(i)])
        result = result.decode('utf8')
        for i in result:
                if i not in WLCHARGOOD:
                        change = True
                        result = result.replace(i, WCHARDEFAULT)
        if change:
                if bool:
                        path = dir
                        pathResult = os.path.join(dir.split("/")[0],result)
                        print "Rename " + path + "   to   " + pathResult + "  (D)  "
                else:
                        path = os.path.join(dir,string)
                        pathResult = os.path.join(dir,result)
                        print "Rename " + path + "   to   " + pathResult + "  (F)  "
                if os.path.exists(pathResult):
                        number = 1
                        pathResult = name_exists(pathResult,number)
                        print "New object name already exists. Adding a number. " + "Rename to " + pathResult
                os.rename(path,pathResult)
        return

# --- Read through file tree

def search_bads(path,replace):
        if replace:
                for root, dirs, files in os.walk(path):
                        for file in files:
                                char_replace(file,root,False)
                        char_replace(root.split("/")[-1],root,True)
        else:
                for root, dirs, files in os.walk(path):
                        char_list(root.split("/")[-1],root,True)
                        for file in files:
                                char_list(file,root,False)

# --- Do the job

if len(sys.argv) < 2:
        usage()
        print "Bad call syntax."
        sys.exit(1)
elif len(sys.argv) > 1 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        usage()
elif len(sys.argv) > 1 and (sys.argv[1] == "-l" or sys.argv[1] == "--list"):
        print
        print("Treat [" + sys.argv[2] + "].")
        print
        print("DSSSCI LISTING --- START " + time.ctime())
        print
        print "Search for eligible objects :"
        print
        search_bads(sys.argv[2],False)
        print
        print("DSSSCI LISTING --- STOP " + time.ctime())
        print
elif len(sys.argv) > 1 and (sys.argv[1] == "-r" or sys.argv[1] == "--rename"):
        print
        print("Treat [" + sys.argv[2] + "].")
        print
        print("DSSSCI REPLACING --- START " + time.ctime())
        print
        print "Processing to objects renaming :"
        print
        search_bads(sys.argv[2],True)
        print
        print("DSSSCI REPLACING --- STOP " + time.ctime())
        print
else:
        usage()

#############################################################################################
