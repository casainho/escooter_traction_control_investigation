import wifi
import espnow

class ESPNowComms(object):
    def __init__(self, mac_address, system_data):
        
        wifi.radio.enabled = True
        wifi.radio.mac_address = bytearray(mac_address)
        self._espnow_comms = espnow.ESPNow()
        self._packets = []
        self._system_data = system_data
        self.message_id = 99 # logger board ESPNow messages ID
        
    def process_data(self):    
        data = None
        try:
            # read a package and discard others available
            while True:
                rx_data = self._espnow_comms.read()
                if rx_data is None:
                    break
                else:
                    data = rx_data

            # process the package, if available
            if data is not None:
                data = [n for n in data.msg.split()]
                # only process packages for us
                if int(data[0]) == self.message_id:
                    self._system_data.battery_voltage_x10 = int(data[1])
                    self._system_data.battery_current_x100 = int(data[2]) * -1.0
                    self._system_data.motor_current_x100 = int(data[3]) * -1.0
                    self._system_data.motor_speed_erpm = int(data[4])
                    self._system_data.brakes_are_active = 1 if int(data[5]) == 1 else 0
        except Exception as e:
                print(e)

    def send_data(self):
        pass