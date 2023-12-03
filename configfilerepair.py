import json
import os
import numpy as np

import fileopen as fo
import configedit as cfe

cflist = fo.filesearch("json",cfe.configfiledirectory,"configfile")
os.chdir(cfe.configfiledirectory)
if __name__ == "__main__":
    for a in range(len(cflist)):
        with open(cflist[a],'r') as cfr:
            configdata = json.load(cfr)
        for b in range(len(cfe.configkeylist)):
            if not(cfe.configkeylist[b] in configdata.keys()):
                configdata[cfe.configkeylist[b]] = cfe.DefaultConfig[cfe.configkeylist[b]]
        with open(cflist[a],'w') as fw:
            json.dump(configdata,fw,indent=4)