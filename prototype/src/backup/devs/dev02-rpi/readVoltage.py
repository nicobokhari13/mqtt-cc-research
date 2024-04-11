from gpiozero import MCP3008
from time import sleep

# Define which channel you are using on the MCP3008
channel = 0  # Example: Channel 0

# Create an MCP3008 object, specifying the SPI port and device
adc = MCP3008(channel=channel)

try:
    while True:
        # Read the analog value from the ADC
        value = adc.value
        print("Analog value:", value)
        
        # Optional: Convert the analog value to voltage (assuming 3.3V reference)
        voltage = value * 5 
        print("Voltage:", voltage, "V")
        
        # Add a small delay before reading again
        sleep(5)

except KeyboardInterrupt:
    print("Exiting...")
