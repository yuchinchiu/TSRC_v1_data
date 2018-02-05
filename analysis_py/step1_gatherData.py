# -*- coding: utf-8 -*-
"""
Created on 2/5/2018 [modify from a similar one from ISSPxVTS_v1]

@author: yc180

This script go through all the log/txt in the folder and extract data to build a "group" DataFrame for later analysis
The output are two files: gpData.pkl & gpSbjInfo.pkl

"""
#%% 
import os
import glob
import pandas as pd
import numpy as np
from copy import copy
from extractData import extractDataFromCSV

#workingDir = os.path.dirname(os.path.realpath(__file__))
workingDir = "C:\\Users\\yc180\\Documents\\YCCProjects\\TSRC_v1_data\\analysis_py"
os.chdir("..")
# go up one level to the experiment directory

dataDir = os.getcwd() + os.sep + 'data' + os.sep + 'v1_batches' + os.sep  # where the log/txt files are located
csvDir  = os.getcwd() + os.sep + 'data' + os.sep + 'v1_csv' + os.sep

# run the following function to extract missing data from CSV files

extractDataFromCSV(dataDir, csvDir)


fileList     = glob.glob(dataDir +  "*.log")
infofileList = glob.glob(dataDir +  "*.txt")


gpSbjInfo=pd.DataFrame()

# From trialGen.js outputData function
# output = [this.runId, this.phase, this.stim, this.stimCat, this.task, this.trialType, this.respComp, this.memCond, this.response, this.sbjResp, this.sbjACC, this.sbjRT];
#%% 

colNames=['runId','phase','stim','stimCat','task','trialType','respComp','memCond','response','sbjResp','sbjACC','sbjRT']
gpData = pd.DataFrame(np.empty((0,len(colNames)),dtype=int), columns=colNames)
SCNT=0

for f in range(0,len(fileList),1):
    SCNT=SCNT+1
    D=np.genfromtxt(fileList[f],delimiter=',',dtype=int)
    D=pd.DataFrame(np.transpose(np.reshape(D,(len(colNames),int(D.shape[0]/len(colNames))))),columns=colNames)
    D['sbjId']=SCNT
    
    txtFileName = fileList[f][:-3]+ "txt"
    # read in the corresponding text file and extract SRmapping, etc
    sbjInfo=np.genfromtxt(txtFileName, delimiter=":", dtype=str)
    sbjInfo=pd.DataFrame(np.transpose(sbjInfo))
    sbjInfo.columns = sbjInfo.iloc[0]
    sbjInfo.drop([0],axis=0,inplace=True)    
    # 0 was the index that become header, hasn't reset index, so taking 1
    sbjInfo['sbjId']=SCNT
    sbjInfo.index = sbjInfo.sbjId
    sbjInfo.drop('sbjId',axis=1,inplace=True)
              
    
    gpSbjInfo = pd.concat([gpSbjInfo,sbjInfo],axis=0)
    gpData=pd.concat([gpData,D],axis=0)
#%%
gpData['sbjResp_mem']=copy(gpData['sbjResp'])
# no response trials
gpData.loc[gpData.sbjResp==99,'sbjACC'] = 0  
gpData.loc[gpData.sbjResp==99,'sbjRT'] = np.nan
# accuracy for memory task , default accuracy is 0
gpData.loc[(gpData.phase==3) & (gpData.sbjResp_mem>=3) & (gpData.memCond<=4),'sbjACC']=1
gpData.loc[(gpData.phase==3) & (gpData.sbjResp_mem<=2) & (gpData.memCond==5),'sbjACC']=1


gpData.loc[(gpData.phase==3) & (gpData.sbjResp_mem==4),'sbjResp']='defOld'
gpData.loc[(gpData.phase==3) & (gpData.sbjResp_mem==3),'sbjResp']='probOld'
gpData.loc[(gpData.phase==3) & (gpData.sbjResp_mem==2),'sbjResp']='probNew'
gpData.loc[(gpData.phase==3) & (gpData.sbjResp_mem==1),'sbjResp']='defNew'


# convert codings to categorical variables with meaningful names
gpData['taskNum']    = copy(gpData['task'])  # 

gpData.phase.replace(1,'TaskSw', inplace=True)
gpData.phase.replace(2,'Filler', inplace=True)
gpData.phase.replace(3,'Mem', inplace=True)
gpData.task.replace(1,'animacy', inplace=True)
gpData.task.replace(2,'size', inplace=True)
gpData.trialType.replace(0,'repeat', inplace=True)
gpData.trialType.replace(1,'switch', inplace=True)
gpData.respComp.replace(0,'RC', inplace=True)
gpData.respComp.replace(1,'RIC', inplace=True)

gpData.memCond.replace(1,'old-switch-RIC', inplace=True)
gpData.memCond.replace(2,'old-switch-RC', inplace=True)
gpData.memCond.replace(3,'old-repeat-RIC', inplace=True)
gpData.memCond.replace(4,'old-repeat-RC', inplace=True)
gpData.memCond.replace(5,'new', inplace=True)

gpData['respComp']   = pd.Categorical(gpData.respComp, categories=['RC','RIC'], ordered=True)
gpData['memCond']     = pd.Categorical(gpData.memCond, categories=['old-switch-RIC','old-switch-RC','old-repeat-RIC','old-repeat-RC','new'], ordered=True)
gpData['trialType']   = pd.Categorical(gpData.trialType, categories=['switch','repeat'], ordered=True)
gpData['sbjResp_mem'] = pd.Categorical(gpData.sbjResp_mem, categories=['defOld','probOld','probNew','defNew'], ordered=True)


# output DataFrame
os.chdir(workingDir)  # scripts directory
gpData.to_pickle('gpData_v1.pkl')
gpSbjInfo.to_pickle('gpSbjInfo_v1.pkl')
gpData.to_csv('gpData.csv',encoding='utf-8', index=False)
gpSbjInfo.to_csv('gpSbjInfo.csv',encoding='utf-8', index=False)

print(SCNT)