import ykosc as cl
import sys
import os
import json
import numpy as np
import subprocess as sp
import configedit as ce
import cv2
import time
import shutil

pickarg = lambda optch: sys.argv[sys.argv.index(optch) + 1]

npzname_base :str= pickarg("-b")#"section_8_%03d.npz"
configfile :str= pickarg("-c")#"20221219005750096876.json"
scrdirtxt :os.PathLike= pickarg("-d")#"C:/Users/yuuk_/OneDrive/private/python_private/yk_oscilloscope/script\\sct_20221219005750096876"
exportmoviename :str= pickarg("-e")#"section_8.mp4"

pngname_base = os.path.splitext(npzname_base)[0] + ".png"
if "-f" in sys.argv:
    forwardfilename :str= pickarg("-f")
else:
    forwardfilename :str= pngname_base % 0


configdict :dict= ce.readconfigfile(configfile)

with open(scrdirtxt,"r",encoding='utf-8',newline='\n') as scr:
    scrdir = scr.read()
os.chdir(scrdir)
sectiondir = os.path.splitext(exportmoviename)[0]
os.mkdir(sectiondir)

imgW = configdict["framewidth"]
imgH = configdict["frameheight"]
smprange = configdict["smprange"]
fps = configdict["fps"]
moviebitrate = configdict["moviebitrate"]
vcodec = configdict["moviecodec"]
backcolor = cl.RGBA2rgbarray(configdict["backcolor"])
linecolor = cl.RGBA2rgbarray(configdict["linecolor"])
linewidth = max(1,int(configdict["linebold"]))

def npz2png(npzfile : os.PathLike):
    pltcrds = np.load(npzfile)
    pngfilename = os.path.splitext(npzfile)[0] + ".png"
    outmat = np.full((imgH,imgW,3),backcolor[::-1],dtype=np.int8)
    for pltcrd in pltcrds:
        cv2.polylines(outmat,[pltcrd],False,linecolor[::-1],thickness=linewidth)
    #cv2.imwrite(pngfilename,outmat)
    #shutil.move(pngfilename,sectiondir)
    cv2.imwrite(os.path.join(sectiondir,pngfilename),outmat)
    while os.path.isfile(npzfile):
        try:
            os.remove(npzfile)
        except:
            time.sleep(1)
    return pngfilename

targetnpzs = []
ind = 0
while os.path.isfile(npzname_base % ind):
    targetnpzs.append(npzname_base % ind)
    ind += 1

pngfilelist = []
for npzfile in targetnpzs:
    pngfilelist.append(npz2png(npzfile))

while not(os.path.isfile(forwardfilename)) and ("-f" in sys.argv):
    time.sleep(1)

#com1 = f"ffmpeg -framerate {fps} -i {pngname_base} -vcodec {vcodec} -pix_fmt yuv420p -r {fps} -b:v {moviebitrate}k -loglevel warning {exportmoviename}"
os.chdir(sectiondir)
com1 = f"ffmpeg -framerate {fps} -i {pngname_base} -pass 1 -vcodec {vcodec} -pix_fmt yuv420p -r {fps} -b:v {moviebitrate}k -loglevel warning {exportmoviename} -y"
com2 = f"ffmpeg -framerate {fps} -i {pngname_base} -pass 2 -vcodec {vcodec} -pix_fmt yuv420p -r {fps} -b:v {moviebitrate}k -loglevel warning {exportmoviename} -y"
sp.run(com1)
sp.run(com2)

for pngfilename in pngfilelist:
    try:
        os.remove(pngfilename)
        pass
    except:
        print(f"{os.path.abspath(pngfilename)} could NOT be removed.")

shutil.move(exportmoviename,scrdir)
os.chdir(scrdir)
with open(os.path.splitext(exportmoviename)[0] + ".txt","w") as fw:
    fw.write("complete")
