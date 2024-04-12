from gpiozero import MCP3008
from time import sleep

# Define which channel you are using on the MCP3008
#channel = 0  # Example: Channel 0

# Create an MCP3008 object, specifying the SPI port and device
adcChannelZero = MCP3008(channel=0)
adcChannelSeven = MCP3008(channel=7)

try:
    while True:
        # Read the analog value from the ADC
        cZeroAnalog = adcChannelZero.value
        cSevenAnalog = adcChannelSeven.value
        print("Channel 0 analog:", cZeroAnalog)
        print("Channel 7 analog:", cSevenAnalog)

        
        # Optional: Convert the analog value to voltage (assuming 3.3V reference)
        cZeroVoltage = cZeroAnalog  * 5 
        cSevenVoltage = cSevenAnalog * 5
        print("Battery Current: ", cSevenVoltage)
        print(f"1/2 Battery Voltage: {cZeroVoltage}")
        print(f"Full Battery Voltage: {2 * cZeroVoltage }")

        print("============")
        
        # Add a small delay before reading again
        sleep(5)

except KeyboardInterrupt:
    print("Exiting...")
