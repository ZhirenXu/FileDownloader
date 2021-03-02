import requests
import progressbar

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
