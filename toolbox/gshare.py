#!/bin/env python
# -*- coding: utf-8 -*-

# =================================================================================================
#
#  File Name      : gshare
#
#  Author         : JFA
#
#  Platform       : Unix / Linux
#
#  Version        :
#       1.4.1     2015/08/13    JFA   - Adding back and help buttons
#       1.4.0     2015/08/12    JFA   - Toolbox integration
#       1.3.0     2015/08/04    JFA   - Include a stylesheet
#       1.2.0     2015/07/30    JFA   - Add a progress bar
#       1.1.0     2015/07/29    JFA   - One screen app
#       1.0.0     2015/07/28    JFA   - Initial Version
#
#  Description    : Allows to know the disk usage of the share file of a specified server
#
# =================================================================================================

import os, sys
import subprocess
import datetime
import copy
from copy import deepcopy
import re, copy, time
import threading, signal
import numpy as np
from scipy import *
from threading import Timer
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *

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

DFDEVFR="df -h /share/fr0_devel"
DFDEVDE="df -h /share/de0_devel"
DFDEVUK="df -h /share/uk0_devel"
DFDEVES="df -h /share/es0_devel"
DFDEVIN="df -h /share/in0_devel"
DFDEVEX="df -h /share/fr0_devel"
DFVALFR="df -h /share/fr0_val"
DFVALDE="df -h /share/de0_val"
DFVALUK="df -h /share/uk0_val"
DFVALES="df -h /share/es0_val"
DFVALIN="df -h /share/fr0_val"
DFVALEX="df -h /share/fr0_val"
DFPRODFR="df -h /share/fr0_prod"
DFPRODDE="df -h /share/de0_prod"
DFPRODUK="df -h /share/uk0_prod"
DFPRODES="df -h /share/es0_prod"
DFPRODIN="df -h /share/fr0_prod"
DFPRODEX="df -h /share/fr0_prod"  

#--------------------------------------------------------------------------------------------------
# List of natco + environment lists
#--------------------------------------------------------------------------------------------------                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       

LISTSDF = []

#--------------------------------------------------------------------------------------------------
# List of natco + environment lists
#--------------------------------------------------------------------------------------------------                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       

LISTNAMEENV = []

#--------------------------------------------------------------------------------------------------
# SSH connexion
# Input: Host, command, progress bar and val
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
# Erase lists
# Input: Nothing
# Output: Empty lists
#--------------------------------------------------------------------------------------------------

def del_lists():
          
        global LISTSDF
        global LISTNAMEENV
         
        LISTSDF[:] = []
        LISTNAMEENV[:] = []

#--------------------------------------------------------------------------------------------------
# Creates the applications versions list, initialise lists, create de name list
# Input: NATCO, environment and progress bar
# Output: List of df and list of names
#--------------------------------------------------------------------------------------------------

def make_lists(natco,env,pbar):

        global LISTSDF
        global LISTNAMEENV

        pbar.setValue(0)

        if natco == "All":
                if env == "All":
                        LISTSDF = [[0 for x in range(18)] for x in range(18)]
                        LISTNAMEENV = [[0 for x in range(18)] for x in range(18)]
                        LISTSDF[0] =ssh_result(DEVFR,DFDEVFR,pbar,5)
                        LISTNAMEENV[0] = "DEV FR"
                        LISTSDF[1] = ssh_result(VALFR,DFVALFR,pbar,10)
                        LISTNAMEENV[1] = "VAL FR"
                        LISTSDF[2] = ssh_result(PRODFR,DFPRODFR,pbar,16)
                        LISTNAMEENV[2] = "PROD FR"
                        LISTSDF[3] = ssh_result(DEVDE,DFDEVDE,pbar,22)
                        LISTNAMEENV[3] = "DEV DE"
                        LISTSDF[4] = ssh_result(VALDE,DFVALDE,pbar,27)
                        LISTNAMEENV[4] = "VAL DE"
                        LISTSDF[5] = ssh_result(PRODDE,DFPRODDE,pbar,33)
                        LISTNAMEENV[5] = "PROD DE"
                        LISTSDF[6] = ssh_result(DEVUK,DFDEVUK,pbar,39)
                        LISTNAMEENV[6] = "DEV UK"
                        LISTSDF[7] = ssh_result(VALUK,DFVALUK,pbar,44)
                        LISTNAMEENV[7] = "VAL UK"
                        LISTSDF[8] = ssh_result(PRODUK,DFPRODUK,pbar,50)
                        LISTNAMEENV[8] = "PROD UK"
                        LISTSDF[9] = ssh_result(DEVES,DFDEVES,pbar,56)
                        LISTNAMEENV[9] = "DEV ES"
                        LISTSDF[10] = ssh_result(VALES,DFVALES,pbar,61)
                        LISTNAMEENV[10] = "VAL ES"
                        LISTSDF[11] = ssh_result(PRODES,DFPRODES,pbar,67)
                        LISTNAMEENV[11] = "PROD ES"
                        LISTSDF[12] = ssh_result(DEVIN,DFDEVIN,pbar,73)
                        LISTNAMEENV[12] = "DEV IN"
                        LISTSDF[13] = ssh_result(VALIN,DFVALIN,pbar,78)
                        LISTNAMEENV[13] = "VAL IN"
                        LISTSDF[14] = ssh_result(PRODIN,DFPRODIN,pbar,84)
                        LISTNAMEENV[14] = "PROD IN"
                        LISTSDF[15] = ssh_result(DEVEX,DFDEVEX,pbar,90)
                        LISTNAMEENV[15] = "DEV EX"
                        LISTSDF[16] = ssh_result(VALEX,DFVALEX,pbar,95)
                        LISTNAMEENV[16] = "VAL EX"
                        LISTSDF[17] = ssh_result(PRODEX,DFPRODEX,pbar,100)
                        LISTNAMEENV[17] = "PROD EX"
                elif env == "DEVelopment":
                        LISTSDF = [[0 for x in range(6)] for x in range(6)]
                        LISTNAMEENV = [[0 for x in range(6)] for x in range(6)]
                        LISTSDF[0] = ssh_result(DEVFR,DFDEVFR,pbar,16)
                        LISTNAMEENV[0] = "DEV FR"
                        LISTSDF[1] = ssh_result(DEVDE,DFDEVDE,pbar,33)
                        LISTNAMEENV[1] = "DEV DE"
                        LISTSDF[2] = ssh_result(DEVUK,DFDEVUK,pbar,50)
                        LISTNAMEENV[2] = "DEV UK"
                        LISTSDF[3] = ssh_result(DEVES,DFDEVES,pbar,67)
                        LISTNAMEENV[3] = "DEV ES"
                        LISTSDF[4] = ssh_result(DEVIN,DFDEVIN,pbar,84)
                        LISTNAMEENV[4] = "DEV IN"
                        LISTSDF[5] = ssh_result(DEVEX,DFDEVEX,pbar,100)
                        LISTNAMEENV[5] = "DEV EX"
                elif env == "VALidation":
                        LISTSDF = [[0 for x in range(6)] for x in range(6)]
                        LISTNAMEENV = [[0 for x in range(6)] for x in range(6)]
                        LISTSDF[0] = ssh_result(VALFR,DFVALFR,pbar,16)
                        LISTNAMEENV[0] = "VAL FR"
                        LISTSDF[1] = ssh_result(VALDE,DFVALDE,pbar,33)
                        LISTNAMEENV[1] = "VAL DE"
                        LISTSDF[2] = ssh_result(VALUK,DFVALUK,pbar,50)
                        LISTNAMEENV[2] = "VAL UK"
                        LISTSDF[3] = ssh_result(VALES,DFVALES,pbar,67)
                        LISTNAMEENV[3] = "VAL ES"
                        LISTSDF[4] = ssh_result(VALIN,DFVALIN,pbar,84)
                        LISTNAMEENV[4] = "VAL IN"
                        LISTSDF[5] = ssh_result(VALEX,DFVALEX,pbar,100)
                        LISTNAMEENV[5] = "VAL EX"
                elif env == "PRODuction":
                        LISTSDF = [[0 for x in range(6)] for x in range(6)]
                        LISTNAMEENV = [[0 for x in range(6)] for x in range(6)]
                        LISTSDF[0] = ssh_result(PRODFR,DFPRODFR,pbar,16)
                        LISTNAMEENV[0] = "PROD FR"
                        LISTSDF[1] = ssh_result(PRODDE,DFPRODDE,pbar,33)
                        LISTNAMEENV[1] = "PROD DE"
                        LISTSDF[2] = ssh_result(PRODUK,DFPRODUK,pbar,50)
                        LISTNAMEENV[2] = "PROD UK"
                        LISTSDF[3] = ssh_result(PRODES,DFPRODES,pbar,67)
                        LISTNAMEENV[3] = "PROD ES"
                        LISTSDF[4] = ssh_result(PRODIN,DFPRODIN,pbar,84)
                        LISTNAMEENV[4] = "PROD IN"
                        LISTSDF[5] = ssh_result(PRODEX,DFPRODEX,pbar,100)
                        LISTNAMEENV[5] = "PROD EX"
        elif natco == "FR":
                if env == "All":
                        LISTSDF = [[0 for x in range(3)] for x in range(3)]
                        LISTNAMEENV = [[0 for x in range(3)] for x in range(3)]
                        LISTSDF[0] = ssh_result(DEVFR,DFDEVFR,pbar,33)
                        LISTNAMEENV[0] = "DEV FR"
                        LISTSDF[1] = ssh_result(VALFR,DFVALFR,pbar,66)
                        LISTNAMEENV[1] = "VAL FR"
                        LISTSDF[2] = ssh_result(PRODFR,DFPRODFR,pbar,100)
                        LISTNAMEENV[2] = "PROD FR"
                elif env == "DEVelopment":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(DEVFR,DFDEVFR,pbar,100)
                        LISTNAMEENV[0] = "DEV FR"
                elif env == "VALidation":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(VALFR,DFVALFR,pbar,100)
                        LISTNAMEENV[0] = "VAL FR"
                elif env == "PRODuction":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(PRODFR,DFPRODFR,pbar,100)
                        LISTNAMEENV[0] = "PROD FR"
        elif natco == "DE":
                if env == "All":
                        LISTSDF = [[0 for x in range(3)] for x in range(3)]
                        LISTNAMEENV = [[0 for x in range(3)] for x in range(3)]
                        LISTSDF[0] = ssh_result(DEVDE,DFDEVDE,pbar,33)
                        LISTNAMEENV[0] = "DEV DE"
                        LISTSDF[1] = ssh_result(VALDE,DFVALDE,pbar,66)
                        LISTNAMEENV[1] = "VAL DE"
                        LISTSDF[2] = ssh_result(PRODDE,DFPRODDE,pbar,100)
                        LISTNAMEENV[2] = "PROD DE"
                elif env == "DEVelopment":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(DEVDE,DFDEVDE,pbar,100)
                        LISTNAMEENV[0] = "DEV DE"
                elif env == "VALidation":
                        LISTSDF = [[0 for x in range(1)] for x in range()]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(VALDE,DFVALDE,pbar,100)
                        LISTNAMEENV[0] = "VAL DE"
                elif env == "PRODuction":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(PRODDE,DFPRODDE,pbar,100)
                        LISTNAMEENV[0] = "PROD DE"
        elif natco == "UK":
                if env == "All":
                        LISTSDF = [[0 for x in range(3)] for x in range(3)]
                        LISTNAMEENV = [[0 for x in range(3)] for x in range(3)]
                        LISTSDF[0] = ssh_result(DEVUK,DFDEVUK,pbar,33)
                        LISTNAMEENV[0] = "DEV UK"
                        LISTSDF[1] = ssh_result(VALUK,DFVALUK,pbar,66)
                        LISTNAMEENV[1] = "VAL UK"
                        LISTSDF[2] = ssh_result(PRODUK,DFPRODUK,pbar,100)
                        LISTNAMEENV[2] = "PROD UK"
                elif env == "DEVelopment":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(DEVUK,DFDEVUK,pbar,100)
                        LISTNAMEENV[0] = "DEV UK"
                elif env == "VALidation":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(VALUK,DFVALUK,pbar,100)
                        LISTNAMEENV[0] = "VAL UK"
                elif env == "PRODuction":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(PRODUK,DFPRODUK,pbar,100)
                        LISTNAMEENV[0] = "PROD UK"
        elif natco == "ES":
                if env == "All":
                        LISTSDF = [[0 for x in range(3)] for x in range(3)]
                        LISTNAMEENV = [[0 for x in range(3)] for x in range(3)]
                        LISTSDF[0] = ssh_result(DEVES,DFDEVES,pbar,33)
                        LISTNAMEENV[0] = "DEV ES"
                        LISTSDF[1] = ssh_result(VALES,DFVALES,pbar,66)
                        LISTNAMEENV[1] = "VAL ES"
                        LISTSDF[2] = ssh_result(PRODES,DFPRODES,pbar,100)
                        LISTNAMEENV[2] = "PROD ES"
                elif env == "DEVelopment":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(DEVES,DFDEVES,pbar,100)
                        LISTNAMEENV[0] = "DEV ES"
                elif env == "VALidation":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(VALES,DFVALES,pbar,100)
                        LISTNAMEENV[0] = "VAL ES"
                elif env == "PRODuction":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(PRODES,DFPRODES,pbar,100)
                        LISTNAMEENV[0] = "PROD ES"
        elif natco == "IN":
                if env == "All":
                        LISTSDF = [[0 for x in range(3)] for x in range(3)]
                        LISTNAMEENV = [[0 for x in range(3)] for x in range(3)]
                        LISTSDF[0] = ssh_result(DEVIN,DFDEVIN,pbar,33)
                        LISTNAMEENV[0] = "DEV IN"
                        LISTSDF[1] = ssh_result(VALIN,DFVALIN,pbar,66)
                        LISTNAMEENV[1] = "VAL IN"
                        LISTSDF[2] = ssh_result(PRODIN,DFPRODIN,pbar,100)
                        LISTNAMEENV[2] = "PROD IN"
                elif env == "DEVelopment":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(DEVIN,DFDEVIN,pbar,100)
                        LISTNAMEENV[0] = "DEV IN"
                elif env == "VALidation":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(VALIN,DFVALIN,pbar,100)
                        LISTNAMEENV[0] = "VAL IN"
                elif env == "PRODuction":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(PRODIN,DFPRODIN,pbar,100)
                        LISTNAMEENV[0] = "PROD IN"
        elif natco == "EX":
                if env == "All":
                        LISTSDF = [[0 for x in range(3)] for x in range(3)]
                        LISTNAMEENV = [[0 for x in range(3)] for x in range(3)]
                        LISTSDF[0] = ssh_result(DEVEX,DFDEVEX,pbar,33)
                        LISTNAMEENV[0] = "DEV EX"
                        LISTSDF[1] = ssh_result(VALEX,DFVALEX,pbar,66)
                        LISTNAMEENV[1] = "VAL EX"
                        LISTSDF[2] = ssh_result(PRODEX,DFPRODEX,pbar,100)
                        LISTNAMEENV[2] = "PROD EX"
                elif env == "DEVelopment":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(DEVEX,DFDEVEX,pbar,100)
                        LISTNAMEENV[0] = "DEV EX"
                elif env == "VALidation":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(VALEX,DFVALEX,pbar,100)
                        LISTNAMEENV[0] = "VAL EX"
                elif env == "PRODuction":
                        LISTSDF = [[0 for x in range(1)] for x in range(1)]
                        LISTNAMEENV = [[0 for x in range(1)] for x in range(1)]
                        LISTSDF[0] = ssh_result(PRODEX,DFPRODEX,pbar,100)
                        LISTNAMEENV[0] = "PROD EX"

#--------------------------------------------------------------------------------------------------
# Back to the toolbox
# Input: Area and frame from toolbox
# Output: Nothing
#--------------------------------------------------------------------------------------------------
                
def exit(area,frameRoot):

        area.setWidget(frameRoot)

#--------------------------------------------------------------------------------------------------
# Displays a popup with an help message
# Input: Nothing
# Output: Help popup
#--------------------------------------------------------------------------------------------------

def help_popup(self):

        QMessageBox.about(self, 'Help', '''Select a <b>NATCO</b> and an <b>Environment</b> or leave it to <i>'All'</i>.''')

#--------------------------------------------------------------------------------------------------
# Fill the table with the results
# Input: Natco, environment, table and progress bar
# Output: Nothing
#--------------------------------------------------------------------------------------------------

def gshare(natco,env,table,pbar):

        del_lists()

        make_lists(natco,env,pbar)

        table.setRowCount(len(LISTSDF))

        # Filling the first column with the natco and environment
        
        if not not LISTNAMEENV:
                line = 0
                for name in LISTNAMEENV:
                        temp = str(name)
                        table.setItem(line,0,QTableWidgetItem(temp))
                        line = line + 1

                # Filling the second column with the filesystem name
                linefs = 0
                for data in LISTSDF:
                        tempfs = str(data[1])
                        table.setItem(linefs,1,QTableWidgetItem(tempfs))
                        
                        tempdata = str(data[2])
                        templist = tempdata.split()
                        table.setItem(linefs,2,QTableWidgetItem(templist[0]))
                        table.setItem(linefs,3,QTableWidgetItem(templist[1]))
                        table.setItem(linefs,4,QTableWidgetItem(templist[2]))
                        table.setItem(linefs,5,QTableWidgetItem(templist[3]))
                        table.setItem(linefs,6,QTableWidgetItem(templist[4]))

                        linefs = linefs + 1

#--------------------------------------------------------------------------------------------------
# Fill the clipboard with printed data
# Input: Clipboard and APP
# Output: Nothing
#--------------------------------------------------------------------------------------------------

def fill_clipboard(clipb,APP):

        temptext = ""

        if not not LISTNAMEENV:

                end = len(LISTNAMEENV)

                for i in range (0,end):

                        temp = str(LISTNAMEENV[i])
                        temptext = temptext + temp + " : " + "\n"

                        tempfs = str(LISTSDF[i][1])
                        temptext = temptext + "Filesystem : " + tempfs
                        
                        tempdata = str(LISTSDF[i][2])
                        templist = tempdata.split()

                        temptext = temptext + " 1K-blocks : " + templist[0] + "\n"
                        temptext = temptext + " Used : " + templist[1] + "\n"
                        temptext = temptext + " Available : " + templist[2] + "\n"
                        temptext = temptext + " Use% : " + templist[3] + "\n"
                        temptext = temptext + " Mounted on : " + templist[4] + "\n"
                        temptext = temptext + "\n"

                clipb.setText(temptext)

                event = QtCore.QEvent(QtCore.QEvent.Clipboard)
                APP.sendEvent(clipb,event)

#--------------------------------------------------------------------------------------------------
# Define the main page
# Input: APP, area and frame from toolbox
# Output: Nothing
#--------------------------------------------------------------------------------------------------

def main_page(self,APP,area,frameRoot):

        # Creating frames widgets
        frame = QtGui.QFrame()

        # Creating progress bar
        pbar = QtGui.QProgressBar()
        pbar.setMinimum(0)
        pbar.setMaximum(100)
        pbar.setAlignment(QtCore.Qt.AlignHCenter)

        # Creating main vertical layout
        vlayout = QtGui.QVBoxLayout()

        # Creating main horizontal layout
        hlayout = QtGui.QHBoxLayout()

        # Creating secondary horizontal layout
        layouth = QtGui.QHBoxLayout()

        # Creating clipboard
        clipboard = APP.clipboard()

        # Creating combo boxes
        natcocb = QtGui.QComboBox()
        envcb = QtGui.QComboBox()

        # Creating labels
        natcolab = QtGui.QLabel("NATCO : ")
        envlab = QtGui.QLabel("Environment : ")

        # Creating result table
        table = QtGui.QTableWidget()
        table.setSortingEnabled(True)

        # Creating ok and copy buttons
        valButton = QtGui.QPushButton("&OK")
        valButton.clicked.connect(lambda: gshare(str(natcocb.currentText()),str(envcb.currentText()),table,pbar))
        buttonCopy = QtGui.QPushButton("&Copy")
        buttonCopy.clicked.connect(lambda: fill_clipboard(clipboard,APP))
        buttonHelp = QtGui.QPushButton("&Help")
        buttonHelp.clicked.connect(lambda: help_popup(self))
        buttonClose = QtGui.QPushButton("&Close")
        buttonClose.clicked.connect(lambda: exit(area,frameRoot))

        # Setting the size of the items
        natcolab.setMaximumWidth(50)
        natcocb.setMaximumWidth(150)
        natcocb.setMinimumWidth(150)
        envlab.setMaximumWidth(92)
        envcb.setMaximumWidth(150)
        envcb.setMinimumWidth(150)
        valButton.setMaximumWidth(100)
        valButton.setMinimumWidth(75)
        buttonCopy.setMaximumWidth(100)
        buttonCopy.setMinimumWidth(75)
        buttonHelp.setMaximumWidth(100)
        buttonHelp.setMinimumWidth(75)
        buttonClose.setMaximumWidth(100)
        buttonClose.setMinimumWidth(75)

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
        
        # Filling list of keys
        list_key = ["Name","Filesystem","1K-blocks","Used","Available","Use%","Mounted on"]

        table.setColumnCount(len(list_key))
        table.setHorizontalHeaderLabels(list_key)

        table.resizeColumnsToContents()

        layouth.addWidget(natcolab)
        layouth.addWidget(natcocb)
        layouth.addWidget(envlab)
        layouth.addWidget(envcb)
        layouth.addWidget(valButton)
        layouth.addWidget(buttonCopy)
        layouth.addWidget(buttonHelp)
        layouth.addWidget(buttonClose)

        # Adding the table to the horizontal layout
        hlayout.addWidget(table)
        
        layouth.setAlignment(Qt.AlignLeft)

        vlayout.addLayout(layouth)
        vlayout.addLayout(hlayout)
        vlayout.addWidget(pbar)

        frame.setLayout(vlayout)

        area.setWidget(frame)

###################################################################################################
