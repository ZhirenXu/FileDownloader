import requests
import progressbar
from Function import Login
from Functiom import SimpleCSV
from Function import Greeting
from Function import Run

url = 'https://library.osu.edu/dc/downloads/hh63sw64g?locale=en'
k = 0

s = requests.session()
file = s.get(url)

fileSize = file.headers["Content-Length"]
contentDisposition = file.headers["Content-Disposition"]
contentDispositionLength = len(contentDisposition)
fileNameIndex = contentDisposition.index("filename")
fileName = contentDisposition[fileNameIndex+10 : contentDispositionLength-1]
print(fileName)

with open(fileName, 'wb') as outFile:
    #for k in progressbar.progressbar(range(int(fileSize)), redirect_stdout=True):
    outFile.write(file.content)
       # k = k+1
#open('testfile2', 'wb').write(myfile.content)
input()

def main():
    urlGroup = []
    
    Greeting.showInfo()
    loginCredit = Login.login()
    inputCSV = SimpleCSV.getCSVInput()
    internalUrlList = SimpleCSV.readCSV(inputCSV)
    totalGroupNum = Run.splitList(internalUrlList, urlGroup)
    for listOfUrl in urlGroup:
        Run.downloadAndSave(loginCredit, internalUrlList)
        if totalGroupNum > 1:
            print("\nOne group of works is scanned. Cleaning memory and reauthorizing now.")
            logSession.close()
            gc.collect()
            logSession = Login.reAuth()
            print("Done")
            urlGroup = urlGroup - 1
            print("Remain group number: ", len(urlGroup))
            
    Greeting.sysExit()
    
