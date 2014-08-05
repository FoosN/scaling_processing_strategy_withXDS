# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 17:17:39 2014

@author: proxima1
"""

import os
import sys
import re
import time
import copy
import glob

def StartingOpen():              
    global arg
    for arg in sys.argv[1:]:
        try:
            if os.path.isfile(arg):
                with open(arg) as input_file :
                    global xdsinp                    
                    xdsinp = input_file.readlines()
                    for lines in xdsinp :
                        #print xdsinp #debug
                        if re.findall(r"XSCALE", lines):
                            print "XSCALE.INP is take in count"
                            create = True
                    return create
                    return xdsinp
                    
        except:
            print ("it's not XSCALE.INP or it's corrupted")
            exit(0)       

def makeResultFile(create):
    if create :
        #global resultFile        
        resultFile = raw_input ('give name for result file, default is : result.' \
+str(time.time())+ ' :')
        if resultFile == '' :
             resultFile = "result."+ str(time.time())
        else :
            resultFile = resultFile
        try:
            os.makedirs(resultFile, 0777)
            return resultFile
        except OSError:
            print 'WARNING : Problem to create Directory for results'
            
def symlink_creation(srcFile, dest):
    os.symlink(srcFile, dest)   


#function to edit the file path    
def editFilePath(xdsinp):
    numberOfFile = []
    for lines in xdsinp:
        if re.findall(r"INPUT_FILE=", lines):
            numberOfFile.append(lines)
            xdsinp.__setitem__(xdsinp.index(lines), "   INPUT_FILE= ../"+str(numberOfFile.index(lines))+".HKL\n")

def changeFriedelsettings(xdsinp, settings):
    if "-ano" in settings:
        for lines in xdsinp:
            if re.findall(r"FRIEDEL'S_LAW=", lines):
                xdsinp.__setitem__(xdsinp.index(lines), "      FRIEDEL'S_LAW= FALSE\n")
    else :
        pass

def settings_XDS_strictAbsCorr(xdsinp, settings):
  ### strict abs correction : 
    if "-sa" in settings:
        for lines in xdsinp:
            if re.findall(r"STRICT_ABSORPTION_CORRECTION=", lines):
                xdsinp.__setitem__(xdsinp.index(lines), "STRICT_ABSORPTION= TRUE \n" )
    else :
        xdsinp.__setitem__(xdsinp.index(lines), "STRICT_ABSORPTION= FALSE \n" )
        pass

def zerodDose(xdsinp, settings):
    if "-zd" in settings:
        if re.findall(r"INPUT_FILE=", lines):        
            xdsinp.insert(xdsinp.index(lines)+1, "      CRYSTAL_NAME=something")
    else :
        pass

def merge(xdsinp, settings):
    if "-merge" in settings:
        for lines in xdsinp:
            if re.findall(r"OUTPUT_FILE=", lines):
                xdsinp.insert(xdsinp.index(lines)+1, "    MERGE=TRUE\n")
    else :
        pass

def correction(xdsinp, settings):
    if "-corr" in settings:
        if re.findall(r"INPUT_FILE=", lines):        
            xdsinp.insert(xdsinp.index(lines)+1, "      CORRECTIONS= DECAY MODULATION ABSORBTION\n")
    if "-corr-none" in settings:
        if re.findall(r"INPUT_FILE=", lines):        
            xdsinp.insert(xdsinp.index(lines)+1, "      !CORRECTIONS= ignored\n")      
    if "-decay" in settings : 
        if re.findall(r"INPUT_FILE=", lines):        
            xdsinp.insert(xdsinp.index(lines)+1, "      CORRECTIONS= DECAY\n")
    if "-mod" in settings :
         if re.findall(r"INPUT_FILE=", lines):        
            xdsinp.insert(xdsinp.index(lines)+1, "      CORRECTIONS= MODULATION\n")       
    if "-abs" in settings :
         if re.findall(r"INPUT_FILE=", lines):        
            xdsinp.insert(xdsinp.index(lines)+1, "      CORRECTIONS= ABSORBTION\n")         







scheme0 = ["all", "-Prs0","-corr","-ano"]
scheme1 = ["all", "-Prs1", "-corr", "-noAno"] 
scheme2 = ["-r", "-Prs0", "-corr-none", "-ano"]
scheme3 = ["-r", "-Prs0", "-corr", "-ano"]
scheme4 = ["-r", "Prs1", "-corr", "-ano"]
 
listOfexperiment = [scheme0, scheme1]
listOfFile = []             

#open file and create output directory
create = StartingOpen()
resultFile = makeResultFile(create)

# create link which point to the original XDS_ASCII.HKL files
for lines in xdsinp:
    if re.findall(r"INPUT_FILE=", lines):
        listOfFile.append(lines)
# create link which point to the original XDS_ASCII.HKL files
for i in listOfFile:        
    symlink_creation(i[15:], "./file"+str(i)+".HKL")

    


base2editeJob = FillinFolder(create, resultFile, listOfexperiment, listOfFile, xdsinp)
newDictsXds = prepare4writing_xdsINP(xdsinp, base2editeJob, listOfexperiment)
listofKey = sorted(newDictsXds)
listofFolder = sorted(glob.glob(resultFile+"/"+"scheme*"))

for key in listofKey:
    key = listofKey.index(key)
    file2write = newDictsXds[listofKey[key]]
    pathXds = str(listofFolder[key])+"/"
    writing_list_in_file(pathXds, file2write)