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
    if "-r" in settings:   
        resolution = str(original_dict_params["INCLUDE_RESOLUTION"])
        resolution_M = resolution.split()[-2]
        resolution_m = float(resolution.split()[-1])
        resolution2test = []
        resolution2test.append(round(resolution_m - 0.35))        
        t = 1
        while t < 4 :
            resolution2test.append(round(resolution_m + t*0.35, 2))
            original_dict_params["res"+str(t)] = " INCLUDE_RESOLUTION_RANGE= "+ resolution_M +" "+ str(resolution2test[t-1]) + "\n"
#            folderNameExtension = resolution2test
            t += 1
        original_dict_params["res"+str(t)] = " INCLUDE_RESOLUTION_RANGE= "+ resolution_M +" "+ str(resolution2test[t-1]) + "\n"
    else :
        t = 1
        resolution = str(original_dict_params["INCLUDE_RESOLUTION"])
        resolution_M = resolution.split()[-2]
        resolution_m = float(resolution.split()[-1]) 
        resolution2test = []
        resolution2test.append(round(resolution_m, 2))
        original_dict_params["res"+str(t)] = " INCLUDE_RESOLUTION_RANGE= "+ resolution_M +" "+ str(resolution2test[t-1]) + "\n"
# ici ce bloc n'est pas teste, ce qui est au dessus est OK
    #elif "-r" or "all" in settings:
        #define the test resolution range pour test :  
#        reso_cut = resolution2test[-1]
#        original_dict_params["TEST_RESOLUTION_RANGE"] = "TEST_RESOLUTION_RANGE= 50 "+ str(reso_cut) +"\n"
#        folderNameExtension = [reso_cut]
#        print folderNameExtension 
#        print "de xds_resolution"
#    else :
#        print "coucou"
    #    print "Problem in resolution settings"
    #return  folderNameExtension
  
def catch_XDS_resolution(original_dict_params, settings):  
#"""settings must be a list of patrameters wich may influence\
#        scaling or integration that we want to explore"""
  ### resolution max setting
    if "-r" in settings:   
        resolution = str(original_dict_params["INCLUDE_RESOLUTION"])
        resolution_m = float(resolution.split()[-1])
        resolution2test = []
        resolution2test.append(round(resolution_m - 0.35))        
        t = 1
        while t < 4 :
            resolution2test.append(round(resolution_m + t*0.35, 2))
            folderNameExtension = resolution2test
            t += 1
    else :
        resolution = str(original_dict_params["INCLUDE_RESOLUTION"])
        resolution_m = float(resolution.split()[-1])
        resolution2test = []
        resolution2test.append(round(resolution_m, 2))        
        folderNameExtension = resolution2test
    return folderNameExtension
# not tested
   # elif "-r" or "all" in settings:
        #define the test resolution range pour test :  
   #     reso_cut = resolution2test[-1]
   #     folderNameExtension = [reso_cut]
   #     print folderNameExtension
   #     print "de catch"
   # else :
   #     print "Problem in resolution settings"
   # return  folderNameExtension
   # print folderNameExtension
   # print "de catch"
    
def settings_XDS_strictAbsCorr(original_dict_params, settings):
  ### strict abs correction : 
    if "-sa0" in settings:
        dictio_value_edition(original_dict_params, "STRICT_ABSORPTION","STRICT_ABSORPTION_CORRECTION= TRUE \n" )
    elif "-sa2" in settings:
        dictio_value_edition(original_dict_params, "STRICT_ABSORPTION","STRICT_ABSORPTION_CORRECTION= TRUE \n")
    elif "-sa1" in settings:
        dictio_value_edition(original_dict_params, "STRICT_ABSORPTION","STRICT_ABSORPTION_CORRECTION= FALSE \n")
       

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
    elif "-corr_decay" in settings :
        original_dict["corrections"] = " CORRECTIONS=DECAY \n"
    elif "-corr_modul" in settings :
        original_dict["corrections"] = " CORRECTIONS=MODULATION \n"        
    elif "-corr_absorp" in settings :
        original_dict["corrections"] = " CORRECTIONS=ABSORP \n"    
    elif "corr_dec_mod" in settings : 
        original_dict["corrections"] = " CORRECTIONS=DECAY MODULATION \n"
    elif "corr_dec_abs" in settings : 
        original_dict["corrections"] = " CORRECTIONS=DECAY ABSORP \n"        
    elif "corr_mod_abs" in settings : 
        original_dict["corrections"] = " CORRECTIONS=MODULATION ABSORP \n"         
    else : 
        original_dict["corrections"] = " CORRECTIONS=ALL \n"
        

def settings_XDS_friedel(original_dict, settings):
    if "-sa1" in settings:
        original_dict["FRIEDEL'S_LAW="] = " FRIEDEL'S_LAW= FALSE \n"
    elif "-sa2" in settings:
        original_dict["FRIEDEL'S_LAW="] = " FRIEDEL'S_LAW= FALSE \n"
    else :
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
        #number4expe =  listOfexperiment.index(schemes) 
        #print number4expe             
        #print dicoNbr         
        dictOfKword1 = copy.deepcopy(dictOfKword)
        #print dictOfKword1
        #print listOfexperiment[dicoNbr]
        settings_XDS_strictAbsCorr(dictOfKword1, listOfexperiment[dicoNbr])
        settings_XDS_friedel(dictOfKword1, listOfexperiment[dicoNbr])
        settings_XDS_correction(dictOfKword1, listOfexperiment[dicoNbr])
        settings_XDS_prescal_factor(dictOfKword1, listOfexperiment[dicoNbr])
        settings_XDS_resolution(dictOfKword1, listOfexperiment[dicoNbr])
        newDico = dictOfKword1
        listofDicos.append(newDico)
        #print newDico
        #print listofDicos
        #print  listOfexperiment[dicoNbr], listofDicos[dicoNbr]   
        dicoNbr += 1
    resNbr = 1
    newDictsXds = {}
    z = 0
    while z < len(listofDicos):
        dico = listofDicos[z]
        for res in dico.keys():
            while dico.get("res"+ str(resNbr)):
        # this loop, is made in the listOfDicos (Dcit list) to generate XDS.INP
        # by adding the parameters contained in the dicts.          
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
                        if re.findall(r"JOB=", lines):
                            print "XDS.INP is take in count"
                            create = True
                    return create
                    return xdsinp
                    
        except:
            print ("it's not XDS.INP or it's corrupted")
            exit(0)    
            
def givenUserOption():
    option1 = raw_input ('Please chose if you want use the parameter\
 which concern the scaling parameters per frames [N/y] : ' )
    if option1 == '' :
        option1 = 'N'
    else:
        option1 = option1
    
    option2 = raw_input ('Please chose if you want use the parameter\
 which modify the CORRECTION options "m" for MODULATION, "d" for DECAY, "a" for\
 ABSORP, "n" for NONE default is ALL (example : md) :')
    if option2 =='':
        option2 = 'all'
    else:
        option2 = option2
    listofOptions = [option1, option2] 
    return listofOptions
    
    
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


""" this is really the program to generate automaticaly different XDS.INP
"""
# reminder : sa0 : Friedel = true and Strict-Abs = true
# sa1 : Friedel = false and Strict-Abs = false
# sa2 : Friedel = false and Strict-Abs = true

scheme0 = ["-Prs0", "-corr", "-sa0"]
scheme1 = ["-Prs0", "-corr", "-sa1"] 
scheme2 = ["-Prs0", "-corr", "-sa2"]

scheme0_1 = ["-r", "-Prs0", "-corr_decay", "-sa0"]
scheme0_2 = ["-r", "-Prs0", "-corr_modul", "-sa0"]
scheme0_3 = ["-r", "-Prs0", "-corr_absorbp", "-sa0"]
scheme0_4 = ["-r", "-Prs0", "-corr_dec_mod", "-sa0"]
scheme0_5 = ["-r", "-Prs0", "-corr_dec_abs", "-sa0"]
scheme0_6 = ["-r", "-Prs0", "-corr_mod_abs", "-sa0"]
scheme0_7 = ["-r", "-Prs0", "-corr_none", "-sa0"]

scheme1_1 = ["-r", "-Prs0", "-corr_decay", "-sa1"]
scheme1_2 = ["-r", "-Prs0", "-corr_modul", "-sa1"]
scheme1_3 = ["-r", "-Prs0", "-corr_absorbp", "-sa1"]
scheme1_4 = ["-r", "-Prs0", "-corr_dec_mod", "-sa1"]
scheme1_5 = ["-r", "-Prs0", "-corr_dec_abs", "-sa1"]
scheme1_6 = ["-r", "-Prs0", "-corr_mod_abs", "-sa1"]
scheme1_7 = ["-r", "-Prs0", "-corr_none", "-sa1"]

scheme2_1 = ["-r", "-Prs0", "-corr_decay", "-sa2"]
scheme2_2 = ["-r", "-Prs0", "-corr_modul", "-sa2"]
scheme2_3 = ["-r", "-Prs0", "-corr_absorbp", "-sa2"]
scheme2_4 = ["-r", "-Prs0", "-corr_dec_mod", "-sa2"]
scheme2_5 = ["-r", "-Prs0", "-corr_dec_abs", "-sa2"]
scheme2_6 = ["-r", "-Prs0", "-corr_mod_abs", "-sa2"]
scheme2_7 = ["-r", "-Prs0", "-corr_none", "-sa2"] 
 
scheme0_a = ["-Prs1", "-corr", "-sa0"]
scheme1_a = ["-Prs1", "-corr", "-sa1"] 
scheme2_a = ["-Prs1", "-corr", "-sa2"] 
 
 
scheme0_1_a = ["-r", "-Prs1", "-corr_decay", "-sa0"]
scheme0_2_a = ["-r", "-Prs1", "-corr_modul", "-sa0"]
scheme0_3_a = ["-r", "-Prs1", "-corr_absorbp", "-sa0"]
scheme0_4_a = ["-r", "-Prs1", "-corr_dec_mod", "-sa0"]
scheme0_5_a = ["-r", "-Prs1", "-corr_dec_abs", "-sa0"]
scheme0_6_a = ["-r", "-Prs1", "-corr_mod_abs", "-sa0"]
scheme0_7_a = ["-r", "-Prs1", "-corr_none", "-sa0"]

scheme1_1_a = ["-r", "-Prs1", "-corr_decay", "-sa1"]
scheme1_2_a = ["-r", "-Prs1", "-corr_modul", "-sa1"]
scheme1_3_a = ["-r", "-Prs1", "-corr_absorbp", "-sa1"]
scheme1_4_a = ["-r", "-Prs1", "-corr_dec_mod", "-sa1"]
scheme1_5_a = ["-r", "-Prs1", "-corr_dec_abs", "-sa1"]
scheme1_6_a = ["-r", "-Prs1", "-corr_mod_abs", "-sa1"]
scheme1_7_a = ["-r", "-Prs1", "-corr_none", "-sa1"]

scheme2_1_a = ["-r", "-Prs1", "-corr_decay", "-sa2"]
scheme2_2_a = ["-r", "-Prs1", "-corr_modul", "-sa2"]
scheme2_3_a = ["-r", "-Prs1", "-corr_absorbp", "-sa2"]
scheme2_4_a = ["-r", "-Prs1", "-corr_dec_mod", "-sa2"]
scheme2_5_a = ["-r", "-Prs1", "-corr_dec_abs", "-sa2"]
scheme2_6_a = ["-r", "-Prs1", "-corr_mod_abs", "-sa2"]
scheme2_7_a = ["-r", "-Prs1", "-corr_none", "-sa2"]


listOfexperiment1 = [scheme0, scheme1, scheme2]
listOfexperiment2 = [scheme0_7, scheme1_7, scheme2_7]
listOfexperiment3 = [scheme0_2, scheme1_2, scheme2_2]
listOfexperiment4 = [scheme0_1, scheme1_1, scheme2_1]
listOfexperiment5 = [scheme0_3, scheme1_3, scheme2_3]
listOfexperiment6 = [scheme0_5, scheme1_5, scheme2_5]
listOfexperiment7 = [scheme0_4, scheme1_4, scheme2_4]
listOfexperiment8 = [scheme0_6, scheme1_6, scheme2_6]

listOfexperiment1_a = [scheme0_a, scheme1_a, scheme2_a]
listOfexperiment2_a = [scheme0_7_a, scheme1_7_a, scheme2_7_a]
listOfexperiment3_a = [scheme0_2_a, scheme1_2_a, scheme2_2_a]
listOfexperiment4_a = [scheme0_1_a, scheme1_1_a, scheme2_1_a]
listOfexperiment5_a = [scheme0_3_a, scheme1_3_a, scheme2_3_a]
listOfexperiment6_a = [scheme0_5_a, scheme1_5_a, scheme2_5_a]
listOfexperiment7_a = [scheme0_4_a, scheme1_4_a, scheme2_4_a]
listOfexperiment8_a = [scheme0_6_a, scheme1_6_a, scheme2_6_a]

listofOptions = givenUserOption()
if listofOptions[0] == 'y':
    Prs = 'Prs1'
else :
    Prs = 'Prs0'
if listofOptions[1] == 'm':
   corr = 'modulation'
elif listofOptions[1] == 'd':
   corr = 'decay'
elif listofOptions[1] == 'a':
   corr = 'absorp'
elif listofOptions[1] == 'n':
   corr = 'none'     
elif listofOptions[1] == 'all':
   corr = 'all'
elif listofOptions[1] == 'da' or 'ad':
   corr = 'abs_dec'
elif listofOptions[1] == 'dm' or 'md':
   corr = 'mod_dec'
else :
   corr = 'abs_mod'

if Prs == 'Prs0' and corr == 'all':
    listOfexperiment = listOfexperiment1
elif Prs == 'Prs0' and corr == 'none':
    listOfexperiment = listOfexperiment2
elif Prs == 'Prs0' and corr == 'modulation':
    listOfexperiment = listOfexperiment3
elif Prs == 'Prs0' and corr == 'decay':
    listOfexperiment = listOfexperiment4
elif Prs == 'Prs0' and corr == 'absorp':
    listOfexperiment = listOfexperiment5
elif Prs == 'Prs0' and corr == 'abs_dec':
    listOfexperiment = listOfexperiment6    
elif Prs == 'Prs0' and corr == 'mod_dec':
    listOfexperiment = listOfexperiment7
elif Prs == 'Prs0' and corr == 'abs_mod':
    listOfexperiment = listOfexperiment8   
    
elif Prs == 'Prs1' and corr == 'all':
    listOfexperiment = listOfexperiment1_a
elif Prs == 'Prs1' and corr == 'none':
    listOfexperiment = listOfexperiment2_a
elif Prs == 'Prs1' and corr == 'modulation':
    listOfexperiment = listOfexperiment3_a
elif Prs == 'Prs1' and corr == 'decay':
    listOfexperiment = listOfexperiment4_a
elif Prs == 'Prs1' and corr == 'absorp':
    listOfexperiment = listOfexperiment5_a
elif Prs == 'Prs1' and corr == 'abs_dec':
    listOfexperiment = listOfexperiment6_a    
elif Prs == 'Prs1' and corr == 'mod_dec':
    listOfexperiment = listOfexperiment7_a
elif Prs == 'Prs1' and corr == 'abs_mod':
    listOfexperiment = listOfexperiment8_a     

        


listOfFile = ["X-CORRECTIONS.cbf", "Y-CORRECTIONS.cbf", "GAIN.cbf", "BLANK.cbf", 
              "BKGINIT.cbf", "img"]             


create = StartingOpen()
resultFile = makeResultFile(create)
#print resultFile
#print listOfexperiment
#print listOfFile
#print xdsinp
base2editeJob = FillinFolder(create, resultFile, listOfexperiment, listOfFile, xdsinp)
#print listOfexperiment
#print base2editeJob
newDictsXds = prepare4writing_xdsINP(xdsinp, base2editeJob, listOfexperiment)
#print newDictsXds
listofKey = sorted(newDictsXds)
listofFolder = sorted(glob.glob(resultFile+"/"+"scheme*"))

for key in listofKey:
#    print listofKey
#    print key
    key = listofKey.index(key)
    file2write = newDictsXds[listofKey[key]]
    #print file2write    
    pathXds = str(listofFolder[key])+"/"
    writing_list_in_file(pathXds, file2write)
         
    