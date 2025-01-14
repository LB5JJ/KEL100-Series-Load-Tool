import serial
from enum import Enum

class Load:
    class Mode(Enum):
        CV = "CV"
        CC = "CC"
        CR = "CR"
        CP = "CW"

    def __init__(self, port: str, baud: int):
        self._port = port
        self._baud = baud

    def __enter__(self):
        self._conn = serial.Serial(self._port, self._baud, timeout=1, write_timeout=1)
        return self

    def __exit__(self, *args):
        self._conn.close()

    def _command(self, command: str):
        self._conn.write(f"{command}\n".encode('utf-8'))

    def _query(self, command: str) -> str:
        self._conn.write(f"{command}\n".encode('utf-8'))
        return self._conn.read_until().decode('utf-8').strip()
    
    def get_id(self):
        return self._query("*IDN?")
    
    def is_enabled(self) -> bool:
        return self._query(":INP?") == "ON"

    def set_enabled(self, value: bool) -> bool:
        self._command(f":INP {'ON' if value else 'OFF'}")

    def get_cv(self) -> float:
        return float(self._query(":VOLT?")[:-1])
    
    def set_cv(self, value: float):
        self._command(f":VOLT {value}V")

    def get_cc(self) -> float:
        return float(self._query(":CURR?")[:-1])

    def set_cc(self, value: float):
        self._command(f":CURR {value}A")

    def get_cr(self) -> float:
        return float(self._query(":RES?")[:-3])

    def set_cr(self, value: float):
        self._command(f":RES {value}OHM")

    def get_cp(self) -> float:
        return float(self._query(":POW?")[:-1])
    
    def set_cp(self, value: float):
        self._command(f":POW {value}W")
    
    def get_voltage(self) -> float:
        return float(self._query(":MEAS:VOLT?")[:-1])

    def get_current(self) -> float:
        return float(self._query(":MEAS:CURR?")[:-1])

    def get_power(self) -> float:
        return float(self._query(":MEAS:POW?")[:-1])

    def get_mode(self) -> Mode:
        return self.Mode(self._query(":FUNC?"))

    def set_mode(self, value: Mode):
        self._command(":FUNC " + value.value)
