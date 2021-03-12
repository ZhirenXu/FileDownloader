import requests
import progressbar
from Function import Login
from Function import SimpleCSV
from Function import Greeting
from Function import Run
from Function import Test

def main():
    urlGroup = []
    
    Greeting.showInfo()
    loginCredit = Login.login()
    inputCSV = SimpleCSV.getCSVInput()
    internalUrlList = SimpleCSV.readCSV(inputCSV)
    totalGroupNum = Run.splitList(internalUrlList, urlGroup)
    for listOfUrl in urlGroup:
        #Run.downloadAndSave(loginCredit, listOfUrl)
        Test.downloadAndSave(loginCredit, listOfUrl)    
        if totalGroupNum > 1:
            print("\nOne group of works is scanned. Cleaning memory and reauthorizing now.")
            logSession.close()
            gc.collect()
            logSession = Login.reAuth()
            print("Done")
            urlGroup = urlGroup - 1
            print("Remain group number: ", len(urlGroup))
            
    Greeting.sysExit()

if __name__ == "__main__":
    main()
