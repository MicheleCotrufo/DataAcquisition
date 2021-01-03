
import pyvisa as visa
import numpy as np  

class scope_virtual:
    def __init__(self):
        self.rm = visa.ResourceManager()
        self.AxisParametersAcquired = {'CH1': 0, 'CH2':0}
        self.offset = {'CH1': 0, 'CH2':0}
        self.scale = {'CH1': 0, 'CH2':0}
        self.yzero = {'CH1': 0, 'CH2':0}
        self.x_0 = {'CH1': 0, 'CH2':0}
        self.delta_x = {'CH1': 0, 'CH2':0}
        self.DeviceIdentifier = {'TEKTRONIX'} #A device will be considered an oscilloscope if its identity (i.e. the answer to '*IDN?') contains any of these words
        self.booster = 0
        self.connected = 0
        
    def ListDevices(self):
        self.listAllDevices = self.rm.list_resources();
        self.listDevices = ['Virtual_Scope_Address'] 
        self.listIDN = ['Virtual Scope']
        # for addr in self.listAllDevices:
        #     if(not(addr.startswith('ASRL'))):
        #         try:
        #             idn = self.rm.open_resource(addr).query('*IDN?').strip()
        #             if(any(word in idn for word  in self.DeviceIdentifier)):
        #                 self.listIDN.append(idn)   
        #                 self.listDevices.append(addr)    
        #         except visa.VisaIOError:
        #             pass
        return (self.listDevices,self.listIDN)
    
    def ConnectDevice(self,DeviceName):
        self.ListDevices();
        if (DeviceName in self.listDevices and DeviceName=='Virtual_Scope_Address'):
            ID = 1
            Msg = "Connected to virtual scope"
        else:
            Msg = "The specified name is not a valid device"
            ID = -1
        if(ID==1):
            self.connected = 1
        return (Msg,ID)
    
    def DisconnectDevice(self):
        if(self.connected == 1):
            try:
                ID = 1
            except Exception:
                ID = 0 
            if(ID==1):
                self.connected =0
            return ID
        else:
            return -1
        
    def ResetAxisParametersAcquired(self):    
        self.AxisParametersAcquired = {'CH1': 0, 'CH2':0}
        
        
    def SetChannel(self, ChannelName):
        #Virtual function to set channel
        return
        
    def ReadParametersYAxis(self):
        offset = 0
        scale = 1
        yzero = 0
        return (offset,scale,yzero)
    
    def ReadParametersXAxis(self):
        x_0 = 0
        delta_x = 0.1
        return (x_0,delta_x)
        
    def GetCurveFromChannel(self, ChannelName):
        if(self.connected == 0):
            print("Error: trying to read from the scope while the scope is not connected")
            return
        self.SetChannel(ChannelName)
        #print(self.booster)
        #print(self.AxisParametersAcquired)
        if(self.booster==0 or self.AxisParametersAcquired[ChannelName]==0):
            #print("Acquiring axis parameters...")    
            #self.instrument.write("DATA:ENCDG RIB")
            #self.instrument.write("WFMO:BYTE_NR 2")
    
            (self.offset[ChannelName] ,self.scale[ChannelName] ,self.yzero[ChannelName] ) = self.ReadParametersYAxis()
            (self.x_0[ChannelName] ,self.delta_x[ChannelName] ) = self.ReadParametersXAxis()
            self.AxisParametersAcquired[ChannelName] = 1

        xaxis = np.arange(0, 1024)
        values = np.heaviside(xaxis-100,0)*np.exp(-(xaxis-100)/300)
        X_axis = self.x_0[ChannelName]  + np.arange(0, len(values))*self.delta_x[ChannelName]             
        Y_axis = (values - self.offset[ChannelName] )*self.scale[ChannelName]  + self.yzero[ChannelName] 
        
        return (X_axis, Y_axis)