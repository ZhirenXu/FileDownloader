import urllib.request
import concurrent.futures
from multiprocessing import Pool
from bs4 import BeautifulSoup
import requests
from requests import Session
import sys
import gc
import os

def loadUrlSession(session, url):
    html = session.get(url)
    return html

def downloadSession(session, url):
    html = session.get(url)
    return html

def process(session, urlList):
    listOfFile = []
    fileTitle = ""
    # iterator to show program progress
    i = 1

    numOfUrl = len(urlList)
    print("There are ", numOfUrl, " records in the input file.\n")
    print("Proceeding......\n")
    with Pool() as p:
        p.map(downloadAndSave, session, listOfFile)
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

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(loadUrlSession, session, url): url for url in urlList}
        for future in concurrent.futures.as_completed(future_to_url):
            print("Processing ",i, " / ", numOfUrl, "records.")
            url = future_to_url[future]
            print("Current URL: ", url)
            try:
                html = future.result()
            except:
                httpNoResponse(url)
                break
            if (html.status_code != 404):
                soup = BeautifulSoup(html.text, 'html.parser')
                recordOfTitle = findRecordTitle(soup)
                listOfFile = findDownloadLink(soup)
                for fileDownloadLink in listOfFile:
                    titleLinkList.append([recordOfTitle, fileDownloadLink])
                #desired data form: [[folder path, downloadLink1], [folderpath, downloadLink2]]
                try:
                    nextPageSoup = findNextPage(soup, session)
                    while nextPageSoup != None:
                        listOfFile = findDownloadLink(nextPageSoup)
                        for fileDownloadLink in listOfFile:
                            titleLinkList.append([recordOfTitle, fileDownloadLink])
                        nextPageSoup = findNextPage(nextPageSoup, session)
                except:
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
    with Pool(9) as p:
        print("Start downloading all files, please wait......")
        print("As long as network usage is high the scripting is running.")
        p.map(downloadFile, titleLinkList)

def findRecordTitle(parsedHtml):
    title = "null"
    # delete front/back whitespace and add to valueList
    tag = parsedHtml.find("div", "col-sm-8")
    try:
        h2 = tag.contents[1]
        #h2 is a list, format as: ['\\n', <h2>The Lantern, Ja...span></small>\n</h2>, '\\n']
        value = h2.contents[0].string
        endIndex = value.index("\n")
        title = value[:endIndex]
    except:
        print("Fail to get record title!")

    return title

def makeDirective(recordTitle):
    rootPath = os.getcwd()
    try:
        os.mkdir(recordTitle)
    except:
        print("Folder already exist or couldn't build a folder")
    fileSavePath = rootPath + "\\" + recordTitle

def findAndDownload(soup, recordTitle, session):
    rootPath = os.getcwd()
    try:
        os.mkdir(recordTitle)
    except:
        print("Folder already exist or couldn't build a folder")
    fileSavePath = rootPath + "\\" + recordTitle
    os.chdir(fileSavePath)
    listOfFile = findDownloadLink(soup)
    
    if not (listOfFile == None):
        with Pool(9) as p:
            p.map(downloadFile, listOfFile)
        #downloadFile(session, listOfFile)
    else:
        print("This record doesn't have any related file!")
    os.chdir(rootPath)
    
def httpNoResponse(url):
    print("No response from this url!")
    print("url: ", url)

def findNextPageErr():
    print("\nError happened when finding next page.")
    print("If this kind of error keep happening, save the error message and send to author.")
    print("Press enter to exit. ", end = '')
    input()
    sys.exit()
                    
## call functions to download each related file
# @param    session
#           login cookie to access private file record
# @param    fileUrl
#           url for related files
def downloadFile(titleLinkList):
    rootPath = os.getcwd()
    title = titleLinkList[0]
    fileSavePath = rootPath + "\\" + title
    try:
        os.mkdir(title)
    except:
        print("Folder already exist or couldn't build a folder")
    try:
        os.chdir(fileSavePath)
        try:
            file = requests.get(titleLinkList[1])
            contentDisposition = file.headers["Content-Disposition"]
            contentDispositionLength = len(contentDisposition)
            fileNameIndex = contentDisposition.index("filename")
            fileName = contentDisposition[fileNameIndex+10 : contentDispositionLength-1]
            with open(fileName, 'wb') as outFile:
                outFile.write(file.content)
            print(fileName, " has been successfully downloaded.")
        except:
            print("Encounter error when downloading: ", fileName)
        os.chdir(rootPath)
    except:
        print("Fail to save file for: ", title)
    
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
        if i > 999:
            urlGroup.append(newList)
            i = 0
            newList = []
        if ((j == totalLength) and (len(newList) > 0)):
            urlGroup.append(newList)
    totalGroupNum = len(urlGroup)
    print("Total group of url: ", totalGroupNum)

    return totalGroupNum
