from models import session, Client ,Device ,engine ,Transaction
from datetime import datetime

# Function that adds data to the client and the device table , and ask the user to enter it
from dataclasses import dataclass

class more_data:
    def __init__(self,session):
        self.session = session
        pass

    def more_clients(self,client_name):

        self.new_client=Client(name=client_name)

        try:
            self.session.add(self.new_client)
        finally:
            self.session.commit()
        
            

    def more_devices(self,device_type,brand):

        new_Device=Device(device_type=device_type ,
                          brand=brand ,
                          client=self.new_client)

        try:
            self.session.add(new_Device)
        finally:
            self.session.commit()

    def more_transaction(self,NumberOfDevices,amount,time,notes):
        
        new_transactio=Transaction(amount=amount ,
                                   NumberOfDevices=NumberOfDevices,
                                   time=time,
                                   notes=notes,
                                   client=self.new_client)

        try:
            self.session.add(new_transactio)
        finally:
            self.session.commit()
        
        

    
    def close(self):
        self.session.close()
'''
client_name=str(input("Enter the user's name : "))
client_age=int(input(f"Enter {client_name}'s age : "))
client_Phone_number=str(input(f"Enter {client_name}'s Phone number :"))

app=more_data(session=session)
app.more_clients(client_name ,client_age,client_Phone_number)


NumberOfDevices=int(input('How many diveces dose the client have ?'))
for i in range(NumberOfDevices) :
    device_type=str(input("Enter the device_type's :"))
    status=str(input(f"Enter {device_type}'s status :"))
    brand=str(input(f"Enter {device_type}'s brand :"))
    app.more_devices(device_type ,status ,brand)


amount=float(input(f"Enter the {NumberOfDevices} devices amount :"))
time=datetime.now()
app.more_transaction(NumberOfDevices ,amount ,time)

app.close()

'''