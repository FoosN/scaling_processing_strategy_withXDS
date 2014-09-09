#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 11:59:14 2014

@author: Nicolas Foos
"""

"""Progs to automaticaly try different scheme for Data processing"""

import os
import sys
import re
import time
import copy
import glob
#from xupy import runxds

USAGE = """ USAGE: %s [OPTION]... FILE1 FILE2
 
FILE1 is one XDS.INP file anf FILE2 is input file wich contain pre-scalling 
parameters by images's batch """

"""function to create symlink according the original repository"""
def symlink_creation(srcFile, dest):
    os.symlink(srcFile, dest)

####################################

"""Reading-informations from XDS.INP"""
# it's necessary to obtain information such as : resolution, image number,
# batch number.
""" make log file with original parameters of XDS.INP and made dictionnary
wich contains all the parameters used and modified in the differents processing
schems""" 

def writing_list_in_file(path, file2write):
    outputfile = open(os.path.join(path, "XDS.INP"), 'a')
    for line in file2write:    
        outputfile.write(line)
    
def information_summary(xdsinp, resultFile):
    """function to collect information from XDS.INP"""
    global informations    
    informations = {}    
    listOfinf = ["JOB=","STRICT_ABSORPTION","DATA_RANGE=",
          "FRIEDEL'S_LAW=", "INCLUDE_RESOLUTION", "BACKGROUND_RANGE", "TEST_RESOLUTION_RANGE",
          "RESOLUTION_SHELLS", ]    
    for lines in xdsinp :
        i = 0        
        while i < len(listOfinf):
            if re.findall((listOfinf[i]), lines):
               informations[listOfinf[i]] = lines
            i +=1
   
#    print informations   #debug
    outputfile = open(os.path.join(resultFile, "XDS.INP.original.log"), 'a')
    outputfile.write(20*"*"+" XDS.INP_SUMMARRY " + 20*"*"+ "\n" + "Input Arg in XDS.INP are : \n")
    for (info, value) in informations.items():
        print  value
        info = ("{}".format(value))
        outputlog = (info)
        outputfile.write(outputlog)
    outputfile.close()
    return informations    

###################################

def dictio_value_edition(dictio, key_entry, newvalue):
    # function to edit key entry from the existing dictio
    for key in dictio.keys():
        if key == key_entry:
            dictio[key] = newvalue

##################################

""" definition of mains processing schems"""
# Control of input file and making folder for each strategy of processing
# with the required file for xds.
def settings_XDS_resolution(original_dict_params, settings):  # settings must be a list of stuff that we want explore
    #original_file is the XDS.INP wich has to be modified, 
# setting is a list. This list contains different parameters for xds executions.
# generic setting for all schems
  ### JOB setting
    original_dict_params["job"] = " JOB= DEFPIX INTEGRATE CORRECT \n"
  ### resolution max setting
    if "-r" or "all" in settings:   
        resolution = str(original_dict_params["INCLUDE_RESOLUTION"])
        resolution_M = resolution.split()[-2]
        resolution_m = float(resolution.split()[-1])
        resolution2test = []
        resolution2test.append(round(resolution_m - 0.35))        
        t = 1
        while t < 4 :
            resolution2test.append(round(resolution_m + t*0.35, 2))
            original_dict_params["res"+str(t)] = " INCLUDE_RESOLUTION_RANGE= "+ resolution_M +" "+ str(resolution2test[t-1]) + "\n"
            folderNameExtension = resolution2test
            t += 1
        original_dict_params["res"+str(t)] = " INCLUDE_RESOLUTION_RANGE= "+ resolution_M +" "+ str(resolution2test[t-1]) + "\n"
        
# ici ce bloc n'est pas teste, ce qui est au dessus est OK
    elif "-r" or "all" in settings:
        #define the test resolution range pour test :  
        reso_cut = resolution2test[-1]
        original_dict_params["TEST_RESOLUTION_RANGE"] = "TEST_RESOLUTION_RANGE= 50 "+ str(reso_cut) +"\n"
        folderNameExtension = [reso_cut]
    else :
        print "Problem in resolution settings"
    return  folderNameExtension
  
def catch_XDS_resolution(original_dict_params, settings):  # settings must be a list of stuff that we want explore
  ### resolution max setting
    if "-r" or "all" in settings:   
        resolution = str(original_dict_params["INCLUDE_RESOLUTION"])
        resolution_m = float(resolution.split()[-1])
        resolution2test = []
        resolution2test.append(round(resolution_m - 0.35))        
        t = 1
        while t < 4 :
            resolution2test.append(round(resolution_m + t*0.35, 2))
            folderNameExtension = resolution2test
            t += 1
        
# ici ce bloc n'est pas teste, ce qui est au dessus est OK
    elif "-r" or "all" in settings:
        #define the test resolution range pour test :  
        reso_cut = resolution2test[-1]
        folderNameExtension = [reso_cut]
    else :
        print "Problem in resolution settings"
    return  folderNameExtension
    
    
def settings_XDS_strictAbsCorr(original_dict_params, settings):
  ### strict abs correction : 
    if "-sa" or "all" in settings:
        dictio_value_edition(original_dict_params, " STRICT_ABSORPTION","STRICT_ABSORPTION= True \n" )
    else :
        dictio_value_edition(original_dict_params, " STRICT_ABSORPTION","STRICT_ABSORPTION= False \n")
        pass

   ### pre-scaling management :
def settings_XDS_prescal_factor(original_dict, settings):
    if "-Prs1" in settings: #all factor for all images set to 1
        image2set = " ".join(map(str, str(original_dict["DATA_RANGE="]).split()[-2:]))
        data_scale = image2set[0:] + " " + "1"
        original_dict["pscale"] = " DATA_RANGE_FIXED_SCALE_FACTOR= "+ data_scale + "\n"  
    # function to be implemented later : prepare input file wich contain x yy z where:
    # x image start yy image end by "subset of images" and z scale correction factor 
    # for this batch (possibly it's only one image).which means for 1000 img, 1000 lines
    elif "-PrsP" in settings: #scale factor personalised with external file of params
        for arg in sys.argv[2:]:
            with open(arg) as pscale_corr :
                data_scale = pscale_corr.readlines()
                for lines in data_scale:
                    i = data_scale.index(lines)
                    original_dict["pscale"+i] = " DATA_RANGE_FIXED_SCALE_FACTOR = " + lines + "\n"
    elif "-Prs0" in settings :
        original_dict["pscale"] = ""
    # in this case : the xds automatic determination will be use.
        pass


def settings_XDS_correction(original_dict, settings):
    if "-corr_none" in settings:
        original_dict["corrections"] = " CORRECTIONS=! \n"
    elif "-corr" in settings:
        original_dict["corrections"] = " CORRECTIONS=ALL \n"
    elif "-coor_decay" in settings :
        original_dict["corrections"] = " CORRECTIONS=DECAY \n"
    elif "-coor_modul" in settings :
        original_dict["corrections"] = " CORRECTIONS=MODULATION \n"        
    elif "-coor_absorp" in settings :
        original_dict["corrections"] = " CORRECTIONS=ABSORP \n"        

def settings_XDS_friedel(original_dict, settings):
    if "-ano" in settings:                     
        original_dict["FRIEDEL'S_LAW="] = " FRIEDEL'S_LAW= FALSE \n"
    elif "-noAno" in settings:
        original_dict["FRIEDEL'S_LAW="] = " FRIEDEL'S_LAW= TRUE \n"
        
##########################
def prepare4writing_xdsINP(xdsinp, dictOfKword, listOfexperiment):

    listofDicos = []               
    dicoNbr = 0
    listOfinf = ["JOB=","STRICT_ABSORPTION",
          "FRIEDEL'S_LAW=", "INCLUDE_RESOLUTION", "BACKGROUND_RANGE", "TEST_RESOLUTION_RANGE",
          "RESOLUTION_SHELLS","CORRECTIONS=", "DATA_RANGE_FIXED_SCALE_FACTOR = "
          , "STRICT_ABSORPTION=","INCLUDE_RESOLUTION_RANGE="]   
    i = 0
    while i < len(listOfinf):
        for lines in xdsinp:#remove old key value in xds INP        
            if re.findall(str(listOfinf[i]), str(lines)):
                xdsinp.remove(lines)
        i += 1      
    while dicoNbr < len(listOfexperiment):               
            #number4expe =  listOfexperiment.index(scheme)              
        dictOfKword1 = copy.deepcopy(dictOfKword)
        settings_XDS_strictAbsCorr(dictOfKword1, listOfexperiment[dicoNbr])
        settings_XDS_friedel(dictOfKword1, listOfexperiment[dicoNbr])
        settings_XDS_correction(dictOfKword1, listOfexperiment[dicoNbr])
        settings_XDS_prescal_factor(dictOfKword1, listOfexperiment[dicoNbr])
        settings_XDS_resolution(dictOfKword1, listOfexperiment[dicoNbr])
        newDico = dictOfKword1
        listofDicos.append(newDico)
        #print  listOfexperiment[dicoNbr], listofDicos[dicoNbr]   
        dicoNbr += 1
    resNbr = 1
    newDictsXds = {}
    z = 0
    while z < len(listofDicos):
        dico = listofDicos[z]
        for res in dico.keys():
            while dico.get("res"+ str(resNbr)):
#ici boucle for avec le listofDicos pour generer les xdsinp en ajoutant le contenu des dicos au xdsinp avec pour chaque res un xdsinp           
                newXdsinp = xdsinp[:]
                newXdsinp.append(dico.get("res"+ str(resNbr)))
                newXdsinp.append(dico.get("FRIEDEL'S_LAW="))
                newXdsinp.append(dico.get("corrections"))
                newXdsinp.append(dico.get("pscale"))
                newXdsinp.append(dico.get("TEST_RESOLUTION_RANGE"))
                newXdsinp.append(dico.get("STRICT_ABSORPTION"))
                newXdsinp.append(dico.get("job"))
                newDictsXds["xdsinp"+"."+str(listofDicos.index(dico))+"."+str(resNbr)] = newXdsinp
                resNbr += 1
        z += 1
        resNbr = 1        
    return newDictsXds
                
                                    
                #outputfile = open(os.path.join(directory2, "XDS.INP"), 'a')
                #outputfile.write(xdsinp)
                    
        
        
##############################
            
            
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
                        if re.findall(r"JOB=", lines):
                            print "XDS.INP is take in count"
                            create = True
                    return create
                    return xdsinp
                    
        except:
            print ("it's not XDS.INP or it's corrupted")
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
            
#        if not "File exists" in e:
#           exit(0)    
    
def FillinFolder(create, resultFile, listOfexperiment, listOfFile, xdsinp):    
    if create:
        base2editeJob = information_summary(xdsinp, resultFile)
        for i in listOfexperiment:
            folderNameExtension = catch_XDS_resolution(base2editeJob, i)         
            for nbr in folderNameExtension:
                resultFile2 = resultFile +"/"+"scheme"+str(listOfexperiment.index(i)) + ".res" + str(nbr)
                try:
                    os.makedirs(resultFile2, 0777)
                except OSError:
                    print 'WARNING : Problem to create Directory for results'
                    #if not "File exists":
                    #  exit(0)
                for kword in listOfFile:        
                    srcFile = arg[:-7] + kword
                    dest = resultFile2 + "/" + kword
                    symlink_creation(srcFile, dest)
                srcFile = arg[:-7] + "GXPARM.XDS"
                dest = resultFile2 + "/" + "XPARM.XDS"
                symlink_creation(srcFile, dest)
    return base2editeJob


#reals final progs:

scheme0 = ["all", "-Prs0","-corr","-ano"]
scheme1 = ["all", "-Prs1", "-corr", "-noAno"] 
scheme2 = ["-r", "-Prs0", "-corr-none", "-ano"]
scheme3 = ["-r", "-Prs0", "-corr", "-ano"]
scheme4 = ["-r", "Prs1", "-corr", "-ano"]
 
listOfexperiment = [scheme0, scheme1]
listOfFile = ["X-CORRECTIONS.cbf", "Y-CORRECTIONS.cbf", "GAIN.cbf", "BLANK.cbf", 
              "BKGINIT.cbf", "img"]             


create = StartingOpen()
resultFile = makeResultFile(create)
base2editeJob = FillinFolder(create, resultFile, listOfexperiment, listOfFile, xdsinp)
newDictsXds = prepare4writing_xdsINP(xdsinp, base2editeJob, listOfexperiment)
listofKey = sorted(newDictsXds)
listofFolder = sorted(glob.glob(resultFile+"/"+"scheme*"))

for key in listofKey:
    key = listofKey.index(key)
    file2write = newDictsXds[listofKey[key]]
    pathXds = str(listofFolder[key])+"/"
    writing_list_in_file(pathXds, file2write)
         
    