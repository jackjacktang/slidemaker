<<<<<<< HEAD
<!--
 Copyright (c) 2018, TRIDENT Pipeline and Reporting Tool, Sydney Neuroimaging 
 Analysis Centre, AU, All rights reserved.
 -->

# Slide Maker Helper

TRIDENT Pipeline and Reporting Tool is a set of Python3 based user interface tool for project TRIDENT.



### 1. Build the execuatbles

Note: pandas/scipy/skimage package has compatible issue with pyinstaller, you need to hidden-import one of the libraries by creating a 'hooks' folder at the same level of the main python function (trident.py), then create a python file named "hook-pandas.py" inside this folder with the following line:
```
hiddenimports = ['pandas._libs.tslibs.timedeltas', 'scipy._lib.messagestream','sklearn.neighbors.typedefs']
```

Similar process should be applied if you want to package the python reporting tool (the hooks folder under the same level of trident_reporting.py), modify the hiddenimports to be
```
hiddenimports = ['pandas._libs.tslibs.timedeltas']
```
Go to the Trident directory in the Scipt folder under TRIDENT on QNAP,
alternatively, you can download the source file from github:
```
$ git clone https://github.com/jacksnac/Trident.git
```
or go to https://github.com/jacksnac/Trident.git and download the zip file

```
$ cd Trident(either on server or downloaded)
```

To package the Pipeline Tool into a standalone executable:
```
$ pyinstaller trident.py --icon=trident.ico --additional-hooks-dir=hooks --onefile --console

```
To package the Reporting Tool into a standalone executable:
```
$ cd Trident(either on server or downloaded)/reporting
$ pyinstaller trident_reporting.py --icon=trident.ico --additional-hooks-dir=hooks --onefile --console

```
This will generate a single executable together with a terminal window open each time starts the software, you can find this executable in the dist folder under the same directory
=======
# slidemaker
>>>>>>> cc5f65e4d2e302d7ca6d7852ade2caa9cbbc72d4
