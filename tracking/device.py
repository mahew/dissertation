import uuid

class iot_device:
    def __init__(self):
        self.mac_address = uuid.getnode()
        print("Device MAC Address: ", self.mac_address)
