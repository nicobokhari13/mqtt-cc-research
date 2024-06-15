import psutil

battery = psutil.sensors_battery()
if battery is not None:
    print("Battery percent:", psutil.sensors_battery().percent)
    print("Power plugged in:", battery.power_plugged)
else:
    print("Battery information not available")
