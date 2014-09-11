# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 17:17:39 2014

@author: proxima1
"""

import os
import sys
import re
import time

def StartingOpen():              
    global arg
    for arg in sys.argv[1:]:
        try:
            if os.path.isfile(arg):
                with open(arg) as input_file :
                    global xdsinp                    
                    xdsinp = input_file.readlines()
                    for lines in xdsinp :
                        if re.search(r"XSCALE", lines):
                            create = True
                    if create == True:
                        print "XSCALE.INP is take in count"
                        return create
                        return xdsinp
                        return arg
                    
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

def writing_list_in_file(path, file2write):
    outputfile = open(os.path.join(path, "XSCALE.INP"), 'a')
    for line in file2write:    
        outputfile.write(line)
        
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
        for lines in xdsinp:
            if re.findall(r"FRIEDEL'S_LAW=", lines):
                xdsinp.__setitem__(xdsinp.index(lines), "      FRIEDEL'S_LAW= TRUE\n")

def settings_XDS_strictAbsCorr(xdsinp, settings):
  ### strict abs correction : 
    if "-sa" in settings:
        for lines in xdsinp:
            if re.findall(r"STRICT_ABSORPTION_CORRECTION=", lines):
                xdsinp.__setitem__(xdsinp.index(lines), "STRICT_ABSORPTION= TRUE \n" )
    else :
        for lines in xdsinp:
            if re.findall(r"STRICT_ABSORPTION_CORRECTION=", lines):
                xdsinp.__setitem__(xdsinp.index(lines), "STRICT_ABSORPTION= FALSE \n" )
        pass

def zerodDose(xdsinp, settings):
    if "-zd" in settings:
        for lines in xdsinp:
            if re.findall(r"INPUT_FILE=", lines):        
                 xdsinp.insert(xdsinp.index(lines)+1, "      CRYSTAL_NAME=something\n")
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
        for lines in xdsinp:
            if re.findall(r"INPUT_FILE=", lines):        
                xdsinp.insert(xdsinp.index(lines)+1, "      CORRECTIONS= DECAY MODULATION ABSORBTION\n")
    elif "-corr-none" in settings:
        for lines in xdsinp:
            if re.findall(r"INPUT_FILE=", lines):        
                xdsinp.insert(xdsinp.index(lines)+1, "      CORRECTIONS=!\n")      
    elif "-decay" in settings : 
         for lines in xdsinp:           
            if re.findall(r"INPUT_FILE=", lines):        
                xdsinp.insert(xdsinp.index(lines)+1, "      CORRECTIONS= DECAY\n")
    elif "-mod" in settings :
         for lines in xdsinp:
            if re.findall(r"INPUT_FILE=", lines):        
                xdsinp.insert(xdsinp.index(lines)+1, "      CORRECTIONS= MODULATION\n")       
    elif  "-abs" in settings :
         for lines in xdsinp:
            if re.findall(r"INPUT_FILE=", lines):        
                 xdsinp.insert(xdsinp.index(lines)+1, "      CORRECTIONS= ABSORBTION\n")         

def resolutionMax(xdsinp):
    global resMax   
    try :
        resMax = float(raw_input('set the resolution maxi, default is : the one used originaly in your input files'))
        for lines in xdsinp:
            if re.findall(r"INCLUDE_RESOLUTION_RANGE=", lines):               
                xdsinp.__setitem__(xdsinp.index(lines), "INCLUDE_RESOLUTION_RANGE= 50.000    "+str(resMax)+"\n")    
    except : 
        
        for lines in xdsinp:
            if re.findall(r"INCLUDE_RESOLUTION_RANGE=", lines):
                resMax = float(lines[-10:])  


def resolutionShells(xdsinp):
    shellsToUse = []
    listOFres = [20, 15, 10, 6, 4, 3, 2.5, 2.2, 2, 1.8, 1.7, 1.6]
    for nb in listOFres:
        if nb >= resMax:
            shellsToUse.append(nb)
            for lines in xdsinp:
                if re.findall(r"RESOLUTION_SHELLS=", lines):
                    xdsinp.__setitem__(xdsinp.index(lines), "RESOLUTION_SHELLS="+str(shellsToUse))
            for lines in xdsinp:
                if re.findall(r"RESOLUTION_SHELLS=", lines):            
                    newline = lines            
                    newline = newline.replace("[", " ")
                    newline = newline.replace("]", "\n")
                    newline = newline.replace(",", "")
                    xdsinp.__setitem__(xdsinp.index(lines), newline)

            
    



scheme0 = ["-corr","-ano"]
scheme1 = ["-sa", "-corr", "-ano"] 
scheme2 = ["-sa","-corr", "-noAno"]
scheme3 = ["-zd", "-corr", "-ano"]
scheme4 = ["-zd", "-sa", "-corr", "-ano"]
scheme5 = ["-zd", "-sa", "-corr", "-noAno"]

 
listOfexperiment = [scheme0, scheme1, scheme2, scheme3, scheme4, scheme5]
listOfFile = []             
print listOfexperiment  #debug
#open file and create output directory
create = StartingOpen()
resultFile = makeResultFile(create)
resolutionMax(xdsinp)
# create link which point to the original XDS_ASCII.HKL files
for lines in xdsinp:
    if re.findall(r"INPUT_FILE=", lines):
        listOfFile.append(lines)
# create link which point to the original XDS_ASCII.HKL files
for i in listOfFile:
    link = symlink_creation(arg[:-10]+i[15:-1], "./"+str(resultFile)+"/"+str(listOfFile.index(i))+".HKL")
listofFolder = []
for scheme in listOfexperiment:
    print scheme
    listofFolder.append(resultFile+"/"+"scheme"+ str(listOfexperiment.index(scheme)))
print str(listofFolder)+"list of folder"   #debug

for path in listofFolder:
    os.mkdir(path)   
file2write = []
for scheme in listOfexperiment:
    settings = scheme
    editFilePath(xdsinp)    
    resolutionShells(xdsinp)
    changeFriedelsettings(xdsinp, settings)
    merge(xdsinp, settings)
    for line in xdsinp:    
        if re.findall(r"CORRECTIONS=", line):        
            xdsinp.pop(xdsinp.index(line))
    correction(xdsinp, settings)
    for line in xdsinp:    
        if re.findall(r"CRYSTAL_NAME=", line):        
            xdsinp.pop(xdsinp.index(line))   
    zerodDose(xdsinp, settings)
    for line in xdsinp:    
        if re.findall(r"STRICT_ABSORPTION=", line):        
            xdsinp.pop(xdsinp.index(line))     
    settings_XDS_strictAbsCorr(xdsinp, settings)
    i = listOfexperiment.index(scheme)
    pathXscaleInp = str(listofFolder[i])+"/"
    writing_list_in_file(pathXscaleInp, xdsinp)



