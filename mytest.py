#coding:utf-8
import win32api, win32con
 
reg_root = win32con.HKEY_LOCAL_MACHINE
reg_path = r"SOFTWARE\1"
reg_flags = win32con.WRITE_OWNER|win32con.KEY_WOW64_64KEY|win32con.KEY_ALL_ACCESS
 
key = win32api.RegOpenKeyEx(reg_root, reg_path, 0, reg_flags)
 
#遍历其他键值
try:
    i = 0
    while True:        
        print(win32api.RegEnumValue(key, i))
        i += 1
except Exception as e:
    #raise(e)
    pass
    
#关闭键
win32api.RegCloseKey(key)