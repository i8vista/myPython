import winreg,re

def findReg(key):
    try:
        i = 0
        while True:
            Name, Value, Type = winreg.EnumValue(key, i)
            if Type == 1:
                if re.compile(r'NVIDIA').search(Value):
                    return True
            i +=1
    except WindowsError:
        return False


def findkey(sub_key):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key,
                        reserved=0, access=winreg.KEY_READ)
    if findReg(key):
        print(sub_key)
        return
    try:
        index = 0
        parentPath = sub_key
        while True:
            sub_key = parentPath + '\\' + winreg.EnumKey(key, index)
            findkey(sub_key)
            index += 1
    except WindowsError:
        pass

findkey(r'SOFTWARE\Classes\CLSID')