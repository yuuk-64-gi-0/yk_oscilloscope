import sys
import os
import time
import glob

pickarg = lambda optch: sys.argv[sys.argv.index(optch) + 1]

scrdirtxt :os.PathLike= pickarg("-d")
totalframe :int= int(pickarg("-f"))
sectionframe :int= int(pickarg("-s"))

with open(scrdirtxt,"r",encoding='utf-8',newline='\n') as str:
    scrdir = str.read()


while os.path.isdir(scrdir):
    #MTfiles = os.listdir(scrdir)
    MTfiles = glob.glob(scrdir+"/**",recursive=True)
    npynum = len(list(filter(lambda file:file.endswith(".npy"),MTfiles)))
    pngnum = len(list(filter(lambda file:file.endswith(".png"),MTfiles)))
    mp4num = len(list(filter(lambda file:file.endswith(".mp4"),MTfiles)))
    txtlist= list(filter(lambda file:file.endswith(".txt"),MTfiles))
    txtnum = len(txtlist)
    prcrate = ((npynum + 2 * pngnum + 3 * sectionframe * txtnum)) / (3 * totalframe)
    prcpercent = ("%.1f" % (min(1,prcrate) * 100)).rjust(5) + " %"
    prcmessage = f"process:{prcpercent} (npyfile:{npynum}, pngfile:{pngnum}, encodedmovie:{txtnum})"
    if mp4num - txtnum > 0:
        prcmessage += f" {mp4num - txtnum} mp4 files encoding"
    print(prcmessage,"\r",end="")
    time.sleep(1)
