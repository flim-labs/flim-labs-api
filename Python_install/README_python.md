# Python 3.10.0 Installation

## Prerequisites

Before you begin, ensure that your system meets the following prerequisites:

    - Operating System: Windows, macOS, or Linux
    - Internet connection for downloading the Python installer (if not already downloaded)
    - Sufficient disk space for the installation

## Check your Python version

If you have already installed Python on your computer, run the following command on your terminal or command prompt to show which version is installed:

```
python --version

```

## Installation steps

Follow the steps below to install Python 3.10.0 on your system:

1. Download the Python Installer:

        * Visit the official Python website at python.org.
		
        * Click on the "Downloads" tab.
		
        * Scroll down to find the "Python 3.10.0" release and select the installer appropriate for your operating system:
		
            * For Windows: Choose the "Windows installer" or "Windows x86-64 executable installer."
			
            * For macOS: Choose the "macOS 64-bit installer."
			
            * For Linux: Choose the package appropriate for your distribution (e.g., ".tar.gz" or ".deb").
			
        * Download the installer to your local machine.
		
2.  Run the Installer:

        * Windows:
		
         * Locate the downloaded installer (e.g., python-3.10.0-amd64.exe).
		 
         * Double-click the installer to launch it.
		 
         * On the first installer page, ensure the option "Add Python 3.10 to PATH" is selected, as shown in figure:
		 
		 ![Python_setup](/images/Python_setup.svg "Add Python to PATH")
		 
         * Click "Customize installation" if you want to modify the installation settings, or click "Install Now" to proceed with the default settings.
		 
         * The installer will install Python and show a progress bar.
		 
         * Once the installation is complete, you can close the installer.

        * macOS:
		
         * Locate the downloaded installer (e.g., python-3.10.0-macosx10.9.pkg).
		 
         * Double-click the installer to launch it.
		 
         * Follow the on-screen instructions provided by the installer.
		 
         * Once the installation is complete, you can close the installer.

        * Linux:
		
         * Open a terminal.
		 
         * Navigate to the directory where you downloaded the installer.
		 
         * Extract the installer if necessary (e.g., using tar -xzvf Python-3.10.0.tar.gz).
		 
         * Navigate into the extracted directory (e.g., cd Python-3.10.0).
		 
         * Run the following command to configure the installation:
		  
		  ```
		  
          ./configure --enable-optimizations

          ```
		  
		 * Run the following command to start the installation: 
		  
		  ```
		  
          make -j <number_of_cores>


          ```
		  
		 Replace <number_of_cores> with the number of CPU cores on your system for faster compilation. If unsure, you can omit the -j option.
		  
		 * After the installation completes, run the following command to install Python:

          ```
		  
          sudo make altinstall


          ```
		  
         Python 3.10.0 will be installed on your system. 		  

3.	Verify the installation	 

        * Open a new terminal or command prompt.
		
        * Run the following command to check if Python 3.10.0 is installed:
		
		 ```
		  
         python --version



         ```
		
        * The output should display Python 3.10.0. 		