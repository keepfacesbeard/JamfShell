import requests
import getpass
from tabulate import tabulate
import os
import pandas as pd
# import numpy as np
# import jamfcreds

jamf_hostname = "https://reedcollege.jamfcloud.com"

print("<<<<  Welcome to Jamf in a Shell >>>>")


### Login and logout and such 

def get_uapi_token():
    global loggedIn
    jamf_test_url = jamf_hostname + "/api/v1/auth/token"
    headers = {'Accept': 'application/json', }
    # jamf_user = input("Enter Jamf Username: ")
    # jamf_password = getpass.getpass("Enter Password for user " + jamf_user + " : ")
    jamf_user = jamfcreds.readonly_username
    jamf_password = jamfcreds.readonly_password
    response = requests.post(url=jamf_test_url, headers=headers, auth=(jamf_user, jamf_password))
    
    if response.status_code == 200:
        print("Login Successful. Token Issued.")
        loggedIn=True
        response_json = response.json()
        return response_json['token']
    else:
        print("Account error. Try again. Make sure you are using the correct credentials")
        get_uapi_token()

def responseCheck(response):
    if response.status_code != 200:
        print ("OH NO!!! That didn't work at all.\nThere was an error finding this data. Please confirm the ID number you're searching is valid, and that you are still connected to the JAMF API.\n")
        return "Failure"
    else:
        return "Success"           

def invalidate_uapi_token(api_token):
    global loggedIn
    jamf_test_url = jamf_hostname + "/api/v1/auth/invalidate-token"
    headers = {'Accept': '*/*', 'Authorization': 'Bearer ' + api_token}
    response = requests.post(url=jamf_test_url, headers=headers)

    if response.status_code == 204:
        print('Token invalidated!')
        loggedIn=False
    else:
        print('Error invalidating token.')


def getJamfProVersion():

  
    # fetch sample Jamf Pro api call
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.get(url=jamf_hostname + "/api/v1/jamf-pro-version", headers=headers)
    response_json = response.json()

    return(response_json['version'])


def inventoryCounts ():
    url = jamf_hostname + "/api/v1/inventory-information"
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}

    response = requests.request("GET", url, headers=headers)

    print(response.text)


### Computer Stuff

def computerSearch (compName, printout):
    resultsList=[]
    url = jamf_hostname + "/api/v1/computers-inventory?section=GENERAL&section=HARDWARE&page=0&page-size=4000"
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", url, headers=headers)
    if responseCheck(response) == "Success":
        response_json=response.json()
        inventoryCount=len(response_json['results'])
        for i in range(0,inventoryCount):
            computerName=response_json['results'][i]['general']['name']
            if compName.lower() in computerName.lower() or compName.lower() == computerName.lower():
                computerJSSID=response_json['results'][i]['id']
                assetTag=response_json['results'][i]['general']['assetTag']
                resultsList.append([computerName, computerJSSID, assetTag])
            else:
                continue
        if len(resultsList) < 1:
            if printout==True:
                print("No results found matching that query. Sorry!")
            return "No Results Found"
        else:
            tableHeaders=["Computer Name", "JSS ID", "RT Asset Number"]
            resultsTable=tabulate(resultsList,tableHeaders)
            if printout==True:
                print("\nSearch Results ("+ str(len(resultsList)) + "): \n")
                print(resultsTable)
                print("  \n")
            return "Search Results", resultsTable
    else:
        return None

def assetSearch (query):
    resultsList=[]
    url = jamf_hostname + "/api/v1/computers-inventory?section=GENERAL&section=HARDWARE&page=0&page-size=4000"
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", url, headers=headers)
    if responseCheck(response) == "Success":
        response_json=response.json()
        inventoryCount=len(response_json['results'])
        for i in range(0,inventoryCount):
            assetTag=response_json['results'][i]['general']['assetTag']
            if assetTag == query:
                computerJSSID=response_json['results'][i]['id']
                computerName=response_json['results'][i]['general']['name']
                resultsList.append([computerName, computerJSSID, assetTag])
            else:
                continue
        if len(resultsList) < 1:
            print("No results found matching that query. Sorry!")
        else:
            print("\nSearch Results ("+ str(len(resultsList)) + "): \n")
            tableHeaders=["Computer Name", "JSS ID", "RT Asset Number"]
            print(tabulate(resultsList,tableHeaders))
            print("  \n")
    else:
        return None

def computerInfo (jssID) :
    global mode
    url = jamf_hostname + "/api/v1/computers-inventory-detail/" + str(jssID)
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", url, headers=headers)
    if responseCheck(response) == "Success":
        response_json=response.json()
        return response_json
    else:
        return None

def printBasicCompInfo (jssID):
        global mode
        response_json=computerInfo(jssID)
        if response_json:    
            compName=response_json['general']['name']
            assetTag=response_json['general']['assetTag']
            ip=response_json['general']['lastIpAddress']
            userName=response_json['userAndLocation']['username']
            lastCheckIn=response_json['general']['lastContactTime']
            compDataTable = [["Computer Name:",compName],["Asset Tag:", assetTag],["User:", userName],["IP Address:",ip],["Last Check-In",lastCheckIn],]
            print(tabulate(compDataTable))
            print("\n")
        else:
            mode = "Home"
            return None
      
def moreCompInfo(jssID, category, printout):
    global mode
    if category.lower() == 'home':
        mode='home'
        print('Returning to Jamf in a Shell home...')
        return
    else:
        response_json=computerInfo(jssID)
        if category.lower() == 'groups':
            groupTable=[]
            for item in response_json['groupMemberships']:
                groupTable.append([item['groupName']])
            infoTable=tabulate(groupTable)
            if printout==True:
                print("\n        Group Memberships for Computer with JSS ID " + str(jssID) +":\n")
                print(infoTable)
                print("\n")
            return infoTable
        elif category.lower() == 'ext':
            extensionAttributeTable=[]
            for item in response_json['extensionAttributes']:
                if "Applications Installed" in item['name']:
                    continue
                else:
                    extensionAttributeTable.append([item['name'],item['values']])
            for item in response_json['general']['extensionAttributes']:
                if "Applications Installed" in item['name']:
                    continue
                else:
                    extensionAttributeTable.append([item['name'],item['values']])
            for item in response_json['hardware']['extensionAttributes']:
                if "Applications Installed" in item['name']:
                    continue
                else:
                    extensionAttributeTable.append([item['name'],item['values']])

            for item in response_json['operatingSystem']['extensionAttributes']:
                if "Applications Installed" in item['name']:
                    continue
                else:
                    extensionAttributeTable.append([item['name'],item['values']])            
            extensionAttributeTable = sorted(extensionAttributeTable,key=lambda x:x[0].lower())
            infoTable=(tabulate(extensionAttributeTable,["Extension Attribute","Value]"]))
            if printout==True:
                print("\n        Extension Attributes for Computer with JSS ID " + str(jssID) +":\n")
                print(infoTable)
                print("\n")
            return infoTable
        elif category.lower() == 'hardware':
            hardwareTable=[]
            for key in response_json['hardware'].keys():
                if key == 'extensionAttributes':
                    continue
                else:     
                    hardwareTable.append([key,response_json['hardware'].get(key)])
            infoTable=tabulate(hardwareTable)
            if printout==True:
                print("\n        Hardware Info for Computer with JSS ID " + str(jssID) +":\n")
                print(infoTable)
                print("\n")
            return infoTable
        else:
            if printout==True:
                print("Invalid entry or error. Try again\n")
            return "Error. Invalid argument, possibly."


## GROUP STUFF

def listAllGroups ():
    groupList = []
    url = jamf_hostname + "/JSSResource/computergroups"
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", url, headers=headers)
    if responseCheck(response) == "Success":
        response_json=response.json()
        for group in response_json['computer_groups']:
            groupList.append([group['name'],group['id']])
        return groupList
    else:
        return None

def printGroupList ():
    groupList=listAllGroups()
    if groupList:
        print("     List of all Computer Groups:\n")
        print(tabulate(groupList, ['Group Name', "Group ID"]))
    else:
        return None

def getGroupNameByID (groupID):
    url = jamf_hostname + "/JSSResource/computergroups/id/" + str(groupID)
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", url, headers=headers)
    response_json=response.json()
    return response_json['computer_group']['name']

def searchGroupByName (query, printout):
    searchResults = []
    groupList=listAllGroups()
    for group in groupList:
        groupName=group[0]
        if query.lower() in groupName.lower() or query.lower() == groupName.lower():
            searchResults.append([group[0],group[1]])
        else:
            continue
    resultsTable=tabulate(searchResults,["Group Name", "Group ID"])
    if printout==True:
        print(resultsTable)
    return resultsTable

def listComputersInGroup(groupID):
    compList=[]
    url = jamf_hostname + "/JSSResource/computergroups/id/" + str(groupID)
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", url, headers=headers)
    response_json=response.json()
    for i in range(0, len(response_json['computer_group']['computers'])):
        # print(id)
        compList.append(response_json['computer_group']['computers'][i]['id'])
    return compList


## POLICY THINGS
            
def listAllPolicies ():
    policyList=[]
    policyUrl = jamf_hostname + "/JSSResource/policies"
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", policyUrl, headers=headers)
    if responseCheck(response) == "Success":
        response_json=response.json()['policies']
        for i in range(0,len(response_json)):
            policyList.append([response_json[i].get('name'),response_json[i].get('id')])
        return policyList
    else:
        return None

def printPolicyList():
    policyList=listAllPolicies()
    if policyList:
        print("     List of all Jamf Policies \n")
        print(tabulate(policyList,["Policy Name", "Policy ID"]))
    else:
        return None

def searchPolicyByName (query):
    policyList = listAllPolicies()
    searchResults = []
    for policy in policyList:
        name = policy[0]
        if query.lower() in name.lower() or query.lower() == name.lower:
            searchResults.append([policy[0],policy[1]])
        else:
            continue
    print("     Search results for policy with '" + query + "' in name: ")
    print(tabulate(searchResults, ["Policy Name", "Policy ID"]))

def policyScope (policyID):
    policyUrl = jamf_hostname + "/JSSResource/policies/id/" + str(policyID)
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", policyUrl, headers=headers)
    response_json = response.json()
    return response_json['policy']['scope']

def policiesByGroup (groupID, printout):
    groupName = getGroupNameByID(groupID)
    print("Fetching all Policies in scope for " + groupName +"...")
    print("...this make take a few minutes.")
    scopeList=[]
    policyList = listAllPolicies()
    for policy in policyList[0:len(policyList)]:
        scope = policyScope(policy[1])
        scope = scope.get('computer_groups')
        if len(scope) == 0:
            continue
        else:
            for i in range(0,len(scope)):
                scopeGroupID=scope[i].get('id')
                if str(scopeGroupID) == str(groupID):
                    scopeList.append([policy[1], policy[0]])
    policyList=tabulate(scopeList, ["Policy ID", "Policy Name"])
    title="     Policies in Scope for " + groupName +"\n"
    if printout==True:
        print("/n"+title)       
        print(policyList)
    return scopeList

## CONFIG PROFILE THINGS
def listAllConfigProfiles ():
    configList=[]
    configsUrl = jamf_hostname + "/JSSResource/osxconfigurationprofiles"
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", configsUrl, headers=headers)
    if responseCheck(response) == "Success":
        response_json=response.json()['os_x_configuration_profiles']
        for i in range(0,len(response_json)):
            configList.append([response_json[i].get('name'),response_json[i].get('id')])
        return configList
    else:
        return None

def configProfileScope(configID):
    url = jamf_hostname + "/JSSResource/osxconfigurationprofiles/id/" + str(configID)
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", url, headers=headers)
    response_json=response.json()
    scope = response_json['os_x_configuration_profile']['scope']
    return scope

def configProfilesByGroup (groupID, printout):
    groupName = getGroupNameByID(groupID)
    print("Fetching all Configuration Profiles in scope for " + groupName +"...")
    print("...this may take a few minutes.")
    scopeList=[]
    configList = listAllConfigProfiles()
    for config in configList[0:len(configList)]:
        scope = configProfileScope(config[1])
        scope = scope.get('computer_groups')
        if len(scope) == 0:
            continue
        else:
            for i in range(0,len(scope)):
                scopeGroupID=scope[i].get('id')
                if str(scopeGroupID) == str(groupID):
                    scopeList.append([config[1], config[0]])
    configResults=tabulate(scopeList, ["Config ID", "Config Name"])
    title="     Configuration Profiles in Scope for " + groupName +"\n"
    if printout==True:
        print("/n"+title)       
        print(configResults)
    return scopeList


## EXTENSION ATTRIBUTE THINGS
def listAllExtAttributes ():
    eaList=[]
    eaUrl = jamf_hostname + "/JSSResource/computerextensionattributes"
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", eaUrl, headers=headers)
    if responseCheck(response) == "Success":
        response_json=response.json()['computer_extension_attributes']
        for i in range(0,len(response_json)):
            eaList.append([response_json[i].get('name'),response_json[i].get('id')])
        return eaList
    else:
        return None

def getEAJson (id):
    url = jamf_hostname + "/JSSResource/computerextensionattributes/id/" + str(id)
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", url, headers=headers)
    if responseCheck(response) == "Success":
        response_json=response.json()['computer_extension_attribute']
        return response_json
    else:
        return None

def getEAScriptContents (id):
    eaContents = getEAJson(id)
    if eaContents['input_type']['type'] == 'script':
        scriptText=eaContents['input_type']['script']
        return scriptText
    else:
        return

def searchEAScriptsByString(query, printout):
    results=[]
    eaList=listAllExtAttributes()
    for ea in eaList:
        contents=getEAScriptContents(ea[1])
        if query.lower() in contents.lower():
            results.append(ea)
        else:
            continue
    title = "         Extension Attributes containing string: " + query +"\n"
    if printout == True:
        print(title)
        print(tabulate(results,["Script Name", "Script ID"]))
    return results

## SCRIPT THINGS

def listAllScripts ():
    scriptList=[]
    scriptUrl = jamf_hostname + "/JSSResource/scripts"
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", scriptUrl, headers=headers)
    if responseCheck(response) == "Success":
        response_json=response.json()['scripts']
        for i in range(0,len(response_json)):
            scriptList.append([response_json[i].get('name'),response_json[i].get('id')])
        return scriptList
    else:
        return None


def getScriptInfo (id):
    url = jamf_hostname + "/JSSResource/scripts/id/" + str(id)
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", url, headers=headers)
    if responseCheck(response) == "Success":
        response_json=response.json()['script']
        return response_json
    else:
        return None

def getScriptContents (id):
    scriptInfo = getScriptInfo(id)
    scriptContents = scriptInfo['script_contents']
    return scriptContents

def searchScriptByString (query, printout):
    print("Fetching all Scripts containing string '" + query +"'...")
    print("...this may take a few minutes.")
    results = []
    scriptList = listAllScripts()
    for script in scriptList:
        contents = getScriptContents(script[1])
        if query.lower() in contents.lower():
            results.append(script)
        else:
            continue
    title = "         Scripts containing string: " + query +"\n"
    if printout == True:
        print(title)
        print(tabulate(results,["Script Name", "Script ID"]))
    return results


## APPLICATION USAGE

def getAppUsage(jssID, startDate, endDate):
    #Start/end date (e.g. yyyy-mm-dd)
    url = jamf_hostname + "/JSSResource/computerapplicationusage/id/" + str(jssID) + "/" + startDate + "_" + endDate
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    response = requests.request("GET", url, headers=headers)
    if responseCheck(response) == "Success":
        response_json=response.json()
        return response_json['computer_application_usage']
    else:
        return None

def parseAppUsage(data, appName):
    values = []
    dates= []
    useTimes = []
    openTimes = []
    for i in range(0, len(data)):
        date = data[i]['date']
        for app in data[i]['apps']:
            if appName.lower() in app['name'].lower():
                useTime=app['foreground']
                values.append([date, int(useTime)])
                dates.append(date)
                useTimes.append(int(useTime))
            else:
                continue
    # appUsageData = pd.DataFrame(values, columns=['Date', 'App Use Time'])
    return values

## groupAppUsage not 100% functional, it is writing duplicate dates instead of summing values for a date, sometimes.

def groupAppUsage(groupID, appName, startDate, endDate):
    compList=listComputersInGroup(groupID)
    # print("Comp List:" + str(compList))
    totalValues = []
    for jssID in compList:
        data=parseAppUsage(getAppUsage(jssID, startDate, endDate), appName)
        # print(data)
        if len(data) > 0:
            for i in range(0, len(data)):
                date = data[i][0]
                usage = data[i][1]
                if any(date in x for x in totalValues):
                    for pair in totalValues:
                        if date == pair[0]:
                            pair[1] += usage
                        else:
                            continue
                else:
                    totalValues.append([date, usage])
    # print(totalValues)
    totalValues.sort()
    return totalValues

# def exportAppUsage(values, filename):
#     appUsageData = pd.DataFrame(values, columns=['Date', 'Total App Use Time'])
#     appUsageData.to_csv(filename, index=False)




## Write an ouput to a file:

def writeFile(data, headers):
    writeIt=input("Would you like to write this data to a file? y/n\n>>>")
    if writeIt.lower()[0]=='y':
        savePath=input("Enter complete file path and name (ex. /users/jim/file.csv):\n>>> ")
        saveFile=savePath.split("/")[-1]
        print("File: " +saveFile)
        split=((len(saveFile))*-1)-1
        saveDir=savePath[0:split]
        print("Dir: " +saveDir)
        if os.path.isdir(saveDir):
            dataExport = pd.DataFrame(data, columns=headers)
            dataExport.to_csv(savePath, index=False)
            print("File Saved.")
            return "written"
        else:
            print("Bad file path. Please check filename and path and try again.")
            writeFile(data, headers)
    elif writeIt.lower()[0] != 'n':
        print("Incorrect command, please try again.")
        writeFile(title,data)
    else:
        return None





def printCommandList ():
    commandList = [
    ["search", "Searches for Computers by name"],
    ["policy-search", "Searches Policies by name, returns Policy ID"],
    ["group-search", "Search Computer Groups by name, returns Group ID"],
    ["info", "Pulls basic Computer info by JSS ID, with options for hardware, ext. attributes, and group membership"],
    ["group-policy", "Finds all Policies scoped to a particular Group, based on Group ID"],
    ["group-config", "Finds all Configuration Profiles scoped to a particular Group, based on Group ID"],
    ["group-list", "Prints list of Group Names and IDs"],
    ["policy-list", "Prints list of Policies Names and IDs"],
    ["asset-search", "Search for Computer by Asset Tag"],
    ["script-string", "Search for all scripts containing specific string."],
    ["extension-string", "Search for all Extension Attribute scripts containing specific string."],
    ["group-app-usage", "Find total usage for a particular app within a computer group, in a date range."],
    ["help", "Prints list of commands. You're looking at it now!"],
    ]
    print("\n")
    print(tabulate(commandList,["Command", "Function"]))



def main ():
    global api_token
    global mode
    api_token = get_uapi_token()
    version=str(getJamfProVersion())
    print("Jamf Pro Version: " + version)
    printCommandList()
    mode='home'
    while loggedIn==True:
        
        command=input("\nEnter a command here, or enter 'quit' to exit Jamf in a Shell. For a list of commands, type 'help.' \n>>> ")
        if command.lower() == "search":
            query=input("Search computers by name: ")
            searchResults=computerSearch(query, True)
        elif command.lower() == "group-policy":
            query=input("Enter group ID number to list policies with that group in scope: ")
            results=policiesByGroup(query,True)
            headers=["Policy ID", "Policy Name"]
            writeFile(results, headers)
        elif command.lower() == "script-string":
            query=input("Enter word or string to find Scripts containing it: ")
            results=searchScriptByString(query,True)
            headers = ["Script Name", "Script ID"]
            writeFile(results, headers)
        elif command.lower() == "extension-string":
            query=input("Enter word or string to find Extension Attribute Scripts containing it: ")
            results=searchEAScriptsByString(query,True)
            headers = ["Ext Attr Name", "Ext Attr ID"]
            writeFile(results, headers)
        elif command.lower() == "group-config":
            query=input("Enter group ID number to list configuration profiles with that group in scope: ")
            results=configProfilesByGroup(query,True)
            headers = ["Config ID", "Config Name"]
            writeFile(results, headers)
        elif command.lower() == "asset-search":
            query=input("Enter Asset Tag number to find Computer Name and JSS ID: ")
            assetSearch(query)
        elif command.lower() == 'help' or command.lower == 'man':
            printCommandList()
        elif command.lower() == "policy-search":
            query = input ("Search Policies by Name: ")
            searchPolicyByName(query)
        elif command.lower() == "group-search":
            query = input ("Search Computer Groups by Name: ")
            searchGroupByName(query, True)
        elif command.lower() == "group-list":
            printGroupList()
        elif command.lower() == "policy-list":
            printPolicyList()
        elif command.lower() == "group-app-usage":
            query1=input('Enter Group ID for Group App Usage: ')
            query2=input('Enter App Name for Group App Usage (note that Adobe will return all Adobe apps, etc. so be as specific as possible): ')
            query3=input('Enter Date Range Start (YYYY-MM-DD): ')
            query4=input('Enter Date Range End (YYYY-MM-DD): ')
            groupname = getGroupNameByID(query1)
            print("Finding app usage for '" + query2 + "' in " + groupname)
            print('...this may take a few minutes')
            results = groupAppUsage(query1, query2, query3, query4)
            print('App Usage for ' + query2 + " for group " + groupname + " from " + query3 + " to " + query4)
            print(tabulate(results, ["Date", "App Usage (min)"]))
            # tofile=input('Would you like to export these results to a file? (yes/no)')
            # if 'y' in tofile.lower():
            #     filename=input('Please input file path (e.g. /users/username/output.csv)')
            #     exportAppUsage(results, filename)
            headers=['Date', 'Total App Use Time']
            writeFile(results, headers)

        elif command.lower() == "info":
            mode='info'
            query=input("Get Info for JSS ID: ")
            if query.lower() != 'quit' and query.lower() != 'home':
                printBasicCompInfo(query)
                while mode == 'info':
                    moreInfo = input("Would you like more detailed info for this computer?\nType 'ext' for extension attributes, 'groups' for a list of groups\n'hardware' for hardware info\nor 'home' to return to search another computer, policy or group.\n")
                    if moreInfo.lower() == 'home':
                        mode='home'
                        moreCompInfo(0,'home', False)
                        break
                    else:
                        info=moreCompInfo(query, moreInfo, True)
            else:
                mode='home'
        elif command.lower() == 'quit':
            invalidate_uapi_token(api_token)
            print("Exiting Jamf in a Shell. Thanks for Jamfin' with us...")
            
        else:
            continue    
     




if __name__ == '__main__':
    main()




## INDIVIDUAL FUNCTION TESTS ####
# fetch Jamf Pro (ex-universal) api token
# api_token = get_uapi_token()

# searchEAScriptsByString("python", True)

# print(getEAScriptContents(71))
# moreCompInfo(2139,'groups')
# print("Number of Devices in Inventory:")
# inventoryCounts()
# computerSearch("tater
# computerList()
# computerSearch("macbook")
# invalidate_uapi_token(api_token)
# policyInfo(49)
# policiesByGroup(87)
# print(getGroupNameByID(87))
# printGroupList()
# searchGroupByName('bio')
# print(computerInfo("2139"))
# print(searchScriptByString('osascript -e'))
# data=getAppUsage(2139, "2022-01-01","2022-04-01")
# parseAppUsage(data, 'Slack.app')
# print(listComputersInGroup(356))
# appUse=groupAppUsage(189, 'InDesign', '2021-01-01', '2022-04-19')
# exportAppUsage(appUse, 'test1.csv')
# appUse.sort()
# print(tabulate(appUse, ["Date", "App Usage"]))
# listAllConfigProfiles()
# configProfileScope(144)
# configProfilesByGroup(189, True)


