import csv
import sys

##open csv file and read handler link, store in a list
# @param    csvName
#           the file name user typed in
# @return   urlList
#           a list contain item url that need to be scraped
def readCSV(csvName):
    urlList = []

    try:
        inFile = open(csvName, 'r')
        csvReader = csv.reader(inFile, delimiter=',')
        for row in csvReader:
            urlList.append(row[0])
        # del the column name read for first line
        urlList.pop(0)
        print ("Open input CSV success.")
        inFile.close()
    except:
        print("Fail to open input CSV. Press enter to exit.")
        key = input()
        sys.exit()
        
    return urlList

##write category and data into csv file
# @param    dataList
#           a list contains data
# @param    outputFile
#           output File pointed by user, unopened
def writeCSV(dataList, outputFile):
    try:
        csvWriter = csv.writer(outputFile)
        csvWriter.writerow(dataList)
        print("Write into CSV success.")
    except:
        print("Fail to write into CSV!")

##get input CSV file name
# @return       fileIn
#               Input CSV file
def getCSVInput():
    print("Please enter csv file name with .csv. \nThe file must in the same folder with your main.py program: ")
    fileIn = input()

    return fileIn

##get output CSV file name
# @return       fileOut
#               Output CSV file
def getCSVOutput():
    print("Please enter output file name (with .csv): ")
    fileOut = input()
 
    return fileOut
    
