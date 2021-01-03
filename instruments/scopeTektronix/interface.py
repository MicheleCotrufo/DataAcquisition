import tkinter as tk
from tkinter import ttk as ttk
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from .scope import scope
from ..instrument import instrument


def MakeExponentialFit(t,y):
    try:
        popt, pcov = curve_fit(funcfit_biexp, t, y, 
                            p0 = np.array([0,y.max(),t.max()-t.min(),t.max()-t.min(),y.min()]),  
                            bounds=([t.min(),0,0,0,-np.inf], [t.max(),np.inf,np.inf,np.inf,np.inf]))
    except:
        popt = []
    return popt

def funcfit_biexp(t, t0, A, tau1, tau2, BaseLine): #Function use for the bi-exponential fit (rise and fall)
    return BaseLine + np.heaviside(t-t0,0)*(A*(1-np.exp(-(t-t0)/tau1)) *np.exp(-(t-t0)/tau2) )

class interface(instrument):
    Data = {'MaxCH1':0,'MaxCH2':0,'AvgCH1':0,'AvgCH2':0,'IntCH1':0,'IntCH2':0,'Pk2PkCH1':0,'Pk2PkCH2':0,'MaxCH1/MaxCH2':0,'AvgCH1/AvgCH2':0,'IntCH1/IntCH2':0,'Pk2PkCH1/Pk2PkCH2':0}
    #The dictionary 'Data' is what will be read by the main program. Each 'interface' object must have a 'Data' property

    def __init__(self, parent,root):
        super().__init__(parent,root)
        
        self.Data = {'MaxCH1':0,'MaxCH2':0,'AvgCH1':0,'AvgCH2':0,'IntCH1':0,'IntCH2':0,'Pk2PkCH1':0,'Pk2PkCH2':0,'MaxCH1/MaxCH2':float('nan'),'AvgCH1/AvgCH2':float('nan'),'IntCH1/IntCH2':float('nan'),'Pk2PkCH1/Pk2PkCH2':float('nan')}
        #The dictionary 'Data' is what will be read by the main program. Each 'interface' object must have a 'Data' property
        self.ContinuousRead = 0  #When this is set to 1, the data from scope are acquired continuosly at the rate set by self.RefreshRate
        self.RefreshRate = 1 #in seconds
        self.FitParams = {'CH1':[],'CH2':[]}
        self.instrument = scope(DeviceIdentifier={'TEKTRONIX'}) #Each SettingPanel needs to be associated to an instrument object
        self.plot = None #When a valid plot object is associated to self.plot, the time traces from the two scope axis are plotted into this plot whenever data is updated

        self.InputReadCH1_var = tk.IntVar(value=1)
        self.InputReadCH2_var = tk.IntVar(value=1)
        self.Boost_var = tk.IntVar(value=1) 
        self.RunAndStop_var = tk.IntVar(value=1) 
        self.MakeExpFits_var = tk.IntVar(value=0) 

    def LinkObjects(self, dictObjects):
        super().LinkObjects(dictObjects)
        if not(self.plot==None):
            self.PlotRawDataFromScope()

    def CreatePanelGUI(self,ContainingFrame):    
        self.ContainingFrame = ContainingFrame 
        
        self.frame = tk.LabelFrame(self.ContainingFrame,text="Scope settings")
        
        self.labelDevice = tk.Label(self.frame, text="Device list: ")
        self.labelDevice.grid(row=0,column=0, sticky=tk.W,pady=3,padx=5)
        self.menuDevices = ttk.Combobox(self.frame,width=16,state="readonly")
        self.menuDevices.grid(row=0,column=1, sticky=tk.W,pady=3,padx=5)
        
        self.ButtonRefreshDeviceList = tk.Button(self.frame, text="Refresh", width=16, command=self.RefreshListScopes)
        self.ButtonRefreshDeviceList.grid(row=0,column=2, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)
        
        self.ButtonConnectDevice = tk.Button(self.frame, text="Connect",width=16, command=self.ConnectScope)
        self.ButtonConnectDevice.grid(row=0,column=3, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=1)
        

        self.labelWhichChannel = tk.Label(self.frame, text="Channels: ")
        self.labelWhichChannel.grid(row=1,column=0, sticky=tk.W,pady=3,padx=5)
        
        self.frameInputChannels = tk.LabelFrame(self.frame,text="",highlightthickness=0,borderwidth = 0)
        self.frameInputChannels.grid(row=1,column=1, sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.InputReadCH1 = tk.Checkbutton(self.frameInputChannels, variable=self.InputReadCH1_var, text="CH 1")
        self.InputReadCH1.pack(fill=tk.BOTH, side=tk.LEFT,padx=5) 
        
        self.InputReadCH2 = tk.Checkbutton(self.frameInputChannels, variable=self.InputReadCH2_var, text="CH 2")
        self.InputReadCH2.pack(fill=tk.BOTH, side=tk.LEFT,padx=5)
        
        self.ButtonExplanationChannels = tk.Button(self.frameInputChannels, text="?", width=2, command=self.ExplanationChannels)
        self.ButtonExplanationChannels.pack(fill=tk.BOTH, side=tk.LEFT,padx=5)
        
        self.labelRefreshRate = tk.Label(self.frame, text="Refresh rate (s) = ")
        self.labelRefreshRate.grid(row=1,column=2, sticky=tk.W,pady=3,padx=5)
        self.InputRefreshRate = tk.Entry(self.frame)
        self.InputRefreshRate.insert(0, "0.2")
        self.InputRefreshRate.grid(row=1,column=3, sticky=tk.W,pady=3,padx=5)
        self.ButtonExplanationRefreshRate = tk.Button(self.frame, text="?", width=2, command=self.ExplanationRefreshRate)
        self.ButtonExplanationRefreshRate.grid(row=1,column=4, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)
        
        self.ButtonStartRawRead = tk.Button(self.frame, text="RUN", width=12, command=self.StartStopReadingOscilloscope)
        self.ButtonStartRawRead.grid(row=2,column=0, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)
           
        self.frameBoost = tk.LabelFrame(self.frame,text="",highlightthickness=0,borderwidth = 0)
        self.frameBoost.grid(row=2,column=1, sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.InputBoost = tk.Checkbutton(self.frameBoost, variable=self.Boost_var, text="Boost")
        self.InputBoost.pack(fill=tk.BOTH, side=tk.LEFT,padx=5)
        
        self.ButtonExplanationBooster = tk.Button(self.frameBoost, text="?", width=2, command=self.ExplanationBooster)
        self.ButtonExplanationBooster.pack(fill=tk.BOTH, side=tk.LEFT,padx=5)

        self.FrameAdditionalController = tk.Frame(self.frame) 
        self.FrameAdditionalController.grid(row=2,column=2, sticky=tk.N+tk.S+tk.E+tk.W,columnspan=3)

        self.InputRunAndStop = tk.Checkbutton(self.FrameAdditionalController, variable=self.RunAndStop_var, text="Run&Stop")
        self.InputRunAndStop.pack(fill=tk.BOTH, side=tk.LEFT,padx=5)

        self.MakeExpFits = tk.Checkbutton(self.FrameAdditionalController, variable=self.MakeExpFits_var, text="exp(x) fit")
        self.MakeExpFits.pack(fill=tk.BOTH, side=tk.LEFT,padx=5)


        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 9))
        style.configure("Treeview", font=(None, 9),borderwidth = 1)

        self.TableOutputData1 = ttk.Treeview(self.frame,selectmode="extended",height=1,columns=list(self.Data.keys())[0:8])
        self.TableOutputData1['show'] = 'headings'
        for key in (list(self.Data.keys())[0:8]):
            self.TableOutputData1.heading(key, text=key)
            self.TableOutputData1.column(key, anchor='center', width=40)
        self.TableOutputData1.grid(row=3,column=0, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5,columnspan=5)

        self.TableOutputData2 = ttk.Treeview(self.frame,selectmode="extended",height=1,columns=list(self.Data.keys())[8:13])
        self.TableOutputData2['show'] = 'headings'
        for key in (list(self.Data.keys())[8:13]):
            self.TableOutputData2.heading(key, text=key)
            self.TableOutputData2.column(key, anchor='center', width=40)
        self.TableOutputData2.grid(row=4,column=0, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5,columnspan=5)

        self.SetWidgetsToDisconnectedState()

        self.ShowCurrentDataInTable()
        self.RefreshListScopes()
        return self
        
    def ExplanationRefreshRate(self):
        tk.messagebox.showinfo(title="Refresh rate", message="In principle the refresh rate can be arbitrarily small. In practice, there is a minimum time required to acquire data from the scope. The minimum refresh rate should be kept above 0.2s to avoid lag.")
            
    def ExplanationChannels(self):
        tk.messagebox.showinfo(title="Select channels", message="Select channels which will be read from the oscilloscope.\nIMPORTANT: the channels need to also be activated manually in the oscilloscope.")

    def ExplanationBooster(self):
        tk.messagebox.showinfo(title="Booster", message="If this checkbox is selected several parameters (e.g. horizontal and vertical axis) will be read from the oscilloscope only once (during the first acquistion), thus making the reading faster. " + 
                              "However, this requires that the oscilloscope settings are manually changed during the measurement, otherwise the data acquired will be wrong.\n\n"+
                              "If 'Boost' is selected and any change is manually done to the oscilloscope settings, then it is necessary to stop the reading (click 'STOP') and to restart it again (clin 'RUN'), so that the scope parameters are read again.")


       
    def ShowCurrentDataInTable(self):
        for row in self.TableOutputData1.get_children():
            self.TableOutputData1.delete(row)
        for row in self.TableOutputData2.get_children():
            self.TableOutputData2.delete(row)
        DataFormatted = ["{:.2e}".format(elem) for elem in list(self.Data.values())]
        self.TableOutputData1.insert('', 'end',    values=  DataFormatted[0:8])
        self.TableOutputData2.insert('', 'end',  values= DataFormatted[8:13])
        return

    def RefreshListScopes(self):
        '''
        Get a list of all scopes connected, by using the method ListDevices() of the object scope. For each device we obtain its identity and its address.
        For each device, we create the string "identity -->  address" and we add the string to the corresponding combobox in the "Scope settings" panel 
        '''
        #First we empty the combobox
        self.menuDevices['values'] = ('')
        self.menuDevices.set('')
        
        #Then we read the list of devices
        (ListDevices,ListIDN) = self.instrument.ListDevices()
        if(len(ListDevices)>0):
            ListIDNandDevice  = [i + " -->  " + j for i, j in zip(ListIDN, ListDevices)] 
            self.menuDevices['values'] = ListIDNandDevice 
            self.menuDevices.current(0)  

    def ConnectScope(self):   
        ''' 
        This function establishes the connection to the scope selected in the combobox list, or disconnects the scope, depending on the value of the variable self.instrument.connected .   
        If self.instrument.connected == 0, then the scope is not connected, and we attempt connection
        If self.instrument.connected == 1, then the scope is connected, and we attempt disconnection
        '''
        if(self.instrument.connected == 0): #if the scope is not already connected, we attenpt connection
            DeviceFullName = self.menuDevices.get() # Get the device name from the combobox
            if(DeviceFullName==''): # Check  that the name is not empty
                tk.messagebox.showerror(title="Error during connection", message="No valid device has been selected")
                return

            #Let's disable several widgets
            self.SetWidgetsToConnectingState()
            
            DeviceName = DeviceFullName.split(' --> ')[1].lstrip() # We extract the device address from the device name
            
            print("Connecting to " + DeviceName + "...") 
            (Msg,ID) = self.instrument.ConnectDevice(DeviceName) #Try to connect by using the method self.instrument.ConnectDevice(DeviceName) 
 
            if(ID==1):  #If connection was successful
                print("Connected.")
                self.instrument.RunAcquisition() #we make sure the scope is in 'Run' mode
                self.StartStopReadingOscilloscope()
                self.SetWidgetsToConnectedState()
            else:       #If connection was not successful
                tk.messagebox.showinfo(title="Error during connection", message=Msg)
                self.SetWidgetsToDisconnectedState()

        elif(self.instrument.connected == 1): # If the scope is connected, we attenpt disconnection
            print("Disconnecting scope...")
            ID = self.instrument.DisconnectDevice()
            if(ID==1): # If disconnection was successful
                print("Disconnected.")
                self.ContinuousRead = 0 # We set this variable to 0 so that the continuous reading from the scope will stop
                #tk.messagebox.showinfo(title="Disconnected!", message="Device disconnected succesfully.")
                self.SetWidgetsToDisconnectedState() 
            else: #If disconnection was not successful
                tk.messagebox.showinfo(title="Error during disconnection", message="Some error occured while disconnecting the device.")
        return            
                
    def StartStopReadingOscilloscope(self):
        #Check if we are trying to start or stop the continuous reading from the scope
        
        #If the reading was off when the function was called, then we want to start reading
        if(self.ContinuousRead == 0): 
            # 1) First check if the scope is connected, and that the value of RefreshRate is valid
            RefreshRate = float(self.InputRefreshRate.get())
            if(self.instrument.connected==0):
                tk.messagebox.showerror(title="Error", message="No scope is connected")
                return
            if(RefreshRate<=0):
                tk.messagebox.showerror(title="Error", message="The 'Refresh Rate' must be a valid positive number")
                return
            if(RefreshRate<=1e-2):
                tk.messagebox.showerror(title="Error", message="The 'Refresh Rate' cannot be less than 10 ms")
                return
            # 2) Disable some the input fields (so the user cannot change them while the acquisition is going) and change the label of the button
            self.SetWidgetsToRunState()
            # 3) We reset the axis parameters of the scope to zero to make sure that the first time we get the curves we read also the parameters of the axis from the scope
            # and we store the variable RefreshRate and the value of the "Booster" checkbox inside the scope object
            self.instrument.ResetAxisParametersAcquired()#
            self.instrument.booster = self.Boost_var.get() # When this variable is equal to 1, the parameters of the axis are NOT read everytime that a curve is acquired from the scope (this is taken care of in the methods of the object scope)
            self.instrument.RefreshRate = RefreshRate
            # 4) Set the variable self.ContinuousReadto 1. Until this variable is set to 1, the function self.UpdateDataFromScopeAndPlots() will be repeated continuosly at the rate set by self.scope.RefreshRate
            self.ContinuousRead = 1
            # 5) Call the function self.UpdateData(), which will do stome stuff (read raw data, plot it (if an axis was specified) and update the post-processed data) and then call itself continuosly until the variable self.ContinuousReadScope is set back to 0
            self.UpdateData()

            return
        
        #If the reading was on, then we want to stop reading   
        if(self.ContinuousRead == 1): 
            # 1) Sets self.ContinuousRead to 0 (this will force the function UpdateDataFromScopeAndPlots() to stop calling itself)
            self.ContinuousRead = 0 
            # 2) Re-enable some of the input fields and change the label of the button
            self.SetWidgetsToStopState()
            return

    def UpdateData(self):
        if(self.ContinuousRead == 1):
            self.ReadRawDataFromScope()
            if not(self.plot==None):
                self.PlotRawDataFromScope()
            self.UpdatePostprocessedData()
            self.ShowCurrentDataInTable()
            super().Update()
            self.root.after(int(self.RefreshRate*1e3), self.UpdateData)   #self.root is the ROOT object of tkinter, we need to call its method 'after'. the delay is in milliseconds
        return

    def ReadRawDataFromScope(self):
        '''
            It reads the Voltage VS time curve from each channel of the scope (if the corresponding checkbox is selected)
            The data are stored in the variables self.instrument.xaxis['CH1'], self.instrument.yaxis['CH1'] and self.instrument.xaxis['CH2'], self.instrument.yaxis['CH2']
        '''
        if self.RunAndStop_var.get()==1:
            self.instrument.StopAcquisition()
            
        if(self.InputReadCH1_var.get() ==1): #When the checkbox for channel 1 is set to 1, we read from channel 1
            self.instrument.GetCurveFromChannel('CH1')
        if(self.InputReadCH2_var.get() ==1): #When the checkbox for channel 2 is set to 1, we read from channel 2
            self.instrument.GetCurveFromChannel('CH2') 
            
        if self.RunAndStop_var.get()==1:
            self.instrument.RunAcquisition()


        if self.MakeExpFits_var.get()==1:
            self.MakeExponentialFits()

    def MakeExponentialFits(self):

        #For some weird reason the first time I call curve_fit the fit always fails. So we call it here once, within a try-except block, and then later we call it for real
        t = self.instrument.xaxis['CH1']
        y = self.instrument.yaxis['CH2']
        try:
            popt, pcov = curve_fit(funcfit_biexp, t, y, 
                               p0 = np.array([0,y.max(),t.max()-t.min(),t.max()-t.min(),y.min()]),  
                               bounds=([t.min(),0,0,0,-np.inf], [t.max(),np.inf,np.inf,np.inf,np.inf]))
        except:
            pass

        for ch in ['CH1','CH2']:
            print('Attempting to fit signal from ' +  ch + ':')
            t = self.instrument.xaxis[ch]
            y = self.instrument.yaxis[ch]
            if len(y)>0:
                p0 = MakeExponentialFit(t=t,y=y)
                if(p0==[]):
                    print('Error when trying exponential fit. Are you sure these data should be fitted?')
                else:
                    print(p0)
                    self.FitParams[ch] = p0

            
    def UpdatePostprocessedData(self):
        '''
            Based on the current values of the raw data in self.instrument.xaxis['CH1'], self.instrument.yaxis['CH1'] and self.instrument.xaxis['CH2'], self.instrument.yaxis['CH2']
            it generates post-processed data and store them.
        '''    
        
        X_axis_ch1 = self.instrument.xaxis['CH1']
        X_axis_ch2 = self.instrument.xaxis['CH2']
        
        if self.MakeExpFits_var.get()==1:
            Y_axis_ch1 =  funcfit_biexp(self.instrument.xaxis['CH1'],*self.FitParams['CH1'])
            Y_axis_ch2 = funcfit_biexp(self.instrument.xaxis['CH2'],*self.FitParams['CH2'])
        else:
            Y_axis_ch1 = self.instrument.yaxis['CH1']
            Y_axis_ch2 = self.instrument.yaxis['CH2']

        self.Data['MaxCH1'] = np.max(Y_axis_ch1)
        self.Data['MaxCH2'] = np.max(Y_axis_ch2)
        self.Data['Pk2PkCH1'] = np.max(Y_axis_ch1)-np.min(Y_axis_ch1)
        self.Data['Pk2PkCH2'] = np.max(Y_axis_ch2)-np.min(Y_axis_ch2)
        self.Data['IntCH1'] = np.trapz(Y_axis_ch1,X_axis_ch1)
        self.Data['IntCH2'] = np.trapz(Y_axis_ch2,X_axis_ch2)
        self.Data['AvgCH1'] = np.mean(Y_axis_ch1)
        self.Data['AvgCH2'] = np.mean(Y_axis_ch2) 

        #calculate two-channel data
        try:
            self.Data['MaxCH1/MaxCH2'] =  self.Data['MaxCH1']/self.Data['MaxCH2']
        except ZeroDivisionError:
            self.Data['MaxCH1/MaxCH2']  = float('nan')   
        try:
            self.Data['Pk2PkCH1/Pk2PkCH2'] =  self.Data['Pk2PkCH1']/self.Data['Pk2PkCH2']
        except ZeroDivisionError:
            self.Data['Pk2PkCH1/Pk2PkCH2']  = float('nan')  
        try:
            self.Data['IntCH1/IntCH2'] =  self.Data['IntCH1']/self.Data['IntCH2']
        except ZeroDivisionError:
            self.Data['IntCH1/IntCH2']  = float('nan') 
        try:
            self.Data['AvgCH1/AvgCH2'] =  self.Data['AvgCH1']/self.Data['AvgCH2']
        except ZeroDivisionError:
            self.Data['AvgCH1/AvgCH2']  = float('nan')  


    def PlotRawDataFromScope(self):
        '''
            Plot the raw data from the oscilloscope in the axis defined by self.ax (which needs to be properly populated by using the LinkObjects method)
            The data is taken from the variables self.instrument.xaxis['CH1'], self.instrument.yaxis['CH1'] and self.instrument.xaxis['CH2'], self.instrument.yaxis['CH2'] which are populated beforehand by calling the function ReadRawDataFromScope()
        '''
        ax = self.plot.ax
        ax.clear()
        ax.set_title('Raw data from oscilloscope')
        
        numcolLeg = 0
        if(self.InputReadCH1_var.get() ==1): #When the checkbox for channel 1 is set to 1, we plot data from channel 1
            ax.plot(self.instrument.xaxis['CH1'],    self.instrument.yaxis['CH1'],    color='yellow',linewidth='2',label='CH1')
            numcolLeg = numcolLeg + 1
            if self.MakeExpFits_var.get()==1 and len(self.FitParams['CH1'])>0:
                ax.plot(self.instrument.xaxis['CH1'],    funcfit_biexp(self.instrument.xaxis['CH1'],*self.FitParams['CH1']),  linestyle= "--",   color='white',linewidth='2',label='CH1 - Fit')
                numcolLeg = numcolLeg + 1

        if(self.InputReadCH2_var.get() ==1): #When the checkbox for channel 2 is set to 1, we plot data from channel 2
            ax.plot(self.instrument.xaxis['CH2'],    self.instrument.yaxis['CH2'],    color='blue',linewidth='2',label='CH2')
            numcolLeg = numcolLeg + 1
            if self.MakeExpFits_var.get()==1 and len(self.FitParams['CH2'])>0:
                ax.plot(self.instrument.xaxis['CH2'],    funcfit_biexp(self.instrument.xaxis['CH2'],*self.FitParams['CH2']),  linestyle= "--",   color='white',linewidth='2',label='CH2 - Fit')
                numcolLeg = numcolLeg + 1
        if(numcolLeg>0):
            leg = ax.legend(bbox_to_anchor=(0, -0.22, 0.2, .102), loc='lower left',
                          borderaxespad=0.,facecolor='black', ncol=numcolLeg, fontsize = 'medium')
            for text in leg.get_texts():
                plt.setp(text, color = 'w')
                
        ax.grid(color='white',linestyle= '--', linewidth =0.5)
        ax.set_xlabel('time [s]', fontsize=12)
        ax.set_ylabel('Voltage [v]')

        self.plot.canvas.draw()

    def DisconnectDevice(self):
        ID = self.instrument.DisconnectDevice()
        return ID

    def SetWidgetsToRunState(self):
        self.InputRefreshRate.configure(state=tk.DISABLED)
        self.InputBoost.configure(state=tk.DISABLED)
        self.InputRunAndStop.configure(state=tk.DISABLED)
        self.ButtonStartRawRead['text'] = "STOP"

    def SetWidgetsToStopState(self):
        self.InputRefreshRate.configure(state=tk.NORMAL)
        self.InputBoost.configure(state=tk.NORMAL)
        self.InputRunAndStop.configure(state=tk.NORMAL)
        self.ButtonStartRawRead['text'] = "RUN"

    def SetWidgetsToConnectedState(self):
        self.ButtonConnectDevice.configure(state='active')    
        self.ButtonConnectDevice['text'] = "Disconnect"
        self.ButtonStartRawRead.configure(state='active') 
        self.InputRefreshRate.configure(state='normal')    
        self.InputReadCH1.configure(state='normal')  
        self.InputReadCH2.configure(state='normal') 
        self.InputBoost.configure(state='normal') 
        self.InputRunAndStop.configure(state='normal') 
        #self.TableOutputData1.state(('enabled',))
        #self.TableOutputData2.state(('enabled',))

    def SetWidgetsToConnectingState(self):
        self.ButtonConnectDevice.configure(state='disabled')
        self.menuDevices.configure(state='disabled')
        self.ButtonRefreshDeviceList.configure(state='disabled')
        self.ButtonConnectDevice['text'] = "Connecting..."
        self.InputRefreshRate.configure(state='disabled')  
        self.InputReadCH1.configure(state='disabled')  
        self.InputReadCH2.configure(state='disabled')  
        self.InputBoost.configure(state='disabled') 
        self.InputRunAndStop.configure(state='disabled') 
        self.ButtonStartRawRead.configure(state='disabled')
        #self.TableOutputData1.state(('disabled',))
        #self.TableOutputData2.state(('disabled',))

    def SetWidgetsToDisconnectedState(self):
        self.ButtonConnectDevice.configure(state='active')  
        self.ButtonConnectDevice['text'] = "Connect"
        self.ButtonRefreshDeviceList.configure(state='active')    
        self.ButtonStartRawRead.configure(state='disabled') 
        self.menuDevices.configure(state='readonly')
        self.InputRefreshRate.configure(state='disabled')  
        self.InputReadCH1.configure(state='disabled')  
        self.InputReadCH2.configure(state='disabled')  
        self.InputBoost.configure(state='disabled')  
        self.InputRunAndStop.configure(state='disabled') 
        #self.TableOutputData1.state(('disabled',))
        #self.TableOutputData2.state(('disabled',))