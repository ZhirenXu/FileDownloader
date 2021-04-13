import requests
import gc
import os
import sys
from Function import Login
from Function import SimpleCSV
from Function import Greeting
from Function import Run

def main():
    urlGroup = []
    
    Greeting.showInfo()
    loginCredit = Login.login()
    cookie = loginCredit.get_cookiejar()
    #use the cookie for download session, try using requests instead of mechanicalsoup
    inputCSV = SimpleCSV.getCSVInput()
    internalUrlList = SimpleCSV.readCSV(inputCSV)
    totalGroupNum = Run.splitList(internalUrlList, urlGroup)
    Run.buildDownloadFolder()
    for listOfUrl in urlGroup:
        Run.downloadAndSave(cookie, listOfUrl)    
    Greeting.sysExit()

if __name__ == "__main__":
    main()
