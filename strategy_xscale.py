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
    """ Function open the initial XSCALE.INP file,
        The easyest way to work is to use standard XSACLE.INP correctly setup 
        with the default parameters you want (output, input). On way is to use
        xscale2.py from Pierre Legrand
        This function return xdsinp which is list containing all the XSCALE.INP 
        lines.     
    """
# arg is global, because it's re-used during code execution as parameters to
# find the relativ-path.           
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
    """ Function create folder to write the file generate by other function
        Default name is given to avoid conflict or error.    
    """    
    if create :        
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
    """ Function to write string contain in a list 
    """    
    outputfile = open(os.path.join(path, "XSCALE.INP"), 'a')
    for line in file2write:    
        outputfile.write(line)
        
#function to edit the file path    
def editFilePath(xdsinp):
    """ Function to modify the path write in original XSCALE.INP, 
        the new path write in the new XSCALE.INP create, will be set according 
        the right path to read the symlink create by the symlink creation 
        function. The old path is change in 0,1,2... .HKL corrsponding to 
        the symlink 
    """
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
        #except is using to take in count the case where the user doesn't 
        # want to modify the resolutuion parameter
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

            
    

# this defined 5 schemes for automatic usage of this script in order to 
# test different strategy of scaling with XSCALE
scheme0 = ["-corr","-ano"]
scheme1 = ["-sa", "-corr", "-ano"] 
scheme2 = ["-sa","-corr", "-noAno"]
scheme3 = ["-zd", "-corr", "-ano"]
scheme4 = ["-zd", "-sa", "-corr", "-ano"]
scheme5 = ["-zd", "-sa", "-corr", "-noAno"]

 
listOfexperiment = [scheme0, scheme1, scheme2, scheme3, scheme4, scheme5]
listOfFile = []             
#open file and create output directory
create = StartingOpen()
resultFile = makeResultFile(create)
resolutionMax(xdsinp)
# create link which point to the original XDS_ASCII.HKL files
for lines in xdsinp:
    if re.findall(r"INPUT_FILE=", lines):
        listOfFile.append(lines)
for i in listOfFile:
    #this line correspond to the need of only one parts of the original path
    # initially typed by the user. It's concatenation of the strating parts of
    # the original path typed and the current path to the symlink newly created
    # just before.
    link = symlink_creation(arg[:-10]+i[15:-1], "./"+str(resultFile)+"/"+str(listOfFile.index(i))+".HKL")
listofFolder = []
for scheme in listOfexperiment:
    # create differents folders for each scheme used
    listofFolder.append(resultFile+"/"+"scheme"+ str(listOfexperiment.index(scheme)))
for path in listofFolder:
    os.mkdir(path)   

file2write = []
for scheme in listOfexperiment:
    settings = scheme
    editFilePath(xdsinp)    
    resolutionShells(xdsinp)
    changeFriedelsettings(xdsinp, settings)
    merge(xdsinp, settings)
# the line just after remove the CORRECTION, CRYSTAL_NAME, STRICT_ABSORBTION
# already write by the precedent round of the loop    
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
# writing XSCALE.INP at each round of the loop, because xdsinp is modify 
# iterativelly and that caused the loose of your parameters
    pathXscaleInp = str(listofFolder[i])+"/"
    writing_list_in_file(pathXscaleInp, xdsinp)



