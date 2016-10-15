#!/bin/env python
# -*- coding: utf-8 -*-

# ======================================================================================
#
#  File Name      : toolbox
#
#  Author         : JFA
#
#  Platform       : Unix / Linux
#
#  Version        :
#       1.2.1     2015/09/18    JFA   - Adding guser script
#       1.2.0     2015/08/13    JFA   - Adding gshare script
#       1.1.0     2015/08/10    JFA   - Adding tab navigation
#       1.0.0     2015/07/20    JFA   - Initial Version
#
#  Description    : Application to provide tools for analysis and bug fixing
#                    on GISEH
#
# ======================================================================================

import os, sys
import subprocess
import datetime
import copy
from copy import deepcopy

#---------------------------------------------------------------------------------------
# Launch the ppack_gnu_435 environment before launching the script
#---------------------------------------------------------------------------------------

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

#---------------------------------------------------------------------------------------
# Import scripts 
#---------------------------------------------------------------------------------------

import gshare
import gnatapp
import guser

#---------------------------------------------------------------------------------------
# Import modules
#---------------------------------------------------------------------------------------

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

#---------------------------------------------------------------------------------------
# Class to display the main gui
# Input: nothing
# Output: the main gui
#---------------------------------------------------------------------------------------

class main_gui(QMainWindow):

        def __init__(self,  conteneur=None):

                if conteneur is None : conteneur = self
                
                QMainWindow.__init__(conteneur)

                self.create_action()

                # Creating menu bar
                self.create_menu()

                # Creating central widget
                self.mdiarea = QtGui.QMdiArea()
                self.Mainwidget = QtGui.QWidget(self)
                self.setCentralWidget(self.mdiarea)
                self.setWindowTitle("GISEH Toolbox")
                self.resize(800,600)

                # Creating sub windows
                self.areaFacility = QtGui.QMdiSubWindow()
                self.areaFacility.setWindowTitle("Facility")
                self.areaDeployment = QtGui.QMdiSubWindow()
                self.areaDeployment.setWindowTitle("Deployment")
                self.areaAdministration = QtGui.QMdiSubWindow()
                self.areaAdministration.setWindowTitle("Administration")
                self.areaLsf = QtGui.QMdiSubWindow()
                self.areaLsf.setWindowTitle("LSF")

                # Creating main vertical layout
                self.vlayout = QtGui.QVBoxLayout()

                # Creating main horizontal layout
                self.hlayout = QtGui.QHBoxLayout()

                # Creating main form layout
                self.flayout = QtGui.QFormLayout()

                # Creating the main tab widget
                self.tabWidget = QtGui.QTabWidget()

                # Creating frame widgets
                self.frameFacility = QtGui.QFrame()
                self.frameDeployment = QtGui.QFrame()
                self.frameAdministration = QtGui.QFrame()
                self.frameLsf = QtGui.QFrame()

                # Creating the main page
                self.main_page()

        def create_action(self):

                self.action_server = QtGui.QAction(self.tr("Server"), self)
                self.connect(self.action_server, SIGNAL("triggered()"), self.server)

                self.action_accounts = QtGui.QAction(self.tr("Accounts"), self)
                self.connect(self.action_accounts, SIGNAL("triggered()"), self.accounts)

                self.action_applications = QtGui.QAction(self.tr("Applications"), self)
                self.connect(self.action_applications, SIGNAL("triggered()"), self.applications)

                self.action_verification = QtGui.QAction(self.tr("Verification"), self)
                #self.connect(self.action_verification, SIGNAL("triggered()"), self.verification)

                self.action_execution = QtGui.QAction(self.tr("Execution"), self)
                #self.connect(self.action_execution, SIGNAL("triggered()"), self.execution)

                self.action_servers = QtGui.QAction(self.tr("Servers"), self)
                #self.connect(self.action_servers, SIGNAL("triggered()"), self.servers)

                self.action_sgd = QtGui.QAction(self.tr("SGD"), self)
                #self.connect(self.action_sgd, SIGNAL("triggered()"), self.sgd)

                self.action_expiration = QtGui.QAction(self.tr("Expiration"), self)
                #self.connect(self.action_expiration, SIGNAL("triggered()"), self.expiration)

                self.action_lsf = QtGui.QAction(self.tr("LSF"), self)
                #self.connect(self.action_lsf, SIGNAL("triggered()"), self.lsf)

                self.action_help = QtGui.QAction(self.tr("&Help"), self)
                self.connect(self.action_help, SIGNAL("triggered()"), self.help_popup)

                self.action_quitter = QtGui.QAction(self.tr("&Close"), self)
                self.action_quitter.setShortcut(self.tr("Ctrl+Q"))
                self.connect(self.action_quitter, SIGNAL("triggered()"), self.exit)

        def server(self) :

                global APP

                gshare.main_page(self,APP,self.areaFacility,self.frameFacility)

        def accounts(self) :

                global APP

                guser.main_page(self,APP,self.areaFacility,self.frameFacility)

        def applications(self) :

                global APP

                gnatapp.main_page(self,APP,self.areaFacility,self.frameFacility)

        def create_menu(self):

                self.statusBar()
                menubar = self.menuBar()

                menu_file = menubar.addMenu('&File')
                menu_file.addAction(self.action_help)
                menu_file.addAction(self.action_quitter)

                menu_facility = menubar.addMenu('&Facility')
                menu_facility.addAction(self.action_server)
                menu_facility.addAction(self.action_accounts)
                menu_facility.addAction(self.action_applications)

                menu_deployment = menubar.addMenu('&Deployment')
                menu_deployment.addAction(self.action_verification)
                menu_deployment.addAction(self.action_execution)

                menu_administration = menubar.addMenu('&Administration')
                menu_administration.addAction(self.action_servers)
                menu_administration.addAction(self.action_sgd)
                menu_administration.addAction(self.action_expiration)

                menu_lsf = menubar.addMenu('&LSF')
                menu_lsf.addAction(self.action_lsf)

                menu_app = menubar.addMenu('&Applications')
                menu_app.addMenu(menu_facility)
                menu_app.addSeparator()
                menu_app.addMenu(menu_deployment)
                menu_app.addSeparator()
                menu_app.addMenu(menu_administration)
                menu_app.addSeparator()
                menu_app.addMenu(menu_lsf)

        def exit(self):

                self.close()

        def help_popup(self):

                QMessageBox.about(self, 'Help', '''Lorem ipsum dolor sit amet.''')

        def facilityTab(self):

                # Creating grid layout
                glayoutFacility = QtGui.QGridLayout()

                # Creating buttons
                serverButton = QtGui.QPushButton("&Server")
                serverButton.clicked.connect(lambda: self.server())
                accountsButton = QtGui.QPushButton("&Accounts")
                accountsButton.clicked.connect(lambda: self.accounts())
                applicationsButton = QtGui.QPushButton("&Applications")
                applicationsButton.clicked.connect(lambda: self.applications())

                # Setting buttons size
                serverButton.setMaximumWidth(100)
                serverButton.setMinimumWidth(100)
                accountsButton.setMaximumWidth(100)
                accountsButton.setMinimumWidth(100)
                applicationsButton.setMaximumWidth(100)
                applicationsButton.setMinimumWidth(100)

                # Creating labels
                serverLab = QtGui.QLabel("Allow to check the free space available on share files on a specified natco and environment.")
                accountsLab = QtGui.QLabel("Allows to find informations on a user.")
                applicationsLab = QtGui.QLabel("Allow to find the differences between application versions in all natcos or to list versions of a spectific application.")

                # Adding buttons and labels to the grid layouts
                glayoutFacility.addWidget(serverButton,0,0)
                glayoutFacility.addWidget(serverLab,0,1)
                glayoutFacility.addWidget(accountsButton,1,0)
                glayoutFacility.addWidget(accountsLab,1,1)
                glayoutFacility.addWidget(applicationsButton,2,0)
                glayoutFacility.addWidget(applicationsLab,2,1)

                self.frameFacility.setLayout(glayoutFacility)

                self.areaFacility.setWidget(self.frameFacility)

        def deploymentTab(self):

                # Creating grid layout
                glayoutDeployment = QtGui.QGridLayout()

                # Creating buttons
                verificationButton = QtGui.QPushButton("&Verification")
                executionButton = QtGui.QPushButton("&Execution")

                # Setting buttons size
                verificationButton.setMaximumWidth(100)
                verificationButton.setMinimumWidth(100)
                executionButton.setMaximumWidth(100)
                executionButton.setMinimumWidth(100)

                # Creating labels
                verificationLab = QtGui.QLabel("Lorem ipsum dolor sit amet test test test test test test test test test test test test.")
                executionLab = QtGui.QLabel("Lorem ipsum dolor sit amet test test test test test test test test test test test test.")

                # Adding buttons and labels to the grid layouts
                glayoutDeployment.addWidget(verificationButton,0,0)
                glayoutDeployment.addWidget(verificationLab,0,1)
                glayoutDeployment.addWidget(executionButton,1,0)
                glayoutDeployment.addWidget(executionLab,1,1)

                self.frameDeployment.setLayout(glayoutDeployment)

                self.areaDeployment.setWidget(self.frameDeployment)

        def administrationTab(self):

                # Creating grid layout
                glayoutAdministration = QtGui.QGridLayout()

                # Creating buttons
                serversButton = QtGui.QPushButton("&Servers")
                sgdButton = QtGui.QPushButton("&SGD")
                expirationButton = QtGui.QPushButton("&Expiration")

                # Setting buttons size
                serversButton.setMaximumWidth(100)
                serversButton.setMinimumWidth(100)
                sgdButton.setMaximumWidth(100)
                sgdButton.setMinimumWidth(100)
                expirationButton.setMaximumWidth(100)
                expirationButton.setMinimumWidth(100)

                # Creating labels
                serversLab = QtGui.QLabel("Lorem ipsum dolor sit amet test test test test test test test test test test test test.")
                sgdLab = QtGui.QLabel("Lorem ipsum dolor sit amet test test test test test test test test test test test test.")
                expirationLab = QtGui.QLabel("Lorem ipsum dolor sit amet test test test test test test test test test test test test.")

                # Adding buttons and labels to the grid layouts
                glayoutAdministration.addWidget(serversButton,0,0)
                glayoutAdministration.addWidget(serversLab,0,1)
                glayoutAdministration.addWidget(sgdButton,1,0)
                glayoutAdministration.addWidget(sgdLab,1,1)
                glayoutAdministration.addWidget(expirationButton,2,0)
                glayoutAdministration.addWidget(expirationLab,2,1)

                self.frameAdministration.setLayout(glayoutAdministration)

                self.areaAdministration.setWidget(self.frameAdministration)

        def lsfTab(self):

                # Creating grid layout
                glayoutLsf = QtGui.QGridLayout()

                # Creating button
                lsfButton = QtGui.QPushButton("&LSF")

                # Setting button size
                lsfButton.setMaximumWidth(100)
                lsfButton.setMinimumWidth(100)

                # Creating label
                lsfLab = QtGui.QLabel("Lorem ipsum dolor sit amet test test test test test test test test test test test test.")

                # Adding buttons and labels to the grid layouts
                glayoutLsf.addWidget(lsfButton,0,0)
                glayoutLsf.addWidget(lsfLab,0,1)
                
                self.frameLsf.setLayout(glayoutLsf)

                self.areaLsf.setWidget(self.frameLsf)

        def main_page(self):

                self.facilityTab()
                self.deploymentTab()
                self.administrationTab()
                self.lsfTab()

                self.mdiarea.addSubWindow(self.areaFacility)
                self.mdiarea.addSubWindow(self.areaDeployment)
                self.mdiarea.addSubWindow(self.areaAdministration)
                self.mdiarea.addSubWindow(self.areaLsf)

                self.mdiarea.setActiveSubWindow(self.areaFacility)

                self.mdiarea.setViewMode(self.mdiarea.TabbedView)

#-----------------------------------------------------------------------------------------------
# Main function
#-----------------------------------------------------------------------------------------------

if __name__ == "__main__":

        global APP

        APP = QApplication(sys.argv)
        APP.setStyle("plastique")

        gui = main_gui()
        gui.show()

        APP.exec_()

##############################################################################################
