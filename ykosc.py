import os
import subprocess as sp
import shutil
import sys
import wave
import time
import numpy as np
from datetime import datetime as dt
import cv2
import psutil
import configedit as ce


def RGBA2rgbarray(RGBAcolor):
    RGBAcolor = list(RGBAcolor) + [1]
    rgbarray = [int(RGBAcolor[a] * RGBAcolor[3] * 255) for a in range(3)]
    return rgbarray

def FFmpegcheck():
    FFmpegError = False
    FFmpegcomst = sp.run("ffmpeg -h",shell=True,stderr=sp.DEVNULL, stdout=sp.DEVNULL).returncode
    if FFmpegcomst == 127:
        print("This python script requires ffmpeg to be installed.")
        print('If ffmpeg is installed, please check the "ffmpeg -h" command to see if it works correctly in your environment.')
        FFmpegError = True
    elif FFmpegcomst == 126:
        print("This python script could NOT run ffmpeg because of permisson problem.")
        FFmpegError = True
    elif FFmpegcomst != 0:
        print(f"ffmpeg could NOT run (status code:{FFmpegcomst}).")
        print('please check the "ffmpeg -h" command to see if it works correctly in your environment.')
        FFmpegError = True
    if FFmpegError:
        if True in ["-f" in sys.argv,"--f" in sys.argv]:
            return False
        else:
            print('If you want to run this python script, add the "-f" or "--f" option.')
            exit(3)
    else:
        return True

FC = FFmpegcheck()

class wavereader():
    now = dt.now().isoformat("-")
    initID = int(now.translate(now.maketrans("","","-:.")))
    rundir = os.getcwd()
    def __init__(self, filepath : os.PathLike, processID : int=initID, convert : bool=True) -> None:
        self.CASHDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),f"audiocash_{processID}")
        os.mkdir(self.CASHDIR)
        self.ORfilepath = filepath
        ORfileext = os.path.splitext(self.ORfilepath)[1][1:].lower()
        self.LWfilename = f"input_{processID}.wav"
        self.LWfilepath = os.path.join(self.CASHDIR,self.LWfilename)
        if FC and convert:
            CPfilename = f"cp_{processID}.{ORfileext}"
            CPfilepath = os.path.join(self.CASHDIR,CPfilename)
            shutil.copy(self.ORfilepath,CPfilepath)
            cmd0 = 'ffmpeg -i ' + CPfilename + " -c:a pcm_s16le -loglevel 24 " + self.LWfilename
            message = f"Converting {os.path.basename(self.ORfilepath)}"
            print(message,end="")
            sp.run(cmd0,check=True,cwd=self.CASHDIR)
            while not(os.access(CPfilepath,os.W_OK)):
                time.sleep(0.1)
            os.remove(CPfilepath)
            print("\b" * len(message) + " " * len(message),"\r",end="")
        else:
            shutil.copy(self.ORfilepath,self.LWfilepath)
        with wave.open(self.LWfilepath,"r") as wr:
            self.channelnum = wr.getnchannels()
            self.sampfreq = wr.getframerate()
            self.sampnum = wr.getnframes()
            wavedata = wr.readframes(self.sampnum)
        self.wavearrays : np.ndarray= np.frombuffer(wavedata,dtype=np.int16).reshape((self.sampnum,self.channelnum)).T
        os.remove(self.LWfilepath)
        while not(os.access(self.CASHDIR,os.W_OK)):
                time.sleep(0.1)
        os.rmdir(self.CASHDIR)
        return None

    def getwave_single(self,channel : int = 0) -> np.ndarray:
        return self.wavearrays[channel]

    def getwave_mixed(self,targetchannels : np.ndarray = "all") -> np.ndarray:
        if targetchannels == "all":
            targetchannels = np.arange(self.channelnum)
        return self.wavearrays[targetchannels].mean(0)
    
    def getwave_multi(self,targetchannels : np.ndarray = "all") -> np.ndarray:
        if targetchannels == "all":
            targetchannels = np.arange(self.channelnum)
        return self.wavearrays[targetchannels]


class arraydeal():
    def __init__(self,waveobj : wavereader, channels : np.ndarray = "all") -> None:
        self.wavearray = waveobj.getwave_mixed(channels)
        diffarray = np.hstack((1,np.diff(self.wavearray)))
        #centeredarray = self.wavearray - (max(self.wavearray) - min(self.wavearray)) / 2
        self.triggerpoints : np.ndarray = np.where(((self.wavearray[:-1] * self.wavearray[1:]) <= 0) * (self.wavearray[:-1] <= 0))[0]
        self.triggerpoints2 :np.ndarray = np.where(diffarray == 0)[0]
        if not(self.triggerpoints.size):
            self.triggerpoints = self.triggerpoints2
        self.sampfreq = waveobj.sampfreq
        
    def pickarray_cand(self,centerind : int,pickrange : int):
        startind = max(0,centerind - pickrange // 2)
        endind = min(len(self.wavearray),startind + pickrange)
        actrange = endind - startind
        temparray = self.wavearray[startind:endind]
        if actrange < pickrange:
            temparray = np.hstack((temparray,np.zeros((pickrange - actrange))))
        return temparray
    
    def pickarray_legacy0(self,time_second : float,pickrange : int,prevarray : np.ndarray = [],searchpoint : int = 6) -> np.ndarray:
        if len(prevarray) == 0:
            prevarray = np.zeros(pickrange,np.float16)
        time_sample = int(time_second * self.sampfreq)
        if bool(self.triggerpoints.any()):
            trgind_start = max(np.searchsorted(self.triggerpoints,time_sample) - searchpoint // 2,0)
            trgind_end = min(len(self.triggerpoints),trgind_start + searchpoint)
            candarrays = np.array([self.pickarray_cand(self.triggerpoints[trgind],pickrange) for trgind in range(trgind_start,trgind_end)])
            diffs : np.ndarray = ((candarrays - prevarray) ** 2).mean(1)
            if not(False in (prevarray == np.zeros(pickrange))):
                outarray = candarrays[diffs.argmax()]
                selectedtrg = self.triggerpoints[range(trgind_start,trgind_end)[diffs.argmax()]]
            else:
                outarray = candarrays[diffs.argmin()]
                selectedtrg = self.triggerpoints[range(trgind_start,trgind_end)[diffs.argmin()]]
            if abs(time_sample - selectedtrg) <= 0.1:
                return outarray
            else:
                pass
        else:
            pass
        trgind_start = max(np.searchsorted(self.triggerpoints2,time_sample) - searchpoint // 2,0)
        trgind_end = min(len(self.triggerpoints2),trgind_start + searchpoint)
        candarrays = np.array([self.pickarray_cand(self.triggerpoints2[trgind],pickrange) for trgind in range(trgind_start,trgind_end)])
        diffs : np.ndarray = ((candarrays - prevarray) ** 2).mean(1)
        if not(False in (prevarray == np.zeros(pickrange))):
            outarray = candarrays[diffs.argmax()]
        else:
            outarray = candarrays[diffs.argmin()]
        return outarray
    
    def pickarray(self,time_second : float,pickrange : int,prevarray : np.ndarray = [],searchpoint : int = 6) -> np.ndarray:
        if len(prevarray) == 0:
            prevarray = np.zeros(pickrange,np.float16)
        time_sample = int(time_second * self.sampfreq)
        trgind_start = max(np.searchsorted(self.triggerpoints,time_sample) - searchpoint // 2,0)
        trgind_end = min(len(self.triggerpoints),trgind_start + searchpoint)
        trgcands = list(filter(lambda trgp:abs(time_sample - trgp) <= 0.05 * self.sampfreq,[self.triggerpoints[trgind] for trgind in range(trgind_start,trgind_end)]))
        if len(trgcands) > 0:
            candarrays = np.array([self.pickarray_cand(trgp,pickrange) for trgp in trgcands])
        else:
            #trgind_start = max(np.searchsorted(self.triggerpoints2,time_sample) - searchpoint // 2,0)
            #trgind_end = min(len(self.triggerpoints2),trgind_start + searchpoint)
            #candarrays = np.array([self.pickarray_cand(self.triggerpoints2[trgind],pickrange) for trgind in range(trgind_start,trgind_end)])
            candarrays = np.array([self.pickarray_cand(centerpoint,pickrange) for centerpoint in range(max(0,time_sample - pickrange // 2),min(len(self.wavearray),time_sample + pickrange // 2))])
        diffs : np.ndarray = ((candarrays - prevarray) ** 2).mean(1)
        if not(False in (prevarray == np.zeros(pickrange))):
            outarray = candarrays[diffs.argmax()]
        else:
            outarray = candarrays[diffs.argmin()]
        return outarray


class movieconfig():
    def __init__(self,filename_or_dict : dict=None) -> None:
        if type(filename_or_dict) == dict:
            self.configdict = filename_or_dict
            self.configfile = None
        elif type(filename_or_dict) == str:
            if os.path.isabs(filename_or_dict):
                self.configfile = filename_or_dict
            else:
                self.configfile = os.path.join(ce.configfiledirectory,filename_or_dict)
            if os.path.isfile(self.configfile):
                self.configdict = ce.readconfigfile(os.path.basename(self.configfile))
        else:
            self.configdict = ce.DefaultConfig
            self.configfile = None
    def changeconfig(self) -> dict:
        self.configdict = ce.configdataedit(self.configdict)
        return self.configdict
    def __call__(self) -> dict:
        return self.configdict


class wave2movie():
    now = dt.now().isoformat("-")
    initID = int(now.translate(now.maketrans("","","-:.")))
    rundir = os.getcwd()
    def __init__(self, plotaudiopaths : list, configure : movieconfig, savemoviepath : os.PathLike, plotchannels : list = None) -> None:
        self.configdict = configure()
        self.pltwvnum = len(plotaudiopaths)
        if plotchannels == None:
            plotchannels = ["all"] * self.pltwvnum
        WRIDs = self.initID * (10 ** (np.floor(np.log10(self.pltwvnum)).astype(int) + 1)) + np.arange(self.pltwvnum)
        self.wavecol = self.configdict["column"]
        self.waverow = np.ceil(self.pltwvnum / self.wavecol).astype(int)
        self.imgW = self.configdict["framewidth"]
        self.imgH = self.configdict["frameheight"]
        self.smprange = self.configdict["smprange"]
        self.backcolor = RGBA2rgbarray(self.configdict["backcolor"])
        self.linecolor = RGBA2rgbarray(self.configdict["linecolor"])
        self.linewidth = max(1,int(self.configdict["linebold"]))
        self.sourcewaves = list(map(lambda file,ID:wavereader(file,ID),plotaudiopaths,WRIDs))
        self.sourcearrays = list(map(lambda wr,rc:arraydeal(wr,rc),self.sourcewaves,plotchannels))
        self.savemoviepath = savemoviepath
        self.savedir = os.path.dirname(savemoviepath)
        self.savemoviename = os.path.basename(savemoviepath)
        self.scratchdir = os.path.join(self.savedir,f"sct_{self.initID}")
        os.mkdir(self.scratchdir)
        self.movielen_sec :float = max(map(lambda wr:wr.sampnum/wr.sampfreq,self.sourcewaves))
        self.totalframe :int = np.ceil(self.movielen_sec * self.configdict["fps"]).astype(int)
    
    def savepng(self,target_sec:float,filename:str,prevarrays:list):
        arraylist = []
        outmat = np.full((self.imgH,self.imgW,3),RGBA2rgbarray(self.backcolor[::-1]))
        for arind,arobj in enumerate(self.sourcearrays):
            row = arind // self.wavecol
            col = arind % self.wavecol
            pltar = arobj.pickarray(target_sec,self.smprange,prevarrays[arind])
            arraylist.append(pltar.copy())
            plot_y = self.imgH * pltar / (- self.waverow * 2 ** 16) + self.imgH * (row + 0.5) / self.waverow
            plot_x = np.linspace(self.imgW * col,self.imgW * (col + 1),self.smprange)
            pltcrd = np.vstack((plot_x,plot_y)).T.astype(int).reshape(self.smprange,1,2)
            cv2.polylines(outmat,[pltcrd],False,self.linecolor[::-1],thickness=self.linewidth)
        cv2.imwrite(os.path.join(self.scratchdir,filename),outmat)
        print(f"Exported:{filename}","\r",end="")
        return arraylist
    
    def savePlotCrd(self,target_sec:float,filename:str,prevarrays:list):
        arraylist = []
        pltcrds = []
        for arind,arobj in enumerate(self.sourcearrays):
            row = arind // self.wavecol
            col = arind % self.wavecol
            pltar = arobj.pickarray(target_sec,self.smprange,prevarrays[arind])
            arraylist.append(pltar.copy())
            plot_y = self.imgH * pltar / (- self.waverow * 2 ** 16) + self.imgH * (row + 0.5) / self.waverow
            plot_x = np.linspace(self.imgW * col / self.wavecol,self.imgW * (col + 1) / self.wavecol,self.smprange)
            pltcrd = np.vstack((plot_x,plot_y)).T.astype(int).reshape(self.smprange,1,2)
            pltcrds.append(pltcrd)
        np.save(os.path.join(self.scratchdir,filename),pltcrds)
        #print(f"Exported:{filename}","\r",end="")
        return arraylist
    
    def savemovie_singlethread(self,masteraudiopath : os.PathLike=""):
        filename = self.savemoviename
        frame_per_section = 300
        frame_inddig = np.floor(np.log10(self.pltwvnum)).astype(int) + 1
        framecount = 0
        sectionind = 0
        prevarraylist = [[] for _ in range(self.pltwvnum)]
        partmovielist = []
        temp_pnglist = []
        fps = self.configdict["fps"]
        moviebitrate = self.configdict["moviebitrate"]
        vcodec = self.configdict["moviecodec"]
        for frameind in range(self.totalframe):
            pngname_base = f"section_{sectionind}_%0{frame_inddig}d.png"
            pngfilename = pngname_base % framecount
            prevarraylist = self.savepng(frameind / fps,pngfilename,prevarraylist)
            temp_pnglist.append(pngfilename)
            framecount += 1
            prclist = []
            if (framecount == frame_per_section) or (frameind == self.totalframe - 1):
                partmoviename = f"section_{sectionind}.mp4"
                com1 = f"ffmpeg -framerate {fps} -i {pngname_base} -vcodec {vcodec} -pix_fmt yuv420p -r {fps} -b:v {moviebitrate}k -loglevel warning {partmoviename}"
                prclist.append(sp.Popen(com1,cwd=self.scratchdir))
                partmovielist.append(partmoviename)
                framecount = 0
                sectionind += 1
        partmovietxt = "file '" + "'\nfile '".join(partmovielist) + "'\n"
        txtname = "partmovie.in"
        txtpath = os.path.join(self.scratchdir,txtname)
        with open(txtpath,'w',encoding='utf-8',newline='\n') as tfw:
            tfw.write(partmovietxt)
        for prc in prclist:
            prc : sp.Popen
            print(f"Waiting ffmpeg processing (pid : {prc.pid})\r",end="")
            prc.wait()
        os.chdir(self.scratchdir)
        print(" " * len(f"Waiting ffmpeg processing (pid : {prc.pid})"),"\r",end="")
        for pngfilename in temp_pnglist:
            try:
                os.remove(pngfilename)
                pass
            except:
                print(f"{os.path.abspath(pngfilename)} could NOT be removed.")
        mergedname0 = "merged0.mp4"
        mergedname1 = "merged1.mp4"
        com2 = f'ffmpeg -safe 0 -f concat -i {txtname} -c:v copy -c:a copy -loglevel warning {mergedname0}'
        sp.run(com2)
        if os.path.isfile(masteraudiopath):
            os.rename(mergedname0,mergedname1)
            print("Inserting masteraudio")
            tempaudioname = "masteraudio" + os.path.splitext(masteraudiopath)[1]
            shutil.copy(masteraudiopath,os.path.join(self.scratchdir,tempaudioname))
            com3 = f"ffmpeg -i {mergedname1} -i {tempaudioname} -c:v copy -c:a aac -ab 384k -map 0:v:0 -map 1:a:0 -loglevel 24 {mergedname0}"
            sp.run(com3)
            if os.path.isfile(mergedname0):
                os.remove(mergedname1)
                os.remove(txtpath)
        shutil.move(mergedname0,os.path.join(self.savedir,filename))
        os.chdir(self.rundir)
        shutil.rmtree(self.scratchdir)
    
    def savemovie_multithread(self,masteraudiopath : os.PathLike="",thread :int=2):
        filename = self.savemoviename
        frame_per_section = 1200#np.ceil(self.totalframe / thread).astype(int)
        frame_inddig = np.floor(np.log10(frame_per_section)).astype(int) + 1
        sectiondig = np.floor(np.log10(self.totalframe / frame_per_section)).astype(int) + 1
        framecount = 0
        sectionind = 0
        prevarraylist = [[] for _ in range(self.pltwvnum)]
        partmovielist = []
        temp_pnglist = []
        fps = self.configdict["fps"]
        moviebitrate = self.configdict["moviebitrate"]
        vcodec = self.configdict["moviecodec"]
        tempconfigfile = f"{self.initID}_config.json"
        ce.ConfigExport2Json(self.configdict,tempconfigfile,owconf=False)
        prclist = []
        scrdirtxt = f"scrdir_{self.initID}.txt"
        with open(scrdirtxt,"w",encoding='utf-8',newline='\n') as stw:
            stw.write(self.scratchdir)
        coms = f"python3 getprcstatus.py -d {scrdirtxt} -f {self.totalframe} -s {frame_per_section}"
        sp.Popen(coms)
        for frameind in range(self.totalframe):
            sectionind_str = f"%0{sectiondig}d" % sectionind
            npzname_base = f"section_{sectionind_str}_%0{frame_inddig}d.npy"
            npzfilename = npzname_base % framecount
            prevarraylist = self.savePlotCrd(frameind / fps,npzfilename,prevarraylist)
            temp_pnglist.append(npzfilename)
            framecount += 1
            
            if (framecount == frame_per_section) or (frameind == self.totalframe - 1):
                partmoviename = f"section_{sectionind}.mp4"
                com1 = f"python3 npCrd2png.py -b {npzname_base} -c {tempconfigfile} -d {scrdirtxt} -e {partmoviename}"
                if sectionind >= thread:
                    com1 += f" -f section_{sectionind - thread}.txt"
                loop0 = True
                while loop0:
                    mem = psutil.virtual_memory()
                    if mem.available > 10 * (1024 ** 3) and mem.percent < 75:
                        loop0 = False
                    else:
                        time.sleep(1)
                prclist.append(sp.Popen(com1))
                partmovielist.append(partmoviename)
                framecount = 0
                sectionind += 1
        partmovietxt = "file '" + "'\nfile '".join(partmovielist) + "'\n"
        txtname = "partmovie.in"
        txtpath = os.path.join(self.scratchdir,txtname)
        with open(txtpath,'w',encoding='utf-8',newline='\n') as tfw:
            tfw.write(partmovietxt)
        for prc in prclist:
            prc : sp.Popen
            print(f"Waiting python processing (pid : {prc.pid})\r",end="")
            prc.wait()
        os.chdir(self.scratchdir)
        print(" " * len(f"Waiting python processing (pid : {prc.pid})"),"\r",end="")
        os.remove(os.path.join(ce.configfiledirectory,tempconfigfile))
        os.remove(os.path.join(self.rundir,scrdirtxt))
        mergedname0 = "merged0.mp4"
        mergedname1 = "merged1.mp4"
        com2 = f'ffmpeg -safe 0 -f concat -i {txtname} -c:v copy -c:a copy -loglevel warning {mergedname0}'
        #com2 = f'ffmpeg -safe 0 -f concat -i {txtname} -pass 1 -vcodec {vcodec} -pix_fmt yuv420p -r {fps} -b:v {moviebitrate}k -c:a copy -loglevel warning {mergedname0} -y'
        #com2_2 = f'ffmpeg -safe 0 -f concat -i {txtname} -pass 2 -vcodec {vcodec} -pix_fmt yuv420p -r {fps} -b:v {moviebitrate}k -c:a copy -loglevel warning {mergedname0} -y'
        sp.run(com2)
        #sp.run(com2_2)
        if os.path.isfile(masteraudiopath):
            os.rename(mergedname0,mergedname1)
            print("Inserting masteraudio")
            tempaudioname = "masteraudio" + os.path.splitext(masteraudiopath)[1]
            shutil.copy(masteraudiopath,os.path.join(self.scratchdir,tempaudioname))
            com3 = f"ffmpeg -i {mergedname1} -i {tempaudioname} -c:v copy -c:a aac -ab 384k -map 0:v:0 -map 1:a:0 -loglevel 24 {mergedname0}"
            sp.run(com3)
            if os.path.isfile(mergedname0):
                os.remove(mergedname1)
                os.remove(txtpath)
        shutil.move(mergedname0,os.path.join(self.savedir,filename))
        os.chdir(self.rundir)
        shutil.rmtree(self.scratchdir)


