# Dumping data from binary files

Here you can find the commented code used in [spectroscopy-output-test.py](/Dumping_from_binary_files/spectroscopy-output-test.py) for dumping data from a [Spectroscopy](/Spectroscopy/spectroscopy.py) output binary file and post-process them.

##### Needed libraries 

```

import os
import glob
import struct
import matplotlib.pyplot as plt
import numpy as np

```

##### Select the file

Get the current working directory and list all the files in the directory. 

```

cwd = os.getcwd()

files = glob.glob(os.path.join(cwd, "spectroscopy-output-*.bin"))
file = None

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

```

You will be prompted to select a file from a list of filenames that match the specified pattern *spectroscopy-output* :

![Prompt](/images/prompt_1.png "command prompts")

Then type the file to be read.

##### Open the file and extract binary data

The file is opened in binary mode and the microtime values are extracted using the *struct* library. The microtime values are stored in an array and then converted to a NumPy array for plotting.

```

microtime_array=[]

with open(file, "rb") as f:
    
    while f.read(1):       
        microtime = struct.unpack('d', f.read(8))
        macrotime = struct.unpack('d', f.read(8))
        microtime_array.append(microtime) 
        
microtime_asarray = np.asarray(microtime_array)

```

The extracted microtime value refers to the arrival time of the photon event within the laser period as shown in this figure for a visual reference:

![input parameters](/images/mic-mac.jpg "parameters")

##### Plot the histogram of the extracted data

You can visualize and post-process the extracted data depending on your needings. As an example here it is shown the code for plotting the histogram of the extracted photons' microtime values:

```

plt.hist(microtime_asarray, bins=256)
plt.xlabel('Microtime')
plt.ylabel('Counts')
plt.title('Microtime Histogram')

plt.show()

```

<img src="/images/histogram_dump.png" style="width:720px;height:381px;">
