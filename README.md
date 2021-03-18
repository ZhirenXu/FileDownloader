# File Downloader

### Prerequisite  
	All outside package requirents are in dependencies.txt  
	An easy way to make sure are packages are ready:
		-open CMD  
		-type "cd Desktop" (" not included)  
		-type "pip install -r dependencies.txt" (" not included)  
		-wait for pip finish its job and close CMD  
	After that, make sure you have a CSV file contains internal url links to each record which has files you want to download. All internal url links shall be put in first colomn, start from second row. The first row can be the name of colomn.

### How to Use
	Double click "FileDownloader.py". 
		- If it's not working, you need to open cmd, copy FileDownloader folder path via file explorer and type "cd [your folder path]" in cmd. After that, type "FileDownloader.py" and hit enter.
	Follow the instruction.

### Expect Behavior:
	After tying in login credential and input csv file name, the program will create a folder called "Download". Inside this folder are folders named by record names. Insides these folders are related files download from each record.
	Also in download folder are error log files. Usually you will find "create folder error log.txt". When there is attempt to create duplicate folder or fail to create folder, it will be logged in this file. In rare case, if files failed to download, there will be "download error log.txt". If files not belong to any of these folders, there will be "move file error log.txt". You can correct files by using these logs.

### Tips:
	Recommand to use in remote control dektops for faster download speed.
