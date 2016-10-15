#!/usr/bin/python
# -*- coding: utf-8 -*-

# ========================================================================================================================
#
#  File Name      : natapp
#
#  Author         : GFI
#
#  Platform       : Unix / Linux
#
#  Version:
#       2.0.0     2015/07/01   JFA   - Adding a filter to search for a single application
#       1.0.0     2015/06/09   JFA   - First version
#
#  Description    : Script to find the differences between application versions in all natcos
#
# ========================================================================================================================

import os
import time
import sys
import subprocess
import copy
from copy import deepcopy

# --- Forcing unicode encoding

reload(sys)
sys.setdefaultencoding("utf-8")

# --- Hosts of Natcos

DEVFR="caefr0p021"
DEVDE="caede0p055"
DEVUK="caeuk0p053"
DEVES="caees0p023"
DEVEX="caefr0p018"
VALFR="caefr0p024"
VALDE="caede0p021"
VALUK="caeuk0p056"
VALES="caees0p024"
VALEX="caefr0p019"
PRODFR="caefr0p015"
PRODDE="caede0p032"
PRODUK="caeuk0p022"
PRODES="caees0p004"
PRODEX="caefr0p025"

# --- Commands to push

LSDEVFR="cd /share/fr0_devel && find -maxdepth 2"
LSDEVDE="cd /share/de0_devel && find -maxdepth 2"
LSDEVUK="cd /share/uk0_devel && find -maxdepth 2"
LSDEVES="cd /share/es0_devel && find -maxdepth 2"
LSDEVEX="cd /share/fr0_devel && find -maxdepth 2"
LSVALFR="cd /share/fr0_val && find -maxdepth 2"
LSVALDE="cd /share/de0_val && find -maxdepth 2"
LSVALUK="cd /share/uk0_val && find -maxdepth 2"
LSVALES="cd /share/es0_val && find -maxdepth 2"
LSVALEX="cd /share/fr0_val && find -maxdepth 2"
LSPRODFR="cd /share/fr0_prod && find -maxdepth 2"
LSPRODDE="cd /share/de0_prod && find -maxdepth 2"
LSPRODUK="cd /share/uk0_prod && find -maxdepth 2"
LSPRODES="cd /share/es0_prod && find -maxdepth 2"
LSPRODEX="cd /share/fr0_prod && find -maxdepth 2"

# --- Print usage

def usage():
        print
        print "Usage: "
        print "natapp {{-f|--full}|{-e|--errors} {-d|--dev}|{-v|--val}|{-p|--prod}} | {{-a|-application} 'application name'}"
        print
        print "-f or --full           List applications and versions of all natcos."
        print "                       Please provide an environment."
        print "-e or --errors         List applications and versions with a synchronisation error."
        print "                       Please provide an environment."
        print "-d or --dev            Development environment."
        print "-v or --val            Validation environement."
        print "-p or --prod           Production environment."
        print "-------------------------------------------------------------------------------------------------------------"
        print "-a or --application    List versions of specified application in all environment."
        print "                       Please provide an application name."
        print

# --- SSH connexion

def ssh_result(host,command):
        ssh = subprocess.Popen(["ssh", "%s" % host, command],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if result == []:
                error = ssh.stderr.readlines()
                # print >>sys.stderr, "ERROR: %s" % error
        return result

# --- Finding natco's apps

def natco_app(fullset,natcoset,listfull):
        setTemp=natcoset-fullset
        tempList=list(setTemp)
        listfull.extend(tempList)
        return listfull

# --- Building the full list

def full_list():
        fulllist=deepcopy(LISTFR)
        # Creating sets
        setFull=set(fulllist)
        setDE=set(LISTDE)
        setUK=set(LISTUK)
        setES=set(LISTES)
        setEX=set(LISTEX)
        # Finding DE apps
        fulllist=natco_app(setFull,setDE,fulllist)
        setFull=set(fulllist)
        # Finding UK apps
        fulllist=natco_app(setFull,setUK,fulllist)
        setFull=set(fulllist)
        # Finding ES apps
        fulllist=natco_app(setFull,setES,fulllist)
        setFull=set(fulllist)
        # Finding EX apps
        fulllist=natco_app(setFull,setEX,fulllist)
        return fulllist


# --- Printing full list

def print_full_list():
        global LISTFULL
        LISTFULL.sort()
        for app in LISTFULL:
                appName=app[2:-1]
                if "/" in appName:
                        print "        ",appName,";",
                else:
                        print
                        print appName,";",
                if app in LISTFR:
                        print "FR-OK ;",
                else:
                        print "FR-KO ;",
                if app in LISTDE:
                        print "DE-OK ;",
                else:
                        print "DE-KO ;",
                if app in LISTUK:
                        print "UK-OK ;",
                else:
                        print "UK-KO ;",
                if app in LISTES:
                        print "ES-OK ;",
                else:
                        print "ES-KO ;",
                if app in LISTEX:
                        print "EX-OK"
                else:
                        print "EX-KO"


# --- Print errors list

def print_errors_list():
        global LISTFULL
        LISTFULL.sort()
        for app in LISTFULL:
                if app not in LISTFR:
                        if app not in LISTDE:
                                if app not in LISTUK:
                                        if app not in LISTES:
                                                if app not in LISTEX:
                                                        print app[2:-1],"FR-KO","DE-KO","UK-KO","ES-KO","EX-KO"
                                                else:
                                                        print app[2:-1],"FR-KO","DE-KO","UK-KO","ES-KO"
                                        else:
                                                print app[2:-1],"FR-KO","DE-KO","UK-KO"
                                else:
                                        print app[2:-1],"FR-KO","DE-KO"
                        else:
                                print app[2:-1],"FR-KO"
                elif app not in LISTDE:
                        if app not in LISTUK:
                                if app not in LISTES:
                                        if app not in LISTEX:
                                                print app[2:-1],"DE-KO","UK-KO","ES-KO","EX-KO"
                                        else:
                                                print app[2:-1],"DE-KO","UK-KO","ES-KO"
                                else:
                                        print app[2:-1],"DE-KO","UK,KO"
                        else:
                                print app[2:-1],"DE-KO"
                elif app not in LISTUK:
                        if app not in LISTES:
                                if app not in LISTEX:
                                        print app[2:-1],"UK-KO","ES-KO","EX-KO"
                                else:
                                        print app[2:-1],"UK-KO","ES-KO"
                        else:
                                app[2:-1],"UK-KO"
                elif app not in LISTES:
                        if app not in LISTEX:
                                print app[2:-1],"ES-KO","EX-KO"
                        else:
                                print app[2:-1],"ES-KO"
                elif app not in LISTEX:
                        print app[2:-1],"EX-KO"


# --- Retrieving app list from environment

def env_list(env):
        global LISTFR
        global LISTDE
        global LISTUK
        global LISTES
        global LISTEX
        if (env == "-d" or env == "--dev"):
                LISTFR=ssh_result(DEVFR,LSDEVFR)
                print "DEV FR OK"
                LISTDE=ssh_result(DEVDE,LSDEVDE)
                print "DEV DE OK"
                LISTUK=ssh_result(DEVUK,LSDEVUK)
                print "DEV UK OK"
                LISTES=ssh_result(DEVES,LSDEVES)
                print "DEV ES OK"
                LISTEX=ssh_result(DEVEX,LSDEVEX)
                print "DEV EX OK"
        elif (env == "-v" or env == "--val"):
                LISTFR=ssh_result(VALFR,LSVALFR)
                print "VAL FR OK"
                LISTDE=ssh_result(VALDE,LSVALDE)
                print "VAL DE OK"
                LISTUK=ssh_result(VALUK,LSVALUK)
                print "VAL UK OK"
                LISTES=ssh_result(VALES,LSVALES)
                print "VAL ES OK"
                LISTEX=ssh_result(VALEX,LSVALEX)
                print "VAL EX OK"
        elif (env == "-p" or env == "--prod"):
                LISTFR=ssh_result(PRODFR,LSPRODFR)
                print "PROD FR OK"
                LISTDE=ssh_result(PRODDE,LSPRODDE)
                print "PROD DE OK"
                LISTUK=ssh_result(PRODUK,LSPRODUK)
                print "PROD UK OK"
                LISTES=ssh_result(PRODES,LSPRODES)
                print "PROD ES OK"
                LISTEX=ssh_result(PRODEX,LSPRODEX)
                print "PROD EX OK"
        else:
                print
                print "Incorrect specified environment."
                print "Please read the help."
                usage()
                sys.exit(0)

# --- Retrieving versions list from all environment

def vers_list(app):
        global LISTDEV
        global LISTVAL
        global LISTPROD
        global LISTDEVEX
        global LISTVALEX
        global LISTPRODEX
        LSDEV="cd /share/fr0_devel/"+app+" && find -maxdepth 1"
        LSVAL="cd /share/fr0_val/"+app+" && find -maxdepth 1"
        LSPROD="cd /share/fr0_prod/"+app+" && find -maxdepth 1"
        LISTDEV=ssh_result(DEVFR,LSDEV)
        print "DEV OK"
        LISTVAL=ssh_result(VALFR,LSVAL)
        print "VAL OK"
        LISTPROD=ssh_result(PRODFR,LSPROD)
        print "PROD OK"
        LISTDEVEX=ssh_result(DEVEX,LSDEV)
        print "DEV EX OK"
        LISTVALEX=ssh_result(VALEX,LSVAL)
        print "VAL EX OK"
        LISTPRODEX=ssh_result(PRODEX,LSPROD)
        print "PROD EX OK"

# --- Finding environment's apps

def envi_app(fullset,enviset,listfull):
        setTemp=enviset-fullset
        tempList=list(setTemp)
        listfull.extend(tempList)
        return listfull

# --- Making a full list of application versions

def full_versions_list():
        fulllist=deepcopy(LISTDEV)
        # Creating sets
        setFull=set(fulllist)
        setVAL=set(LISTVAL)
        setPROD=set(LISTPROD)
        setDEVEX=set(LISTDEVEX)
        setVALEX=set(LISTVALEX)
        setPRODEX=set(LISTPRODEX)
        # Finding VAL versions
        fulllist=natco_app(setFull,setVAL,fulllist)
        setFull=set(fulllist)
        # Finding PROD versions
        fulllist=natco_app(setFull,setPROD,fulllist)
        setFull=set(fulllist)
        # Finding PROD EX versions
        fulllist=natco_app(setFull,setDEVEX,fulllist)
        setFull=set(fulllist)
        # Finding VAL EX versions
        fulllist=natco_app(setFull,setVALEX,fulllist)
        setFull=set(fulllist)
        # Finding PROD EX versions
        fulllist=natco_app(setFull,setPRODEX,fulllist)
        setFull=set(fulllist)
        return fulllist

# --- Printing full list of versions

def print_full_versions_list():
        global LISTVERSFULL
        LISTVERSFULL.sort()
        # Deleting first line "."
        LISTVERSFULL=LISTVERSFULL[1:]
        print
        for vers in LISTVERSFULL:
                versName=vers[2:-1]
                print versName,";",
                if vers in LISTDEV:
                        print "\033[32mDEV-OK\033[0m ;",
                else:
                        print "\033[31mDEV-KO\033[0m ;",
                if vers in LISTVAL:
                        print "\033[32mVAL-OK\033[0m ;",
                else:
                        print "\033[31mVAL-KO\033[0m ;",
                if vers in LISTPROD:
                        print "\033[32mPROD-OK\033[0m ;",
                else:
                        print "\033[31mPROD-KO\033[0m ;",
                if vers in LISTDEVEX:
                        print "\033[32mDEV-EX-OK\033[0m ;",
                else:
                        print "\033[31mDEV-EX-KO\033[0m ;",
                if vers in LISTVALEX:
                        print "\033[32mVAL-EX-OK\033[0m ;",
                else:
                        print "\033[31mVAL-EX-KO\033[0m ;",
                if vers in LISTPRODEX:
                        print "\033[32mPROD-EX-OK\033[0m ;",
                else:
                        print "\033[31mPROD-EX-KO\033[0m ;",
                print
                print

# --- Do the job

if len(sys.argv) < 2:
        usage()
        print "Bad call syntax."
        sys.exit(1)
elif len(sys.argv) > 1 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        usage()
elif len(sys.argv) > 2 and (sys.argv[1] == "-f" or sys.argv[1] == "--full"):
        print
        print("NATAPP --- START " + time.ctime())
        print
        print "Retrieving app list from all natcos..."
        env_list(sys.argv[2])
        print "DONE"
        print
        print "Building app list..."
        LISTFULL=full_list()
        print "DONE"
        print
        print "Applications List : "
        print_full_list()
        print
        print "DONE"
        print
elif len(sys.argv) > 2 and (sys.argv[1] == "-e" or sys.argv[1] == "--errors"):
        print
        print("NATAPP --- START " + time.ctime())
        print
        print "Retrieving app list with synchronisation errors..."
        env_list(sys.argv[2])
        print "DONE"
        print
        print "Building app list..."
        LISTFULL=full_list()
        print "DONE"
        print
        print "Applications List : "
        print_errors_list()
        print
        print "DONE"
        print
elif len(sys.argv) > 2 and (sys.argv[1] == "-a" or sys.argv[1] == "--application"):
        print
        print("NATAPP --- START " + time.ctime())
        print
        print "Retrieving versions list of \033[32m"+sys.argv[2]+"\033[0m on all natcos..."
        vers_list(sys.argv[2])
        print "DONE"
        print
        print "Building versions list..."
        LISTVERSFULL=full_versions_list()
        print "DONE"
        print
        print "Versions List : "
        print_full_versions_list()
        print "DONE"
        print
else:
        usage()

#############################################################################################