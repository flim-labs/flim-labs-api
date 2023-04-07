import os
import glob
import struct
import matplotlib.pyplot as plt
import numpy as np

# get current working directory
cwd = os.getcwd()

# list all files in this directory
files = glob.glob(os.path.join(cwd, "spectroscopy-output-*.bin"))
file = None

# select file to be read
while True:
    try:
        for i in range(len(files)):
            print(str(i) + ": " + files[i].replace(os.path.join(cwd, "spectroscopy-output-"), "").replace(".bin", ""))
        file = files[int(input("Select file: "))]
    except:
        print("Please enter a valid selection")
        continue
    else:
        break
        
microtime_array=[]

with open(file, "rb") as f:
    
    while f.read(1):       
        microtime = struct.unpack('d', f.read(8))
        macrotime = struct.unpack('d', f.read(8))
        microtime_array.append(microtime) 
        
microtime_asarray = np.asarray(microtime_array)

plt.hist(microtime_asarray, bins=256)
plt.xlabel('Microtime')
plt.ylabel('Counts')
plt.title('Microtime Histogram')

plt.show()

        

