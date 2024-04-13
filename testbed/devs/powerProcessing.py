from gpiozero import MCP3008

ADD_CONSTANT  = 0.6
CH_7_DIVISION_CONSTANT = (1.0526 + 0.9524)/2
CH_0_DIVISION_CONSTANT = (0.4524 + 0.5526)/2
STUNT_RESISTOR_OHMS = 1000

def readVoltage():
    channel0 = MCP3008(channel = 0)
    analogValue = float(channel0.value)
    cZeroVoltage = analogValue  * 5 + ADD_CONSTANT
    voltage = cZeroVoltage / CH_0_DIVISION_CONSTANT
    print(f"voltage {voltage}")
    return voltage

def readCurrent():
    channel7 = MCP3008(channel=7)
    analogValue = float(channel7.value)
    cSevenVoltage = analogValue * 5 / STUNT_RESISTOR_OHMS 
    current = cSevenVoltage / CH_7_DIVISION_CONSTANT
    print(f"current {current}")
    return current