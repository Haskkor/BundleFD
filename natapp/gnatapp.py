#!/bin/env python
# -*- coding: utf-8 -*-

# =================================================================================================
#
#  File Name      : natappGUI
#
#  Author         : JFA
#
#  Platform       : Unix / Linux
#
#  Version        :
#       3.2.0     2015/08/03    JFA   - Add a progress bar
#       3.1.0     2015/07/29    JFA   - One screen app
#       3.0.0     2015/07/22    JFA   - Initial Version
#
#  Description    : GUI for natapp script (allow to retrieve all versions of an app on a
#                   specific environment or a specific natco)
#
# =================================================================================================

import os, sys
import subprocess
import datetime
import copy
from copy import deepcopy

#--------------------------------------------------------------------------------------------------     
# Launch the ppack_gnu_435 environment before launching the script
#--------------------------------------------------------------------------------------------------

# If ppack_gnu_435 is set, skip this part
if not 'CDTNG_PPACK_GNU_435_CMD' in os.environ:

        command = ['bash', '-c', "eval $(ppack_gnu_435 --version 3.3 --setenvironment) && env"]

        proc = subprocess.Popen(command, stdout = subprocess.PIPE)
        stdout, stderr = proc.communicate()
        lp_save = ["", ""]
        for line in stdout.split("\n")[:-1]:
                lp = line.split("=",1)
                if len(lp) > 2:
                        continue
                # For HPC : BASH_FUNC_module() written on 2 lines. Second line only contains "}"
                elif len(lp) == 1:
                        os.environ[lp_save[0]] = lp_save[1] + "\n" + lp[0]
                else:
                        os.environ[lp[0]] = lp[1]
                        lp_save = lp

        # Launch again the process with the new environment
        os.execve(os.path.realpath(__file__), sys.argv, os.environ)

#--------------------------------------------------------------------------------------------------
# Import modules
#--------------------------------------------------------------------------------------------------

import re, copy, time
import threading, signal
import numpy as np
from scipy import *
from threading import Timer
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#--------------------------------------------------------------------------------------------------
# Forcing unicode encoding
#--------------------------------------------------------------------------------------------------

reload(sys)
sys.setdefaultencoding("utf-8")

#--------------------------------------------------------------------------------------------------
# Hosts of Natcos
#--------------------------------------------------------------------------------------------------

DEVFR="caefr0p021.eu.airbus.corp"
DEVDE="caede0p055.eu.airbus.corp"
DEVUK="caeuk0p053.eu.airbus.corp"
DEVES="caees0p023.eu.airbus.corp"
DEVIN="caein0p009.as.airbus.corp"
DEVEX="caefr0p018.eu.airbus.corp"
VALFR="caefr0p024.eu.airbus.corp"
VALDE="caede0p021.eu.airbus.corp"
VALUK="caeuk0p056.eu.airbus.corp"
VALES="caees0p024.eu.airbus.corp"
VALIN="caefr0p021.eu.airbus.corp"
VALEX="caefr0p019.eu.airbus.corp"
PRODFR="caefr0p015.eu.airbus.corp"
PRODDE="caede0p032.eu.airbus.corp"
PRODUK="caeuk0p022.eu.airbus.corp"
PRODES="caees0p004.eu.airbus.corp"
PRODIN="caefr0p021.eu.airbus.corp"
PRODEX="caefr0p025.eu.airbus.corp"

#--------------------------------------------------------------------------------------------------
# Commands to push
#--------------------------------------------------------------------------------------------------

LSDEVFR="cd /share/fr0_devel && find -maxdepth 2"
LSDEVDE="cd /share/de0_devel && find -maxdepth 2"
LSDEVUK="cd /share/uk0_devel && find -maxdepth 2"
LSDEVES="cd /share/es0_devel && find -maxdepth 2"
LSDEVIN="cd /share/in0_devel && find -maxdepth 2"
LSDEVEX="cd /share/fr0_devel && find -maxdepth 2"
LSVALFR="cd /share/fr0_val && find -maxdepth 2"
LSVALDE="cd /share/de0_val && find -maxdepth 2"
LSVALUK="cd /share/uk0_val && find -maxdepth 2"
LSVALES="cd /share/es0_val && find -maxdepth 2"
LSVALIN="cd /share/fr0_val && find -maxdepth 2"
LSVALEX="cd /share/fr0_val && find -maxdepth 2"
LSPRODFR="cd /share/fr0_prod && find -maxdepth 2"
LSPRODDE="cd /share/de0_prod && find -maxdepth 2"
LSPRODUK="cd /share/uk0_prod && find -maxdepth 2"
LSPRODES="cd /share/es0_prod && find -maxdepth 2"
LSPRODIN="cd /share/fr0_prod && find -maxdepth 2"
LSPRODEX="cd /share/fr0_prod && find -maxdepth 2"  

#--------------------------------------------------------------------------------------------------
# Applications lists
#--------------------------------------------------------------------------------------------------

LISTDEVFR=[]
LISTVALFR=[]
LISTPRODFR=[]
LISTDEVDE=[]
LISTVALDE=[]
LISTPRODDE=[]
LISTDEVUK=[]
LISTVALUK=[]
LISTPRODUK=[]
LISTDEVES=[]
LISTVALES=[]
LISTPRODES=[]
LISTDEVIN=[]
LISTVALIN=[]
LISTPRODIN=[]
LISTDEVEX=[]
LISTVALEX=[]
LISTPRODEX=[]            
FULLLIST=[]

#--------------------------------------------------------------------------------------------------
# List of natco + environment lists
#--------------------------------------------------------------------------------------------------                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       

LISTLISTS = []

#--------------------------------------------------------------------------------------------------
# SSH connexion
# Input: Host and command
# Output: Command result
#--------------------------------------------------------------------------------------------------

def ssh_result(host,command,pbar,val):

        ssh = subprocess.Popen(["ssh", "%s" % host, command],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if result == []:
                error = ssh.stderr.readlines()

        pbar.setValue(val)

        return result

#--------------------------------------------------------------------------------------------------
# Make the OK / KO list
# Input: Environment list, column index and environment name
# Output: Nothing
#--------------------------------------------------------------------------------------------------

def fill_okko_lists(envlist,ind,name):

        global LISTLISTS

        i = 0
        for app in FULLLIST:
                if app not in envlist:
                        LISTLISTS[i][ind] = name + " KO"
                else:
                        LISTLISTS[i][ind] = name + " OK"
                i = i + 1

#--------------------------------------------------------------------------------------------------
# Make the list of the wanted app
# Input: application name or version name
# Output: Nothing
#--------------------------------------------------------------------------------------------------

def grep_name(name):

        global FULLLIST

        temp = []
        for app in FULLLIST:
                if app.find(name) != -1:
                        temp.append(app)

        FULLLIST = temp


def del_lists():

        global LISTDEVFR
        global LISTVALFR
        global LISTPRODFR
        global LISTDEVDE
        global LISTVALDE
        global LISTPRODDE
        global LISTDEVUK
        global LISTVALUK
        global LISTPRODUK
        global LISTDEVES
        global LISTVALES
        global LISTPRODES
        global LISTDEVIN
        global LISTVALIN
        global LISTPRODIN
        global LISTDEVEX
        global LISTVALEX
        global LISTPRODEX            
        global FULLLIST

        LISTDEVFR[:] = []
        LISTVALFR[:] = []
        LISTPRODFR[:] = []
        LISTDEVDE[:] = []
        LISTVALDE[:] = []
        LISTPRODDE[:] = []
        LISTDEVUK[:] = []
        LISTVALUK[:] = []
        LISTPRODUK[:] = []
        LISTDEVES[:] = []
        LISTVALES[:] = []
        LISTPRODES[:] = []
        LISTDEVIN[:] = []
        LISTVALIN[:] = []
        LISTPRODIN[:] = []
        LISTDEVEX[:] = []
        LISTVALEX[:] = []
        LISTPRODEX[:] = []            
        FULLLIST[:] = []

#--------------------------------------------------------------------------------------------------
# Make the list of natco + environment lists
# Input: NATCO and environment
# Output: Nothing
#--------------------------------------------------------------------------------------------------

def make_listlists(natco,env):

        global LISTLISTS

        if natco == "All":
                if env == "All":
                        LISTLISTS = [[0 for x in range(18)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVFR,0,"DEV FR")
                        fill_okko_lists(LISTVALFR,1,"VAL FR")
                        fill_okko_lists(LISTPRODFR,2,"PROD FR")
                        fill_okko_lists(LISTDEVDE,3,"DEV DE")
                        fill_okko_lists(LISTVALDE,4,"VAL DE")
                        fill_okko_lists(LISTPRODDE,5,"PROD DE")
                        fill_okko_lists(LISTDEVUK,6,"DEV UK")
                        fill_okko_lists(LISTVALUK,7,"VAL UK")
                        fill_okko_lists(LISTPRODUK,8,"PROD UK")
                        fill_okko_lists(LISTDEVES,9,"DEV ES")
                        fill_okko_lists(LISTVALES,10,"VAL ES")
                        fill_okko_lists(LISTPRODES,11,"PROD ES")
                        fill_okko_lists(LISTDEVIN,12,"DEV IN")
                        fill_okko_lists(LISTVALIN,13,"VAL IN")
                        fill_okko_lists(LISTPRODIN,14,"PROD IN")
                        fill_okko_lists(LISTDEVEX,15,"DEV EX")
                        fill_okko_lists(LISTVALEX,16,"VAL EX")
                        fill_okko_lists(LISTPRODEX,17,"PROD EX")
                elif env == "DEVelopment":
                        LISTLISTS = [[0 for x in range(6)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVFR,0,"DEV FR")
                        fill_okko_lists(LISTDEVDE,1,"DEV DE")
                        fill_okko_lists(LISTDEVUK,2,"DEV UK")
                        fill_okko_lists(LISTDEVES,3,"DEV ES")
                        fill_okko_lists(LISTDEVIN,4,"DEV IN")
                        fill_okko_lists(LISTDEVEX,5,"DEV EX")
                elif env == "VALidation":
                        LISTLISTS = [[0 for x in range(6)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTVALFR,0,"VAL FR")
                        fill_okko_lists(LISTVALDE,1,"VAL DE")
                        fill_okko_lists(LISTVALUK,2,"VAL UK")
                        fill_okko_lists(LISTVALES,3,"VAL ES")
                        fill_okko_lists(LISTVALIN,4,"VAL IN")
                        fill_okko_lists(LISTVALEX,5,"VAL EX")
                elif env == "PRODuction":
                        LISTLISTS = [[0 for x in range(6)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTPRODFR,0,"PROD EX")
                        fill_okko_lists(LISTPRODDE,1,"PROD DE")
                        fill_okko_lists(LISTPRODUK,2,"PROD UK")
                        fill_okko_lists(LISTPRODES,3,"PROD ES")
                        fill_okko_lists(LISTPRODIN,4,"PROD IN")
                        fill_okko_lists(LISTPRODEX,5,"PROD EX")
        elif natco == "FR":
                if env == "All":
                        LISTLISTS = [[0 for x in range(3)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVFR,0,"DEV FR")
                        fill_okko_lists(LISTVALFR,1,"VAL FR")
                        fill_okko_lists(LISTPRODFR,2,"PROD FR")
                elif env == "DEVelopment":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVFR,0,"DEV FR")
                elif env == "VALidation":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTVALFR,0,"VAL FR")
                elif env == "PRODuction":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTPRODFR,0,"PROD FR")
        elif natco == "DE":
                if env == "All":
                        LISTLISTS = [[0 for x in range(3)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVDE,0,"DEV DE")
                        fill_okko_lists(LISTVALDE,1,"VAL DE")
                        fill_okko_lists(LISTPRODDE,2,"PROD DE")
                elif env == "DEVelopment":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVDE,0,"DEV DE")
                elif env == "VALidation":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTVALDE,0,"VAL DE")
                elif env == "PRODuction":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTPRODDE,0,"PROD DE")
        elif natco == "UK":
                if env == "All":
                        LISTLISTS = [[0 for x in range(3)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVUK,0,"DEV UK")
                        fill_okko_lists(LISTVALUK,1,"VAL UK")
                        fill_okko_lists(LISTPRODUK,2,"PROD UK")
                elif env == "DEVelopment":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVUK,0,"DEV UK")
                elif env == "VALidation":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTVALUK,0,"VAL UK")
                elif env == "PRODuction":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTPRODUK,0,"PROD UK")
        elif natco == "ES":
                if env == "All":
                        LISTLISTS = [[0 for x in range(3)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVES,0,"DEV ES")
                        fill_okko_lists(LISTVALES,1,"VAL ES")
                        fill_okko_lists(LISTPRODES,2,"PROD ES")
                elif env == "DEVelopment":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVES,0,"DEV ES")
                elif env == "VALidation":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTVALES,0,"VAL ES")
                elif env == "PRODuction":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTPRODES,0,"PROD ES")
        elif natco == "IN":
                if env == "All":
                        LISTLISTS = [[0 for x in range(3)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVIN,0,"DEV IN")
                        fill_okko_lists(LISTVALIN,1,"VAL IN")
                        fill_okko_lists(LISTPRODIN,2,"PROD IN")
                elif env == "DEVelopment":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVIN,0,"DEV IN")
                elif env == "VALidation":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTVALIN,0,"VAL IN")
                elif env == "PRODuction":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTPRODIN,0,"PROD IN")
        elif natco == "EX":
                if env == "All":
                        LISTLISTS = [[0 for x in range(3)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVEX,0,"DEV EX")
                        fill_okko_lists(LISTVALEX,1,"VAL EX")
                        fill_okko_lists(LISTPRODEX,2,"PROD EX")
                elif env == "DEVelopment":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTDEVEX,0,"DEV EX")
                elif env == "VALidation":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTVALEX,0,"VAL EX")
                elif env == "PRODuction":
                        LISTLISTS = [[0 for x in range(1)] for x in range(len(FULLLIST))]
                        fill_okko_lists(LISTPRODEX,0,"PROD EX")

#--------------------------------------------------------------------------------------------------
# Adding lists applications to the full list
# Input: Full set, applications set, full list
# Output: Full list
#--------------------------------------------------------------------------------------------------

def list_app(fullset,appset,listfull):

        setTemp=appset-fullset
        tempList=list(setTemp)
        listfull.extend(tempList)
        return listfull

#--------------------------------------------------------------------------------------------------
# Building the full list
# Input: Nothing
# Output: Nothing
#--------------------------------------------------------------------------------------------------

def full_list():

        global LISTDEVFR
        global LISTVALFR
        global LISTPRODFR
        global LISTDEVDE
        global LISTVALDE
        global LISTPRODDE
        global LISTDEVUK
        global LISTVALUK
        global LISTPRODUK
        global LISTDEVES
        global LISTVALES
        global LISTPRODES
        global LISTDEVIN
        global LISTVALIN
        global LISTPRODIN
        global LISTDEVEX
        global LISTVALEX
        global LISTPRODEX  
        global FULLLIST 

        FULLLIST=deepcopy(LISTDEVFR)

        # Creating sets
        setFull=set(FULLLIST)
        setVALFR=set(LISTVALFR)
        setPRODFR=set(LISTPRODFR)
        setDEVDE=set(LISTDEVDE)
        setVALDE=set(LISTVALDE)
        setPRODDE=set(LISTPRODDE)
        setDEVUK=set(LISTDEVUK)
        setVALUK=set(LISTVALUK)
        setPRODUK=set(LISTPRODUK)
        setDEVES=set(LISTDEVES)
        setVALES=set(LISTVALES)
        setPRODES=set(LISTPRODES)
        setDEVIN=set(LISTDEVIN)
        setVALIN=set(LISTVALIN)
        setPRODIN=set(LISTPRODIN)
        setDEVEX=set(LISTDEVEX)
        setVALEX=set(LISTVALEX)
        setPRODEX=set(LISTPRODEX)

        # Finding VAL FR apps
        FULLLIST=list_app(setFull,setVALFR,FULLLIST)
        setFull=set(FULLLIST)
        # Finding PROD FR apps
        FULLLIST=list_app(setFull,setPRODFR,FULLLIST)
        setFull=set(FULLLIST)
        # Finding DEV DE apps
        FULLLIST=list_app(setFull,setDEVDE,FULLLIST)
        setFull=set(FULLLIST)
        # Finding VAL DE apps
        FULLLIST=list_app(setFull,setVALDE,FULLLIST)
        setFull=set(FULLLIST)
        # Finding PROD DE apps
        FULLLIST=list_app(setFull,setPRODDE,FULLLIST)
        setFull=set(FULLLIST)
        # Finding DEV UK apps
        FULLLIST=list_app(setFull,setDEVUK,FULLLIST)
        setFull=set(FULLLIST)
        # Finding VAL UK apps
        FULLLIST=list_app(setFull,setVALUK,FULLLIST)
        setFull=set(FULLLIST)
        # Finding PROD UK apps
        FULLLIST=list_app(setFull,setPRODUK,FULLLIST)
        setFull=set(FULLLIST)
        # Finding DEV ES apps
        FULLLIST=list_app(setFull,setDEVES,FULLLIST)
        setFull=set(FULLLIST)
        # Finding VAL ES apps
        FULLLIST=list_app(setFull,setVALES,FULLLIST)
        setFull=set(FULLLIST)
        # Finding PROD ES apps
        FULLLIST=list_app(setFull,setPRODES,FULLLIST)
        setFull=set(FULLLIST)
        # Finding DEV IN apps
        FULLLIST=list_app(setFull,setDEVIN,FULLLIST)
        setFull=set(FULLLIST)
        # Finding VAL IN apps
        FULLLIST=list_app(setFull,setVALIN,FULLLIST)
        setFull=set(FULLLIST)
        # Finding PROD IN apps
        FULLLIST=list_app(setFull,setPRODIN,FULLLIST)
        setFull=set(FULLLIST)
        # Finding DEV EX apps
        FULLLIST=list_app(setFull,setDEVEX,FULLLIST)
        setFull=set(FULLLIST)
        # Finding VAL EX apps
        FULLLIST=list_app(setFull,setVALEX,FULLLIST)
        setFull=set(FULLLIST)
        # Finding PROD EX apps
        FULLLIST=list_app(setFull,setPRODEX,FULLLIST)

        FULLLIST.sort()
        FULLLIST = FULLLIST[1:]

        temp = []
        for item in FULLLIST:
                if item[2] != ".":
                        temp.append(item)
        FULLLIST = temp

#--------------------------------------------------------------------------------------------------
# Creates the applications versions list
# Input: NATCO, environment
# Output: Lists of applications versions
#--------------------------------------------------------------------------------------------------

def make_lists(natco,env,pbar):

        global LISTDEVFR
        global LISTVALFR
        global LISTPRODFR
        global LISTDEVDE
        global LISTVALDE
        global LISTPRODDE
        global LISTDEVUK
        global LISTVALUK
        global LISTPRODUK
        global LISTDEVES
        global LISTVALES
        global LISTPRODES
        global LISTDEVIN
        global LISTVALIN
        global LISTPRODIN
        global LISTDEVEX
        global LISTVALEX
        global LISTPRODEX   

        pbar.setValue(0)

        if natco == "All":
                if env == "All":
                        LISTDEVFR=ssh_result(DEVFR,LSDEVFR,pbar,5)
                        LISTVALFR=ssh_result(VALFR,LSVALFR,pbar,10)
                        LISTPRODFR=ssh_result(PRODFR,LSPRODFR,pbar,16)
                        LISTDEVDE=ssh_result(DEVDE,LSDEVDE,pbar,22)
                        LISTVALDE=ssh_result(VALDE,LSVALDE,pbar,27)
                        LISTPRODDE=ssh_result(PRODDE,LSPRODDE,pbar,33)
                        LISTDEVUK=ssh_result(DEVUK,LSDEVUK,pbar,39)
                        LISTVALUK=ssh_result(VALUK,LSVALUK,pbar,44)
                        LISTPRODUK=ssh_result(PRODUK,LSPRODUK,pbar,50)
                        LISTDEVES=ssh_result(DEVES,LSDEVES,pbar,56)
                        LISTVALES=ssh_result(VALES,LSVALES,pbar,61)
                        LISTPRODES=ssh_result(PRODES,LSPRODES,pbar,67)
                        LISTDEVIN=ssh_result(DEVIN,LSDEVIN,pbar,73)
                        LISTVALIN=ssh_result(VALIN,LSVALIN,pbar,78)
                        LISTPRODIN=ssh_result(PRODIN,LSPRODIN,pbar,84)
                        LISTDEVEX=ssh_result(DEVEX,LSDEVEX,pbar,90)
                        LISTVALEX=ssh_result(VALEX,LSVALEX,pbar,95)
                        LISTPRODEX=ssh_result(PRODEX,LSPRODEX,pbar,100)
                elif env == "DEVelopment":
                        LISTDEVFR=ssh_result(DEVFR,LSDEVFR,pbar,16)
                        LISTDEVDE=ssh_result(DEVDE,LSDEVDE,pbar,33)
                        LISTDEVUK=ssh_result(DEVUK,LSDEVUK,pbar,50)
                        LISTDEVES=ssh_result(DEVES,LSDEVES,pbar,67)
                        LISTDEVIN=ssh_result(DEVIN,LSDEVIN,pbar,84)
                        LISTDEVEX=ssh_result(DEVEX,LSDEVEX,pbar,100)
                elif env == "VALidation":
                        LISTVALFR=ssh_result(VALFR,LSVALFR,pbar,16)
                        LISTVALDE=ssh_result(VALDE,LSVALDE,pbar,33)
                        LISTVALUK=ssh_result(VALUK,LSVALUK,pbar,50)
                        LISTVALES=ssh_result(VALES,LSVALES,pbar,67)
                        LISTVALIN=ssh_result(VALIN,LSVALIN,pbar,84)
                        LISTVALEX=ssh_result(VALEX,LSVALEX,pbar,100)
                elif env == "PRODuction":
                        LISTPRODFR=ssh_result(PRODFR,LSPRODFR,pbar,16)
                        LISTPRODDE=ssh_result(PRODDE,LSPRODDE,pbar,33)
                        LISTPRODUK=ssh_result(PRODUK,LSPRODUK,pbar,50)
                        LISTPRODES=ssh_result(PRODES,LSPRODES,pbar,67)
                        LISTPRODIN=ssh_result(PRODIN,LSPRODIN,pbar,84)
                        LISTPRODEX=ssh_result(PRODEX,LSPRODEX,pbar,100)
        elif natco == "FR":
                if env == "All":
                        LISTDEVFR=ssh_result(DEVFR,LSDEVFR,pbar,33)
                        LISTVALFR=ssh_result(VALFR,LSVALFR,pbar,66)
                        LISTPRODFR=ssh_result(PRODFR,LSPRODFR,pbar,100)
                elif env == "DEVelopment":
                        LISTDEVFR=ssh_result(DEVFR,LSDEVFR,pbar,100)
                elif env == "VALidation":
                        LISTVALFR=ssh_result(VALFR,LSVALFR,pbar,100)
                elif env == "PRODuction":
                        LISTPRODFR=ssh_result(PRODFR,LSPRODFR,pbar,100)
        elif natco == "DE":
                if env == "All":
                        LISTDEVDE=ssh_result(DEVDE,LSDEVDE,pbar,33)
                        LISTVALDE=ssh_result(VALDE,LSVALDE,pbar,66)
                        LISTPRODDE=ssh_result(PRODDE,LSPRODDE,pbar,100)
                elif env == "DEVelopment":
                        LISTDEVDE=ssh_result(DEVDE,LSDEVDE,pbar,100)
                elif env == "VALidation":
                        LISTVALDE=ssh_result(VALDE,LSVALDE,pbar,100)
                elif env == "PRODuction":
                        LISTPRODDE=ssh_result(PRODDE,LSPRODDE,pbar,100)
        elif natco == "UK":
                if env == "All":
                        LISTDEVUK=ssh_result(DEVUK,LSDEVUK,pbar,33)
                        LISTVALUK=ssh_result(VALUK,LSVALUK,pbar,66)
                        LISTPRODUK=ssh_result(PRODUK,LSPRODUK,pbar,100)
                elif env == "DEVelopment":
                        LISTDEVUK=ssh_result(DEVUK,LSDEVUK,pbar,100)
                elif env == "VALidation":
                        LISTVALUK=ssh_result(VALUK,LSVALUK,pbar,100)
                elif env == "PRODuction":
                        LISTPRODUK=ssh_result(PRODUK,LSPRODUK,pbar,100)
        elif natco == "ES":
                if env == "All":
                        LISTDEVES=ssh_result(DEVES,LSDEVES,pbar,33)
                        LISTVALES=ssh_result(VALES,LSVALES,pbar,66)
                        LISTPRODES=ssh_result(PRODES,LSPRODES,pbar,100)
                elif env == "DEVelopment":
                        LISTDEVES=ssh_result(DEVES,LSDEVES,pbar,100)
                elif env == "VALidation":
                        LISTVALES=ssh_result(VALES,LSVALES,pbar,100)
                elif env == "PRODuction":
                        LISTPRODES=ssh_result(PRODES,LSPRODES,pbar,100)
        elif natco == "IN":
                if env == "All":
                        LISTDEVIN=ssh_result(DEVIN,LSDEVIN,pbar,33)
                        LISTVALIN=ssh_result(VALIN,LSVALIN,pbar,66)
                        LISTPRODIN=ssh_result(PRODIN,LSPRODIN,pbar,100)
                elif env == "DEVelopment":
                        LISTDEVIN=ssh_result(DEVIN,LSDEVIN,pbar,100)
                elif env == "VALidation":
                        LISTVALIN=ssh_result(VALIN,LSVALIN,pbar,100)
                elif env == "PRODuction":
                        LISTPRODIN=ssh_result(PRODIN,LSPRODIN,pbar,100)
        elif natco == "EX":
                if env == "All":
                        LISTDEVEX=ssh_result(DEVEX,LSDEVEX,pbar,33)
                        LISTVALEX=ssh_result(VALEX,LSVALEX,pbar,66)
                        LISTPRODEX=ssh_result(PRODEX,LSPRODEX,pbar,100)
                elif env == "DEVelopment":
                        LISTDEVEX=ssh_result(DEVEX,LSDEVEX,pbar,100)
                elif env == "VALidation":
                        LISTVALEX=ssh_result(VALEX,LSVALEX,pbar,100)
                elif env == "PRODuction":
                        LISTPRODEX=ssh_result(PRODEX,LSPRODEX,pbar,100)

#--------------------------------------------------------------------------------------------------
# Class to display the main gui
# Input: nothing
# Output: the main gui
#--------------------------------------------------------------------------------------------------

class main_gui(QMainWindow):

        def __init__(self,  conteneur=None):

                if conteneur is None : conteneur = self
                QMainWindow.__init__(conteneur)

                # Creating progress bar
                self.pbar = QtGui.QProgressBar(self)
                self.pbar.setMinimum(0)
                self.pbar.setMaximum(100)
                self.pbar.setAlignment(QtCore.Qt.AlignHCenter)

                # Creating menu bar
                self.create_action()
                self.create_menu()

                # Creating central widget
                self.Mainwidget = QtGui.QWidget(self)
                self.setCentralWidget(self.Mainwidget)
                self.setWindowTitle("NatApp GUI")
                self.setFixedSize(750,600)

                # Creating main vertical layout
                self.vlayout = QtGui.QVBoxLayout()

                # Creating main horizontal layout
                self.hlayout = QtGui.QHBoxLayout()

                # Creating main grid layout
                self.glayout = QtGui.QGridLayout()

                # Creating secondary horizontal layout
                self.layouth = QtGui.QHBoxLayout()

                # Creating main form layout
                self.flayout = QtGui.QFormLayout()

                # Creating the main page
                self.main_page()

        def create_action(self):

                self.action_help = QtGui.QAction(self.tr("&Help"), self)
                self.connect(self.action_help, SIGNAL("triggered()"), self.help_popup)

                self.action_quitter = QtGui.QAction(self.tr("&Close"), self)
                self.action_quitter.setShortcut(self.tr("Ctrl+Q"))
                self.connect(self.action_quitter, SIGNAL("triggered()"), self.exit)

                self.action_styledarkorange = QtGui.QAction(self.tr("&DarkOrange"), self)
                self.connect(self.action_styledarkorange, SIGNAL("triggered()"), self.tweak_darkorange)

                self.action_stylebasic = QtGui.QAction(self.tr("&Basic"), self)
                self.connect(self.action_stylebasic, SIGNAL("triggered()"), self.tweak_basic)

                self.action_styleplastique = QtGui.QAction(self.tr("&PLastique"), self)
                self.connect(self.action_styleplastique, SIGNAL("triggered()"), self.tweak_plastique)

                self.action_stylecde = QtGui.QAction(self.tr("&Cde"), self)
                self.connect(self.action_stylecde, SIGNAL("triggered()"), self.tweak_cde)

                self.action_stylemotif = QtGui.QAction(self.tr("&Motif"), self)
                self.connect(self.action_stylemotif, SIGNAL("triggered()"), self.tweak_motif)

                self.action_stylecleanlooks = QtGui.QAction(self.tr("&CleanLooks"), self)
                self.connect(self.action_stylecleanlooks, SIGNAL("triggered()"), self.tweak_cleanlooks)

                self.action_styledark = QtGui.QAction(self.tr("&Dark"), self)
                self.connect(self.action_styledark, SIGNAL("triggered()"), self.tweak_dark)

        def create_menu(self):

                self.statusBar()
                menubar = self.menuBar()

                menu_file = menubar.addMenu('&File')
                menu_file.addAction(self.action_help)
                menu_file.addAction(self.action_quitter)

                menu_tweak = menubar.addMenu('&Tweak')
                menu_tweak.addAction(self.action_stylebasic)
                menu_tweak.addAction(self.action_styledarkorange)
                menu_tweak.addAction(self.action_styledark)
                menu_tweak.addAction(self.action_styleplastique)
                menu_tweak.addAction(self.action_stylecde)
                menu_tweak.addAction(self.action_stylemotif)
                menu_tweak.addAction(self.action_stylecleanlooks)

        def exit(self):

                self.close()

        def tweak_basic(self):

                global GUI

                qssFile = ""
                GUI.setStyleSheet(qssFile)

        def tweak_darkorange(self):

                global GUI

                qssFile = open('darkorange_ss.qss').read()
                GUI.setStyleSheet(qssFile)

        def tweak_dark(self):

                global GUI

                qssFile = open('dark_ss.qss').read()
                GUI.setStyleSheet(qssFile)

        def tweak_plastique(self):

                global APP

                APP.setStyle("plastique")

        def tweak_cde(self):

                global APP

                APP.setStyle("cde")

        def tweak_motif(self):

                global APP

                APP.setStyle("motif")

        def tweak_cleanlooks(self):

                global APP

                APP.setStyle("cleanlooks")

        def help_popup(self):

                QMessageBox.about(self, 'Help', '''Write an <b>Application Name</b> and a <b>Version Name</b> if needed.<br />
                Select a <b>NATCO</b> and an <b>Environment</b> or leave it to <i>'All'</i>.''')

        def main_page(self):

                global APP

                # Creating clipboard
                clipboard = APP.clipboard()

                # Creating combo boxes and line edits
                appname = QtGui.QLineEdit()
                versname = QtGui.QLineEdit()
                natcocb = QtGui.QComboBox()
                envcb = QtGui.QComboBox()

                # Creating labels
                appnamelab = QtGui.QLabel("Application Name : ")
                appverslab = QtGui.QLabel("Version : " ) 
                natcolab = QtGui.QLabel("NATCO : ")
                envlab = QtGui.QLabel("Environment : ")

                # Creating result table
                self.table = QtGui.QTableWidget(self)
                self.table.setSortingEnabled(True)

                # Creating close and copy buttons
                valButton = QtGui.QPushButton("&OK")
                valButton.clicked.connect(lambda: self.natapp(appname.text(),versname.text(),str(natcocb.currentText()),str(envcb.currentText())))
                self.buttonCopy = QtGui.QPushButton("&Copy")
                self.buttonCopy.clicked.connect(lambda: self.fill_clipboard(clipboard))

                # Setting the size of the items
                appnamelab.setMaximumWidth(127)
                appverslab.setMaximumWidth(55)
                envlab.setMaximumWidth(92)
                natcolab.setMaximumWidth(50)
                appname.setMaximumWidth(150)
                appname.setMinimumWidth(150)
                versname.setMaximumWidth(150)
                versname.setMinimumWidth(150)
                natcocb.setMaximumWidth(150)
                natcocb.setMinimumWidth(150)
                envcb.setMaximumWidth(150)
                envcb.setMinimumWidth(150)
                valButton.setMaximumWidth(100)
                valButton.setMinimumWidth(75)
                buttonCopy.setMaximumWidth(100)
                buttonCopy.setMinimumWidth(75)

                # Filling the combo boxes
                natcocb.addItem('All')
                natcocb.addItem('FR')
                natcocb.addItem('DE')
                natcocb.addItem('UK')
                natcocb.addItem('ES')
                natcocb.addItem('IN')
                natcocb.addItem('EX')
                envcb.addItem('All')
                envcb.addItem('DEVelopment')
                envcb.addItem('VALidation')
                envcb.addItem('PRODuction')

                self.glayout.addWidget(appnamelab,0,0)
                self.glayout.addWidget(appname,0,1)
                self.glayout.addWidget(appverslab,0,2)
                self.glayout.addWidget(versname,0,3)
                self.glayout.addWidget(natcolab,1,0)
                self.glayout.addWidget(natcocb,1,1)
                self.glayout.addWidget(envlab,1,2)
                self.glayout.addWidget(envcb,1,3)
                self.glayout.addWidget(valButton,0,4)
                self.glayout.addWidget(buttonCopy,1,4)

                # Adding the table to the horizontal layout
                self.hlayout.addWidget(self.table)

                self.layouth.setAlignment(Qt.AlignLeft)

                self.vlayout.addLayout(self.glayout)
                self.vlayout.addLayout(self.hlayout)
                self.vlayout.addWidget(self.pbar)
                self.Mainwidget.setLayout(self.vlayout)

        def natapp(self,appname,versname,natco,env):

                global FULLLIST

                del_lists()
                make_lists(natco,env,self.pbar)
                full_list()

                if appname != "":
                        grep_name(appname)
                if versname != "":
                        grep_name(versname)

                make_listlists(natco,env)

                self.table.setRowCount(len(FULLLIST))

                # Filling list of keys

                list_key = ["Versions"]

                if not not LISTLISTS:
                        for item in LISTLISTS[0]:
                                list_key.append(item[:-2])

                self.table.setColumnCount(len(list_key))
                self.table.setHorizontalHeaderLabels(list_key)

                # Filling the result table

                if not not LISTLISTS:

                        line = 0
                        for vers in FULLLIST:
                                namevers = vers[2:-1]
                                self.table.setItem(line, 0, QtGui.QTableWidgetItem(namevers))
                                line = line + 1

                        for line in range(0,len(FULLLIST)):
                                col = 1
                                i = 0
                                for item in LISTLISTS[0]:
                                        tablewidgetitem = QtGui.QTableWidgetItem(LISTLISTS[line][i])

                                        if LISTLISTS[line][i].find("KO") != -1:
                                                tablewidgetitem.setForeground(QtCore.Qt.red)
                                        else:
                                                tablewidgetitem.setForeground(QtCore.Qt.darkGreen)

                                        self.table.setItem(line,col,tablewidgetitem)
                                        i = i + 1
                                        col = col + 1

                self.table.resizeColumnsToContents()

#--------------------------------------------------------------------------------------------------
# Fill the clipboard with printed data
# Input: Clipboard
# Output: Nothing
#--------------------------------------------------------------------------------------------------

        def fill_clipboard(self,clipb):

                global APP

                temptext = ""

                if not not LISTLISTS:

                        line = 0
                        for vers in FULLLIST:
                                namevers = vers[2:-1]
                                self.table.setItem(line, 0, QtGui.QTableWidgetItem(namevers))
                                line = line + 1

                        for line in range(0,len(FULLLIST)):

                                temptext = temptext + FULLLIST[line][2:-1] + " : "

                                for i in range(0,len(LISTLISTS[0])):

                                        temptext = temptext + LISTLISTS[line][i] + " "

                                temptext = temptext + "\n"

                        clipb.setText(temptext)

                        event = QtCore.QEvent(QtCore.QEvent.Clipboard)
                        APP.sendEvent(clipb,event)     

#--------------------------------------------------------------------------------------------------
# Main function
#--------------------------------------------------------------------------------------------------

if __name__ == "__main__":

        global APP
        global GUI

        APP = QApplication(sys.argv)
        GUI = main_gui()
        GUI.show()
        APP.exec_()

###################################################################################################