import os
try:
    import tkinter, tkinter.filedialog, tkinter.messagebox
    mode = "GUI"
except:
    print("FileManager Launching in CUI mode")
    mode = "CUI"

extlist = [
    ["wav","yaml","mp3","m4a","ogg","aiff"],
    ["wave file","yaml project file","mp3 audio file","m4a audio file","ogg vorbis audio file","Apple PCM audio file"]
]

def ext2Typename(extension):
    Typename = extension + " file"
    if extension in extlist[0]:
        Typename = extlist[0][extlist[0].index(extension)]
    return Typename

def listselect(chosenlist : list):
    showtxt = "\n".join(["[%d] %s" % (ind,str(chosenlist[ind])) for ind in range(len(chosenlist))])
    print(showtxt)
    loop0 = True
    while loop0:
        com = input("index or name > ")
        if com in chosenlist:
            outval = com
            loop0 = False
        elif com in list(map(str,range(len(chosenlist)))):
            outval = chosenlist[int(com)]
            loop0 = False
        else:
            pass
    return outval

# ファイル選択ダイアログの表示
def fileselect(extension = False,defaultDir = False):
    rundir = os.getcwd()
    if mode == "GUI":
        root = tkinter.Tk()
        root.withdraw()
        if extension:
            if type(extension) == list:
                fTyp = []
                for a in range(len(extension)):
                    addextension = extension[a].replace(".","")
                    FTname = ext2Typename(addextension)
                    fTyp += [(FTname,"*." + addextension)]
                fTyp += [("all file","*")]
            else:
                extension = extension.replace(".","")
                FTname = ext2Typename(extension)
                fTyp = [(FTname,"*." + extension),("all file","*")]
        else:
            fTyp = [("all file","*")]
        if defaultDir:
            iDir = os.path.abspath(defaultDir)
        else:
            iDir = os.path.abspath(os.path.dirname(__file__))
        #tkinter.messagebox.showinfo('○×プログラム','処理ファイルを選択してください！')
        file = tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
    else:
        nowdir = os.path.abspath(os.path.dirname(__file__))
        loop0 = True
        while loop0:
            lslist = [".."] + os.listdir(nowdir)
            print("-"*10,"\n",nowdir,"> ls")
            selectval = listselect(lslist)
            if os.path.isfile(selectval):
                file = os.path.join(nowdir,selectval)
                loop0 = False
            elif os.path.isdir(selectval):
                os.chdir(os.path.join(nowdir,selectval))
                nowdir = os.getcwd()
    os.chdir(rundir)
    return file

def folderselect(defaultDir = False):
    rundir = os.getcwd()
    if mode == "GUI":
        root = tkinter.Tk()
        root.withdraw()
        fTyp = [("","*")]
        if defaultDir:
            iDir = os.path.abspath(defaultDir)
        else:
            iDir = os.path.abspath(os.path.dirname(__file__))
        #tkinter.messagebox.showinfo('○×プログラム','処理ファイルを選択してください！')
        folderpath = tkinter.filedialog.askdirectory(initialdir = iDir)
    else:
        nowdir = os.path.abspath(os.path.dirname(__file__))
        os.chdir(nowdir)
        loop0 = True
        while loop0:
            lslist = [".."] + [lsval for lsval in os.listdir() if os.path.isdir(lsval)] + ["select" + nowdir]
            print("-"*10,"\n",nowdir,"> ls")
            selectval = listselect(lslist)
            if selectval == "select" + nowdir:
                folderpath = nowdir
                loop0 = False
            else:
                os.chdir(os.path.join(nowdir,selectval))
                nowdir = os.getcwd()
    os.chdir(rundir)
    return folderpath

def Multifileselect(extension = False,defaultDir = False):
    rundir = os.getcwd()
    if mode == "GUI":
        root = tkinter.Tk()
        root.withdraw()
        if extension:
            if type(extension) == list:
                fTyp = []
                for a in range(len(extension)):
                    addextension = extension[a].replace(".","")
                    FTname = ext2Typename(addextension)
                    fTyp += [(FTname,"*." + addextension)]
                fTyp += [("all file","*")]
            else:
                extension = extension.replace(".","")
                FTname = ext2Typename(extension)
                fTyp = [(FTname,"*." + extension),("all file","*")]
        else:
            fTyp = [("all file","*")]
        if defaultDir:
            iDir = os.path.abspath(defaultDir)
        else:
            iDir = os.path.abspath(os.path.dirname(__file__))
        #tkinter.messagebox.showinfo('○×プログラム','処理ファイルを選択してください！')
        filelist = list(tkinter.filedialog.askopenfilenames(filetypes = fTyp,initialdir = iDir))
    else:
        loop2 = True
        while loop2:
            filelist.append(fileselect(extension,defaultDir))
            if input("finish? (Y or y / any)> ") in ["Y","y"]:
                loop2 = False
    os.chdir(rundir)
    return filelist

def filesave(extension = False,defaultDir = False,defaultfile = ""):
    rundir = os.getcwd()
    if mode == "GUI":
        root = tkinter.Tk()
        root.withdraw()
        if extension:
            if type(extension) == list:
                fTyp = []
                for a in range(len(extension)):
                    addextension = extension[a].replace(".","")
                    FTname = ext2Typename(addextension)
                    fTyp += [(FTname,"*." + addextension)]
                fTyp += [("all file","*")]
            else:
                extension = extension.replace(".","")
                FTname = ext2Typename(extension)
                fTyp = [(FTname,"*." + extension),("all file","*")]
        else:
            fTyp = [("all file","*")]
        if defaultDir:
            iDir = os.path.abspath(defaultDir)
        else:
            iDir = os.path.abspath(os.path.dirname(__file__))
        if defaultfile:
            defaultfile = os.path.basename(defaultfile)
        #tkinter.messagebox.showinfo('○×プログラム','処理ファイルを選択してください！')
        file = tkinter.filedialog.asksaveasfilename(filetypes = fTyp,initialdir = iDir,initialfile = defaultfile)
    else:
        print("select the directory to save at")
        savedir = folderselect(defaultDir)
        print(f"directory:\n{savedir}")
        print(f"input filename (default:{os.path.basename(defaultfile)})")
        filename = input(" > ")
        file = os.path.join(savedir,filename)
    os.chdir(rundir)
    return file


#bibliography = "https://qiita.com/666mikoto/items/1b64aa91dcd45ad91540"