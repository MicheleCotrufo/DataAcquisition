import pyvisa as visa
import numpy as np  

class scope:

    def __init__(self,DeviceIdentifier,virtualMode=0):
        self.rm = visa.ResourceManager()
        self.AxisParametersAcquired = {'CH1': 0, 'CH2':0}
        self.offset = {'CH1': 0, 'CH2':0}
        self.scale = {'CH1': 0, 'CH2':0}
        self.yzero = {'CH1': 0, 'CH2':0}
        self.x_0 = {'CH1': 0, 'CH2':0}
        self.delta_x = {'CH1': 0, 'CH2':0}
        self.DeviceIdentifier = DeviceIdentifier #A device will be considered an oscilloscope if its identity (i.e. the answer to '*IDN?') contains any of these words
        self.booster = 0
        self.connected = 0
        self.xaxis = {'CH1':[0],'CH2':[0]} #Initialize the x and y axis of each channel to [0]
        self.yaxis = {'CH1':[0],'CH2':[0]}
        self.virtualMode = 0 #When this variable is set to 1, we are working in virtual mode (no need to have a device connected). This is useful for testing purposes
        
    def ListDevices(self):
        if(self.virtualMode==1):
            self.listDevices = ['Virtual_Scope_Address'] 
            self.listIDN = ['Virtual Scope']
            return

        self.listAllDevices = self.rm.list_resources();
        self.listDevices = [] 
        self.listIDN = []
        for addr in self.listAllDevices:
            if(not(addr.startswith('ASRL'))):
                try:
                    idn = self.rm.open_resource(addr).query('*IDN?').strip()
                    if(any(word in idn for word  in self.DeviceIdentifier)):
                        self.listIDN.append(idn)   
                        self.listDevices.append(addr)    
                except visa.VisaIOError:
                    pass
        return (self.listDevices,self.listIDN)
    
    # def Query(self,q):
    #     if(self.virtualMode==0):
    #         return self.instrument.query(q)
    #     else:
            
    
    def ConnectDevice(self,DeviceName):
        #self.ListDevices();
            
        if (DeviceName in self.listDevices):
            if(self.virtualMode==1): 
                self.instrument = VirtualInstrument()
                self.connected = 1
                return ('Connected to virtual scope',1)
            try:         
                self.instrument = self.rm.open_resource(DeviceName)
                Msg = self.instrument.query('*IDN?')
                ID = 1
            except Exception:
                Msg = "Error while connecting"
                ID = 0 
        else:
            Msg = "The specified name is not a valid device"
            ID = -1
        if(ID==1):
            self.connected = 1
            sets = self.instrument.query('SET?')
            self.settings = dict([e.split(' ', 1) for e in sets.split(';')[1:]])
        return (Msg,ID)
    
    def DisconnectDevice(self):
        if(self.connected == 1):
            try:         
                self.instrument.close()
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
        self.instrument.write('DAT:SOUR '+ChannelName)   
        
    def IsChannelSelected(self, ChannelName):
        return int(self.instrument.query('SEL:'+ChannelName+'?'))   
        
    def ReadParametersYAxis(self):
        offset = float(self.instrument.query('WFMO:YOF?'))
        scale = float(self.instrument.query('WFMO:YMU?'))
        yzero = float(self.instrument.query('WFMO:YZE?'))
        return (offset,scale,yzero)
    
    def ReadParametersXAxis(self):
        x_0 = float(self.instrument.query('WFMO:XZERO?')) #x0
        delta_x = float(self.instrument.query('WFMO:XIN?')) #xstep
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
            self.instrument.write("DATA:ENCDG RIB")
            self.instrument.write("WFMO:BYTE_NR 2")
    
            (self.offset[ChannelName] ,self.scale[ChannelName] ,self.yzero[ChannelName] ) = self.ReadParametersYAxis()
            (self.x_0[ChannelName] ,self.delta_x[ChannelName] ) = self.ReadParametersXAxis()
            self.AxisParametersAcquired[ChannelName] = 1

        values =np.array(self.instrument.query_binary_values('CURV?', datatype='b')) #'b' = short signed integer. Depending on the oscilloscope used and on the computer, you may need to change it
        X_axis = self.x_0[ChannelName]  + np.arange(0, len(values))*self.delta_x[ChannelName]             
        Y_axis = (values - self.offset[ChannelName] )*self.scale[ChannelName]  + self.yzero[ChannelName] 
        self.xaxis[ChannelName]  = X_axis
        self.yaxis[ChannelName]  = Y_axis
        return
    
    
# class  VirtualInstrument:
#     def __init__(self):
#         return
#     def close(self):
#         return 1
#     def write(self,str):
#     def query(self,q):
        