import sys

## print program info
def showInfo():
    print("*******************************")
    print("*    File Downloader v1.1.0   *")
    print("*      Author: Zhiren Xu      *")
    print("*   published data: 04/06/21  *")
    print("*******************************")
        
## print exit message

def sysExit():
    print("\nThe program is finished. It is located in the folder 'download'. Press enter to exit.")
    key = input()
    sys.exit()
