class instrument:
	def __init__(self, parent,root):
		self.parent = parent #This is the main window
		self.root = root #This is the root object of TKinter
		self.ActAsClock = 0 #When this variable is set to 1, this instrument will act as a clock for the whole software: whenever its data is update it will call the Update function of the main program
                            #NOTE: only one instrument at a time per can act as a clock! 
		Data = {'BlankData':0}
		#The dictionary 'Data' is what will be read by the main program. Each 'interface' object must have a 'Data' property, even if it does not return any data (in which case it can be empty)

	def LinkObjects(self, dictObjects):
		self.__dict__.update(dictObjects)

	def Update(self):
		if self.ActAsClock == 1: #If this instrument has been designated to be the 'clock' for the whole system 
			self.parent.Update() #Then we let the main window know that it's time to collect all data
		return