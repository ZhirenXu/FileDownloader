import requests
import mechanicalsoup
import sys
import getpass
import time
# When login successful, this should include in the response
SuccessfulLogin = "Signed in successfully"
# when login is not vaild, the length of response text is 11864
BadLogin = 11864

def login():
    url = "https://library.osu.edu/dc/users/sign_in"
    crediential = {}
    browser = ()
    i = 0
    
    print("Login url: https://library.osu.edu/dc/users/sign_in")
    status = True
    if status:
        browser = mechanicalsoup.StatefulBrowser()
        login_page = browser.open(url)
        login_form = browser.select_form('form[action="/dc/users/sign_in?locale=en"]')
        crediential = getCreditential()
        t_start = time.process_time()
        browser["user[email]"] = crediential["Email"]
        browser["user[password]"] = crediential["Password"]
        response = browser.submit_selected()
        #print(response.text)
        if (response.status_code == 200) and (SuccessfulLogin in response.text):
            print("\nLogin Success!\n")
        else:
            print("\nLogin Fail!\n")
            print("Would you want to try it again? Y/N: ", end = "")
            userChoice = input()
            if userChoice == "N" or userChoice == "n":
                sys.exit()
            elif userChoice == "Y" or userChoice == "y":
                login()
        t_end = time.process_time()
        print("Process Time: ", t_end - t_start)
        print("\n")
    return browser

## ask user to type in login info
def getCreditential():
    credit = {}
    
    print("Please enter your user name(email address): ", end = "")
    email = input()
    #error check
    while (("." not in email) or ("@" not in email) or (len(email) == 0)):
        print("Invaild email address. Please type again. Ctrl+C to quit.")
        print("user name(email address): ", end = "")
        email = input()
    credit["Email"] = email
    print("Please enter your password. For privacy the password is invisible")
    password = getpass.getpass()
    while len(password) == 0:
        print("Invaild password. Please type again. Ctrl+C to quit.")
        password = getpass.getpass()
    credit["Password"] = password

    return credit

def wantLogin():
    print("Do you need to login? Y/N: ", end = "")
    choice = input()
    if choice == 'Y' or choice == 'y':
        return True
    return False

