#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

# ========================================================================================================================
#
#  File Name      : dsssci
#
#  Author         : GFI  - subcontracted by AIRBUS
#
#  Platform       : Unix / Linux
#
#  Version:
#       1.0.6     2015/04/24   JFA   - Python
#                              GRO
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

WLCHARGOOD=[']', '[', '!', '#', '$', '%', '(', ')', '+', '-', '.', '<', '>', '=', '?', '@', '_',
 '{', '}', '~', ' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', '
I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '1', '2
', '3', '4', '5', '6', '7', '8', '9', '0']
WLCHARBAD=['Æ', 'æ', 'Œ', 'œ', 'À', 'à', 'Á', 'á', 'Â', 'â', 'Ã', 'ã', 'Ä', 'ä', 'È', 'è', 'É',
'é', 'Ê', 'ê', 'Ë', 'ë', 'Ì', 'ì', 'Í', 'í', 'Î', 'î', 'Ï', 'ï', 'Ò', 'ò', 'Ó', 'ó', 'Ô', 'ô', '
Õ', 'õ', 'Ö', 'ö', 'Ù', 'ù', 'Ú', 'ú', 'Û', 'û', 'Ü', 'ü', 'Ý', 'ý', 'Ÿ', 'ÿ', 'Ñ', 'ñ', 'Ç', 'ç
', '€', '\\']
WLCHARREP=['AE', 'ae', 'OE', 'oe', 'A', 'a', 'A', 'a', 'A', 'a', 'AE', 'ae', 'A', 'a', 'E', 'e',
 'E', 'e', 'E', 'e', 'E', 'e', 'I', 'i', 'I', 'i', 'I', 'i', 'I', 'i', 'O', 'o', 'O', 'o', 'O',
'o', 'O', 'o', 'O', 'o', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'Y', 'y', 'Y', 'y', 'N', 'n', '
C', 'c', 'e', '\#']
WCHARDEFAULT='_'

# --- Print usage

def usage():
        print "Usage: dsssci {{-l|--list}|{-r|--replace}} <root directory>"
        print
        print "-l or --list     List files whose name contain an illegal character."
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
        for i in result:
                if i not in WLCHARGOOD:
                        change = True
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

# --- Replace bad characters

def char_replace(string,dir,bool):
        result = copy.deepcopy(string)
        change = False
        for i in WLCHARBAD:
                if i in string:
                        change = True
                        result = string.replace(i, WLCHARREP[WLCHARBAD.index(i)])
        for i in result:
                if i not in WLCHARGOOD:
                        change = True
                        result = string.replace(i, WCHARDEFAULT)
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
                        print "[ERROR] New object name already exists"
                else:
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

if len(sys.argv) > 1:
        print
        print("Treat [" + sys.argv[2] + "].")
        print
        print("DSSSCI --- START " + time.ctime())
        print

if len(sys.argv) < 2:
        usage()
        print "Bad call syntax."
        sys.exit(1)
elif len(sys.argv) > 1 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        usage()
elif len(sys.argv) > 1 and (sys.argv[1] == "-l" or sys.argv[1] == "--list"):
        print "Search for eligible objects :"
        print
        search_bads(sys.argv[2],False)
        print
        print("DSSSCI --- STOP " + time.ctime())
        print
elif len(sys.argv) > 1 and (sys.argv[1] == "-r" or sys.argv[1] == "--rename"):
        print "Processing to objects renaming :"
        print
        search_bads(sys.argv[2],True)
        print
        print("DSSSCI --- STOP " + time.ctime())
        print
else:
        usage()

#############################################################################################

