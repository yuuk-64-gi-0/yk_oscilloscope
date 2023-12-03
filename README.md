# yk_oscilloscope
## Abstract
This python program files make oscilloscope movie from one or multiple audio file.
[Reference movie for oscilloscope movie](https://youtu.be/N1_gtjSBPDw)

## Requirements (Software)
* ffmpeg (equal or more than version 4.2.3)
* python3 (equial or more than version 3.7)

## Requirements (python libraries)
* numpy>=1.24.0
* opencv-contrib-python>=4.8.0.0
* psutil>=5.8.0

## Usage
1. Move to directory containing these python files.
2. Open cuilch.py with python3
3. Select the audio file you wish to plot as a waveform.<br>You can select multiple audio files, but these audio files should be in the one directory.
4. Select the audio file to insert as audio into the output movie file.
5. Select the destination for the output movie file.
6. Select the profile for movie file setting.
   * If you want to specify the video settings in detail, press "Y" and Enter when you are asked "Edit config? if yes, input 'Y' or 'y' >".
   * If you don't, Just press Enter when you are asked "Edit config? if yes, input 'Y' or 'y' >". The movie generating process will start.
7. Please wait until the elapsed time in seconds and the destination path are displayed on terminal.
8. Check the output movie file.
