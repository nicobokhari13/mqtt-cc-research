from gpiozero import MCP3008
from time import sleep

# Define which channel you are using on the MCP3
# Create an MCP3008 object, specifying the SPI port and device
adcChannelZero = MCP3008(channel=0)
adcChannelSeven = MCP3008(channel=7)
ADD_CONSTANT  = 0.6
CH_7_DIVISION_CONSTANT = (1.0526 + 0.9524)/2
CH_0_DIVISION_CONSTANT = (0.4524 + 0.5526)/2
STUNT_RESISTOR_OHMS = 1000
try:
    while True:
        # Read the analog value from the ADC
        cZeroAnalog = adcChannelZero.value
        cSevenAnalog = adcChannelSeven.value
        print("Channel 0 analog:", cZeroAnalog)
        print("Channel 7 analog:", cSevenAnalog)

        
        # Optional: Convert the analog alue to voltage (assuming 3.3V reference)
        cZeroVoltage = cZeroAnalog  * 5 + ADD_CONSTANT
        cSevenVoltage = cSevenAnalog * 5 / STUNT_RESISTOR_OHMS 
        print(f"Battery Current is {cSevenVoltage / CH_7_DIVISION_CONSTANT}")
        print(f"1/2 Battery Voltage: {cZeroVoltage}")
        print(f"Full Battery Voltage is between: {cZeroVoltage / CH_0_DIVISION_CONSTANT}")

        print("============")
        
        # Add a small delay before reading again
        sleep(10)

except KeyboardInterrupt:
    print("Exiting...")
