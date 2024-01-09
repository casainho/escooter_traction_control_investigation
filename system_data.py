import time

class SystemData(object):

    def __init__(self):
        self.battery_voltage_x10 = 0
        self.battery_current_x100 = 0
        self.motor_current_x100 = 0
        self.motor_speed_erpm = 0
        self.brakes_are_active = 99
        