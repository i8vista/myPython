import winreg,re,pprint

def findReg(key,compilestr):
    try:
        i = 0
        while True:
            Name, Value, Type = winreg.EnumValue(key, i)
            if Type == 1:
                if re.compile(compilestr).search(Value):
                    return True
            i +=1
    except WindowsError:
        return False

def findkey(sub_key,reg_list,compilestr):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key,
                        reserved=0, access=winreg.KEY_READ)
    if findReg(key,compilestr):
        reg_list.append(re.compile(r'^(.*?\\.*?\\.*?\\)([^\\]*)').search(sub_key).group(2))
    else:
        try:
            index = 0
            parentPath = sub_key
            while True:
                sub_key = parentPath + '\\' + winreg.EnumKey(key, index)
                findkey(sub_key,reg_list,compilestr)
                index += 1
        except WindowsError:
            pass


# Find CLSID
print(r'HKEY_LOCAL_MACHINE\SOFTWARE\Classes\CLSID')
mylist = []
findkey(r'SOFTWARE\Classes\CLSID',mylist,'NVIDIA|Nv3D')
newlist = []
for i in mylist:
    if i not in newlist:
        newlist.append(i)
pprint.pprint(newlist)

# Find CLSID
print('\n')
print(r'HKEY_LOCAL_MACHINE\SOFTWARE\Classes\Interface')
mylist = []
findkey(r'SOFTWARE\Classes\Interface',mylist,'{DC09760E-9FDA-454A-B9D2-7E663E58C39D}')
newlist = []
for i in mylist:
    if i not in newlist:
        newlist.append(i)
pprint.pprint(newlist)