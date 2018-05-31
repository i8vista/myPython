import os,shutil
for foldername, subfoldernames, filenames in os.walk(r'c:\windows\inf'):
    for filename in filenames:
        if filename.endswith('.inf'):
            shutil.copy(os.path.join(foldername,filename),r'e:\software\wzw')