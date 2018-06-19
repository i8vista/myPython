import winreg,re,pprint

def findReg(key):
    try:
        i = 0
        while True:
            Name, Value, Type = winreg.EnumValue(key, i)
            if Type == 1:
                if re.compile(r'NVIDIA|Nv3D').search(Value):
                    return True
            i +=1
    except WindowsError:
        return False

def text1(sub_key,reg_list = []):
    def findkey():
        nonlocal sub_key
        nonlocal reg_list
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key,
                            reserved=0, access=winreg.KEY_READ)
        if findReg(key):
            reg_list.append(re.compile(r'^(.*?\\.*?\\.*?\\)([^\\]*)').search(sub_key).group(2))
        else:
            try:
                index = 0
                parentPath = sub_key
                while True:
                    sub_key = parentPath + '\\' + winreg.EnumKey(key, index)
                    findkey()
                    index += 1
            except WindowsError:
                pass
    return findkey

mylist = []
text1(r'SOFTWARE\Classes\CLSID',mylist)()
pprint.pprint(set(mylist))