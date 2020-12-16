# Data Acquisition: Oscilloscope&Powermeter
A Python interface to automatize data acquisition from a Tektronix scope and a Thorlabs powermeter - and it comes with a GUI!


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

I developed this Python script / GUI to automatize some measurement in the lab. The software read data from the two channels of a Tektronix oscilloscope and from a Thorlabs powermeter, and it creates in real-time plots of, for example, the peak-to-peak voltage of each scope channel (or their ratio) versus power, or versus the acquisition number. The plots are generated either continuosly or when the user decides so. Each data point can correspond to an instantaneous read, or it can be calculated as an average (accompanied by a standard deviation) over a certain number of acquisition.

The software is designed for an experiment where the powermeter is used to measure the power impinging on a sample, and two photodiodes (connected to the two channels of the oscilloscope) are used to measure the fraction of the power transmitted through the sample. 


### Built With
The software is built with Python, Tkinter, and it uses the NI-VISA and py-visa libraries. I learnt several commands and procedures related to VISA & oscilloscope by reading the code of PyTektronixScope (https://github.com/clade/PyTektronixScope)

<!-- GETTING STARTED -->
## Getting Started

The software has been tested with Python 3.8.5 on Windows 10. It should work on other operating systems as well. To install, clone the repo (or simply download the whole code) anywhere on your computer.

IMPORTANT: the library TEKVisa might generate conflicts with the library pyvisa used by this software. Before proceeding with installation, make sure you uninstall any version of TEKVisa. Usually this library gets installed together with the OpenChoice software from Tektronix.

### Installation

1. Check that the Python version is > 3.8.5 (The software might work with other versions)
2. Make sure that tkinter is installed (pip install tkinter)
3. Install numpy (pip install numpy)
4. Install matplotlib>3.3.1 (pip install matplotlib>3.3.1)
5. Install the NI-VISA library from https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html#346210
6. Install pyvisa (pip install pyvisa)

<!-- USAGE EXAMPLES -->
## Usage

Just run the file main.pyw, either via the command 'python main.pyw' or by double-clicking on it (if the operating system is properly set to open .pyw files via python). This will start the GUI.

![Image of GUI](https://github.com/MicheleCotrufo/DataAcquisition_Oscilloscope-Powermeter/blob/main/docs/docs1.png?raw=true)

When started the software automatically looks for any oscilloscope and/or powermeter connected to the computer. The devices are recognized as scopes or powermeters by looking for specific keywords in the answer they send to the query '*IDN?' (see code of files instruments/scope.py and instruments/powermeter.py for list of keywords). The dropdown lists labeled 'Device list:' in the 'Scope settings' and 'Powermeter settings' panels are populated with the corresponding devices found. Each list can be refreshed at any moment by clicking the corresponding 'Refresh' button. 

After a device is selected, connection can be established by clicking on 'Connect'. If connection is succesful, the corresponding 'Connect' button will turn its caption into 'Disconnect', and the software will start to read data continuosly from the device, at a rate set by the value specified by the user in the corresponding  textbox (note: the effective refresh rate might be slower due to delay in communication with the devices. For the scope, it is recommended to use a refresh rate bigger than 0.2s).

### Oscilloscope
The raw data from the two channels of the oscilloscope is continuosly updated and shown in the left-most plot. The continuous reading can be stopped at any time by clicking on the 'STOP' button in the 'Scope settings' panel, and re-started by clicking on the 'RUN' button. The user can choose which channel is continuosly acquired by (de)selecting the corresponding checkboxes in the 'Scope settings' panel (if only one channel is required, deselecting the other channel will speed up acquisition). If the checkbox "Boost" is selected, certain parameters regarding the horizontal and vertical axis of the raw data will be acquired only one time, during the first acquisition. This trick (inspired by https://github.com/clade/PyTektronixScope) can drastically reduce the time required to transfer data from the scope to the computer. However, this only works well if the scope settings (such as vertical and horizontal zoom and translation) are not manually changed on the scope during the continuous acquisition. 
If any of these settings needs to be manually changed during the measurements, after all changes are done stop the continuous acquisition (click on 'STOP') and restart it again (click on 'RUN'), so that the axis parameters are properly stored in the software. This procedure needs to be repeated **everytime** any scope setting is manually changed. In alternative, the checkbox "Boost" can be kept de-selected: in this case the axis parameters will be always read before every acquisition (at the cost of slower reading time)


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


