import os
import glob

list_path = glob.glob(r'E:\MyProjects\python_tools\*')
for x in list_path:
    print(x.split('\\'))

