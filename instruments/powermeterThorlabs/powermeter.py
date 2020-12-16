import pyvisa as visa

class powermeter:
    def __init__(self):
        self.rm = visa.ResourceManager()
        self.connected = 0
        self.DeviceIdentifier = {'THORLABS','Thorlabs'} #A device will be considered a powermeter if its identity (i.e. the answer to '*IDN?') contains any of these words
        self.BeingZeroed = 0 #This flag is set to 1 while the powermeter is being zeroed, and it stops the continuos power reading
        
    def ListDevices(self):
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
    
    def ConnectDevice(self,DeviceName):
        self.ListDevices();
        if (DeviceName in self.listDevices):
            try:         
                self.instrument = self.rm.open_resource(DeviceName, timeout=1)
                Msg = self.instrument.query('*IDN?')
                ID = 1
            except visa.VisaIOError:
                Msg = "Error while connecting"
                ID = 0 
        else:
            Msg = "The specified name is not a valid device"
            ID = -1
        if(ID==1):
            self.connected = 1
            # sets = self.instrument.query('SET?')
            # self.settings = dict([e.split(' ', 1) for e in sets.split(';')[1:]])
        return (Msg,ID)
    
    def DisconnectDevice(self):
        if(self.connected == 1):
            try:         
                self.instrument.close()
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
            try:
                return ( float(self.instrument.query('measure:power?')), str(self.instrument.query('power:dc:unit?')).strip('\n') )
            except visa.VisaIOError:
                return (float("nan"),'W')
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
        