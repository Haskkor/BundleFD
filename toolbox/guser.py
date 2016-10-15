#!/bin/env python
# -*- coding: utf-8 -*-

# =================================================================================================
#
#  File Name      : guser
#
#  Author         : JFA
#
#  Platform       : Unix / Linux
#
#  Version        :
#       1.0.0     2015/09/16    JFA   - Initial Version
#
#  Description    : Allows to find informations on a user
#
# =================================================================================================

import os, sys, platform
import shlex
import subprocess
import datetime
import re, copy, time
import threading, signal
import numpy as np
from scipy import *
from threading import Timer
from threading import Timer
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#--------------------------------------------------------------------------------------------------
# Variables
#--------------------------------------------------------------------------------------------------                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       

LOGIN = ""
NAME = ""
DIRECTORY = ""
ONLAST = ""
HOST = ""

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

    QMessageBox.about(self, 'Help', '''Write a <b>user ID</b>.''')

#--------------------------------------------------------------------------------------------------
# Displays a popup with an error message
# Input: Nothing
# Output: Help popup
#--------------------------------------------------------------------------------------------------

def error_popup(self):

    QMessageBox.about(self, 'Error', '''User doesn't exist.''')

#--------------------------------------------------------------------------------------------------
# Fill the clipboard with printed data
# Input: Clipboard and APP
# Output: Nothing
#--------------------------------------------------------------------------------------------------

def fill_clipboard(clipb,APP):

        temptext = ""

        if LOGIN != "" :
                
                temptext = "Login : " + LOGIN + "\n"
                temptext = temptext + "Name : " + NAME + "\n"
                temptext = temptext + "Directory : " + DIRECTORY + "\n"
                temptext = temptext + ONLAST + "\n"
                temptext = temptext + "Host : " + HOST + "\n"
                temptext = temptext + "\n"

                clipb.setText(temptext)

                event = QtCore.QEvent(QtCore.QEvent.Clipboard)
                APP.sendEvent(clipb,event)

#--------------------------------------------------------------------------------------------------
# Make the command, get the result and parse it
# Input: User ID
# Output: Table filled
#--------------------------------------------------------------------------------------------------

def guser(self,userid,table):

    global LOGIN
    global NAME
    global DIRECTORY
    global ONLAST
    global HOST 

    command = "finger " + str(userid)
    command = shlex.split(command)

    finger = subprocess.Popen(command, shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    result = finger.stdout.readlines()
    if result == []:
        error = finger.stderr.readlines()
        error_popup(self)
    else:
        table.setRowCount(1)
        
        part1 = result[0].split()
        part2 = result[1].split()
        part3 = result[2].split()
            
        table.setItem(0,0,QTableWidgetItem(part1[1]))
        LOGIN = part1[1]
        table.setItem(0,1,QTableWidgetItem(part1[3]))
        NAME = part1[3]
        table.setItem(0,2,QTableWidgetItem(part2[1]))
        DIRECTORY = part2[1]
        line = part3[0] + " " + part3[1] + " " + part3[2] + " " + part3[3] + " " + part3[4] + " " + part3[5] + " " + part3[6]
        table.setItem(0,3,QTableWidgetItem(line))
        ONLAST = line
        table.setItem(0,4,QTableWidgetItem(part3[10]))
        HOST = part3[10]

#--------------------------------------------------------------------------------------------------
# Define the main page
# Input: APP, area and frame from toolbox
# Output: Nothing
#--------------------------------------------------------------------------------------------------

def main_page(self,APP,area,frameRoot):

    # Creating frames widgets
    frame = QtGui.QFrame()

    # Creating main vertical layout
    vlayout = QtGui.QVBoxLayout()

    # Creating main horizontal layout
    hlayout = QtGui.QHBoxLayout()

    # Creating secondary horizontal layout
    layouth = QtGui.QHBoxLayout()

    # Creating clipboard
    clipboard = APP.clipboard()

    # Creating label
    useridlab = QtGui.QLabel("User ID : ")

    # Creating line edit
    useridedit = QtGui.QLineEdit()

    # Creating result table
    table = QtGui.QTableWidget()
    table.setSortingEnabled(True)

    # Creating ok and copy buttons
    valButton = QtGui.QPushButton("&OK")
    valButton.clicked.connect(lambda: guser(self,useridedit.text(),table))
    buttonCopy = QtGui.QPushButton("&Copy")
    buttonCopy.clicked.connect(lambda: fill_clipboard(clipboard,APP))
    buttonHelp = QtGui.QPushButton("&Help")
    buttonHelp.clicked.connect(lambda: help_popup(self))
    buttonClose = QtGui.QPushButton("&Close")
    buttonClose.clicked.connect(lambda: exit(area,frameRoot))

    # Setting the size of the items
    useridlab.setMaximumWidth(50)
    valButton.setMaximumWidth(100)
    valButton.setMinimumWidth(75)
    buttonCopy.setMaximumWidth(100)
    buttonCopy.setMinimumWidth(75)
    buttonHelp.setMaximumWidth(100)
    buttonHelp.setMinimumWidth(75)
    buttonClose.setMaximumWidth(100)
    buttonClose.setMinimumWidth(75)
        
    # Filling list of keys
    list_key = ["Login","Name","Directory","On Since / Last Login","Host"]

    table.setColumnCount(len(list_key))
    table.setHorizontalHeaderLabels(list_key)

    table.resizeColumnsToContents()

    layouth.addWidget(useridlab)
    layouth.addWidget(useridedit)
    layouth.addWidget(valButton)
    layouth.addWidget(buttonCopy)
    layouth.addWidget(buttonHelp)
    layouth.addWidget(buttonClose)

    # Adding the table to the horizontal layout
    hlayout.addWidget(table)
        
    layouth.setAlignment(Qt.AlignLeft)

    vlayout.addLayout(layouth)
    vlayout.addLayout(hlayout)

    frame.setLayout(vlayout)

    area.setWidget(frame)

###################################################################################################























