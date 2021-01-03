import tkinter as tk
from tkinter import ttk as ttk
from .powermeter import powermeter
from ..instrument import instrument

class interface(instrument):
    Data = {'Power':0,'PowerUnits':'W'} #The dictionary Data is what will be read by the main program. Each 'interface' object must have a 'Data' property

    def __init__(self, parent, root):
        super().__init__(parent,root)
        self.Data = {'Power':0,'PowerUnits':'W'} #The dictionary Data is what will be read by the main program. Each 'interface' object must have a 'Data' property
        self.ContinuousRead = 0 #When this is set to 1, the data from powermeters are acquired continuosly at the rate set by self.RefreshRate
        self.RefreshRate = 1 #in seconds
        self.instrument = powermeter() #Each SettingPanel needs to be associated to an instrument object
        
    def CreatePanelGUI(self,master):    
        self.master = master #This is the frame which contains this panel
      
        self.frame = tk.LabelFrame(self.master,text="Ophir Powermeter ")
        self.labelDevice = tk.Label(self.frame, text="Device list: ")
        self.labelDevice.grid(row=0,column=0, sticky=tk.W,pady=3,padx=5)
        self.menuDevices = ttk.Combobox(self.frame,width=16,state="readonly")
        self.menuDevices.grid(row=0,column=1, sticky=tk.W,pady=3,padx=5)
        
        self.ButtonRefreshDeviceList = tk.Button(self.frame, text="Refresh", width=16, command=self.RefreshListPowermeters)
        self.ButtonRefreshDeviceList.grid(row=1,column=0, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)
        
        self.ButtonConnectDevice = tk.Button(self.frame, text="Connect",width=16, command=self.ConnectPowermeter)
        self.ButtonConnectDevice.grid(row=1,column=1, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=1)
        
        self.labelRefreshRate = tk.Label(self.frame, text="Refresh rate (s) = ")
        self.labelRefreshRate.grid(row=2,column=0, sticky=tk.W,pady=3,padx=5)
        self.EntryRefreshRate = tk.Entry(self.frame)
        self.EntryRefreshRate.insert(0, "0.2")
        self.EntryRefreshRate.grid(row=2,column=1, sticky=tk.W,pady=3,padx=5)
        self.ButtonExplanationRefreshRate = tk.Button(self.frame, text="?", width=3, command=self.ExplanationPowermeterRefreshRate)
        self.ButtonExplanationRefreshRate.grid(row=2,column=2, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)
        
        self.ButtonStartReadPower= tk.Button(self.frame, text="Start Reading Power", width=16, command=self.StartStopReadingPower)
        self.ButtonStartReadPower.grid(row=3,column=0, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)
        #self.ButtonSetZeroPowermeter = tk.Button(self.frame, text="Set Zero Powermeter", width=16, command=self.SetZeroPowermeter)
        #self.ButtonSetZeroPowermeter.grid(row=3,column=1, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)
        

        self.labelPowerText = tk.Label(self.frame, text="Power: ",font=("Helvetica", 20))
        self.labelPowerText.grid(row=4,column=0, sticky=tk.W,pady=3,padx=5)
        
        
        self.currentPowerString =  tk.StringVar()
        self.labelPower = tk.Label(self.frame, textvariable=self.currentPowerString , font=("Helvetica", 20),width=7, anchor="e")
        self.labelPower.grid(row=4,column=1, sticky=tk.N+tk.S+tk.E+tk.W,pady=3,padx=5,columnspan=2)
        
        self.SetWidgetsToDisconnectedState()

        self.RefreshListPowermeters()
        return self
        
        
    def ExplanationPowermeterRefreshRate(self):
        tk.messagebox.showinfo(title="Refresh rate powermeter", message="This is the rate at which the power from the powermeter is read and stored.")
        
        
    def RefreshListPowermeters(self):
        '''
        Get a list of all powermeters connected, by using the method ListDevices() of the object powermeter. For each device we obtain its identity and its address.
        For each device, we create the string "identity -->  address" and we add the string to the corresponding combobox in the "Powermeter settings" panel 
        '''
        #First we empty the combobox
        self.menuDevices['values'] = ('')
        self.menuDevices.set('')
        
        #Then we read the list of devices
        (ListDevices,ListIDN) = self.instrument.ListDevices()
        if(len(ListDevices)>0):
            ListIDNandDevice = [i + " -->  " + j for i, j in zip(ListIDN, ListDevices)] 
            self.menuDevices['values'] = ListIDNandDevice 
            self.menuDevices.current(0)   


    def ConnectPowermeter(self):
        ''' 
        This function establishes the connection to the powermeter selected in the combobox list, or disconnects the powermeter, depending on the value of the variable self.powermeterThorlabs.connected .   
        If self.powermeterThorlabs.connected == 0, then the powermeter is not connected, and we attempt connection
        If self.powermeterThorlabs.connected == 1, then the powermeter is connected, and we attempt disconnection
        '''
        if(self.instrument.connected == 0): # We attenpt connection       
            DeviceFullName = self.menuDevices.get() # Get the device name from the combobox
            if(DeviceFullName==''): # Check  that the name is not empty
                tk.messagebox.showerror(title="Error during connection", message="No valid device has been selected")
                return
            self.SetWidgetsToConnectingState()
            DeviceName = DeviceFullName.split(' --> ')[1].lstrip() # We extract the device address from the device name
            print("Connecting to powermeter " + DeviceName + "...")
            (Msg,ID) = self.instrument.ConnectDevice(DeviceName) # Try to connect by using the method self.powermeterThorlabs.ConnectDevice(DeviceName) 
            if(ID==1):  #If connection was successful
                print("Connected.")
                self.StartStopReadingPower() #We automatically start reading the power as soon as the powermeter is connected
                self.SetWidgetsToConnectedState()
            else: #If connection was not successful
                tk.messagebox.showinfo(title="Error during connection", message=Msg)
                self.SetWidgetsToDisconnectedState()
                self.RefreshListPowermeters()
        elif(self.instrument.connected == 1): # We attenpt disconnection
            print("Disconnecting powermeter...")
            ID = self.DisconnectDevice()
            if(ID==1): # If disconnection was successful
                print("Disconnected.")
                self.ContinuousRead= 0 # We set this variable to 0 so that the continuous reading from the powermeter will stop
                #tk.messagebox.showinfo(title="Disconnected!", message="Powermeter disconnected succesfully.")
                self.SetWidgetsToDisconnectedState()
            else: #If disconnection was not successful
                tk.messagebox.showinfo(title="Error during disconnection", message="Some error occured while disconnecting the Powermeter.")
                
    def StartStopReadingPower(self):
        #Check if we are trying to start or stop the continuous reading from the powermeter
        
        #If the reading was off, then we want to start reading
        if(self.ContinuousRead == 0):
            # 1) First check if the powermeter is connected, and that the value of RefreshRate is valid
            RefreshRate = float(self.EntryRefreshRate.get())
            if(self.instrument.connected==0):
                tk.messagebox.showerror(title="Error", message="No powermeter is connected")
                return
            if(RefreshRate<=0):
                tk.messagebox.showerror(title="Error", message="The 'Refresh Rate' of powermeter must be a valid positive number")
                return
            if(RefreshRate<=1e-2):
                tk.messagebox.showerror(title="Error", message="The 'Refresh Rate' of powermeter cannot be less than 10 ms")
                return
            # 2) Disable some the input fields (so the user cannot change them while the acquisition is going) and change the label of the button
            self.EntryRefreshRate.configure(state=tk.DISABLED)
            self.ButtonStartReadPower['text'] = "STOP"
            # 3) W store the variable RefreshRate
            self.RefreshRate = RefreshRate
            # 4) Set the variable self.ContinuousRead to 1. Until this variable is set to 1, the function self.UpdatePower() will be repeated continuosly at the rate set by self.powermeterThorlabs.RefreshRate
            self.ContinuousRead = 1 #Until this variable is set to 1, the function UpdatePower will be repeated continuosly 
            # 5) Call the function self.UpdatePower(), which will do stome stuff (read power and store it in a global variable) and then call itself continuosly until the variable self.ContinuousRead is set back to 0
            self.UpdatePower()
            return
        #If the reading was on, then we want to stop reading       
        if(self.ContinuousRead == 1):
            # 1) Sets self.ContinuousRead to 0 (this will force the function UpdatePower() to stop calling itself)
            self.ContinuousRead= 0 
            # 2) Re-enable some of the input fields and change the label of the button
            self.EntryRefreshRate.configure(state=tk.NORMAL)
            self.ButtonStartReadPower['text'] = "Start Reading Power"
            return
        
    def UpdatePower(self):
        '''
        This routine reads continuosly the power from the powermeter and stores its value
        If we are continuosly acquiring the power (i.e. if self.ContinuousRead = 1) then:
            1) Reads the power from the powermeter object and stores it in the variables self.currentPower and self.currentPowerUnits
            2) Update the value of the variable self.currentPowerString by generating a string containing the power and its units
                The variable self.currentPowerString is linked to a Label object (self.labelPowerText) contained in the ThorlabsPowermeterSettingsPanel object of the GUI.
                Thus updating the value of the variable  self.currentPowerString will automatically update the text inside the label
            3) Call itself after a time given by self.powermeterThorlabs.RefreshRate
        '''
        if(self.ContinuousRead == 1):
            (self.currentPower,self.currentPowerUnits) = self.instrument.ReadPower()
            self.Data['Power'] = self.currentPower
            self.Data['PowerUnits'] = self.currentPowerUnits
            super().Update()
            self.currentPowerString.set("{:.2e}".format(self.currentPower) + ' ' + self.currentPowerUnits)
            self.root.after(int(self.RefreshRate*1e3), self.UpdatePower)   #self.root is the ROOT object of tkinter, we need to call its method 'after'. the delay is in milliseconds
        return
    
    
    def DisconnectDevice(self):
        ID = self.instrument.DisconnectDevice()
        return ID

    def SetWidgetsToConnectedState(self):
        self.ButtonConnectDevice.configure(state='active')    
        self.ButtonConnectDevice['text'] = "Disconnect"
        self.ButtonStartReadPower.configure(state='active') 
        self.EntryRefreshRate.configure(state='normal')    

    def SetWidgetsToConnectingState(self):
        self.ButtonConnectDevice.configure(state='disabled')
        self.menuDevices.configure(state='disabled')
        self.ButtonRefreshDeviceList.configure(state='disabled')
        self.ButtonConnectDevice['text'] = "Connecting..."
        self.EntryRefreshRate.configure(state='disabled')    

    def SetWidgetsToDisconnectedState(self):
        self.ButtonConnectDevice.configure(state='active')  
        self.ButtonConnectDevice['text'] = "Connect"
        self.ButtonRefreshDeviceList.configure(state='active')    
        self.ButtonStartReadPower.configure(state='disabled') 
        self.menuDevices.configure(state='readonly')
        self.EntryRefreshRate.configure(state='disabled')    