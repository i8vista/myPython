import os
for foldername, subfoldernames, filenames in os.walk(r'e:'):
    for filename in filenames:
        if os.path.getsize(os.path.join(foldername,filename)) /1024/1024 > 100:
            print(os.path.join(foldername,filename))
