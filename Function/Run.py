from multiprocessing import Pool
from bs4 import BeautifulSoup
from Function import Login
import requests
import urllib.request
import concurrent.futures
import sys
import gc
import os
import traceback

## Send requests to download/get info about file
# @param    cookie
#           cookie jar, include login info
# @param    url
#           the link you want to send request to
# @return   html
#           response object from requests.get()
def loadUrlSession(cookie, url):
    html = requests.get(url, cookies = cookie, timeout = 15)
    return html

## Download file from each urlLink and save it in its record's folder
# @param cookie
#        login cookie for download private files
# @param urlList
#        A list contain recods' that need to download files
def downloadAndSave(cookie, urlList):
    listOfFile = []
    titleLinkList = []
    fileTitle = ""
    # iterator to show program progress
    i = 1
    global session

    numOfUrl = len(urlList)
    print("There are ", numOfUrl, " records in the input file.\n")
    print("Proceeding......\n")
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_url = {executor.submit(loadUrlSession, cookie, url): url for url in urlList}
        for future in concurrent.futures.as_completed(future_to_url):
            print("Processing ",i, " / ", numOfUrl, "records.")
            url = future_to_url[future]
            print("Current URL: ", url)
            try:
                html = future.result()
            except Exception as exc:
                print("\n")
                traceback.print_exc()
                httpNoResponse(url)
                break
            if (html.status_code != 404):
                soup = BeautifulSoup(html.text, 'html.parser')
                recordOfTitle = findRecordTitle(soup)
                try:
                    os.mkdir(recordOfTitle)
                except Exception as exc:
                    print("\n")
                    traceback.print_exc()
                    createFolderError(recordOfTitle, url)
                listOfFile = findDownloadLink(soup)
                if len(listOfFile) > 0:
                    for fileDownloadLink in listOfFile:
                        titleLinkList.append([recordOfTitle, fileDownloadLink])
                    #desired data form: [[folder name, downloadLink1], [folder name, downloadLink2]]
                    try:
                        nextPageSoup = findNextPage(soup, cookie)
                        while nextPageSoup != None:
                            listOfFile = findDownloadLink(nextPageSoup)
                            if len(listOfFile) > 0:
                                for fileDownloadLink in listOfFile:
                                    titleLinkList.append([recordOfTitle, fileDownloadLink])
                            else:
                                downloadFileError(url, recordOfTitle, os.getcwd())
                            nextPageSoup = findNextPage(nextPageSoup, cookie)
                    except Exception as exc:
                        print("\n")
                        traceback.print_exc()
                        findNextPageErr()
                else:
                    downloadFileError(url, recordOfTitle, os.getcwd())
            else:
                print("\nCan't open url: 404 page not found. null will be used as filled value")
                print("url: ", url, "\n")
            print("All pages processed. No more next page.")
            print("Successfully find download link from ", i, " / ", numOfUrl, "records.\n")
            urlList.remove(url)
            i = i + 1
            gc.collect()
    #desired data form: [[folder name, downloadLink1, cookie], [folder name, downloadLink2, cookie]]
    for titleLink in titleLinkList:
        titleLink.append(cookie)
    with Pool() as p:
        print("\nStart downloading all files, please wait......")
        print("As long as network usage is high the scripting is running.\n")
        p.map(downloadFile, titleLinkList)

## Get the name of records in order to build folder
# @param    parsedHtml
#           parsed response object using bs4, can be used to search tags/attribs
# @return   title
#           the name of the record, used to build folder for download files
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
        print("\n")
        traceback.print_exc()
        print("Fail to get record title!")
    if title == "null":
        print("Null title, value = ", value, "\n")

    return title

## Sanitize record titles so that they fit Window's requirement
# @param    recordTitle
#           raw title info from attribs
# @return   title
#           sanized title, no tailing space and '&'
def sanitizeValue(recordTitle):
    title = ""
    illegalChar = ['\n', '\t', '\\', '/', '|', '"', ':','<', '>', '*', '?', "LPT", "COM", ".."]
    
    if len(recordTitle) > 255:
        recordTitle = recordTitle[:255]
    for char in recordTitle:
        if not char in illegalChar:
            title += char
    while title[-1] == ' ':
        title = title[:-1]
    if title[-1] == '&':
        title = title[:-1]
    
    return title

## Output error info when fail to build a new folder
# @param    recordOfTitle
#           folder name
# @param    url
#           the url of record
def createFolderError(recordOfTitle, url):
    print("Folder already exist or couldn't build a folder")
    print("Folder Title: ", recordOfTitle)
    with open("create folder error log.txt", 'a') as errLog:
        errLog.write("Folder already exist or couldn't build a folder\n")
        errLog.write("Folder(record) Title: "+recordOfTitle+"\n")
        errLog.write("FileLink: "+url+"\n")
        errLog.write("\n")

## Output error info when requests do not get a valid response
# @param    url
#           the url of record
def httpNoResponse(url):
    print("No response from this url!")
    print("url: ", url)

## Output error info when fail happened while find next page of a record
def findNextPageErr():
    print("\nError happened when finding next page.")
    print("If this kind of error keep happening, save the error message and send to author.")
    print("Press enter to exit. ", end = '')
    input()
    sys.exit()

## Output error info when fail save file (download is ok)
# @param    title
#           downloaded file title
# @param    fileSavePath
#           path to a folder that a file supose to be moved in
def saveFileError(title, fileSavePath):
    print("Fail to save file for: ", title)
    print("Fail to enter folder: ", fileSavePath, "\n")
    with open("move file error log.txt", 'a') as errLog:
        errLog.write("Fail to move file into folder: "+fileSavePath+"\n")

## Output error info when fail to download file
# @param    fileLink
#           downloaded link of a file
# @param    title
#           record title where download filr belongs to
# @param    rootPath
#           the path to save this error log
def downloadFileError(fileLink, title, rootPath):
    currentPath = os.getcwd()
    os.chdir(rootPath)
    print("\nEncounter error when downloading: ", fileLink)
    with open("download error log.txt", 'a') as errLog:
        errLog.write("Encounter error when downloading: "+fileLink+"\n")
        errLog.write("File belongs to record: "+title+"\n")
        errLog.write("\n")
    os.chdir(currentPath)
    
## call functions to download each related file
# @param    titleLinkList
#           list contain download file folder name and url
#           [recordOfTitle, fileDownloadLink, cookie]
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
            print("\n")
            traceback.print_exc()
            saveFileError(title, fileSavePath)
    try:
        fileRequest = requests.get(titleLinkList[1], cookies = titleLinkList[2], timeout=15)
        contentDisposition = fileRequest.headers["Content-Disposition"]
        contentDispositionLength = len(contentDisposition)
        fileNameIndex = contentDisposition.index("filename")
        fileName = contentDisposition[fileNameIndex+10 : contentDispositionLength-1]
        with open(fileName, 'wb') as outFile:
            outFile.write(fileRequest.content)
        print(fileName, " has been successfully downloaded.\n")
        gc.collect()
    except Exception as exc:
        print("\n")
        traceback.print_exc()
        downloadFileError(titleLinkList[1], title, rootPath)
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
        print("Please restart the script, usually it will fix the problem.\n")
        
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
        if i == 50:
            urlGroup.append(newList)
            i = 0
            newList = []
        if ((j == totalLength) and (len(newList) > 0)):
            urlGroup.append(newList)
    totalGroupNum = len(urlGroup)
    print("Total group of url: ", totalGroupNum)

    return totalGroupNum

## Create a new folder for download files
def buildDownloadFolder():
    try:
        os.mkdir("Download")
    except Exception as exc:
        print("\n")
        traceback.print_exc()
    os.chdir(os.getcwd() + "\\" + "Download")
