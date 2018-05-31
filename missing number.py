import os,shutil,re
folder = r'd:\test'
filelist = os.listdir(folder)
print(filelist)
newFilelist = []
filenameRegex = re.compile(r'^spam\d\d\d\.txt$')
for filename in filelist:
    if filenameRegex.search(filename) != None:
        newFilelist.append(filename)

newFilelist.sort()
print(newFilelist)
for i in range(len(newFilelist)):
    if newFilelist[i] != 'spam%03d.txt' % (i+1):
        print('we lost '+ newFilelist[i])
        shutil.move(os.path.join(folder,newFilelist[i]),os.path.join(folder,'spam%03d.txt' % (i+1)))
    
