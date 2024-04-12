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

        
        # Optional: Convert the analog alue to voltage (assuming 3.3V reference)
        cZeroVoltage = cZeroAnalog  * 5 + 0.6 
        cSevenVoltage = cSevenAnalog * 5 / 1000 
        print(f"Battery Current is between: {cSevenVoltage / 1.0526} and {cSevenVoltage / 0.9524}")
        print(f"1/2 Battery Voltage: {cZeroVoltage}")
        print(f"Full Battery Voltage is between: {cZeroVoltage / 0.5526} and {cZeroVoltage / 0.4524}")

        print("============")
        
        # Add a small delay before reading again
        sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
