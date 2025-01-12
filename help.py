
from serial.tools import list_ports


def main(command = None, error = None):
    if error:
        print("Error:", error + "\n")

    match command:
        case "id":
            id()
        case "enable":
            enable()
        case "disable":
            disable()
        case "status":
            status()
        case "constant-voltage":
            constant_voltage()
        case "constant-current":
            constant_current()
        case "constant-resistance":
            constant_resistance()
        case "constant-power":
            constant_power()
        case "battery-test":
            battery_test()
        case _:
            load()

    exit(1 if error else 0)

def load():
    print("Usage: load <CONNECT> <COMMAND> <ARGUMENT> <OPTIONS>")
    print("<CONNECT>:")
    print("--serial-port <SERIAL-PORT>")
    print("  Defaults to the contents of environment variable SERIAL_PORT")
    print("--serial-speed <SERIAL-SPEED>")
    print("  Defaults to environment variable SERIAL_SPEED or 115200")
    print("<COMMAND>:")
    print("  id, enable, disable, status, constant-voltage, constant-current")
    print("  constant-resistance, constant-power, battery-test, help")
    print("For details, run: load help <COMMAND>")

def id():
    print("Usage: load id")
    print("Display type and serial number from load")

def enable():
    print("Usage: load enable")
    print("Enable the load; start drawing current")

def disable():
    print("Usage: load disable")
    print("Disable the load; stop drawing current")

def status():
    print("Usage: status")
    print("Show configuration status and measurements")

def constant_voltage():
    print("Usage: load constant-voltage <VOLTAGE>")
    print("Set constant voltage mode for <VOLATGE> volts")

def constant_current():
    print("Usage: constant-current <CURRENT>")
    print("Set constant current mode for <CURRENT> amps")

def constant_resistance():
    print("Usage: constant-resistance <RESISTANCE>")
    print("Set constant resistance mode for <RESISTANCE> ohms")

def constant_power():
    print("Usage: constant-power <POWER>")
    print("Set constant power mode for <POWER> watts")

def battery_test():
    print("Usage: battery-test <OPTIONS>")
    print("Start battery test. <OPTIONS>:")
    print("--cutoff-voltage <VOLTAGE>")
    print("  Stop test and disable load when voltage drops below <VOLTAGE>")
    print("--cutoff-seconds <SECONDS>")
    print("  Stop test and disable load after <SECONDS> seconds")
    print("--no-cutoff")
    print("  Do not automatically stop the test (can be dangerous)")
    print("--constant-current <CURRENT>")
    print("  Draw a constant current of <CURRENT> amps")
    print("--constant-power <POWER>")
    print("  Draw a constant power of <POWER> watts")
    print("--sampling-interval <SECONDS>")
    print("  Read new sample every <SECONDS> second (default 5)")
    print("--file-base-name <NAME>")
    print("  Save report in <NAME>.csv and <NAME>.png (default report)")
    print("--verbose")
    print("  Print measurements to console every <sampling-interval> seconds")

def ports():
    ports = list_ports.comports()
    for port in ports:
        print(port.device + ": ", port.description)
    exit(0)
