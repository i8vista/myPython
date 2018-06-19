import os
import codecs
import winreg
import re
import shutil
import json
import logging
import datetime
# 格式化16进制字符串


def regValueFomat(regValueHexStr, regName, regType):
    if regType == 2 or regType == 7:
        extraCharNum = 10
    elif regType == 3:
        extraCharNum = 7
    if 79 - len(regName) - len(regValueHexStr) - extraCharNum > 0:
        valueHexF = regValueHexStr + '\n'
    else:
        if 79 - len(regName) - extraCharNum <= 5:
            number = 3
        elif (79 - len(regName) - extraCharNum) % 3 == 0:
            number = 79 - len(regName) - extraCharNum
        elif (79 - len(regName) - extraCharNum) % 3 == 1:
            number = 79 - len(regName) - extraCharNum - 1
        else:
            number = 79 - len(regName) - extraCharNum - 2
        valueHexF = regValueHexStr[:number] + '\\\n'
        valueHexList = re.compile('.{1,75}').findall(
            regValueHexStr[number:])
        for i in range(len(valueHexList)):
            if i != len(valueHexList) - 1:
                valueHexF = valueHexF + '  ' + \
                    valueHexList[i] + '\\\n'
            else:
                valueHexF = valueHexF + '  ' + \
                    valueHexList[i] + '\n'
    return valueHexF

# 枚举键下的所有值并根据类型写值


def writeRegValue(key, regObj):
    try:
        enumValue_i = 0
        while True:
            regName, regValue, regType = winreg.EnumValue(key, enumValue_i)
            if regName == '':
                regName = '@'
            if regType == 1:      # REG_SZ
                regValue = regValue.replace('\\', '\\\\')
                regValue = regValue.replace(r'"', r'\"')
                if regName == '@':
                    regObj.write('%s="%s"\n' % (regName, regValue))
                else:
                    regObj.write('"%s"="%s"\n' % (regName, regValue))
            if regType == 2:      # REG_EXPAND_SZ
                if regValue == '':
                    regValue = '00,00'
                elif len(regValue) == 1:
                    regValueHexStr = str(hex(ord(regValue))[2:]) + ',00,00,00'
                else:
                    regValueHexStr = ',00,'.join(
                        str(hex(ord(c))[2:]) for c in regValue) + ',00,00,00'
                valueHexF = regValueFomat(regValueHexStr, regName, regType)
                regObj.write('"%s"=hex(%s):%s' %
                             (regName, regType, valueHexF))
            if regType == 3:      # REG_BINARY
                if regValue == None:
                    regValue = ''
                else:
                    regValueHexStr = ''
                    for regValue_i in range(len(regValue)):
                        regValueHexChar = '%02x' % regValue[regValue_i]
                        if regValue_i != len(regValue) - 1:
                            regValueHexStr = regValueHexStr + regValueHexChar + ','
                        else:
                            regValueHexStr = regValueHexStr + regValueHexChar
                    valueHexF = regValueFomat(regValueHexStr, regName, regType)
                regObj.write('"%s"=hex:%s' % (regName, valueHexF))
            if regType == 4:      # REG_DWORD
                regValue = '%08x' % regValue
                if regName == '@':
                    regObj.write('%s=dword:%s\n' % (regName, regValue))
                else:
                    regObj.write('"%s"=dword:%s\n' % (regName, regValue))
            if regType == 7:      # REG_MULTI_SZ
                if regValue == []:
                    regValue = '00,00\n'
                else:
                    regValueHex = ''
                    for regValue_i in range(len(regValue)):
                        if len(regValue[regValue_i]) == 1:
                            if regValue_i != len(regValue) - 1:
                                regValueHex = regValueHex + \
                                    str(hex(ord(regValue[regValue_i]))[
                                        2:]) + ',00,00,00,'
                            else:
                                regValueHex = regValueHex + \
                                    str(hex(ord(regValue[regValue_i]))[
                                        2:]) + ',00,00,00'
                        elif len(regValue[regValue_i]) > 1:
                            if regValue_i != len(regValue) - 1:
                                regValueHex = regValueHex + \
                                    ',00,'.join(
                                        str(hex(ord(c))[2:]) for c in regValue[regValue_i]) + ',00,00,00,'
                            else:
                                regValueHex = regValueHex + \
                                    ',00,'.join(
                                        str(hex(ord(c))[2:]) for c in regValue[regValue_i]) + ',00,00,00'
                    regValueHexStr = regValueHex + ',00,00'
                    valueHexF = regValueFomat(regValueHexStr, regName, regType)
                regObj.write('"%s"=hex(%s):%s' %
                             (regName, regType, valueHexF))
            if regType == 11:
                
            enumValue_i += 1
    except WindowsError:
        regObj.write('\n')

# 枚举注册表键及其子键


def writeRegKey(regPath, regObj):
    regRegx = re.compile(r'(.+?)\\(.+)')
    mo = regRegx.search(regPath)
    regHead = mo.group(1)
    regEnd = mo.group(2)

    if regHead == 'HKEY_LOCAL_MACHINE':
        regHeadKey = winreg.HKEY_LOCAL_MACHINE
    try:
        key = winreg.OpenKey(regHeadKey, regEnd,
                             reserved=0, access=winreg.KEY_READ)
        regObj.write('[' + regPath + ']' + '\n')
        writeRegValue(key, regObj)
        try:
            i = 0
            parentPath = regPath
            while True:
                regKey = winreg.EnumKey(key, i)
                regPath = parentPath + '\\' + regKey
                writeRegKey(regPath, regObj)
                i += 1
        except WindowsError:
            pass
    except:
        logging.warning('Not found: ' + regPath)

# 拷贝文件


def copyReg(displayFolder, reg_dict):
    regObj = codecs.open(
        displayFolder + '\\DisplayPnp.reg', 'w', 'utf8')
    regObj.write('Windows Registry Editor Version 5.00\n\n')
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
reg_dict, folder_list, file_dict = config_dict['reg'], config_dict['folder'], config_dict['file']
logging.info('Begin copying registry...')
copyReg(displayFolder, reg_dict)
logging.info('Begin copying folders...')
copyFolder(displayFolder, folder_list)
logging.info('Begin copying files...')
copyFile(displayFolder, file_dict)
config.close()
logging.info('Done!')

# 批量拷贝注册名字生成ini文件
# import re,codecs
# reg = open(r'D:\Work\云更新\tool\显卡pnp\显卡pnp\nvidia\397.64\win10\950.安装.reg','r',encoding = 'utf8')
# S = reg.read()
# T = re.compile(r'\[HKEY_LOCAL_MACHINE\\SOFTWARE\\Classes\\Interface\\\{.*\}\]').findall(S)
# for i in T:
#     i = i.lstrip('[')
#     i = i.rstrip(']')
#     print(i)
