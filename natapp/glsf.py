#!/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
#
#  File Name      : glsf
#
#  Author         : RG
#
#  Platform       : Unix / Linux
#
#  Version        : 1.0 - 2015/06/19 RG - Initial Version
#
#  $Header: @(#) bsub.  v1.0  2015/05/19  fdb.tfite.unix@gfi.fr
#
#
#  Description    : Script to check LSF jobs
#
# =============================================================================

import os, sys
import subprocess
import datetime

#---------------------------------------------------------------------------------------
# We launch the ppack_gnu_435 environment before launching the script
#---------------------------------------------------------------------------------------

# if the new environment is set then we skip this part
if not 'CDTNG_PPACK_GNU_435_CMD' in os.environ:

        command = ['bash', '-c', "eval $(ppack_gnu_435 --version 3.3 --setenvironment) && env"]

        proc = subprocess.Popen(command, stdout = subprocess.PIPE)
        stdout, stderr = proc.communicate()

        lp_save = ["", ""]
        for line in stdout.split("\n")[:-1]:
                lp = line.split("=",1)
                if len(lp) > 2:
                        continue
                elif len(lp) == 1: # cas HPC ou la variable BASH_FUNC_module() est sur deux lignes avec un } seul sur la deuxième pour finir la fonction
                        os.environ[lp_save[0]] = lp_save[1] + "\n" + lp[0]
                else:
                        os.environ[lp[0]] = lp[1]
                        lp_save = lp

        # we launch again the process with the new environment
        os.execve(os.path.realpath(__file__), sys.argv, os.environ)

#---------------------------------------------------------------------------------------
# import modules
#---------------------------------------------------------------------------------------

import re, copy, time
import threading, signal
import numpy as np
from threading import Timer
import pyqtgraph as pg
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication, QMainWindow
from PyQt4.QtCore import SIGNAL

#---------------------------------------------------------------------------------------
# function to send command through a forked process in order to kill it after some time
# input: command
# output: output and error
#---------------------------------------------------------------------------------------

def send_command(command_list):

        global command_failed
        global res_command

        res_command = ["", "", "", ""]
        command_failed = [False, "ERROR: The following command has been killed after waiting " + str(timeout) +  "s:\n"]

        nb_command = len(command_list)
        for command in command_list:
                semaphore.acquire()

                threads = []

                #print command
                fct_command = threading.Thread(target=send_command_into_fork, args=(command, nb_command, command_list.index(command),))

                threads.append(fct_command)

                fct_command.start()

        #wait end of all thread
        for thread in threading.enumerate():
                if thread is not threading.currentThread():
                        thread.join()

        if command_failed[0]:
                message(command_failed[1])
                res_command[2] = True
        command_failed = [False, ""]

        return res_command

#---------------------------------------------------------------------------------------
# function to send command
# input: command
# output: output and error
#---------------------------------------------------------------------------------------

def send_command_into_fork(command, nb_command, ind):

        def kill_process(pid, command):

                global command_failed

                message =  command + "\n"
                os.killpg(pid, signal.SIGTERM)
                command_failed = [True, command_failed[1] + message]

        proc = subprocess.Popen([command],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,preexec_fn=os.setsid)

        timer = Timer(timeout, kill_process, [proc.pid, command])
        timer.start()
        stdout, stderr = proc.communicate()
        timer.cancel()

        res_command[0] = res_command[0] + stdout
        res_command[1] = res_command[1] + stderr

        semaphore.release()

        #print command, " ------------DONE-------------- ", str(ind+1) + "/" + str(nb_command)

        return

#---------------------------------------------------------------------------------------
# function pour trouver la liste des clusters
# input: rien
# output: liste des clusters lsf
#---------------------------------------------------------------------------------------

def get_clusters():

        out = send_command(["lsclusters | sed '1d' | awk '{print $1}'"])
        stdout = out[0]
        stderr = out[1]

        cluster_list = []
        for cluster in stdout.split("\n"):
                if cluster != "":
                        cluster_list.append(cluster)

        return cluster_list
#---------------------------------------------------------------------------------------
# function pour trouver la liste des clusters
# input: un uid
# output: liste des jobs
#---------------------------------------------------------------------------------------

def get_jobs(user, liste):

        list_jobs = []
        now = datetime.datetime.now()

        bar = progressbar()
        for cluster in liste:
                bar.update_progressbar(cluster, cluster_list.index(cluster))
                out = send_command(["bjobs -w -u " + user + " -m " + cluster + " 2>/dev/null"])
                stdout = out[0]
                stderr = out[1]

                #print stdout
                if stdout != "" or stdout != ' ':
                        jobs = stdout.split("\n")[1:]
                        for linejob in jobs:

                                #print linejob
                                job = re.sub(r"\s+","-_-",linejob).split("-_-")
                                #print job
                                if len(job) == 10:
                                        tmp = {}
                                        tmp['CLUSTER'] = cluster
                                        tmp['JOBID'] = job[0]
                                        tmp['USER'] = job[1]
                                        tmp['STAT'] = job[2]
                                        tmp['QUEUE'] = job[3]
                                        tmp['FROM_HOST'] = job[4]
                                        tmp['EXEC_HOST'] = job[5]
                                        tmp['JOB_NAME'] = job[6]
                                        month = datetime.datetime.strptime(job[7], "%b").month
                                        tmp['SUBMIT_TIME'] = datetime.datetime(now.year, month, int(job[8]), int(job[9].split(":")[0]), int(job[9].split(":")[1])).strftime("%Y/%m/%d - %H:%M")

#                                       print tmp
                                        list_jobs.append(tmp)

        return list_jobs

#---------------------------------------------------------------------------------------
# function pour trouver un job
# input: un jobid
# output: liste des jobs
#---------------------------------------------------------------------------------------

def recherche_job(jobid):

        list_jobs = []
        now = datetime.datetime.now()

        bar = progressbar()
        for cluster in cluster_list:
                bar.update_progressbar(cluster, cluster_list.index(cluster))
                out = send_command(["bjobs -a -w -m " + cluster + " " + jobid + " 2>/dev/null"])
                stdout = out[0]
                stderr = out[1]

                #print stdout
                if stdout != "" or stdout != ' ':
                        jobs = stdout.split("\n")[1:]
                        for linejob in jobs:

                                #print linejob
                                job = re.sub(r"\s+","-_-",linejob).split("-_-")
                                #print job, len(job)
                                if len(job) == 10:
                                        tmp = {}
                                        tmp['CLUSTER'] = cluster
                                        tmp['JOBID'] = job[0]
                                        tmp['USER'] = job[1]
                                        tmp['STAT'] = job[2]
                                        tmp['QUEUE'] = job[3]
                                        tmp['FROM_HOST'] = job[4]
                                        tmp['EXEC_HOST'] = job[5]
                                        tmp['JOB_NAME'] = job[6]
                                        month = datetime.datetime.strptime(job[7], "%b").month
                                        tmp['SUBMIT_TIME'] = datetime.datetime(now.year, month, int(job[8]), int(job[9].split(":")[0]), int(job[9].split(":")[1]))

                                        #print tmp
                                        list_jobs.append(tmp)

        return list_jobs

#-----------------------------------------------------------------------------------------------
# fonction qui cherche le meilleur noeud d'un cluster pour faire un ssh
# input: cluster
# output: best node
#-----------------------------------------------------------------------------------------------

def best_node(cluster):

        out = send_command(["lsload -w " + cluster + " | grep 'ok' | sort -g -k9 -k3 -k4"])
        stdout = out[0]
        stderr = out[1]

        node = ""
        if stdout != "" or stdout != ' ':
                nodes = stdout.split("\n")[1:]
                for linenode in nodes:
                        node =  re.sub(r"\s+","-_-",linenode).split("-_-")[0]
                        break

        return node

#-----------------------------------------------------------------------------------------------
# fonction qui cherche les jobs à travers bhist
# input: donne sur un job
# output: liste des jobs trouvé
#-----------------------------------------------------------------------------------------------

def recherche_ancien_job(job_data):

        if job_data[1] == "":
                user = "all"
        else:
                user = job_data[1]

        #bar = progressbar()
        liste_command = []
        for cluster in cluster_list:
                if cluster[-2:] == "_s" or cluster[-2:] == "_i":
                        continue
                #bar.update_progressbar(cluster, cluster_list.index(cluster))

                node = best_node(cluster)

                if job_data[0] == "":
                        liste_command.append("echo '" + cluster + " " + node + "'; ssh " + node + " bhist -n " + job_data[2] + " -d -e -u " + user + " | sed '1,2d'")
                else:
                        liste_command.append("echo '" + cluster + " " + node + "'; ssh " + node + " bhist -n " + job_data[2] + " -d -e -u " + user + " " + job_data[0] + " | sed '1,2d'")

        out = send_command(liste_command)
        stdout = out[0]
        stderr = out[1]

        list_jobs = []
        if stdout != "" or stdout != ' ':
                line = stdout.split("\n")
                if '' in line:
                        # on enlève tous les '' de la ligne
                        line = filter(lambda a: a != '', line)
                if len(line) > 1:
                        for linejob in line:
                                job = re.sub(r"\s+","-_-",linejob).split("-_-")

                                if job[0] in cluster_list:
                                        cluster = job[0]
                                        node = job[1]
                                        continue

                                tmp = {}
                                tmp['CLUSTER'] = cluster
                                tmp['JOBID'] = job[0]
                                tmp['USER'] = job[1]
                                tmp['JOB_NAME'] = job[2]
                                tmp['PEND'] = job[3]
                                tmp['PSUSP'] = job[4]
                                tmp['RUN'] = job[5]
                                tmp['USUSP'] = job[6]
                                tmp['SSUSP'] = job[7]
                                tmp['UNKWN'] = job[8]
                                tmp['TOTAL'] = job[9]
                                tmp['node'] = node

                                list_jobs.append(tmp)

        return list_jobs

#-----------------------------------------------------------------------------------------------
# fonction pour faire des stats sur un profile
# input: nom du profile
# output: les stats
#-----------------------------------------------------------------------------------------------

def stat_profile(profile):

        liste_command = []
        for cluster in cluster_list:
                if cluster[-2:] == "_s" or cluster[-2:] == "_i":
                        continue
                #bar.update_progressbar(cluster, cluster_list.index(cluster))

                node = best_node(cluster)

                liste_command.append("ssh " + node + " bhist -n4 -d -u all -app " + profile + " -l | grep -A1 ' PEND ' | grep -v '-' | grep -v 'PEND'")
                liste_command.append("ssh " + node + " bhist -n4 -d -u all -app " + profile + " -l | grep 'MAX MEM:'")

        out = send_command(liste_command)

        stdout_mem = [item for item in out[0].split("\n") if 'MEM' in item]
        stdout_time = [item for item in out[0].split("\n") if 'MEM' not in item]

        list_mem_max = []
        list_mem_avg = []
        list_run_time = []

        for line in stdout_mem:
                lines = line.split(';')
                for line2 in lines:
                        tmp = re.findall(':\s\w.*', line2)
                        #print line, line2, tmp, tmp[0][-6]
                        if tmp[0][-6] == 'G':
                                if lines.index(line2) == 0:
                                        list_mem_max.append(float(tmp[0][1:-6]) * 1000)
                                else:
                                        list_mem_avg.append(float(tmp[0][1:-6]) * 1000)
                        elif tmp[0][-6] == 'M':
                                if lines.index(line2) == 0:
                                        list_mem_max.append(int(tmp[0][1:-6]))
                                else:
                                        list_mem_avg.append(int(tmp[0][1:-6]))
                        else:
                                continue

        for line in stdout_time:
                tmp = re.sub(r"\s+","-_-", line).split("-_-")
                if len(tmp) >= 8:
                        try:
                                list_run_time.append(int(tmp[3]))
                        except:
                                print line, tmp

        if len(list_mem_max) ==0 or len(list_mem_avg) == 0:
                message(u"Rien de trouvé")

        return list_mem_max, list_mem_avg, list_run_time

#-----------------------------------------------------------------------------------------------
# fonction pour récupérer toutes les infos sur les queues d'un cluster donnée
# input: nom du cluster
# output: liste de dictionaire des différentes queues
#-----------------------------------------------------------------------------------------------

def get_queue(cluster):

        list_queue = []
        out = send_command(["bqueues -l -m " + cluster + " 2>/dev/null"])
        stdout = out[0]
        stderr = out[1]

        for queue_raw in stdout.split('-------------------------------------------------------------------------------\n\n'):
                queue = {}
                for line in queue_raw.split('\n'):
                        if re.search('^.*: ', line):
                                queue[re.findall('^.*: ', line)[0][:-2]] = re.findall(': .*$', line)[0][2:]
                list_queue.append(queue)

        return list_queue

#-----------------------------------------------------------------------------------------------
# fonction pour récupérer les queues dont fait partie un noeud d'un cluster
# input: cluster
# output: dictionnaire des noeuds
#-----------------------------------------------------------------------------------------------

def get_bmgroup(cluster):

        list_queue = get_queue(cluster)

        list_node = {}
        list_group = {}

        out = send_command(["bmgroup -w " + cluster + " 2>/dev/null | grep 'hg_'"])
        stdout = out[0]
        stderr = out[1]

        # on crée la liste des groupes
        for line in stdout.split('\n'):
                if line == '':
                        continue
                tmp = re.sub(r"\s+","-_-", line).split("-_-")
                tmp.remove('')
#               print line, tmp
                for item in tmp:
                        if '/' in item:
                                tmp[tmp.index(item)] = tmp[tmp.index(item)].replace('/', '')
                if tmp[0] != '':
                        list_group[tmp[0]] = tmp[1:]

#       print list_group

        # on crée la liste des noeuds (en inversant celle des groupes)
        for queue in list_queue:
                group = queue['HOSTS'].rsplit()
                for item in group:
                        # on enlève les \ des nom des groupes dans les queues
                        if '/' in item:
                                group[group.index(item)] = group[group.index(item)].replace('/', '')
                node = []
#               print group
                for item in group:
                        if item not in list_group:
                                # necessaire pour prendre en compte les cas avec 'hg_dev_hiio+20', 'hg_dev_loio+80'
                                if not re.search('\+\d{2}$', item):
                                        continue
                                else:
                                        item = item[:-3]
                        node = recursiv_group(list_group, item, node)

#               print node
                for item in node:
                        if item not in list_node:
                                list_node[item] = [queue['QUEUE']]
                        else:
                                list_node[item].append(queue['QUEUE'])

#       print list_node

        return list_node

#-----------------------------------------------------------------------------------------------
# fonction recursive pour explorer l'intérieur des groupes
# input: la liste des groupes, le groupe recherché et les résultats en cours
# output: la liste des noeuds correspondant à la liste des groupes d'une queue
#-----------------------------------------------------------------------------------------------

def recursiv_group(list_group, group, node):

        for item in list_group[group]:
                if item in list_group:
                        recursiv_group(list_group, item, node)
                else:
                        if item not in node:
                                node.append(item)

        return node

#---------------------------------------------------------------------------------------
# classe d'affiche d'histogramme
# input: 2 listes
# output: histogrammes
#---------------------------------------------------------------------------------------

class histo(QtGui.QWidget):

        def __init__(self, titre, label, l1, l2, l3, parent=None, conteneur=None):

                self.win = pg.GraphicsWindow()
                self.win.resize(800,350)
                self.win.setWindowTitle(titre[0])

                plt1 = self.win.addPlot(title=titre[1])
                plt2 = self.win.addPlot(title=titre[2])
                plt3 = self.win.addPlot(title=titre[3])

                # calcul des moyenne et mediane
                avg1 =np.mean(l1)
                med1 = np.median(l1)

                avg2 =np.mean(l2)
                med2 = np.median(l2)

                avg3 =np.mean(l3)
                med3 = np.median(l3)

                # on met la legende
                text1 = pg.TextItem(html='<div style="text-align: left"><span style="color: rgb(200, 0, 0);">Moyenne = ' + str(avg1)  + '</span><br><span style="color: rgb(0, 200, 0);">Mediane = ' + str(med1) + '</span></div>', anchor=(1,0), border='w')
                plt1.addItem(text1)

                text2 = pg.TextItem(html='<div style="text-align: left"><span style="color: rgb(200, 0, 0);">Moyenne = ' + str(avg2)  + '</span><br><span style="color: rgb(0, 200, 0);">Mediane = ' + str(med2) + '</span></div>', anchor=(1,0), border='w')
                plt2.addItem(text2)

                text3 = pg.TextItem(html='<div style="text-align: left"><span style="color: rgb(200, 0, 0);">Moyenne = ' + str(avg3)  + '</span><br><span style="color: rgb(0, 200, 0);">Mediane = ' + str(med3) + '</span></div>', anchor=(1,0), border='w')
                plt3.addItem(text3)

                # on dessine les lignes de moyenne et de médiane
                plt1.addLine(x=avg1, pen='r')
                plt1.addLine(x=med1, pen='g')

                plt2.addLine(x=avg2, pen='r')
                plt2.addLine(x=med2, pen='g')

                plt3.addLine(x=avg3, pen='r')
                plt3.addLine(x=med3, pen='g')

                # on écrite les label des axes
                plt1.setLabel('left', text=label[0])
                plt1.setLabel('bottom', text=label[1])

                plt2.setLabel('left', text=label[0])
                plt2.setLabel('bottom', text=label[1])

                plt3.setLabel('left', text=label[0])
                plt3.setLabel('bottom', text=label[2])

                # on crée les histogrammes et les ajoutes aux graph
                y,x = np.histogram(l1, bins=np.linspace(min(l1), max(l1), 50))
                curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 80))
                plt1.addItem(curve)

                y2,x2 = np.histogram(l2, bins=np.linspace(min(l2), max(l2), 50))
                curve = pg.PlotCurveItem(x2, y2, stepMode=True, fillLevel=0, brush=(0, 0, 255, 80))
                plt2.addItem(curve)

                y3,x3 = np.histogram(l3, bins=np.linspace(min(l3), max(l3), 50))
                curve = pg.PlotCurveItem(x3, y3, stepMode=True, fillLevel=0, brush=(0, 0, 255, 80))
                plt3.addItem(curve)

                text1.setPos(x.max(), y.max())
                text2.setPos(x2.max(), y2.max())
                text3.setPos(x3.max(), y3.max())

#---------------------------------------------------------------------------------------
# classe pour afficher une barre de progression
# input: degrée de completion de la tache
# output: barre de progrès
#---------------------------------------------------------------------------------------

class progressbar(QtGui.QWidget):

        def __init__(self, parent=None, conteneur=None):

                super(progressbar, self).__init__( parent )

                self.setWindowTitle(u"Avancement")

                self.pbar = QtGui.QProgressBar()
                self.pbar.setGeometry(30, 40, 200, 25)
                self.pbar.setMinimum(0)
                self.pbar.setMaximum(len(cluster_list))

                self.text = QtGui.QLabel()

                self.pbar.setValue(0)

                self.layout = QtGui.QVBoxLayout(self)

                self.layout.addWidget(self.pbar)
                self.layout.addWidget(self.text)

                self.setLayout(self.layout)

                self.show()

        def update_progressbar(self, cluster, step):

                self.pbar.setValue(step)
                QtGui.qApp.processEvents()
                self.text.setText(cluster + ": " + str(step) + "/" + str(len(cluster_list)))

#---------------------------------------------------------------------------------------
# class to display a warning message
# input: a message to display
# output: message error gui
#---------------------------------------------------------------------------------------

class message(QMainWindow):

        def __init__(self, arg, typ="crit", conteneur=None):

                QMainWindow.__init__(self, conteneur)
                if typ == 'crit':
                        QtGui.QMessageBox.critical(self, "Erreur", arg)
                elif typ == 'info':
                        QtGui.QMessageBox.information(self, "Information", arg)
#-----------------------------------------------------------------------------------------------
# classe affichage de la boite d'entree des donnees
# input: une question
# output: la réponse donnée
#-----------------------------------------------------------------------------------------------

class input(QtGui.QWidget):

        def __init__(self, arg, conteneur=None, parent=None):

                super(input, self).__init__( parent )

                # on crée le widget central
                self.Mainwidget = QtGui.QWidget(self)
                self.setWindowTitle(u"Input")

                # on crée le layout principal
                self.layout = QtGui.QHBoxLayout()

                self.input = QtGui.QLineEdit()

                self.question = QtGui.QLabel(arg)

                self.button_ok = QtGui.QPushButton("&OK")
#               self.button_ok.keyPressEvent(self, eventQKeyEvent)
#               QtGui.QShortcut(QtGui.QKeySequence("Ctrl+A"), self, None, lambda: self.exit(self.input.text()))

                self.button_ok.clicked.connect(lambda: self.exit(self.input.text()))

                self.layout.addWidget(self.question)
                self.layout.addWidget(self.input)
                self.layout.addWidget(self.button_ok)

                self.setLayout(self.layout)

        def createConnexions(self):
                self.pushButton.clicked.connect(self.exit)

        def exit(self, arg):

                if arg == "":
                        message(u'Vous devez donné un UID')
                        return
                # emettra un signal "fermeturequelclient()" avec l'argument cite
                self.emit(SIGNAL("close_input(PyQt_PyObject)"), arg)
                # fermer la fenetre
                self.close()

        # Comment on gère les raccourcis claviers pour un boutton
        def keyPressEvent(self, event):

                if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                        self.exit(self.input.text())

#-----------------------------------------------------------------------------------------------
# classe d'affichage du choix d'un profile applicatif
# input:
# output: le profile
#-----------------------------------------------------------------------------------------------

class profile_input(QtGui.QWidget):

        def __init__(self, conteneur=None, parent=None):

                super(profile_input, self).__init__( parent )

                # on crée le widget central
                self.Mainwidget = QtGui.QWidget(self)
                self.setWindowTitle(u"Profile applicatif ?")

                # on crée le layout principal
                self.layout = QtGui.QHBoxLayout()

                self.profilebox = QtGui.QComboBox()
                out = send_command(["bapp | sed '1d' | awk '{print $1}'"])
                if out[2]:
                        self.close()
                for arg in out[0].split('\n'):
                        if arg != '':
                                self.profilebox.addItem(str(arg))

                self.button_ok = QtGui.QPushButton("&OK")

                self.button_ok.clicked.connect(lambda: self.exit(self.profilebox.currentText()))

                self.layout.addWidget(self.profilebox)
                self.layout.addWidget(self.button_ok)

                self.setLayout(self.layout)

        def createConnexions(self):
                self.pushButton.clicked.connect(self.exit)

        def exit(self, arg):
                # emettra un signal "fermeturequelclient()" avec l'argument cite
                self.emit(SIGNAL("close_profile_input(PyQt_PyObject)"), arg)
                # fermer la fenetre
                self.close()

        # Comment on gère les raccourcis claviers pour un boutton
        def keyPressEvent(self, event):

                if event.key() == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
                        self.emit(SIGNAL("close_profile_input(PyQt_PyObject)"), self.profilebox.currentText())
                        self.close()

#---------------------------------------------------------------------------------------
# classe pour afficher le detail d'un job
# input: jobid et cluster name
# output: detail du job
#---------------------------------------------------------------------------------------

class get_detail_job(QtGui.QWidget):

        def __init__(self, jobid, cluster, stat, node, conteneur=None, parent=None):

                super(get_detail_job, self).__init__( parent )

                # on crée le layout principal
                self.layout = QtGui.QVBoxLayout(self)

                # on crée une zone scrollable
                self.scrollArea = QtGui.QScrollArea(self)
                self.scrollArea.setWidgetResizable(True)
                self.scrollArea.setMinimumWidth(670)
                self.scrollArea.setMinimumHeight(600)

                # on crée le widget central
                self.Mainwidget = QtGui.QWidget()
                self.setWindowTitle(u"JobId: " + jobid)

                # on crée le layout vertical principal
                self.layoutV = QtGui.QVBoxLayout(self.Mainwidget)

                if stat == 'RUN' and node == '':
                        out = send_command(["bjobs -m " + cluster + " -l " + jobid + " 2>/dev/null"])
                        self.text = QtGui.QLabel(out[0])
                        if out[2]:
                                self.close()
                elif node == '':
                        out = send_command(["bjobs -m " + cluster + " -lp " + jobid + " 2>/dev/null"])
                        self.text = QtGui.QLabel(out[0])
                        if out[2]:
                                self.close()
                elif node != '':
                        self.setWindowTitle(u"JobId: " + jobid + " -> bhist + bacct")
                        out = send_command(["ssh " + node + " bhist -n 10  -l " + jobid])
                        out2 = send_command(["ssh " + node + " bacct -l " + jobid])
                        self.text = QtGui.QLabel(out[0] + "\n--------------------------------------------\n" + out2[0])
                        if out[2] and out2[2]:
                                self.close()

                self.button_ok = QtGui.QPushButton("&OK")
                self.button_ok.clicked.connect(self.exit)

                self.layoutV.addWidget(self.text)

                # on place le layout vertical comme le layout principal du widget
                self.Mainwidget.setLayout(self.layoutV)
                # on rajoute le Mainwidget à la zone scrollable
                self.scrollArea.setWidget(self.Mainwidget)

                # on rajoute la zone scrollable au layout principal
                self.layout.addWidget(self.scrollArea)
                self.layout.addWidget(self.button_ok)

                # on ajuste le widget à la taille de la zone scrollable
                self.adjustSize()

                # on fixe la taille du widget
                size = self.size()
                w = size.width()
                h = size.height()
                self.setMinimumWidth(w)
                self.setMinimumHeight(h)


        def exit(self):
                self.close()

#---------------------------------------------------------------------------------------
# classe pour afficher la liste des licences
# input: rien
# output: liste des licences
#---------------------------------------------------------------------------------------

class get_licences(QtGui.QWidget):

        def __init__(self, conteneur=None, parent=None):

                super(get_licences, self).__init__( parent )

                # on crée le layout principal
                self.layout = QtGui.QVBoxLayout(self)

                # on crée une zone scrollable
                self.scrollArea = QtGui.QScrollArea(self)
                self.scrollArea.setWidgetResizable(True)
                self.scrollArea.setMinimumWidth(700)
                self.scrollArea.setMinimumHeight(600)

                # on crée le widget central
                self.Mainwidget = QtGui.QWidget()
                self.setWindowTitle(u"Licences")

                # on crée le layout vertical principal
                self.layoutV = QtGui.QVBoxLayout(self.Mainwidget)

                out1 = send_command(["bhosts -s | egrep -v \"^ \" | egrep  \"lic_\""])
                stdout1 = out1[0]
                stderr1 = out1[1]
                out2 = send_command(["lsload -s | egrep -v \"^ \" | egrep  \"lic_\""])
                stdout2 = out2[0]
                stderr2 = out2[1]
                if out1[2] and out2[2]:
                        self.close()

                text = ""
                list_lic = []
                if stdout1 != "" and stdout2 != "":
                        bhost = stdout1.split("\n")
                        for line in bhost:
                                lic = re.sub(r"\s+","-_-",line).split("-_-")
                                lic.remove('')
                                tmp = {}
                                if len(lic) == 3:
                                        tmp['lic'] = lic[0]
                                        tmp['free'] = lic[1]
                                        tmp['reserved'] = lic[2]
                                        list_lic.append(tmp)
                                elif len(lic) == 2:
                                        lic2 = re.split('(\d+)', line)
                                        tmp['lic'] = lic2[0]
                                        tmp['free'] = lic2[1]
                                        tmp['reserved'] = lic[1]
                                        list_lic.append(tmp)

                        lsload = stdout2.split("\n")
                        for line in lsload:
                                lic = re.sub(r"\s+","-_-",line).split("-_-")
                                lic.remove('')
                                tmp = {}
                                if len(lic) == 2:
                                        tmp = (item for item in list_lic if item["lic"] == lic[0]).next()
                                        ind = list_lic.index(tmp)
                                        list_lic[ind]['total'] = lic[1]

                # On crée la table de résultat
                self.table = QtGui.QTableWidget(self)

                self.table.setSortingEnabled(True)

                list_key = ('Licence', 'Libre', u'Reservé', u'Utilisé', 'Total')

                self.table.setColumnCount(len(list_key))
                self.table.setRowCount(len(list_lic))

                self.table.setHorizontalHeaderLabels(list_key)

                line = 0
                for lic in list_lic:
                        if "total" not in lic:
                                lic['total'] = "0"
                        for item in lic:
                                if lic[item] == "-":
                                        lic[item] = "0"
                        self.table.setItem(line, 0, QtGui.QTableWidgetItem(lic['lic']))
                        self.table.setItem(line, 1, QtGui.QTableWidgetItem(lic['free']))
                        self.table.setItem(line, 2, QtGui.QTableWidgetItem(lic['reserved']))
                        self.table.setItem(line, 3, QtGui.QTableWidgetItem(str(float(lic['total'])-float(lic['free']))))
                        self.table.setItem(line, 4, QtGui.QTableWidgetItem(lic['total']))
                        line = line + 1

                self.table.resizeColumnsToContents()

                self.button_ok = QtGui.QPushButton("&OK")
                self.button_ok.clicked.connect(self.exit)

                self.layoutV.addWidget(self.table)

                # on place le layout vertical comme le layout principal du widget
                self.Mainwidget.setLayout(self.layoutV)

                # on rajoute le Mainwidget à la zone scrollable
                self.scrollArea.setWidget(self.Mainwidget)

                # on rajoute la zone scrollable au layout principal
                self.layout.addWidget(self.scrollArea)
                self.layout.addWidget(self.button_ok)

                # on ajuste le widget à la taille de la zone scrollable
                self.adjustSize()

                # on fixe la taille du widget
                size = self.size()
                w = size.width()
                h = size.height()
                self.setMinimumWidth(w)
                self.setMinimumHeight(h)


        def exit(self):
                self.close()

#---------------------------------------------------------------------------------------
# classe pour afficher le status des clusters
# input: rien
# output: liste des noeuds des clusters
#---------------------------------------------------------------------------------------

class cluster_status(QtGui.QWidget):

        def __init__(self, cluster, conteneur=None, parent=None):
                super(cluster_status, self).__init__( parent )

                # on crée le layout principal
                self.layout = QtGui.QVBoxLayout(self)

                # on crée une zone scrollable
                self.scrollArea = QtGui.QScrollArea(self)
                self.scrollArea.setWidgetResizable(True)
                self.scrollArea.setMinimumWidth(1600)
                self.scrollArea.setMinimumHeight(600)

                # on crée le widget central
                self.Mainwidget = QtGui.QWidget()
                self.setWindowTitle(u"Noeuds du cluster")

                # on crée le layout vertical principal
                self.layoutV = QtGui.QVBoxLayout(self.Mainwidget)

                out1 = send_command(["bhosts -w " + cluster + "| sed '1d'"])
                stdout1 = out1[0]
                stderr1 = out1[1]
                out2 = send_command(["lsload -w " + cluster + "| sed '1d'"])
                stdout2 = out2[0]
                stderr2 = out2[1]
                if out1[2] and out2[2]:
                        self.close()

                text = ""
                list_node = []
                if stdout1 != "" and stdout2 != "":
                        bhost = stdout1.split("\n")
                        for line in bhost:
                                node = re.sub(r"\s+","-_-",line).split("-_-")
                                tmp = {}
                                if len(node) == 9:
                                        tmp['HOST_NAME'] = node[0]
                                        tmp['STATUS'] = node[1]
                                        tmp['JL/U'] = node[2]
                                        tmp['MAX'] = node[3]
                                        tmp['NJOBS'] = node[4]
                                        tmp['RUN'] = node[5]
                                        tmp['SSUSP'] = node[6]
                                        tmp['USUSP'] = node[7]
                                        tmp['RSV'] = node[8]

                                        list_node.append(tmp)


                        lsload = stdout2.split("\n")
                        for line in lsload:
                                if line == "":
                                        continue
                                node = re.sub(r"\s+","-_-",line).split("-_-")
                                tmp = {}
                                tmp = (item for item in list_node if item["HOST_NAME"] == node[0]).next()
                                ind = list_node.index(tmp)
                                list_node[ind]['lsload_status'] = node[1]
                                if node[1] != "unavail":
                                        list_node[ind]['r15s'] = node[2]
                                        list_node[ind]['r1m'] = node[3]
                                        list_node[ind]['r15m'] = node[4]
                                        list_node[ind]['ut'] = node[5]
                                        list_node[ind]['pg'] = node[6]
                                        list_node[ind]['ls'] = node[7]
                                        list_node[ind]['it'] = node[8]
                                        list_node[ind]['tmp'] = node[9]
                                        list_node[ind]['swp'] = node[10]
                                        list_node[ind]['mem'] = node[11]

                # on récupère les queues de chaque noeuds
                list_queue = get_bmgroup(cluster)
                for node in list_node:
                        if node['HOST_NAME'] in list_queue.keys():
                                txt = ''
                                for item in list_queue[node['HOST_NAME']]:
                                        txt = item + ', ' + txt
                                node['QUEUE'] = txt[:-2]
                        elif re.search('.eu.airbus.corp$', node['HOST_NAME']):
                                if node['HOST_NAME'][:-15] in list_queue.keys():
                                        txt = ''
                                        for item in list_queue[node['HOST_NAME'][:-15]]:
                                                txt = item + ', ' + txt
                                        node['QUEUE'] = txt[:-2]
                                else:
                                        node['QUEUE'] = 'NOT AVAILABLE IN QUEUE'
                        else:
                                node['QUEUE'] = 'NOT AVAILABLE IN QUEUE'

                # On créer les stats du cluster

                # états des noeuds
                stat = {}
                stat['STATUS'] = {'ok': 0, 'closed_Full': 0, 'closed_Adm': 0, 'closed_Wind': 0, 'unavail': 0, 'unreach': 0, 'closed_Busy': 0}
                stat['MAX'] = 0
                stat['RUN'] = 0
                for node in list_node:
                        stat['STATUS'][node['STATUS']] = stat['STATUS'][node['STATUS']] + 1
                        stat['MAX'] = stat['MAX'] + int(node['MAX'])
                        stat['RUN'] = stat['RUN'] + int(node['RUN'])

                # message de stat
                stat_message = '''---------- Status du cluster ''' +  cluster + ' ----------\n'
                stat_message = stat_message + "Etat des noeuds : \n"
                for status in stat['STATUS']:
                         stat_message = stat_message + '   -' + status + " : " + str(stat['STATUS'][status]) + "\n"
                stat_message = stat_message + "MAX JOBS : " + str(stat['MAX']) + "\n"
                stat_message = stat_message + "RUN JOBS : " + str(stat['RUN'])

                # On crée le lable pour le stat message
                self.label_stat = QtGui.QLabel(self)

                self.label_stat.setText(stat_message)

                self.label_stat.setAlignment(QtCore.Qt.AlignCenter)

                # On crée la table de résultat
                self.table = QtGui.QTableWidget(self)

                self.table.setSortingEnabled(True)

                self.list_key = ('HOST_NAME', 'STATUS', 'JL/U', 'MAX', 'NJOBS', 'RUN', 'SSUSP', 'USUSP', 'RSV', 'lsload_status', 'r15s', 'r1m', 'r15m', 'ut', 'pg', 'ls', 'it', 'tmp', 'swp', 'mem', 'QUEUE')

                self.table.setColumnCount(len(self.list_key))
                self.table.setRowCount(len(list_node))

                self.table.setHorizontalHeaderLabels(self.list_key)

                self.connect(self.table,SIGNAL('cellClicked(int,int)'), self.detail_node)

                line = 0
                self.list_node = list_node
                self.cluster = cluster

                for node in list_node:
                        self.table.setItem(line, 0, QtGui.QTableWidgetItem(node['HOST_NAME']))
                        self.table.setItem(line, 1, QtGui.QTableWidgetItem(node['STATUS']))
                        self.table.setItem(line, 2, QtGui.QTableWidgetItem(node['JL/U']))
                        self.table.setItem(line, 3, QtGui.QTableWidgetItem(node['MAX']))
                        self.table.setItem(line, 4, QtGui.QTableWidgetItem(node['NJOBS']))
                        self.table.setItem(line, 5, QtGui.QTableWidgetItem(node['RUN']))
                        self.table.setItem(line, 6, QtGui.QTableWidgetItem(node['SSUSP']))
                        self.table.setItem(line, 7, QtGui.QTableWidgetItem(node['USUSP']))
                        self.table.setItem(line, 8, QtGui.QTableWidgetItem(node['RSV']))
                        self.table.setItem(line, 9, QtGui.QTableWidgetItem(node['lsload_status']))
                        if node['lsload_status'] != "unavail":
                                self.table.setItem(line, 10, QtGui.QTableWidgetItem(node['r15s']))
                                self.table.setItem(line, 11, QtGui.QTableWidgetItem(node['r1m']))
                                self.table.setItem(line, 12, QtGui.QTableWidgetItem(node['r15m']))
                                self.table.setItem(line, 13, QtGui.QTableWidgetItem(node['ut']))
                                self.table.setItem(line, 14, QtGui.QTableWidgetItem(node['pg']))
                                self.table.setItem(line, 15, QtGui.QTableWidgetItem(node['ls']))
                                self.table.setItem(line, 16, QtGui.QTableWidgetItem(node['it']))
                                self.table.setItem(line, 17, QtGui.QTableWidgetItem(node['tmp']))
                                self.table.setItem(line, 18, QtGui.QTableWidgetItem(node['swp']))
                                self.table.setItem(line, 19, QtGui.QTableWidgetItem(node['mem']))
                                self.table.setItem(line, 20, QtGui.QTableWidgetItem(node['QUEUE']))
                        if node['STATUS'] == "ok" and "lic" not in node['HOST_NAME'] and "viz" not in node['HOST_NAME'] and "tran" not in node['HOST_NAME']:
                                for col in range(0, len(self.list_key)):
                                        #print line, col, node
                                        self.table.item(line, col).setBackground(QtGui.QColor(QtCore.Qt.green))
                        line = line + 1

                self.table.resizeColumnsToContents()

                self.button_ok = QtGui.QPushButton("&OK")
                self.button_ok.clicked.connect(self.exit)

                # on ajoute les widget au layout
                self.layoutV.addWidget(self.label_stat)
                self.layoutV.addWidget(self.table)

                # on place le layout vertical comme le layout principal du widget
                self.Mainwidget.setLayout(self.layoutV)

                # on rajoute le Mainwidget à la zone scrollable
                self.scrollArea.setWidget(self.Mainwidget)

                # on rajoute la zone scrollable au layout principal
                self.layout.addWidget(self.scrollArea)
                self.layout.addWidget(self.button_ok)

                # on ajuste le widget à la taille de la zone scrollable
                self.adjustSize()

                # on fixe la taille du widget
                size = self.size()
                w = size.width()
                h = size.height()
                self.setMinimumWidth(w)
                self.setMinimumHeight(h)

        def detail_node(self, row, col):

                col_hostname = self.list_key.index("HOST_NAME")

                tmp = (item for item in self.list_node if item["HOST_NAME"] == self.table.item(row,col_hostname).text()).next()

                node = tmp['HOST_NAME']

                self.detail = get_detail_node(self.cluster, node)
                self.detail.show()

        def exit(self):
                self.close()

#---------------------------------------------------------------------------------------
# classe pour afficher le detail d'un noeud
# input: nom du noeud
# output: detail du noeud
#---------------------------------------------------------------------------------------

class get_detail_node(QtGui.QWidget):

        def __init__(self, cluster, node, conteneur=None, parent=None):

                super(get_detail_node, self).__init__( parent )

                # on crée le layout principal
                self.layout = QtGui.QVBoxLayout(self)

                # on crée une zone scrollable
                self.scrollArea = QtGui.QScrollArea(self)
                self.scrollArea.setWidgetResizable(True)
                self.scrollArea.setMinimumWidth(670)
                self.scrollArea.setMinimumHeight(600)

                # on crée le widget central
                self.Mainwidget = QtGui.QWidget()
                self.setWindowTitle(u"Node: " + node)

                # on crée le layout vertical principal
                self.layoutV = QtGui.QVBoxLayout(self.Mainwidget)

                out = send_command(["bhosts -l " + cluster + "| sed -n '/" + node + "/,/HOST/p' | head -n -1"])
                if out[2]:
                        self.close()
                self.text = QtGui.QLabel(out[0])

                self.button_ok = QtGui.QPushButton("&OK")
                self.button_ok.clicked.connect(self.exit)

                self.layoutV.addWidget(self.text)

                # on place le layout vertical comme le layout principal du widget
                self.Mainwidget.setLayout(self.layoutV)

                # on rajoute le Mainwidget à la zone scrollable
                self.scrollArea.setWidget(self.Mainwidget)

                # on rajoute la zone scrollable au layout principal
                self.layout.addWidget(self.scrollArea)
                self.layout.addWidget(self.button_ok)

                # on ajuste le widget à la taille de la zone scrollable
                self.adjustSize()
               # on fixe la taille du widget
                size = self.size()
                w = size.width()
                h = size.height()
                self.setMinimumWidth(w)
                self.setMinimumHeight(h)


        def exit(self):
                self.close()

#-----------------------------------------------------------------------------------------------
# classe affichage de la boite d'entree des donnees
# input: une question
# output: la réponse donnée
#-----------------------------------------------------------------------------------------------

class old_job_input(QtGui.QWidget):

        def __init__(self, conteneur=None, parent=None):

                super(old_job_input, self).__init__( parent )

                # on crée le widget central
                self.Mainwidget = QtGui.QWidget(self)
                self.setWindowTitle(u"Input")

                self.layout = QtGui.QVBoxLayout()

                # on crée le layout 1
                self.layoutH1 = QtGui.QHBoxLayout()

                self.input1 = QtGui.QLineEdit()

                self.question1 = QtGui.QLabel("Id du job ?")

                self.layoutH1.addWidget(self.question1)
                self.layoutH1.addWidget(self.input1)

                # on crée le layout 2
                self.layoutH2 = QtGui.QHBoxLayout()

                self.input2 = QtGui.QLineEdit()

                self.question2 = QtGui.QLabel("UID de l'utilisateur ?")

                self.layoutH2.addWidget(self.question2)
                self.layoutH2.addWidget(self.input2)

                # on crée le layout 3

                self.layoutH3 = QtGui.QHBoxLayout()
                self.question3 = QtGui.QLabel("Profondeur de la recherche ?")

                self.input3 = QtGui.QComboBox()
                for arg in range(1,1000):
                        self.input3.addItem(str(arg))

                self.layoutH3.addWidget(self.question3)
                self.layoutH3.addWidget(self.input3)

                self.button_ok = QtGui.QPushButton("&OK")
                self.button_ok.clicked.connect(lambda: self.exit(self.input1.text(), self.input2.text(), self.input3.currentText()))

                self.layout.addLayout(self.layoutH1)
                self.layout.addLayout(self.layoutH2)
                self.layout.addLayout(self.layoutH3)
                self.layout.addWidget(self.button_ok)

                self.setLayout(self.layout)

        def createConnexions(self):
                self.pushButton.clicked.connect(self.exit)

        def exit(self, arg1, arg2, arg3):
                # emettra un signal "fermeturequelclient()" avec l'argument cite
                self.emit(SIGNAL("close_old_job_input(PyQt_PyObject)"), [arg1, arg2, arg3])
                # fermer la fenetre
                self.close()

#---------------------------------------------------------------------------------------
# class to display the main gui
# input: nothing
# output: the main gui
#---------------------------------------------------------------------------------------

class main_gui(QMainWindow):

        def __init__(self,  conteneur=None):

                if conteneur is None : conteneur = self
                QMainWindow.__init__(conteneur)

                # on crée la barre de menu
                self.create_action()
                self.create_menu()

                # on crée le widget central
                self.Mainwidget = QtGui.QWidget(self)
                self.setCentralWidget(self.Mainwidget)
                self.setWindowTitle("LSF")
                self.resize(1000,300)

                # on crée le layout vertical principal
                self.layout = QtGui.QVBoxLayout()
                # on ajoute la layout vertical au widget
                self.Mainwidget.setLayout(self.layout)

                # On crée la table de résultat
                self.table = QtGui.QTableWidget(self)

                self.layout.addWidget(self.table)

                if len(cluster_list) == 0:
                        message(u'Pas de cluster trouvé...')

        def create_action(self):

                self.action_mes_jobs = QtGui.QAction(self.tr("Mes jobs"), self)
                self.connect(self.action_mes_jobs, SIGNAL("triggered()"), self.mes_jobs)

                self.action_user_jobs = QtGui.QAction(self.tr("Jobs d'un utilisateurs"), self)
                self.connect(self.action_user_jobs, SIGNAL("triggered()"), self.user_jobs_input)

                self.action_all_jobs = QtGui.QAction(self.tr("Tous les jobs"), self)
                self.connect(self.action_all_jobs, SIGNAL("triggered()"), self.all_jobs)

                self.action_rechercher_job = QtGui.QAction(self.tr("Rechercher un job"), self)
                self.connect(self.action_rechercher_job, SIGNAL("triggered()"), self.recherche_job_input)

                self.action_rechercher_ancien_job = QtGui.QAction(self.tr("Rechercher un ancien job"), self)
                self.connect(self.action_rechercher_ancien_job, SIGNAL("triggered()"), self.recherche_ancien_job_input)

                self.action_stat_profile = QtGui.QAction(self.tr("Statistique d'un profile"), self)
                self.connect(self.action_stat_profile, SIGNAL("triggered()"), self.recherche_profile_input)

                self.action_quitter = QtGui.QAction(self.tr("Quitter"), self)
                self.action_quitter.setShortcut(self.tr("Ctrl+Q"))
                self.connect(self.action_quitter, SIGNAL("triggered()"), self.exit)

                self.action_list_licence = QtGui.QAction(self.tr("Liste des licences vue par LSF"), self)
                self.connect(self.action_list_licence, SIGNAL("triggered()"), self.list_licences)

        def create_menu(self):

                self.statusBar()
                menubar = self.menuBar()

                menu_job = menubar.addMenu('&Job')
                menu_job.addAction(self.action_mes_jobs)
                menu_job.addAction(self.action_user_jobs)
                menu_job_all_jobs = menu_job.addMenu('&Tous les jobs')
                menu_job_all_jobs.addAction(self.action_all_jobs)
                for cluster in cluster_list:
                        ind = cluster_list.index(cluster)
                        clus = QtGui.QAction(self.tr(cluster), self)
                        self.connect(clus, SIGNAL("triggered()"), lambda nom=cluster : self.lien_cluster(nom))
                        menu_job_all_jobs.addAction(clus)
                menu_job.addAction(self.action_rechercher_job)
                menu_job.addAction(self.action_rechercher_ancien_job)
                menu_job.addAction(self.action_stat_profile)
                menu_job.addAction(self.action_quitter)

                menu_licence = menubar.addMenu('&Licence')
                menu_licence.addAction(self.action_list_licence)

                menu_cluster = menubar.addMenu("&Cluster")
                for cluster in cluster_list:
                        ind = cluster_list.index(cluster)
                        clus = QtGui.QAction(self.tr(cluster), self)
                        self.connect(clus, SIGNAL("triggered()"), lambda nom=cluster : self.lien_cluster_status(nom))
                        menu_cluster.addAction(clus)

        def lien_cluster(self, cluster):
                list_jobs = get_jobs("all", [cluster])
                list_key = ('CLUSTER', 'JOBID', 'USER', 'STAT', 'QUEUE', 'FROM_HOST', 'EXEC_HOST', 'JOB_NAME', 'SUBMIT_TIME')
                self.affiche_list(list_jobs, list_key, (0, 1, 2, 3, 4, 8))

        def lien_cluster_status(self, cluster):
                self.state = cluster_status(cluster)
                self.state.show()

        def exit(self):
                self.close()

        def mes_jobs(self):
                moi = os.environ['USER']
                list_jobs = get_jobs(moi, cluster_list)
                list_key = ('CLUSTER', 'JOBID', 'USER', 'STAT', 'QUEUE', 'FROM_HOST', 'EXEC_HOST', 'JOB_NAME', 'SUBMIT_TIME')
                self.affiche_list(list_jobs, list_key, (0, 1, 2, 3, 4, 8))

        def user_jobs_input(self):
                self.user = input(u'UID de l\'utilisateur ?')
                self.connect(self.user, SIGNAL("close_input(PyQt_PyObject)"), self.user_jobs)
                self.user.setWindowModality(QtCore.Qt.ApplicationModal)
                self.user.show()

        def user_jobs(self, user):
                list_jobs = get_jobs(user, cluster_list)
                list_key = ('CLUSTER', 'JOBID', 'USER', 'STAT', 'QUEUE', 'FROM_HOST', 'EXEC_HOST', 'JOB_NAME', 'SUBMIT_TIME')
                self.affiche_list(list_jobs, list_key, (0, 1, 2, 3, 4, 8))

        def all_jobs(self):
                list_jobs = get_jobs("all", cluster_list)
                list_key = ('CLUSTER', 'JOBID', 'USER', 'STAT', 'QUEUE', 'FROM_HOST', 'EXEC_HOST', 'JOB_NAME', 'SUBMIT_TIME')
                self.affiche_list(list_jobs, list_key, (0, 1, 2, 3, 4, 8))

        def affiche_list(self, list_jobs, list_key, col_resize = ()):
                if len(list_jobs) == 0:
                        message(u"Aucun job trouvé", "info")
                        return
                self.table.setSortingEnabled(True)

                self.table.setColumnCount(len(list_key))
                self.table.setRowCount(len(list_jobs))

                self.table.setHorizontalHeaderLabels(list_key)
                self.connect(self.table,SIGNAL('cellClicked(int,int)'), self.detail_job)

                self.list_jobs = list_jobs
                self.list_key = list_key

                line = 0
                for job in list_jobs:
                        for key in list_key:
                                col = list_key.index(key)
                                self.table.setItem(line, col, QtGui.QTableWidgetItem(job[key]))

                        line = line + 1

                for row in col_resize:
                        self.table.resizeColumnToContents(row)

                return

        def detail_job(self, row, col):

                col_jobid = self.list_key.index("JOBID")

                tmp = (item for item in self.list_jobs if item["JOBID"] == self.table.item(row,col_jobid).text()).next()

                jobid = tmp['JOBID']
                cluster = tmp['CLUSTER']
                node = ''
                if 'STAT' in self.list_key:
                        stat = tmp['STAT']
                else:
                        stat = ''
                        node = tmp['node']

                self.get_detail_job = get_detail_job(jobid, cluster, stat, node)
                self.get_detail_job.show()


        def recherche_job_input(self):
                self.jobid = input(u'ID du job ?')
                self.connect(self.jobid, SIGNAL("close_input(PyQt_PyObject)"), self.recherche_job)
                self.jobid.setWindowModality(QtCore.Qt.ApplicationModal)
                self.jobid.show()

        def recherche_job(self, jobid):
                list_jobs = recherche_job(jobid)
                list_key = ('CLUSTER', 'JOBID', 'USER', 'STAT', 'QUEUE', 'FROM_HOST', 'EXEC_HOST', 'JOB_NAME', 'SUBMIT_TIME')
                self.affiche_list(list_jobs, list_key, (0, 1, 2, 3, 4, 8))
        def recherche_ancien_job_input(self):
                self.job_data = old_job_input()
                self.connect(self.job_data, SIGNAL("close_old_job_input(PyQt_PyObject)"), self.recherche_ancien_job_ssh)
                self.job_data.setWindowModality(QtCore.Qt.ApplicationModal)
                self.job_data.show()

        def recherche_ancien_job_ssh(self, job_data):
                list_jobs = recherche_ancien_job(job_data)
                list_key = ('CLUSTER', 'JOBID', 'USER', 'JOB_NAME', 'PEND', 'PSUSP', 'RUN', 'USUSP', 'SSUSP', 'UNKWN', 'TOTAL')
                self.affiche_list(list_jobs, list_key)

        def recherche_profile_input(self):
                self.profile = profile_input()
                self.connect(self.profile, SIGNAL("close_profile_input(PyQt_PyObject)"), self.recherche_profile)
                self.profile.setWindowModality(QtCore.Qt.ApplicationModal)
                self.profile.show()

        def recherche_profile(self, profile):
                list_mem_max, list_mem_avg, list_run_time = stat_profile(profile)
                if len(list_mem_max) !=0 and len(list_mem_avg) != 0 and len(list_run_time) != 0:
                        titre = [u'Histogramme de mémoire pour ' + profile, u'Mémoire MAX utilisé', u'Mémoire moyenne utilisé', u"Temps d'exécution du job"]
                        label = [u'Nombre de jobs', u'Mémoire (Mo)', u"Temps d'exécution (s)"]
                        self.h = histo(titre, label, list_mem_max, list_mem_avg, list_run_time)

        def list_licences(self):
                self.get_lic = get_licences()
                self.get_lic.show()


#-----------------------------------------------------------------------------------------------
# fonction principale
#-----------------------------------------------------------------------------------------------

global clusters_list
global timeout
global res_command
global command_failed
global semaphore

timeout = 30 #timeout in second for kill a command
res_command = ["", "", "", ""] #array to get back the result from the thread
command_failed = [False, ""]
semaphore = threading.BoundedSemaphore(8)

cluster_list = get_clusters()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    f = main_gui()
    f.show()
    r = a.exec_()
