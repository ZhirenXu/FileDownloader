from multiprocessing import Pool
from bs4 import BeautifulSoup
from requests import Session
from Function import Login
import requests
import urllib.request
import concurrent.futures
import sys
import gc
import os
import traceback

downloadSession = requests.session()

def loadUrlSession(session, url):
    html = session.get(url)
    return html

## Download file from each urlLink and save it in its record's folder
# @param session
#        Session contain login cookie for download private files
# @param urlList
#        A list contain recods' that need to download files
def downloadAndSave(session, urlList):
    listOfFile = []
    titleLinkList = []
    fileTitle = ""
    # iterator to show program progress
    i = 1

    numOfUrl = len(urlList)
    print("There are ", numOfUrl, " records in the input file.\n")
    print("Proceeding......\n")
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(loadUrlSession, session, url): url for url in urlList}
        for future in concurrent.futures.as_completed(future_to_url):
            print("Processing ",i, " / ", numOfUrl, "records.")
            url = future_to_url[future]
            print("Current URL: ", url)
            try:
                html = future.result()
            except Exception as exc:
                print(str(exc))
                httpNoResponse(url)
                break
            if (html.status_code != 404):
                soup = BeautifulSoup(html.text, 'html.parser')
                recordOfTitle = findRecordTitle(soup)
                try:
                    os.mkdir(recordOfTitle)
                except Exception as exc:
                    print(str(exc))
                    createFolderError(recordOfTitle, url)
                listOfFile = findDownloadLink(soup)
                if len(listOfFile) > 0:
                    for fileDownloadLink in listOfFile:
                        titleLinkList.append([recordOfTitle, fileDownloadLink])
                #desired data form: [[folder name, downloadLink1], [folder name, downloadLink2]]
                try:
                    nextPageSoup = findNextPage(soup, session)
                    while nextPageSoup != None:
                        listOfFile = findDownloadLink(nextPageSoup)
                        for fileDownloadLink in listOfFile:
                            titleLinkList.append([recordOfTitle, fileDownloadLink])
                        nextPageSoup = findNextPage(nextPageSoup, session)
                except Exception as exc:
                    print(str(exc))
                    findNextPageErr()
            else:
                print("\nCan't open url: 404 page not found. null will be used as filled value")
                print("url: ", url, "\n")
            print("All pages processed. No more next page.")
            print("Successfully download files from ", i, " / ", numOfUrl, "records.\n")
            urlList.remove(url)
            i = i + 1
    session.close()
    gc.collect()
    with Pool(4) as p:
        print("\nStart downloading all files, please wait......")
        print("As long as network usage is high the scripting is running.\n")
        p.map(downloadFile, titleLinkList)

def findRecordTitle(parsedHtml):
    title = "null"
    # delete front/back whitespace and add to valueList
    tag = parsedHtml.find("div", "col-sm-8")
    try:
        h2 = tag.contents[1]
        #h2 is a list, format as: ['\\n', <h2>The Lantern, Ja...span></small>\n</h2>, '\\n']
        value = h2.contents[0].string
        title = sanitizeValue(value)        
    except Exception as exc:
        print(str(exc))
        print("Fail to get record title!")
    if title == "null":
        print("Null title, value = ", value, "\n")

    return title

def sanitizeValue(recordTitle):
    title = ""
    illegalChar = ['\n', '\t', '\\', '/', '|', '"', ':','<', '>', '*', '?', "LPT", "COM", ".."]
    
    if len(recordTitle) > 255:
        recordTitle = recordTitle[:255]
    for char in recordTitle:
        if not char in illegalChar:
            title += char
            
    return title

def createFolderError(recordOfTitle, url):
    print("Folder already exist or couldn't build a folder")
    print("Folder Title: ", recordOfTitle)
    with open("create folder error log.txt", 'a') as errLog:
        errLog.write("Folder already exist or couldn't build a folder\n")
        errLog.write("Folder(record) Title: "+recordOfTitle+"\n")
        errLog.write("FileLink: "+url+"\n")
        errLog.write("\n")
        
def httpNoResponse(url):
    print("No response from this url!")
    print("url: ", url)

def findNextPageErr():
    print("\nError happened when finding next page.")
    print("If this kind of error keep happening, save the error message and send to author.")
    print("Press enter to exit. ", end = '')
    input()
    sys.exit()

def saveFileError(title, fileSavePath):
    print("Fail to save file for: ", title)
    print("Fail to enter folder: ", fileSavePath, "\n")
    with open("move file error log.txt", 'a') as errLog:
        errLog.write("Fail to move file into folder: "+fileSavePath+"\n")

def downloadFileError(fileName, title, rootPath):
    currentPath = os.getcwd()
    os.chdir(rootPath)
    print("\nEncounter error when downloading: ", fileName)
    with open("error log.txt", 'a') as errLog:
        errLog.write("Encounter error when downloading: "+fileName+"\n")
        errLog.write("File belongs to record: "+title+"\n")
        errLog.write("\n")
    os.chdir(currentPath)
    
## call functions to download each related file
# @param    session
#           login cookie to access private file record
# @param    fileUrl
#           url for related files
def downloadFile(titleLinkList):
    hasChangePath = False
    rootPath = os.getcwd()
    title = titleLinkList[0]
    fileSavePath = rootPath + "\\" + title

    try:
        os.chdir(fileSavePath)
        hasChangePath = True
    except:
        try:
            os.mkdir(title)
            os.chdir(fileSavePath)
            hasChangePath = True
        except Exception as exc:
            print(str(exc))
            saveFileError(title, fileSavePath)
    try:
        fileRequest = downloadSession.get(titleLinkList[1])
        contentDisposition = fileRequest.headers["Content-Disposition"]
        contentDispositionLength = len(contentDisposition)
        fileNameIndex = contentDisposition.index("filename")
        fileName = contentDisposition[fileNameIndex+10 : contentDispositionLength-1]
        with open(fileName, 'wb') as outFile:
            outFile.write(fileRequest.content)
        print(fileName, " has been successfully downloaded.\n")
    except Exception as exc:
        print(str(exc))
        downloadFileError(fileName, title, rootPath)
    if hasChangePath:
        os.chdir(rootPath)
    
    
## find url that related to file download
# @param    source
#           parsed html of master file(or previous page if there is multiple nextpage)
# @return   fileUrlList
#           a list of related file url
#           Otherwise, return None
def findDownloadLink(source):
    fileUrlList = []
    hrefList = []
    urlPrefix = "https://library.osu.edu"
    
    result = source.find_all('a', attrs={'id': 'file_download'})
    for a in result:
        url = a['href']
        hrefList.append(url)
    if (hrefList != []):
        for href in hrefList:
            fileUrl = urlPrefix + href
            fileUrlList.append(fileUrl)
        print("File download link has been found, processing...")
        return fileUrlList
    else:
        print("File download link not found!")
        return None

## if items are more than 9, it will continue in next page.
## find the next page and return the parsed html of next page
# @param    source
#           parsed html of master file(or previous page if there is multiple nextpage)
# @param    session
#           A web cookie object which include login info in order to get private record.
# @return   nextPageSoup
#           if there is a next page, return a parsed html of next page
#           Otherwise, return None
def findNextPage(source, session):
    nextPage = ""
    urlPrefix = "https://library.osu.edu/"
    result = source.find_all('a', attrs={'rel': 'next'})
    if (result != None and len(result) > 1):
        nextPage = urlPrefix + result[0]['href']
        print("Next page of files is found, processing...")
        html = loadUrlSession(session, nextPage)
        nextPageSoup = BeautifulSoup(html.text, 'html.parser')
        return nextPageSoup
    else:
        return None

## Split a biglist into several small group for better memory management
# @param    urlList
#           the list wait to be splited
# @param    urlGroup
#           a list of list contain url, each small list have 100 url
# @return   totalGroupNum
def splitList(urlList, urlGroup):
    i = 0
    j = 0
    newList = []
    totalLength = len(urlList)
    
    for url in urlList:
        newList.append(url)
        i = i + 1
        j = j + 1
        if i == 100:
            urlGroup.append(newList)
            i = 0
            newList = []
        if ((j == totalLength) and (len(newList) > 0)):
            urlGroup.append(newList)
    totalGroupNum = len(urlGroup)
    print("Total group of url: ", totalGroupNum)

    return totalGroupNum

def cleanUp(groupNum, loginSession):
    print("\nOne group of works is scanned. Cleaning memory and reauthorizing now.")
    try:
        loginSession.close()
        gc.collect()
        newLoginSession = Login.reAuth()
    except Exception as exc:
        print("\nError: ", str(exc), "\n")
        print("Press enter to exit")
        input()
    print("Done")
    downloadSession.close()
    
    return newLoginSession

def buildDownloadFolder():
    try:
        os.mkdir("Download")
    except Exception as exc:
        print("\n Error: ", exc, "\n")
    os.chdir(os.getcwd() + "\\" + "Download")
