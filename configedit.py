import json
import os
import numpy as np


#defaultc config
configfiledirectory = os.path.abspath("config")
reservedconfigfilename = "temp_configdata"
"""
fps = 30
downfr = 1
moviebitrate = 1250
moviecodec = ["h264","h265"][0]

column = 1
linecoror = (0,1,0.6,1)
colorname = "ykgreen"
#purple:c000ff:192,0,255=0.753,0,1
#ykgreen:00ff99:0,255,153=0,1,0.6
#sakurazaka46:f19db5:241,157,181=0.9451,0.6157,0.7098
#TokyoDisneySea:0,0.5,1
#SixTINES,masukara:ff00c6:255,0,198=1,0,0.7765
#Sexy Zone,Honey Honey:ebd354:235,211,84=0.9216,0.8275,0.3294
backcolor = (0,0,0,1)
smprange = 1000 // downfr
frameheight = 2160
framewidth = int(frameheight * 16 // 9)
linebold = 0.2 * max(framewidth / 1920 , frameheight / 1080)
"""

configkeylist = [
    "configname",
    "fps",
    "downfr",
    "moviebitrate",
    "moviecodec",
    "column",
    "linecolor",
    "backcolor",
    "smprange",
    "frameheight",
    "framewidth",
    "linebold",
    "visualtype"
]

visualtypelist = ["oscilloscope","spectrum"]

DefaultConfig = {
    "configname":"4k60fps",
    "fps":60,
    "downfr":1,
    "moviebitrate":10000,
    "moviecodec":"h264",
    "column":1,
    "linecolor":(0,1,0.6,1),
    "backcolor":(0,0,0,1),
    "smprange":1000,
    "frameheight":2160,
    "framewidth":3840,
    "linebold":0.4,
    "visualtype":visualtypelist[0]
}

def ConfigExport2Json(configdata,configfilename = False,owconf = True):
    if configfilename and type(configfilename) == str:
        configname = configfilename
    else:
        configname = configdata["configname"] + ".json"
    cm0 = "Y"
    if os.path.isfile(configfiledirectory + "/" + configname) and owconf:
        print("'" + configname + "' file already exists.")
        print("Do you want to overwrite?")
        cm0 = input("If so, input 'Y' > ")
    if cm0 == "Y" or cm0 =="y":
        with open(configfiledirectory + "/" + configname,'w') as fw:
            json.dump(configdata,fw,indent=4)
    return False

def readconfigfile(configfile):
    if configfile and os.path.isfile(configfiledirectory + "/" + configfile):
        with open(configfiledirectory + "/" + configfile,'r') as cfr:
            configdata = json.load(cfr)
        for a in range(len(configkeylist)):
            if type(configdata[configkeylist[a]]) == list:
                configdata[configkeylist[a]] = tuple(configdata[configkeylist[a]])
    else:
        if configfile:
            print("failed to read:" + configfile)
        configdata = DefaultConfig
    return configdata

def colorchange(cm0 = False):
    if cm0:
        cm0 = cm0.replace("'","").replace(" ","")
    else:
        print("Please input the color as RGB or RGBA.")
        print("ex: '00ff99' '0,255,153' '0,1,0.6' '0,1,0.6,1'")
        cm0 = input(" > ").replace("'","").replace(" ","")
    if not("," in cm0):
        cm0 = [int(cm0[0:2],16),int(cm0[2:4],16),int(cm0[4:6],16),255]
    else:
        cm0 = cm0.split(",")
    if max(np.array(cm0).astype(float)) > 1:
        cm0 = list(np.array(cm0).astype(float) / 255)
    else:
        cm0 = list(np.array(cm0).astype(float))
    for a in range(len(cm0)):
        cm0[a] = max(0,min(1,cm0[a]))
    if len(cm0) == 3:
        cm0 += [1]
    cm0 = tuple(cm0)
    return cm0

def visualtypechange(beforetype):
    for a in range(len(visualtypelist)):
        print("[" + str(a) + "] " + visualtypelist[a])
    print("Please select the number (or value name) to change visualtype.")
    roop0 = True
    aftertype = beforetype
    while roop0:
        roop0 = False
        cm0 = input(" > ")
        if cm0 == "":
            pass
        elif cm0 in visualtypelist:
            aftertype = cm0
        elif int(cm0) in range(len(visualtypelist)):
            aftertype = visualtypelist[int(cm0)]
        else:
            roop0 = True
    return aftertype

def showconfigdata(configdata,Editmode = False):
    for a in range(len(configkeylist)):
        print("[" + str(a) + "] " + configkeylist[a] + ": " + str(configdata[configkeylist[a]]))
    if Editmode:
        print("[" + str(a+1) + "] " + ": finish editing and save")
    return False

def configdataedit(configfile = ""):
    if type(configfile) == dict:
        editconfigdata = configfile
    else:
        editconfigdata = readconfigfile(configfile)
    roop0 = True
    while roop0:
        showconfigdata(editconfigdata,True)
        print("Please select the number (or value name) to customize.")
        cm0 = input(" > ")
        if cm0 in configkeylist:
            cm0 = configkeylist.index(cm0)
        elif cm0 == "finish editing and save":
            cm0 = len(configkeylist)
        elif cm0 in np.array(range(len(configkeylist)+1)).astype('str'):
            cm0 = int(cm0)
        else:
            cm0 = -1
        if cm0 in range(len(configkeylist)):
            if type(editconfigdata[configkeylist[cm0]]) == tuple: 
                editconfigdata[configkeylist[cm0]] = colorchange()
            elif configkeylist[cm0] == "visualtype":
                editconfigdata[configkeylist[cm0]] = visualtypechange(editconfigdata[configkeylist[cm0]])
            else:
                try:
                    editconfigdata[configkeylist[cm0]] = type(editconfigdata[configkeylist[cm0]])(input(configkeylist[cm0] + " : "))
                except:
                    pass
        elif cm0 == len(configkeylist):
            roop0 = False
        else:
            pass
    return editconfigdata

if __name__ == "__main__":
    print("Edit Config Mode")
    rundir = os.getcwd()
    os.chdir(configfiledirectory)
    roop1 = True
    while roop1:
        #configfiles = fo.filesearch("json",configfiledirectory,"configfile")
        configfiles = list(filter(lambda file:file.endswith(".json"),os.listdir(".")))
        if configfiles:
            #configdata = configdataedit(fo.fileselect(configfiles,[configfiledirectory] * len(configfiles),"configfile")[1].replace(".json",""))
            configdata = configdataedit(configfiles[int(input("\n".join([f"[{ind}]:{file}" for ind,file in enumerate(configfiles)])+"\n > "))])
        else:
            configdata = configdataedit()
        print("Save configfile? (Unsaved config data will be lost.)")
        cm1 = input("If so, input 'Y' > ")
        if cm1 == "Y" or cm1 == 'y':
            roop2 = True
            while roop2:
                print("Please input config name.")
                print("If you don't input anything,'configname'value(" + configdata["configname"] + ") will be used.")
                configfilename = input(" > ")
                if configfilename == "":
                    configfilename = configdata["configname"]
                if configfilename == reservedconfigfilename:
                    print("This filename can't be used.")
                else:
                    ConfigExport2Json(configdata,configfilename)
                    roop2 = False
        print("Will you end Edit Config Mode?")
        cm2 = input("If so, input 'Y' > ")
        if cm2 == "Y" or cm2 == 'y':
            roop1 = False
    os.chdir(rundir)


