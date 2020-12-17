import tkinter as tk
from tkinter import ttk as ttk
import numpy as np  
import importlib
import os 
import gui
from plots import PlotContainer
import json
np.set_printoptions(precision=3)

class MainApplication():

    def __init__(self,ConfigFile):
        self.master =  tk.Tk()
        self.master.geometry("1900x1000")
        self.master.protocol("WM_DELETE_WINDOW", self.CloseWindow)
        
        self.LoadConfig(ConfigFile)  #We import all settings from the specified config file
 
        #Each device specified in 'deviceNames' must correspond to a subfolder of the 'instruments' folder. Let's check that all names are valid
        #We load the names of all sub-folders to check
        path = os.path.join(os.path.dirname(__file__), 'instruments')
        dirs = [ name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) ]  #dirs will contain the names of all subfolders of the 'instruments' folder, and thus of the (potentially) valid device names

        #For each device specified in self.deviceNames we check that the corresponding subfolder exists, and then we istantiate an object of the 'interface' class of that instrument
        #The list self.instruments will contain the interface objects for all instruments, in the same order in which they appear in self.deviceNames
        self.instruments = []
        for (deviceID,device) in enumerate(self.deviceNames):
            if not(device in dirs):
                tk.messagebox.showerror(title="Error", message="The device name '" + device + "' does not correspond to a valid subfolder inside the 'instruments' folder.\nThe application will be closed. Fix the problem and restart the application.")
                self.CloseWindow()
                break
            try:
                DeviceClass =  importlib.import_module('instruments.' + device, package='instruments') #Load the class corresponding to this instrument
                self.instruments.append( DeviceClass.interface(self,self.master) ) #The elements of the list self.instruments are istances of the interface class of the corresponding instrument
            except:
                tk.messagebox.showerror(title="Error", message="Error when trying to load the module for the device '" + device + "'. Check that the corresponding folder (inside the 'instruments' folder) contains a valied 'interface.py' file with an interface class.\nThe application will be closed. Fix the problem and restart the application.")
                self.CloseWindow()

            #Now we check that all data inside deviceDataToAcquire (for this specific device) are valid data names, i.e. they are mentioned in the dictionary 'Data' defined as property of the interface class of this instrument
            for data in self.deviceDataToAcquire[deviceID]:
                if not(data in DeviceClass.interface.Data.keys()):
                    tk.messagebox.showerror(title="Error", message="The data labelled '"+data+"' is not defined for the device '"+device+"'. Check the 'interface.py' file of this device for a list of valid data names.\nThe application will be closed. Fix the problem and restart the application.")
                    self.CloseWindow()

        #Set the clock instrument
        self.instruments[self.WhichInstrumentActsAsClock].ActAsClock = 1
         
        #We create the list self.NameData which contains the name of each data. The names have the format "devN_DataName', where N is the device index and 
        # DataName is the corresponding data name from the list self.deviceDataToAcquire.
        # The first data element in self.NameData is the acquisition index (labelled 'Acq_#')
        # The list self.NameData will not be changed at any time during the program execution. It can only be changed by terminating the program and changing the settings in config.py
        self.NameData = []
        self.NameData.append('Acq_#')
        #For each device we look into the corresponding entry of the list self.deviceDataToAcquire, and from that entry we add all data to self.NameData
        for (deviceID,data) in enumerate(self.deviceDataToAcquire):
            for key in data:
                self.NameData.append ('Dev' + str(deviceID) + '_' + key ) 

        #Initialize empty data
        self.InitializeStorageVariables()
        self.InitializeTemporaryVariables()
        
        # Create GUI
        self.CreateGUI()      
        
        # Link plots to devices. Here we check if any device needs to be directly linked to one of the plots of the GUI. For example, we might want to give to the oscilloscope an 'axis' object, to let it plot the traces from both channels as soon as they are acquired
        # This is specified by the list PlotsConfig in the config.py file. If any element PlotsConfig[i] is an integer, than the i-th plot is assigned to the instrument with index = PlotsConfig[i]
        for PlotIndex, PlotConfig in enumerate(self.PlotsConfig):
            if type(PlotConfig)==int: #If the element WhatToPlot in the list PlotsConfig is an intenger, it identifies an instrument. We assign to that instrument this plot (identified by the index PlotIndex)
                self.instruments[PlotConfig].LinkObjects({'plot':self.Plots.ListPlots[PlotIndex]}) 

    def LoadConfig(self,ConfigFile):
        #We import the variables 'deviceNames' and 'deviceDataToAcquire' from the config file. 
        #These variables specify how many and which devices will be connected to the software, and which output data to extract from each device
        #Each device in 'deviceNames' will generate a corresponding GUI panel in the main window to interact with it (see the method CreateGUI() of this class)
        #We also import the variable WhichInstrumentActsAsClock, which is an index. The corresponding instrument will become the 'clock' for the whole application.
        #We also import the variable DataPlottingStyle and store it in memory. This contains the plotting style for each data specified in 'deviceDataToAcquire'
        with open(ConfigFile) as jsonfile:
            config = json.load(jsonfile)
            self.deviceNames = config['deviceNames']
            self.deviceDataToAcquire = config['deviceDataToAcquire']
            self.WhichInstrumentActsAsClock = config['WhichInstrumentActsAsClock']
            self.DataPlottingStyle = [{'color':'white','linewidth':2,'marker':'o'}] + list(config['DataPlottingStyle']) #We add one element at the beggining of the DataPlottingStyle tuple, which corresponds to the style for the 'Acq_#' column data
            self.PlotsConfig = config['PlotsConfig'] # We store PlotsConfig in self.PlotsConfig. Some elements of self.PlotsConfig can change during the program execution, if the user choose to change what is plotted in certain plots
            self.PlotsSizes = config['PlotsSizes']
            self.NCols= config['NCols']

    def GetPlotConfig(self,PlotIndex): 
        ''' It returns the configuration of a specific plot with index = PlotIndex
        '''
        #print("Reading PlotConfig of plot " +str(PlotIndex)+ ": " + str(self.PlotsConfig[PlotIndex]))
        return self.PlotsConfig[PlotIndex]

    def SetPlotConfig(self,PlotIndex,PlotConfigThisPlot): 
        ''' Sets the PlotConfig list for the a plot with index = PlotIndex
        '''
        self.PlotsConfig[PlotIndex] = PlotConfigThisPlot
        #print("Setting PlotConfig of plot " +str(PlotIndex)+ " to " + str(self.PlotsConfig[PlotIndex]))

    def GetCurrentData(self):
        ''' It returns the currently stored data and data errors
        '''
        return (self.DataAcquired, self.DataAcquired_StdDev)

    def GetNameData(self):
        ''' It returns the Namedata vector
        '''
        return self.NameData

    def GetDataPlottingStyle(self):
        ''' It returns the Plotting style of the data
        '''
        return self.DataPlottingStyle


    def InitializeStorageVariables(self):
        ''' Initialize all arrays for data storage. The number of columns in the storage matrices is given by the length of self.NameData. '''      
        self.DataAcquired = np.empty([0,len(self.NameData)]) 
        self.DataAcquired_StdDev = np.empty([0,len(self.NameData)]) #Note: each column of self.DataAcquired_StdDev contains the error of each data in the same column of self.DataAcquired, if that data was acquired via an average (otherwise the error is set to zero)
                                                                    #The first column of self.DataAcquired is the acquisition number, for which of course there is no error. 
                                                                    #Nonetheless we define self.DataAcquired_StdDev with the same dimension as self.DataAcquired for consistency 
    
    def InitializeTemporaryVariables(self):
        ''' These variables will only be used as temporary arrays for averaging purposes. The number of columns in the storage matrices is given by the length of self.NameData. '''
        self.NumbAcqToAverage = 0 # This will contain the number of acquisitions to be averaged, chosen by the user
        self.DataBeingAveraged = 0
        self.DataAcquired_Temp = np.empty([0,len(self.NameData)-1]) #The number of columns of self.DataAcquired_Temp is 1 less than the number of columns of self.DataAcquired 
                                                                    #because the first column of self.DataAcquired is for the acquisition number
        return
    
    def CreateGUI(self):
        '''
        It creates the GUI. Each part of the general GUI is defined as a class inside the module GUI.py. Moreover, for each instrument contained in the list self.instruments, we load the corresponding
        GUI defined in the method CreatePanelGUI() of the interface class of that instrument
        '''
        self.master.title("Data Acquisition")
        
        tk.Grid.rowconfigure( self.master, 0, weight=1)
        tk.Grid.rowconfigure( self.master, 1, weight=20)
        tk.Grid.rowconfigure( self.master, 2, weight=1)
        tk.Grid.columnconfigure(self.master, 0, weight=1)

        #TopFrame contains the setting panel for each instrument, and the setting panel for data acquisition
        self.TopFrame = tk.LabelFrame(self.master,text="")
        self.TopFrame.config( borderwidth = 0, highlightthickness=0)
        self.TopFrame.grid(row=0,column=0, sticky=tk.N+tk.S+tk.E+tk.W)

        #The object ContainerForInstrumentFrames is a TK frame which contains all the instrument panels
        self.ContainerForInstrumentFrames = tk.LabelFrame(self.TopFrame,text="Instruments")
        self.ContainerForInstrumentFrames.config(highlightbackground = "red", highlightcolor= "red", highlightthickness=1,bd=1)
        self.ContainerForInstrumentFrames.pack(fill=tk.BOTH, side=tk.LEFT,padx=2,pady=0)

        self.InstrumentFrames = [] #The elements of self.InstrumentFrames are TK frames, each of them containing the GUI for the corresponding object defined in self.instruments     
        for instrument in self.instruments:
            Frame = instrument.CreatePanelGUI(self.ContainerForInstrumentFrames) #For each instrument, we call the method CreatePanelGUI of the corresponding Interface object
            Frame.frame['height'] =200
            Frame.frame.pack(fill=tk.BOTH, side=tk.LEFT,padx=2,pady=0)
            self.InstrumentFrames.append(Frame)
       
        #The object ContainerForSettingFrames is a TK frame which contains all the other setting panels
        self.ContainerForSettingFrames = tk.LabelFrame( self.TopFrame,text="")
        self.ContainerForSettingFrames.config( borderwidth = 0, highlightthickness=0)
        self.ContainerForSettingFrames.pack(fill=tk.BOTH, side=tk.LEFT,padx=5)

        self.SettingsPanel = gui.DataAcquisitionSettingsPanel(self.ContainerForSettingFrames,self)
        self.SettingsPanel.frame['height'] =150
        self.SettingsPanel.frame.pack(fill=tk.BOTH, side=tk.LEFT,padx=5)
        
        #In the bottom part of the GUI there are the plots 
        #We create a PlotContainer Object, which will create 'PlotObject' objects inside itself.
        #The PlotContainer object is also a TK Frame object, and its parent frame is the root TK object (i.e. self.master)
        #The PlotContainer will access directly to the properties self.DataAcquired, self.DataAcquired_StdDev, self.PlotsConfig and self.NameData of the MainWindow object
        #In this way any change in stored data will automatically reflect in the plots. Moreover, the 'PlotObject' objects conntained inside PlotContainer can modify the self.PlotsConfig list
  
        self.Plots = PlotContainer(self.master,self,self.PlotsSizes,self.NCols) #This create a "container of Plots" , which is also a Frame object
                                                                                                  #It will automatically create plots based on the number of elements in PlotsConfig
                                                                                                  #and it will use PlotsSizes and NCols for the geometry
                                                                                                  #For each plot, the corresponding element in PlotsConfig can also be changed dynamically by the user
                                                                                                  #(unless the plots is directly assigned to an instrument)
        self.Plots.grid(row=1,column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        #Initialize plots        
        self.UpdateAllPlots()

        #The bottom part of the window contains a textbox which will show the output from the Python consol, so we can send messages to the user about what's going on
        self.BottomFrame = tk.LabelFrame(self.master,text="")
        self.BottomFrame.config( borderwidth = 0, highlightthickness=0)
        self.BottomFrame.grid(row=2,column=0, sticky=tk.N+tk.S+tk.E+tk.W)

        self.OutputTextBox = gui.ConsoleText(self.BottomFrame, height = 15, width = 160)
        self.OutputTextBox.pack(fill=tk.BOTH, side=tk.LEFT, expand=1)
        self.ScrollBar = tk.Scrollbar(self.BottomFrame, command=self.OutputTextBox.yview, orient="vertical")
        self.ScrollBar.pack(fill=tk.BOTH, side=tk.LEFT, expand=0)
        self.OutputTextBox.configure(yscrollcommand=self.ScrollBar.set)
        self.OutputTextBox.start()
        return
               
    def CloseWindow(self):
        '''
        Makes sure that all instruments are disconnected when the window is closed.
        '''
        for instrument in self.instruments:
            instrument.DisconnectDevice()
        self.master.destroy()
        
    def DeleteStoredData(self):
        '''
        Deletes all stored post-processed data, and refreshes the plots.
        '''
        self.InitializeStorageVariables()
        self.InitializeTemporaryVariables()
        self.UpdateAllPlots()
        print("Deleted all stored data")
        return
    
    def DeleteLastData(self):
        '''
        Removes the last element of all lists containing post-processed data, and refreshes the plots.
        '''
        self.DataAcquired = self.DataAcquired[0:-1,:]
        self.DataAcquired_StdDev = self.DataAcquired_StdDev[0:-1,:]
        self.UpdateAllPlots()
        print("Deleted last data. Number of rows currently stored = " + str(self.DataAcquired.shape[0]))
        return

    def SaveStoredData(self):
        '''
        Saves the values of all currently stored data on file. The file name is specified by the user via a filedialog widget.
        The data are saved in a tabular form and delimited by a comma.
        '''
        d =','
        header = ''
        for h in self.NameData:
            header = header + h + d 
        for h in self.NameData:
            header = header + d + (h+'_STD')

        files = [('Csv File', '*.csv'),('Text Document', '*.txt')] 
        file = tk.filedialog.asksaveasfile(filetypes = files, defaultextension = files) 
        if not file: return

        A = np.concatenate((self.DataAcquired, self.DataAcquired_StdDev),axis=1)
        np.savetxt(file.name, A, delimiter=d, header=header, comments="",fmt=d.join(['%i'] + ['%e']*(A.shape[1]-1)))#
        print("Saved all stored data (number of rows = " + str(self.DataAcquired.shape[0]) + ") in the file " +  file.name)
        return

    def ReadCurrentData(self):
        '''
        It looks into all the instruments interfaces (inside the list self.instruments) and from each instrument it extracts the data specified in the corresponding element of self.deviceDataToAcquire
        The function returns all the data from all instruments as an ordered list, in the same format specified by self.NameData
        '''
        CurrentData = []
        for (instrumentID,instrument) in enumerate(self.instruments):
            for data in self.deviceDataToAcquire[instrumentID]:
                CurrentData.append(instrument.Data[data])  
        return np.array(CurrentData)

    def Update(self):
        '''
        Everytime this function is called, if we are in 'Continuous' acquisition modality ( i.e. if self.AcqMod_var.get()==1, which means that the corresponding
        radio button is set to 'Continuous') the software will acquire data from all instruments, store it and plot it
        If we are not in 'Continuous' acquisition modality, but we are performing an averaged acquisition (i.e. self.DataBeingAveraged == 1) then we read all data
        but store them in temporary arrays, which will be used to perform the average. The function self.StoreCurrentData() will take care of checking if we are performing an average or not, and then
        store the data in the proper array

        If we are NOT in 'Continuous' acquisition modality and also NOT performing an average, then no action is done by this function

        NOTE: this function will not call itself again. Thus, another part of the program needs to make sure that this function is called repeatedly (at a certain rate).
        The best thing to ensure this is to have one of the instruments to act as a clock, i.e. everytyime the instrument updates its own data it will also call this function.
        The instrument which acts as a clock is specified in the config.py file with the variable WhichInstrumentActsAsClock
        One can also define a virtual instrument which acts as a clock (and thus defines the refresh rate of the entire application)
        '''
        if self.AcqMod_var.get()==1: #i.e. if we are in "continuous acquisition" mode
            self.StoreCurrentData()
            self.UpdateAllPlots()
        elif self.DataBeingAveraged == 1 :
            self.StoreCurrentData()    
        return

    def UpdateAllPlots(self):
        self.Plots.UpdateAllPlots()
                     
    
    def StoreCurrentData(self):
        '''
            We read the data from the interface object of each instrument, and we store it as a data point.
            
            If we are doing an averaged acquisition (i.e. if self.DataBeingAveraged == 1), the data point is stored in self.DataAcquired_Temp
            After that, we check if we have accumulated enough datapoints for the average. If yes, we calculate average values and errors, and store them in self.DataAcquired and self.DataAcquired_StdDev

            If we not doing an averaged acquisition (i.e. self.DataBeingAveraged == 0) then we directly store all data in the self.DataAcquired array
            and the corresponding row in self.DataAcquired_StdDev is set to zeros

        '''

        CurrentData = self.ReadCurrentData() #Read the current data from all instruments

        # if we are not doing an average (i.e. self.DataBeingAveraged = 0), we store the CurrentData row in the regular array, and we set the errors to zero
        if (self.DataBeingAveraged == 0):
            AcquisitionNumber = self.DataAcquired.shape[0] + 1 #We look at the number of rows of self.DataAcquired to determine the next acquistion number
            NewRowData =  np.concatenate( ([AcquisitionNumber] , CurrentData)  )
            NewRowData_STD = 0*NewRowData


        if( self.DataBeingAveraged == 1): #If this variable is 1, it means that if we are in the middle of an averaging process. In this case we add the data to the temporary array self.DataAcquired_Temp 
            
            self.DataAcquired_Temp = np.append(self.DataAcquired_Temp , [CurrentData] ,axis=0)
            self.StringAveragin_var.set( "Averaging. Acquisition #" + str(self.DataAcquired_Temp.shape[0]) + " of " + str(int(self.NumbAcqToAverage)) ) #This automatically updates the text in the message box
            print(self.StringAveragin_var.get()) 
            
            #Now we check if we accumulated enough points to do the average. If no, then nothing else happens in this function. The variable self.DataBeingAveraged remains equal to 1. 
            #This funnction will be called again and keep storing data in self.DataAcquired_Temp until we accumulated enough points.

            # If we have accumualted enough data points, we calculate the average and STD of each data, and then we set self.DataBeingAveraged  to -1
            if(self.DataAcquired_Temp .shape[0]==self.NumbAcqToAverage):            #If we have collected enough data points for the average,
                DataAveraged = self.DataAcquired_Temp.mean(axis=0)                  #Calculate the averaged data points
                DataAveraged_STD = self.DataAcquired_Temp.std(axis=0)               #Calculate the errors
                self.InitializeTemporaryVariables()                                 #This empties the temporary arrays, and reset temporary variables to their default value
                self.DataBeingAveraged = -1                                         #Setting this variable to -1 specifies that the averaging process is JUST terminated
                self.PopUpAveraging.destroy()
                #gui.enableChildren(self.master)
                AcquisitionNumber = self.DataAcquired.shape[0] + 1 #We look at the number of rows of self.DataAcquired to determine the next acquistion number
                NewRowData =  np.concatenate( ([AcquisitionNumber] , DataAveraged)  )
                NewRowData_STD = np.concatenate( ([0] , DataAveraged_STD)  ) 
        
        if (not(self.DataBeingAveraged == 1)):
            print("Acquisition #" + str(AcquisitionNumber)+ ": " ,end='')
            print(NewRowData.tolist()) 
            self.DataAcquired = np.append( self.DataAcquired ,[NewRowData] ,axis=0)
            self.DataAcquired_StdDev = np.append(self.DataAcquired_StdDev ,[NewRowData_STD] ,axis=0)  
            self.UpdateAllPlots()
            self.DataBeingAveraged = 0

    
    def TakeSingleAcquisition(self):
        '''
            This function is called when the user click on the 'Take single acquisition' button. We collect data from all connected instruments, add it to self.DataAcquired, and call the function to update plots
        '''
        if(self.AverageData_var.get()==1): #If the user wants to take an averaged acquisition
            self.NumbAcqToAverage = float(self.SettingsPanel.NumbAcqAverage.get()) #we read the number of acquisitions to be averaged
            if(self.NumbAcqToAverage<=0):
                tk.messagebox.showerror(title="Error", message="The number of acquisitions to be averaged must be a valid positive number")
                return
            self.DataBeingAveraged = 1 #By changing this variable to 1 we ensure that the function StoreCurrentData, which is called by the function Update (which in turn is called everytime the clock instrument ticks) will store data in temporary arrays
            #gui.disableChildren(self.master)
            self.StringAveragin_var = tk.StringVar(value="Averaging...")
            self.PopUpAveraging = gui.WaitWindow(self.master,self.StringAveragin_var )
        else: #if we are doing a single acquisition without any average, we just store data (by a single call to StoreCurrentData ) and update all plots
            self.StoreCurrentData() 
            self.UpdateAllPlots()
        return


import os
import sys

os.chdir(os.path.dirname(sys.argv[0]))

# Count the input arguments
NArgsIn = len(sys.argv) - 1

if NArgsIn > 0:
    ConfigFile = sys.argv[1]
else:
    ConfigFile = "config.json"
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


App = MainApplication(ConfigFile)
App.master.mainloop()