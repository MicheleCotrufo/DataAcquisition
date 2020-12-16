# Data Acquisition
A Python modular interface to interface to different instruments and automatize data acquisition


<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Installation](#installation)
* [Usage](#usage)
* [License](#license)


<!-- ABOUT THE PROJECT -->
## About The Project




### Built With
The software is built with Python, Tkinter, and it uses the NI-VISA and py-visa libraries for certain instruments. I learnt several commands and procedures related to VISA & oscilloscope by reading the code of PyTektronixScope (https://github.com/clade/PyTektronixScope)

<!-- GETTING STARTED -->
## Getting Started

The software has been tested with Python 3.8.5 on Windows 10. It should work on other operating systems as well. To install, clone the repo (or simply download the whole code) anywhere on your computer.



### Installation

1. Check that the Python version is > 3.8.5 (The software might work with other versions)
2. Make sure that tkinter is installed (```pip install tkinter```)
3. Install numpy (```pip install numpy```)
4. Install matplotlib>3.3.1 (```pip install matplotlib>3.3.1```)

Different intruments will require different additional libraries. Many instruments (e.g. the Tektronik scope and the Thorlabs powermeter) work with the pyvisa library. Install pyvisa (```pip install pyvisa```)

#### Thorlabs powermeter
The Thorlabs powermeter does not require any additional library apart from pyvisa!

#### Tektronix scope
The Tektronix scope requires the pyvisa library, and it is necessary to install also the NI-VISA library from https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html#346210. 
IMPORTANT: the library TEKVisa might generate conflicts with the library pyvisa. Before proceeding with installation, make sure you uninstall any version of TEKVisa. Usually this library gets installed together with the OpenChoice software from Tektronix.

#### Ophir powermeter
The ophir powermeter does not work with the pyvisa library, the communication is instead provided through the pywin32 library.
Install via ``` pip install pywin32 ```.
Note: The ophir powermeter also needs to be enabled for USB communication, which might require buying as serial code from Ophir.


<!-- USAGE EXAMPLES -->
## Usage
A .json file is used to specify the software settings. In this file we can specify how many and which instruments to connect to the software, which data to extract from each instrument, which plots to show, etc. One can create different .json files corresponding to different interfaces.
One the .json file has been created, launch the software with command line
```
python "Path\To\MainApplication\MainApplication.pyw" "Path\To\jsonFile\FileName.json"
```


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


