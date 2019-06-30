# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 15:52:55 2018

@author: muyiw
"""
import numpy as np
import pandas as pd
import os
import datetime 
from math import sqrt
import matplotlib.pyplot as plt
from matplotlib import dates
from matplotlib import axis
import scipy
from scipy import stats
from matplotlib import pylab
station = 'C:/Users/muyiw/OneDrive/Documents/NOAA/BLENDEDSM/BLENDEDSM_Validation'
Reg_list = list()
headerproblem = list()

for t in range(len(os.listdir(station))):
#  try:  
    k = os.listdir(station)[int(t)]

    sitelist = 'C:/Users/muyiw/OneDrive/Documents/NOAA/RAWSCAN_SiteList_WithSiteName.txt'
    
    #Acquire Lat/Lon data from text file
    sitelist =  pd.read_table(sitelist, delimiter=',', header='infer' )
    sitelist.columns = sitelist.columns.str.strip()
    sitelist = sitelist.set_index('station id')
    sitelist.index = sitelist.index.str.strip()
    k = int(k)
    lat = sitelist.loc[str(int(k))].lat
    lon = sitelist.loc[str(int(k))].lon 
    lat = lat.strip()
    lon = lon.strip()

    sitename = sitelist.loc[str(k)].site_name.strip()
    state = sitelist.loc[str(k)].state.strip()
    
    curr_station = station + '/' + '%04d'%int(k)
    os.chdir(curr_station)
    blist = {}

    
    frame = station + '/'+  '%04d'%int(k) +'/'+'%04d'%int(k)+'_Validation_Table.txt' 
    frame =  pd.read_table(frame, delimiter=',', header='infer')
    
    if len(frame.columns) < 8:
        frame = station + '/'+  '%04d'%int(k) +'/'+'%04d'%int(k)+'_Validation_Table.txt' 
        frame =  pd.read_table(frame, delimiter='\t', header='infer')


#    frame = frame.drop(['Day'],axis=1)
#    frame = frame.rename(columns={'Month':'Day'})  
#    frame = frame.rename(columns={'Year':'Month'})
#    frame = frame.reset_index().rename(columns={'index':'Year'})
#      
#    
    try:
      groundss = list()
     
      #### Make all SM values a decimal########----------  
      for e in range(len(frame)):
            if frame.InSitu_SM[e] > 1:
               frame.InSitu_SM[e] = round(frame.InSitu_SM[e]/100,2) 
               
      for m in range(len(frame)):
            if frame.Satellite_SM[m] > 1:
               frame.Satellite_SM[m] = round(frame.Satellite_SM[m]/100,2)       
      #########################################----------
      
      for q in range(len(frame)):
        ground = frame.InSitu_SM.values[q]
        satellite = frame.Satellite_SM.values[q]
        try:
            delta =  round(satellite -ground,2)
        except AttributeError:
            break
        mts = frame.Month.values[q]
        year = frame.Year.values[q]
        day = frame.Day.values[q]
        ts = datetime.date(year, mts, day) 
        blist.update({ts: [delta,frame.InSitu_SM.values[q],frame.Satellite_SM.values[q]]})
        groundss.append(ground)
    except ValueError:
        del frame
        frame = station + '/'+  '%04d'%int(k) +'/'+'%04d'%int(k)+'_Validation_Table.txt'        
        frame =  pd.read_table(frame, delimiter=',', header='infer')
        
        if len(frame.columns) < 8:
            frame = station + '/'+  '%04d'%int(k) +'/'+'%04d'%int(k)+'_Validation_Table.txt' 
            frame =  pd.read_table(frame, delimiter='\t', header='infer')
            
        groundss = list()
        
        
        #### Make all SM values a decimal########----------  

        for e in range(len(frame)):
            if frame.InSitu_SM[e] > 1:
               frame.InSitu_SM[e] = round(frame.InSitu_SM[e]/100,2) 
               
        for m in range(len(frame)):
            if frame.Satellite_SM[m] > 1:
               frame.Satellite_SM[m] = round(frame.Satellite_SM[m]/100,2) 
               
        #########################################----------

               
               
        for q in range(len(frame)):
            ground = frame.InSitu_SM.values[q]
            satellite = frame.Satellite_SM.values[q]
            delta =  round(satellite -ground,2)
            mts = frame.Month.values[q]
            year = frame.Year.values[q]
            day = frame.Day.values[q]
            ts = datetime.date(year, mts, day) 
            blist.update({ts: [delta,frame.InSitu_SM.values[q],frame.Satellite_SM.values[q]]})
            groundss.append(ground)
    Nans = list()
    for key, value in blist.items():
        for o in value:
            if o < -999:
                Nans.append(key)
                continue
            
    
    for u in range(len(Nans)):
        try:
            del blist[Nans[u]]
        except KeyError:
            continue
        
    bias = pd.DataFrame.from_dict(blist, orient='index',columns = ['Bias','InSitu_SM','Satellite_SM'])
    bias = bias.reset_index().rename(columns={'index':'Timestamp'})
   



#        
    avgB = round(np.mean(bias.Bias),3)    
    
    try:
        RMSE = round(sqrt(sum(n*n for n in bias.Bias)/len(bias.Bias)),3)
    except ZeroDivisionError:
        continue
#    UB = sum((n-avgB) for n in bias.Bias)
#    ww =  UB-p for p in bias.InSitu_SM
    ub_val = list()
   
    
    
    
    
    
    
    
    
    for f in range(len(bias.Bias)):
        normalize = bias.Bias[f] - avgB
        try: 
           unbias = normalize - groundss[f]
        except IndexError:
           headerproblem.append(k)
           continue
       
        
        
        
        
        
        
        
        ub_val.append(normalize)
    
    ubRMSE = round(sqrt(sum((j*j) for j in ub_val)/(len(ub_val))),3)
      #UNBIASED DIFF BIAS-MEANBIAS
      #CORRELATION COEFFICIENT FIX!!!!!!!!!!!!!!!!
    reg = scipy.stats.linregress(bias.InSitu_SM,bias.Satellite_SM)
    reg = round(reg[2],3)
    

    fig = plt.figure()
    Y = dates.YearLocator()
    M = dates.MonthLocator(interval = 8)
    dfmt = dates.DateFormatter('%b')
    ax = fig.add_subplot(111)
    ax.xaxis.set_major_locator(Y)
#    ax.xaxis.set_minor_locator(M)
    ax.xaxis.set_minor_formatter(dfmt)
   
    ax.xaxis.set_label_position('bottom')
    
    
    plt.plot(bias.Timestamp,bias.InSitu_SM, label = 'In-Situ',color = 'r', linestyle = '-.', \
             linewidth = 2)
    plt.plot(bias.Timestamp,bias.Satellite_SM, label = 'SatSM', color='blue', linestyle='-' \
             , linewidth = 2)
    
    plt.ylabel('Soil Moisture (m3/m3)')
    plt.xlabel('Date')
    plt.title('BLENDEDSM  @ ' +sitename + ', '+state+  ' ('+lat+' , ' + lon + ')')
#    plt.legend()
    plt.ylim((0,1))
#    plt.xlim((bias.Timestamp[0],bias.Timestamp[len(bias)-1]))
    pylab.legend(loc=9, bbox_to_anchor=(0.8, 0.9), ncol=1)
    stat = str('Bias    '+ str(avgB) +'\n'+ \
                  'RMSE:   ' + str(RMSE) + '\n'+ \
                  'ubRMSE: ' + str(ubRMSE) +'\n'+\
                  'r:       '+ str(reg))
    font = {'family': 'sans-serif', \
        'color':  'b',\
        'weight': 'normal',\
        'size': 12}
    plt.text(bias.Timestamp[2],.65,stat, fontdict = font)
    plotname = '%04d'%int(k) + '_Stat_Anl.png'
    fig.savefig(plotname)
    plt.ioff
    regressions = '%04d'%int(k) + ',' + str(reg)
    Reg_list.append(regressions)
    os.chdir(station)



##  PUT HEADER ON ALL FILES:
#problems = list()
#for t in range(len(os.listdir(station))):    
#    k = os.listdir(station)[int(t)]
#    k = int(k)
#    site = station + '/%04d'%k
#
#    contents = site+'/%04d'%int(k)+'_Validation_Table.txt'
#    header = 'Year,Month,Day,SiteID,lat,lon,InSitu_SM,Satellite_SM'
#
#    append_copy = open(contents, "r")
#    line = append_copy.readline()
#    
#    if line[0] != 'Y':
#   
#        append_copy = open(contents, "r")
#        original_text = append_copy.read()
#        
#        
#        append_copy.close()
#    
#        append_copy = open(contents, "w")
#        append_copy.write(header+'\n')
#        append_copy.write(original_text)
#        append_copy.close()
#        problems.append(k)
#
#    else:
#        append_copy.close()
  

#######     DELETE CONSCUTIVE COMMAS IN TEXT LINES
# commaprobs = list()
# for t in range(len(os.listdir(station))):    
#    k = os.listdir(station)[int(t)]
#    k = int(k)
#    site = station + '/%04d'%k
#
#    contents = site+'/%04d'%int(k)+'_Validation_Table.txt'
#    header = 'Year,Month,Day,SiteID,lat,lon,InSitu_SM,Satellite_SM'
#
#    append_copy = open(contents, "r")
#    line = append_copy.readlines()
#    for w in range(len(line)):
#        if ',,' in line[w]:
#            line[w] = line[w].replace(',,',',')
#            commaprobs.append(k)
##    
##    original_text = append_copy.read()
#    append_copy.close()
#    
#    append_copy = open(contents, "w")
#    append_copy.writelines(line)
##    fake.write(original_text)
#    append_copy.close()

####### COREECTLY SPELL SATELLITE IN HEADER
#problems =list()
#for t in range(len(os.listdir(station))):    
#    k = os.listdir(station)[int(t)]
#    k = int(k)
#    site = station + '/%04d'%k
#
#    contents = site+'/%04d'%int(k)+'_Validation_Table.txt'
#    header = 'Year,Month,Day,SiteID,lat,lon,InSitu_SM,Satellite_SM'
#
#    append_copy = open(contents, "r")
#    line = append_copy.readlines()
#    line[1]
#    if 'Skte' in line:
#        line = line.replace('Skte', 'Sate')
#        append_copy = open(contents, "r")
#        original_text = append_copy.read()
#        
#        
#        append_copy.close()
#    
#        append_copy = open(contents, "w")
#        append_copy.write(line+'\n')
#        append_copy.write(original_text)
#        append_copy.close()
#        problems.append(k)
#
#    else:
#       append_copy.close()
  
