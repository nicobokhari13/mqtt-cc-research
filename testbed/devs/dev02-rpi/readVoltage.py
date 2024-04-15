from gpiozero import MCP3008
from time import sleep
import pigpio 
pi = pigpio.pi()

handle = pi.spi_open(0, 1000000)  # Open SPI device 0 with a baud rate of 1 MHz

def read_adc(channel):
    if channel < 0 or channel > 7:
        return -1  # Invalid channel number
    # SPI message format for MCP3008: [start bit, single-ended, channel number (3 bits), null bit (1 bit), data (10 bits)]
    msg = [1, (8 + channel) << 4, 0]
    data = pi.spi_xfer2(handle, msg)
    adc_value = ((data[1] & 3) << 8) + data[2]  # Extract ADC value from received data
    return adc_value

# Define which channel you are using on the MCP3
# Create an MCP3008 object, specifying the SPI port and device
adcChannelZero = MCP3008(channel=0)
adcChannelSeven = MCP3008(channel=7)
ADD_CONSTANT  = 0.6
CH_7_DIVISION_CONSTANT = (1.0526 + 0.9524)/2
CH_0_DIVISION_CONSTANT = (0.4524 + 0.5526)/2
STUNT_RESISTOR_OHMS = 1000

adc_value_channel0 = read_adc(0)
adc_value_channel7 = read_adc(7)

print(adc_value_channel0)
print(adc_value_channel7)
# try:
#     while True:
#         # Read the analog value from the ADC
#         cZeroAnalog = adcChannelZero.value
#         cSevenAnalog = adcChannelSeven.value
#         print("Channel 0 analog:", cZeroAnalog)
#         print("Channel 7 analog:", cSevenAnalog)

        
#         # Optional: Convert the analog alue to voltage (assuming 3.3V reference)
#         cZeroVoltage = cZeroAnalog  * 5 + ADD_CONSTANT
#         cSevenVoltage = cSevenAnalog * 5 / STUNT_RESISTOR_OHMS 
#         print(f"Battery Current is {cSevenVoltage / CH_7_DIVISION_CONSTANT}")
#         print(f"1/2 Battery Voltage: {cZeroVoltage}")
#         print(f"Full Battery Voltage is between: {cZeroVoltage / CH_0_DIVISION_CONSTANT}")

#         print("============")
        
#         # Add a small delay before reading again
#         sleep(10)

# except KeyboardInterrupt:
#     print("Exiting...")
