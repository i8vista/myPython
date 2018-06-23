import os
import codecs
import winreg
import re
import shutil
import json
import logging
import datetime
import binascii
import win32api, win32con
# 格式化16进制字符串


def regValueFomat(regValueHexStr, regName, regType):
    if regType == 2 or regType == 7 or regType == 0:
        if regName == '@':
            extraCharNum = 8
        else:
            extraCharNum = 10
    elif regType == 3:
        if regName == '@':
            extraCharNum = 5
        else:
            extraCharNum = 7
    if 79 - len(regName) - len(regValueHexStr) - extraCharNum > 0:
        valueHexF = regValueHexStr + '\r\n'
    else:
        if 79 - len(regName) - extraCharNum <= 5:
            number = 3
        elif (79 - len(regName) - extraCharNum) % 3 == 0:
            number = 79 - len(regName) - extraCharNum
        elif (79 - len(regName) - extraCharNum) % 3 == 1:
            number = 79 - len(regName) - extraCharNum - 1
        else:
            number = 79 - len(regName) - extraCharNum - 2
        valueHexF = regValueHexStr[:number] + '\\\r\n'
        valueHexList = re.compile('.{1,75}').findall(
            regValueHexStr[number:])
        for i in range(len(valueHexList)):
            if i != len(valueHexList) - 1:
                valueHexF = valueHexF + '  ' + \
                    valueHexList[i] + '\\\r\n'
            else:
                valueHexF = valueHexF + '  ' + \
                    valueHexList[i] + '\r\n'
    return valueHexF

# 枚举键下的所有值并根据类型写值


def writeRegValue(key1, key2, regObj):
    try:
        enumValue_i = 0
        while True:
            regName, regValue, regType = winreg.EnumValue(key1, enumValue_i)  #不用win32api.RegEnumValue是因为读取的dowrd值为负数
            if regType == 7 and regValue != None:
                regName, regValue, regType = win32api.RegEnumValue(key2, enumValue_i) #不用winreg.EnumValue是因为不能处理值超过4K，不能区分REG_MULTI_SZ全空和单行空情况
            if regName == '':
                regName = '@'
            regName = regName.replace('\\', '\\\\')
            regName = regName.replace(r'"', r'\"')
            if regType == 0:    # REG_NONE
                if regValue == None:
                    regValueHexStr = ''
                else:
                    regValueHexStr = ''
                    for regValue_i in range(len(regValue)):
                        regValueHexChar = '%02x' % regValue[regValue_i]
                        if regValue_i != len(regValue) - 1:
                            regValueHexStr = regValueHexStr + regValueHexChar + ','
                        else:
                            regValueHexStr = regValueHexStr + regValueHexChar
                valueHexF = regValueFomat(regValueHexStr, regName, regType)
                if regName == '@':
                    regObj.write('%s=hex(%x):%s' % (regName, regType, valueHexF))
                else:
                    regObj.write('"%s"=hex(%x):%s' % (regName, regType, valueHexF))
            if regType == 1:      # REG_SZ
                regValue = regValue.replace('\\', '\\\\')
                regValue = regValue.replace(r'"', r'\"')
                if regName == '@':
                    regObj.write('%s="%s"\r\n' % (regName, regValue))
                else:
                    regObj.write('"%s"="%s"\r\n' % (regName, regValue))
            if regType == 2:      # REG_EXPAND_SZ
                if regValue == '':
                    regValueHexStr = '00,00'
                else:
                    regValueHexStr = ','.join(re.compile(r'.{2}').findall(str(binascii.b2a_hex(regValue.encode('utf_16_le')))[2:-1])) + ',00,00'
                valueHexF = regValueFomat(regValueHexStr, regName, regType)
                if regName == '@':
                    regObj.write('%s=hex(%x):%s' % (regName, regType, valueHexF))
                else:
                    regObj.write('"%s"=hex(%x):%s' % (regName, regType, valueHexF))
            if regType == 3:      # REG_BINARY
                if regValue == None:
                    regValueHexStr = ''
                else:
                    regValueHexStr = ''
                    for regValue_i in range(len(regValue)):
                        regValueHexChar = '%02x' % regValue[regValue_i]
                        if regValue_i != len(regValue) - 1:
                            regValueHexStr = regValueHexStr + regValueHexChar + ','
                        else:
                            regValueHexStr = regValueHexStr + regValueHexChar
                valueHexF = regValueFomat(regValueHexStr, regName, regType)
                if regName == '@':
                    regObj.write('%s=hex:%s' % (regName, valueHexF))
                else:
                    regObj.write('"%s"=hex:%s' % (regName, valueHexF))
            if regType == 4:      # REG_DWORD
                regValue = '%08x' % regValue
                if regName == '@':
                    regObj.write('%s=dword:%s\r\n' % (regName, regValue))
                else:
                    regObj.write('"%s"=dword:%s\r\n' % (regName, regValue))
            if regType == 7:      # REG_MULTI_SZ
                if regValue == None:
                    regValueHexStr = ''
                elif regValue == []:
                    regValueHexStr = '00,00'
                elif len(regValue) == 1 and regValue[0] == '':
                    regValueHexStr = '00,00,00,00'
                else:
                    regValueHexStr = ''
                    for regValue_i in range(len(regValue)):
                        regValueHex = ','.join(re.compile(r'.{2}').findall(str(binascii.b2a_hex(regValue[regValue_i].encode('utf_16_le')))[2:-1]))
                        if regValue_i == 0 and regValue[regValue_i] == '':
                            regValueHexStr = regValueHex + '00,00,'
                        else:
                            regValueHexStr = regValueHexStr + regValueHex + ',00,00,'
                    regValueHexStr = regValueHexStr + '00,00'
                valueHexF = regValueFomat(regValueHexStr, regName, regType)
                if regName == '@':
                    regObj.write('%s=hex(%x):%s' % (regName, regType, valueHexF))
                else:
                    regObj.write('"%s"=hex(%x):%s' % (regName, regType, valueHexF))
            if regType == 11: # REG_QWORD
                if regValue == 0:
                    regValueHexStrList = ['00'] * 8
                else:
                    regValueHexStr = '%x' % regValue
                    if len(regValueHexStr) % 2 !=0:
                        regValueHexStr = '0' + regValueHexStr
                    regValueHexStrList = re.compile(r'.{2}').findall(regValueHexStr)
                    regValueHexStrList.reverse()
                    num = 8 - len(regValueHexStrList)
                    if num > 0:
                        regValueHexStrList = regValueHexStrList + ['00'] * num
                valueHexF = ','.join(regValueHexStrList)
                if regName == '@':
                    regObj.write('%s=hex(%x):%s\r\n' % (regName, regType, valueHexF))
                else:
                    regObj.write('"%s"=hex(%x):%s\r\n' % (regName, regType, valueHexF))
            enumValue_i += 1
    except Exception as e:
            # logging.warning(str(e))
            regObj.write('\r\n')

# 枚举注册表键及其子键


def writeRegKey(regPath, regObj):
    regRegx = re.compile(r'(.+?)\\(.+)')
    mo = regRegx.search(regPath)
    regHead = mo.group(1)
    regEnd = mo.group(2)

    if regHead == 'HKEY_LOCAL_MACHINE':
        regHeadKey = winreg.HKEY_LOCAL_MACHINE
    try:
        key1 = winreg.OpenKey(regHeadKey, regEnd, reserved=0, access=winreg.KEY_READ)
        key2 = win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE, regEnd, 0, win32con.KEY_READ)
        regObj.write('[' + regPath + ']' + '\r\n')
        writeRegValue(key1, key2, regObj)
        try:
            i = 0
            parentPath = regPath
            while True:
                regKey = winreg.EnumKey(key1, i)
                regPath = parentPath + '\\' + regKey
                writeRegKey(regPath, regObj)
                i += 1
        except Exception as f:
            pass
            # logging.warning(str(f))
    except WindowsError as err:
        logging.warning('[' + regPath + ']' + str(err))
# 拷贝文件


def copyReg(displayFolder, reg_dict):
    regObj = codecs.open(displayFolder + '\\DisplayPnp.reg', 'w', 'utf_16')
    regObj.write('Windows Registry Editor Version 5.00\r\n\r\n')
    for reg_key, reg_value in reg_dict.items():
        for regPath in reg_value:
            regPath = reg_key + '\\' + regPath
            writeRegKey(regPath, regObj)
    regObj.close()


def copyFolder(displayFolder, folder_list):
    for folder in folder_list:
        displayPath = os.getcwd() +'\\' +displayFolder + \
            re.compile(r'\\.*').search(folder).group()
        shutil.copytree(folder, displayPath)


def copyFile(displayFolder, file_dict):
    for file_key, file_value in file_dict.items():
        filePath = displayFolder + re.compile(r'\\.*').search(file_key).group()
        os.makedirs(filePath)
        for filename in file_value:
            filename = file_key + filename
            try:
                shutil.copy(filename, filePath)
            except WindowsError:
                logging.warning('Not found: ' + filename)


logging.basicConfig(level=logging.DEBUG,
                    format=' %(asctime)s - %(levelname)s - %(message)s')
logging.info('Create the working directories...')
time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
displayFolder = 'DisplayPnp' + time
os.makedirs(displayFolder)
logging.info('Read the configuration file...')
config = open('config.json', 'r')
config_dict = json.load(config)
if 'reg' in config_dict:
    reg_dict = config_dict['reg']
    logging.info('Begin copying registry...')
    copyReg(displayFolder, reg_dict)
if 'folder' in config_dict:
    folder_list = config_dict['folder']
    logging.info('Begin copying folders...')
    copyFolder(displayFolder, folder_list)
if 'file' in config_dict:
    file_dict = config_dict['file']
    logging.info('Begin copying files...')
    copyFile(displayFolder, file_dict)
config.close()
logging.info('Done!')

# 批量拷贝注册名字生成ini文件
# import re,codecs
# reg = open(r'D:\Work\云更新\tool\显卡pnp\显卡pnp\r\nvidia\397.64\win10\950.安装.reg','r',encoding = 'utf8')
# S = reg.read()
# T = re.compile(r'\[HKEY_LOCAL_MACHINE\\SOFTWARE\\Classes\\Interface\\\{.*\}\]').findall(S)
# for i in T:
#     i = i.lstrip('[')
#     i = i.rstrip(']')
#     print(i)
