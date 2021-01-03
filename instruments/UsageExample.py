from powermeter import powermeter

Pow = powermeter() 


(ListDevices,ListIDN) = Pow.ListDevices() #Read a list of devices. The elements in ListDevices are the addresses, the elements in ListIDN are the corresponding "identities


(Msg,ID) = Pow.ConnectDevice('USB0::0x1313::0x8079::P1000322::INSTR') #Replace this string with the address of your device


(Power,PowerUnits) = Pow.ReadPower()

ID = Pow.SetZero()


(Msg,ID) = Pow.DisconnectDevice()

