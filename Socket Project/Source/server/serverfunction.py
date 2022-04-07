import sys
import json
def updatedataFromJson():
    global arr
    f = open('./data.json', "r")
    arr = json.loads(f.read())
    f.close()

def checkExistUsername(user):
    if user['username'] == '':
        return False # not exists username
    user_str = user['username']
    for i in arr['users']:
        if user_str == i['username']:
            return True # existed username
    return False # not exists username

def checkUserPassword(user):
    for i in arr['users']:
        if user['username'] == i['username'] and user['password'] == i['password']:
            return True # right password
    else: return False # wrong password

def checkLogin(user):
    updatedataFromJson()
    if checkExistUsername(user) == False: 
        return 'Username does not found!'  # not exists username
    elif checkUserPassword(user) == False: 
        return 'Your password is incorrect!'  # wrong password
    else: return 'Logged in successfully!'

def createNewUser(user):
    updatedataFromJson()
    if user['username'] == '':
        return False # user ảo
    if checkExistUsername(user) == False:
        arr['users'].append(user)
        newF = open('./data.json',"w")
        newF.write(json.dumps(arr))
        newF.close()
        return True # create user successfully
    else: return False # create user failed (existed username in json file)

def searchDefault(searchType, inpStr):
    updatedataFromJson()
    returnArr = []
    for infor in arr['infors']:
        if searchType == 'id':
            infor['id'] = str(infor['id'])
        if infor[searchType].startswith(inpStr):
            infor['id'] = int(infor['id'])
            returnArr.append(infor)
    if returnArr == []: return False # return False if can't find
    else: return returnArr  # return Arr if found

def searchInfor(inpStr):
    arr = inpStr.split(' ', 1)
    for i in range(len(arr)):
        arr[i] = arr[i].strip().replace('"', '')
    if arr[0] == "F_ID":        arr[1] = arr[1].replace(' ', '')
    if arr[0] == "":            return False   # wrong search syntax (space at the begining)
    elif arr[0] == "F_ID":      return searchDefault('id' , arr[1])
    elif arr[0] == "F_Name":    return searchDefault('name', arr[1])
    elif arr[0] == "F_Mail":    return searchDefault('mail', arr[1])
    elif arr[0] == "F_MSSV":    return searchDefault('mssv', arr[1])

def myfunc(key):
    return int(key[1])

def getsearcHeader():
    updatedataFromJson()
    headerarr=[]
    for i in arr['searchheader']:
        for key in i:
            headerarr.append([key,i[key]])
    headerarr.sort(key = myfunc) #maybe it not read in order
    res = []
    for i in headerarr:
        res.append(i[0])
    return res


arr = 0

