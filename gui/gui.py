import tkinter as tk
from tkinter import ttk as ttk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import sys
'''
Each class contained in this module corresponds to a different part of the GUI.
'''
   
            
class DataAcquisitionSettingsPanel():
    def __init__(self, master,parent):
        self.master = master #master = Containing Frame
        #parent = MainWindow Object
        
        self.frame = tk.LabelFrame(self.master,text="Data Acquisition settings")

        self.labelAcquisModality = tk.Label(self.frame, text="Acquisition Modality:")
        self.labelAcquisModality.grid(row=0,column=0, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5) 
        parent.AcqMod_var = tk.IntVar(value=2)
        
        self.RadioButtonAcqMod_Cont = tk.Radiobutton(self.frame, text="Continuous", variable=parent.AcqMod_var, value=1, 
                                                     command = lambda : [SetWidgetState(self.ButtonSingleAcq ,parent.AcqMod_var.get()==2) , 
                                                                         SetWidgetState(self.ButtonDeleteLastAcq ,parent.AcqMod_var.get()==2),
                                                                         SetWidgetState(self.AverageData_checkbutton ,parent.AcqMod_var.get()==2),
                                                                         SetWidgetState(self.NumbAcqAverage ,parent.AcqMod_var.get()==2)]
                                                     )
        self.RadioButtonAcqMod_Cont.grid(row=0,column=1, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5) 
        self.RadioButtonAcqMod_CkByCk  = tk.Radiobutton(self.frame, text="Click-by-click", variable=parent.AcqMod_var, value=2, 
                                                        command = lambda : [SetWidgetState(self.ButtonSingleAcq ,parent.AcqMod_var.get()==2) , 
                                                                         SetWidgetState(self.ButtonDeleteLastAcq ,parent.AcqMod_var.get()==2),
                                                                         SetWidgetState(self.AverageData_checkbutton ,parent.AcqMod_var.get()==2),
                                                                         SetWidgetState(self.NumbAcqAverage ,parent.AcqMod_var.get()==2)]
                                               )
        
        self.RadioButtonAcqMod_CkByCk.grid(row=0,column=2, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5) 
        
        self.ButtonExplanationAcquisModality = tk.Button(self.frame, text="?", width=3, command=ExplanationAcquisModality)
        self.ButtonExplanationAcquisModality.grid(row=0,column=3, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)


        self.ButtonSingleAcq = tk.Button(self.frame, text="Take single acquisition", width=18, command=parent.TakeSingleAcquisition)
        self.ButtonSingleAcq.grid(row=1,column=0, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)
        

        
        parent.AverageData_var = tk.IntVar(value=0) #NOTE: the variable belongs to the MainWindow object
        self.AverageData_checkbutton = tk.Checkbutton(self.frame, variable=parent.AverageData_var, text="Average data over")
        self.AverageData_checkbutton.grid(row=1,column=1, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)
        
        self.FrameNumbAcqAverage = tk.Frame(self.frame)
        self.NumbAcqAverage = tk.Entry(self.FrameNumbAcqAverage,width=4)
        self.NumbAcqAverage.insert(0, "5")
        self.NumbAcqAverage.pack(fill=tk.BOTH, side=tk.LEFT,padx=5)
        self.labelAcquisAverage = tk.Label(self.FrameNumbAcqAverage, text="acquisitions")
        self.labelAcquisAverage.pack(fill=tk.BOTH, side=tk.LEFT,padx=5)

        self.FrameNumbAcqAverage.grid(row=1,column=2, sticky=tk.W,pady=3,padx=5)
        
        self.ButtonExplanationTimeAverage = tk.Button(self.frame, text="?", width=3, command=ExplanationTimeAverage)
        self.ButtonExplanationTimeAverage.grid(row=1,column=3, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)

        self.ButtonDeleteData = tk.Button(self.frame, text="Delete stored data", width=16, command=parent.DeleteStoredData)
        self.ButtonDeleteData.grid(row=3,column=1, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)
        
        self.ButtonSaveData = tk.Button(self.frame, text="Save stored data", width=16, command=parent.SaveStoredData)
        self.ButtonSaveData.grid(row=3,column=0, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)

        self.ButtonDeleteLastAcq = tk.Button(self.frame, text="Delete last acquisition", width=16, command=parent.DeleteLastData)
        self.ButtonDeleteLastAcq.grid(row=3,column=2, sticky=tk.N+tk.S+tk.E+tk.W,pady=1,padx=5)
              
        
class ConsoleText(tk.Text):
    '''A Tkinter Text widget that provides a scrolling display of console
    stderr and stdout.'''

    class IORedirector(object):
        '''A general class for redirecting I/O to this Text widget.'''
        def __init__(self,text_area):
            self.text_area = text_area

    class StdoutRedirector(IORedirector):
        '''A class for redirecting stdout to this Text widget.'''
        def write(self,str):
            self.text_area.write(str,False)

    class StderrRedirector(IORedirector):
        '''A class for redirecting stderr to this Text widget.'''
        def write(self,str):
            self.text_area.write(str,True)

    def __init__(self, master=None, cnf={}, **kw):
        '''See the __init__ for Tkinter.Text for most of this stuff.'''

        tk.Text.__init__(self, master, cnf, **kw)

        self.started = False
        ###self.write_lock = threading.Lock()

        self.tag_configure('STDOUT',background='white',foreground='black')
        self.tag_configure('STDERR',background='white',foreground='red')

        self.config(state=tk.DISABLED)

    def start(self):

        if self.started:
            return

        self.started = True

        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        stdout_redirector = ConsoleText.StdoutRedirector(self)
        stderr_redirector = ConsoleText.StderrRedirector(self)

        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def stop(self):

        if not self.started:
            return

        self.started = False

        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    def write(self,val,is_stderr=False):

        #Fun Fact:  The way Tkinter Text objects work is that if they're disabled,
        #you can't write into them AT ALL (via the GUI or programatically).  Since we want them
        #disabled for the user, we have to set them to NORMAL (a.k.a. ENABLED), write to them,
        #then set their state back to DISABLED.

        #self.write_lock.acquire()
        self.config(state=tk.NORMAL)

        self.insert('end',val,'STDERR' if is_stderr else 'STDOUT')
        self.see('end')

        self.config(state=tk.DISABLED)
        #self.write_lock.release()


## General Purpose Functions
def enableChildren(parent):
    for child in parent.winfo_children():
        wtype = child.winfo_class()
        if wtype not in ('Frame','Labelframe'):
            child.configure(state='normal')
        else:
            enableChildren(child)
            
def disableChildren(parent):
    for child in parent.winfo_children():
        wtype = child.winfo_class()
        if wtype not in ('Frame','Labelframe'):
            child.configure(state='disable')
        else:
            disableChildren(child)
            
def WaitWindow(parent,message):
    win = tk.Toplevel(parent)
    win.geometry('500x100')
    win.transient()
    win.title('Wait')
    tk.Label(win, textvariable=message).pack()
    return win

def SetWidgetState(button,state):
    if (state==True):
        button["state"] = "normal"
    else:
        button["state"] = "disabled"
        
#TIP boxes
def ExplanationTimeAverage():
    tk.messagebox.showinfo(title="Average", 
                           message=
"If the 'Average data' checkbox  is selected, when the user clicks on 'Take single acquisition' all data is acquired N consecutive times (where N is specified in the '# acquisitions' textbox)" +
"at a rate set by the refresh rate of the instrument used as a clock. The N accumulated values are used to calculate averages and standard deviations of all data.\n\n" + 
"Note: Make sure that all other instruments update their data at a rate equal or faster than the clock instrument. Typically, it is better to designate the slowest instrument as 'clock instrument'.")

    
def ExplanationPlots():
    tk.messagebox.showinfo(title="Two-channel plots", message="The plots will be generated only when both channel 1 and channel 2 are continuosly acquired.")
    

    
def ExplanationAcquisModality():
    tk.messagebox.showinfo(title="Acquisition modality", 
                           message=
 "If 'Continuous' is selected, everytime that the instrument designated as clock updates its own data, the software collects the current value of the data from ALL instruments, " +
"generates and stores a corresponding data point and refreshes all plots.\n "+
"Note: when 'Continuous' is used, the instrument designated as a clock MUST be continuosly running, otherwise nothing will happen. \n \n"
"If 'Click-by-click' is selected, whenever the user clicks on 'Take single acquisition' the software collects the current value of the data from ALL instruments, " + 
"generates and stores a corresponding data point and refreshes all plots.\n\n" +
"If the 'Average data' checkbox  is selected, the software makes N consecutive acquisitions (where N is specified in the '# acquisitions' textbox) and calculates the average and standard deviation of each data.\n "+
"The 'Average data' feature is currently available only in 'Click-by-click' modality.")

def ExplanationPlotErrorBars():
    tk.messagebox.showinfo(title="Plot Error Bars", message="The error bars are automatically calculated for each post-processed data if the acqusition is done by averaging multiple acquisition. Otherwise the errorbars are set to zero.")
 