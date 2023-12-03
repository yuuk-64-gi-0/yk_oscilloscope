import time
import platform
import os
import filemng as fm
import ykosc


if __name__ == "__main__":
    MachineOS = platform.system()
    print("Please select audiofiles to plot.")
    testfiles = fm.Multifileselect(["wav","mp3","ogg"])
    print("Please select audiofiles to insert as master_audio.")
    masteraudiopath = fm.fileselect(["wav","mp3","ogg"],os.path.dirname(testfiles[0]))
    print("Please select save_directory and file_name.")
    savemoviepath = fm.filesave("mp4",os.path.dirname(masteraudiopath),os.path.splitext(os.path.basename(masteraudiopath))[0] + ".mp4")
    configfiles = list(filter(lambda file:file.endswith(".json"),os.listdir(ykosc.ce.configfiledirectory)))
    mcon = ykosc.movieconfig(configfiles[int(input("\n".join([f"[{ind}]:{file}" for ind,file in enumerate(configfiles)])+"\n > "))])
    ykosc.ce.showconfigdata(mcon())
    if input("Edit config? if yes, input 'Y' or 'y' > ") in ['Y','y']:
        mcon.changeconfig()
    T0 = time.time()
    w2m = ykosc.wave2movie(testfiles,mcon,savemoviepath)
    w2m.savemovie_multithread(masteraudiopath)
    T1 = time.time()
    print("\n\n",T1-T0,"s")
    if MachineOS == "Windows":
        print(savemoviepath.replace("/","\\"))
        
