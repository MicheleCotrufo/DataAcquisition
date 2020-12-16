# Use of Ophir COM object. 
# Works with python 3.5.1 & 2.7.11
# Uses pywin32
import win32gui
import win32com.client
import time
import traceback

class powermeter:
    def __init__(self):
        self.connected = 0
        self.OphirCOM = None
        self.BeingZeroed = 0 #This flag is set to 1 while the powermeter is being zeroed, and it stops the continuos power reading
        
    def ListDevices(self,KeepOpen=0):
        if (self.OphirCOM == None):
            self.OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement") #Creates the COM object. This will not return an error if the powermeter is not connected.
        self.listAllDevices = self.OphirCOM.ScanUSB();
        self.listDevices = [] 
        self.listIDN = []
        for device in  self.listAllDevices:
            self.listDevices.append(device)
            self.listIDN.append('Ophir') #This  is just to ensure compatibility with other code. Each device must have an 'address' (contained in self.listDevices) and a 'name', which in this case is set to 'Ophir' for any device
        if KeepOpen==0:
            self.OphirCOM.StopAllStreams()
            self.OphirCOM.CloseAll()
            self.OphirCOM = None
        return (self.listDevices,self.listIDN)
    
    def ConnectDevice(self,DeviceName):
        self.ListDevices(KeepOpen = 1);
        if (DeviceName in self.listDevices):
            try:         
                DeviceHandle = self.OphirCOM.OpenUSBDevice(DeviceName)
                exists = self.OphirCOM.IsSensorExists(DeviceHandle, 0)
                if exists:
                    self.instrument = DeviceHandle
                    Msg = 'Connected.'
                    ID = 1
            except OSError as err:
                Msg = "The device name is valid, but connection was not possible due to OS error: {0}".format(err)
                ID = 0 
        else:
            Msg = "The specified name is not a valid device"
            ID = -1
        if(ID==1):
            self.connected = 1
            self.OphirCOM.StartStream(self.instrument, 0)		# start measuring
        else:
            self.OphirCOM.StopAllStreams()
            self.OphirCOM.CloseAll()
            # Release the object
            self.OphirCOM = None
        return (Msg,ID)
    
    def DisconnectDevice(self):
        if(self.connected == 1):
            try:         
                # Stop & Close all devices
                self.OphirCOM.StopAllStreams()
                self.OphirCOM.CloseAll()
                # Release the object
                self.OphirCOM = None
                ID = 1
            except Exception:
                ID = 0 
            if(ID==1):
                self.connected = 0
            return ID
        else:
            return -1

    def ReadPower(self):
        if(self.BeingZeroed ==0):
            #try:
            while True:
                data = self.OphirCOM.GetData(self.instrument, 0)
                if len(data[0]) > 0:
                    break
            return ( float(data[0][-1]), 'W')
            # except OSError as err:
            #     return (float("nan"),'W')
        else:
            return (0,'W')
        
    def SetZero(self):
        if(self.connected==1):
            try:
                self.BeingZeroed = 1
                ID = self.instrument.write('sense:correction:collect:zero')
                self.BeingZeroed = 0
            except visa.VisaIOError:
                ID = 0
                pass
        return ID
        