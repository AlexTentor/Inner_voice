import serial.tools.list_ports

def list_arduino_ports():
    """
    List all available serial ports that could be an Arduino on a Mac.
    
    Returns:
        list: A list of serial port names that could be an Arduino.
    """
    ports = serial.tools.list_ports.comports()
    arduino_ports = []
    for port in ports:
        if "usbmodem" in port.device or "usbserial" in port.device:
            arduino_ports.append(port.device)
    return arduino_ports

if __name__ == "__main__":
    available_ports = list_arduino_ports()
    if available_ports:
        print("Available Arduino ports:")
        for port in available_ports:
            print(f"- {port}")
    else:
        print("No Arduino ports found.")