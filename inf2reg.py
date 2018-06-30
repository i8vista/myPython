import codecs
import pprint
import datetime
import re
import logging


def writereg(regObj, regName, regValue, regType):
    """Write regfile."""
    if regType == 'REG_SZ':
        regObj.write('"%s"="%s"\r\n' % (regName, regValue))
    elif regType == 'REG_DWORD':
        d = '%08d' % int(regValue[2:])
        regObj.write('"%s"=dword:%s\r\n' % (regName, regValue))
        # return '"%s"="%s"\r\n' % (regName, regValue)


def formatAllInf(value):
    """把INF字典值，按照行格式化为列表，并去掉注释、空格"""
    tlist = value.split('\r\n')
    newtlist = []
    for elem in tlist:
        if elem.find(';') > -1:
            elem = elem[:elem.find(';')]
        if len(elem) == 0:
            continue
        elem = elem.strip()
        newtlist.append(elem)
    return newtlist


def value2Dict(valueList):
    """把字典值按照等号，格式化为字典"""
    valueDict = {}
    for elem in valueList:
        key = elem[:elem.find('=')].strip()
        value = elem[elem.find('=')+1:].strip()
        valueDict[key] = value
    return valueDict


def value2Dict_list(valueList):
    """把字典值按照等号，格式化为字典，字典的值为列表"""
    valueDict = {}
    for elem in valueList:
        key = elem[:elem.find('=')].strip()
        value = elem[elem.find('=')+1:].strip()
        sublist = [elem.strip() for elem in value.split(',')]
        valueDict[key] = sublist
    return valueDict


def value2Dict_reverse(valueList, seq):
    """把字典值按照等号，格式化为字典，字典的key为指定的列，字典value为列表"""
    valueDict = {}
    for elem in valueList:
        item = elem[:elem.find('=')].strip()
        value = elem[elem.find('=')+1:].strip()
        sublist = [elem.strip() for elem in value.split(',')]
        key = sublist.pop(seq-1)
        sublist.append(item)
        valueDict[key] = sublist
    return valueDict


def value2list(valueList):
    """把字典值按照等号，格式化为列表"""
    _value = valueList[0][valueList[0].find('=')+1:].strip()
    _valueList = [elem.strip() for elem in _value.split(',')]
    return _valueList


def value2reglist(valueList, reg_class_path, regObj):
    for i in range(len(valueList)):
        valueList[i] = valueList[i].split(',')
        valueList[i] = [elem.strip() for elem in valueList[i]]
        if valueList[i][0] == 'HKR':
            reg_path = reg_class_path + '\\' + valueList[i][1]
            if i == 0 or valueList[i][1] != valueList[i-1][1]:
                regObj.write('\r\n')
                regObj.write(reg_path +'\r\n')
        if valueList[i][3] == '0':
            regType = 'REG_SZ'
        regName = valueList[i][2]
        regValue = valueList[i][4]
        writereg(regObj, regName, regValue, regType)    
    """把字典值中的reg部分格式化为列表"""

# 把inf安装section格式化为字典
osVer = 'NTx86'
device_id = 'PCI\\VEN_15AD&DEV_0720'
infFile = codecs.open('vmxnet.inf', "r", encoding='utf8')
infStr = infFile.read()
infStrList = infStr.split('[')
fsSectionDict = {}
for infStr in infStrList:
    if infStr.find(']') > 0:
        key = infStr[:infStr.find(']')]
        value = infStr[infStr.find(']')+1:]
        valueList = formatAllInf(value)
        fsSectionDict[key] = valueList
# pprint.pprint(fsSectionDict)

#查找section并根据section名，采用不同的方式初始化值
for k, v in fsSectionDict.items():
    if re.compile('Version$', re.I).search(k) != None:
        section_Version = value2Dict(v)
        continue
    if re.compile('Strings$', re.I).search(k) != None:
        section_Strings = value2Dict(v)
        continue
    if re.compile('Manufacturer$', re.I).search(k) != None:
        section_OSVersion = value2list(v)
        continue



#匹配硬件ID，与操作系统版本，获取硬件的device_description和install_section_name
if osVer in section_OSVersion:
    if osVer != section_OSVersion[0]:
        osVer = section_OSVersion[0] + '.' + osVer
else:
    osVer = section_OSVersion[0]
for k, v in fsSectionDict.items():    
    if re.compile('%s$' % osVer, re.I).search(k) != None:
        section_Models = value2Dict_reverse(v, 2)
        break
if device_id in section_Models:
    device_description = section_Models[device_id][0]
    install_section_name = section_Models[device_id][1].strip('%')
else:
    logging.warning('can not find: ' )

for k, v in fsSectionDict.items(): 
    if re.compile('%s.NT.Services$' % device_description, re.I).search(k) != None:
        section_AddService = value2list(v)
        driver_ServiceName = section_AddService[0]
        service_install_section = section_AddService[2]
        continue
    if re.compile('%s.NT$' % device_description, re.I).search(k) != None:
        section_DDInstall = value2Dict(v)
        

#解析Version节
for k, v in section_Version.items():
    if re.compile('Signature$', re.IGNORECASE).search(k) != None:
        driver_Signature = v
        continue
    if re.compile('Class$', re.I).search(k) != None:
        driver_Class = v
        continue
    if re.compile('ClassGUID$', re.I).search(k) != None:
        driver_ClassGUID = v
        continue
    if re.compile('Provider$', re.I).search(k) != None:
        driver_ProviderVar = v.strip('%')
        continue
    if re.compile('DriverVer$', re.I).search(k) != None:
        driver_DriverVer = v
        driver_DriverDate = v[:v.find(',')].strip()
        driver_DriverVersion = v[v.find(',')+1:].strip()
        continue

#解析string节
for k, v in section_Strings.items():
    if re.compile('^%s$' % driver_ProviderVar, re.I).search(k) != None:
        driver_Provider = v.strip('\"')
    if re.compile('^%s$' % install_section_name, re.I).search(k) != None:
        driver_DeviceDesc = v.strip('\"')

#解析DDInstall节
for k, v in section_DDInstall.items():
    if re.compile('Characteristics$', re.IGNORECASE).search(k) != None:
        driver_Characteristics = v
    if re.compile('BusType$', re.IGNORECASE).search(k) != None:
        driver_BusType = v
    if re.compile('AddReg$', re.IGNORECASE).search(k) != None:
        install_addReg_section = v
    if re.compile('CopyFiles$', re.IGNORECASE).search(k) != None:
        install_copyFile_section = v

#解析class下的注册表
for k, v in fsSectionDict.items():
    if re.compile('^%s$' % install_addReg_section, re.I).search(k) != None:
        driver_install_addReg_section = v

#解析服务
for k, v in fsSectionDict.items():
    if re.compile('^%s$' % service_install_section, re.I).search(k) != None:
        driver_service_install_section = value2Dict(v)
        break

for k, v in driver_service_install_section.items():        
    if re.compile('DisplayName$', re.IGNORECASE).search(k) != None:
        driver_DisplayName = driver_service_install_section['DisplayName']
    if re.compile('ServiceBinary$', re.IGNORECASE).search(k) != None:
        driver_ImagePath = driver_service_install_section['ServiceBinary']
    if re.compile('LoadOrderGroup$', re.IGNORECASE).search(k) != None:
        driver_Group = driver_service_install_section['LoadOrderGroup']
    if re.compile('ServiceType$', re.IGNORECASE).search(k) != None:
        driver_Type = driver_service_install_section['ServiceType']
    if re.compile('StartType$', re.IGNORECASE).search(k) != None:
        driver_Start = driver_service_install_section['StartType']
    if re.compile('ErrorControl$', re.IGNORECASE).search(k) != None:
        driver_ErrorControl = driver_service_install_section['ErrorControl']

regObj = codecs.open('inf_%s.reg' % datetime.datetime.now().strftime(
    '%Y%m%d%H%M%S'), 'w', 'utf_16')
regObj.write('Windows Registry Editor Version 5.00\r\n\r\n')
regObj.write('[HKEY_LOCAL_MACHINE\\SYSTEM\\kpnp\\VEN_15AD&DEV_0720\\Pci]\r\n')
writereg(regObj, regName='Class', regValue=driver_Class, regType='REG_SZ')
writereg(regObj, regName='ClassGUID',
         regValue=driver_ClassGUID, regType='REG_SZ')
writereg(regObj, regName='ConfigFlags',
         regValue='00000000', regType='REG_DWORD')
writereg(regObj, regName='Driver',
         regValue=driver_ClassGUID + '\\\\2000', regType='REG_SZ')
writereg(regObj, regName='Service',regValue=driver_ServiceName, regType='REG_SZ')
writereg(regObj, regName='Mfg',regValue=driver_Provider, regType='REG_SZ')
writereg(regObj, regName='DeviceDesc',regValue=driver_DeviceDesc, regType='REG_SZ')
regObj.write('\r\n')
regObj.write('[HKEY_LOCAL_MACHINE\\SYSTEM\\kpnp\\VEN_15AD&DEV_0720\\Class]\r\n')
reg_class_path = 'HKEY_LOCAL_MACHINE\\SYSTEM\\kpnp\\VEN_15AD&DEV_0720\\Class'
writereg(regObj, regName='BusType', regValue=driver_BusType, regType='REG_SZ')
writereg(regObj, regName='Characteristics', regValue=driver_Characteristics, regType='REG_DWORD')
writereg(regObj, regName='InfSection', regValue='%s.NT$' % device_description, regType='REG_SZ')
writereg(regObj, regName='DriverDesc', regValue=driver_DeviceDesc, regType='REG_SZ')
writereg(regObj, regName='DriverVersion', regValue=driver_DriverVersion, regType='REG_SZ')
writereg(regObj, regName='DriverDate', regValue=driver_DriverDate, regType='REG_SZ')
writereg(regObj, regName='ProviderName', regValue=driver_Provider, regType='REG_SZ')
writereg(regObj, regName='ComponentId', regValue=device_id, regType='REG_SZ')
value2reglist(driver_install_addReg_section, reg_class_path, regObj)
regObj.write('\r\n')
regObj.write('[HKEY_LOCAL_MACHINE\\SYSTEM\\kpnp\\VEN_15AD&DEV_0720\\Service]\r\n')
writereg(regObj, regName='DisplayName', regValue=driver_DisplayName, regType='REG_SZ')
writereg(regObj, regName='ImagePath', regValue=driver_ImagePath, regType='REG_SZ')
writereg(regObj, regName='Group', regValue=driver_Group, regType='REG_SZ')
writereg(regObj, regName='Type', regValue=driver_Type, regType='REG_DWORD')
writereg(regObj, regName='Start', regValue=driver_Start, regType='REG_DWORD')
writereg(regObj, regName='ErrorControl', regValue=driver_ErrorControl, regType='REG_DWORD')
regObj.close()
