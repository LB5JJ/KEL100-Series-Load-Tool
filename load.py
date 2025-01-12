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
    
    @property
    def id(self):
        return self._query("*IDN?")
    
    @property
    def enabled(self) -> bool:
        return self._query(":INP?") == "ON"

    @enabled.setter
    def enabled(self, value: bool) -> bool:
        self._command(f":INP {'ON' if value else 'OFF'}")

    @property
    def cv(self) -> float:
        return float(self._query(":VOLT?")[:-1])
    
    @cv.setter
    def cv(self, value: float):
        self._command(f":VOLT {value}V")

    @property
    def cc(self) -> float:
        return float(self._query(":CURR?")[:-1])

    @cc.setter    
    def cc(self, value: float):
        self._command(f":CURR {value}A")

    @property
    def cr(self) -> float:
        return float(self._query(":RES?")[:-3])

    @cr.setter
    def cr(self, value: float):
        self._command(f":RES {value}OHM")

    @property
    def cp(self) -> float:
        return float(self._query(":POW?")[:-1])
    
    @cp.setter
    def cp(self, value: float):
        self._command(f":POW {value}W")
    
    @property
    def voltage(self) -> float:
        return float(self._query(":MEAS:VOLT?")[:-1])

    @property
    def current(self) -> float:
        return float(self._query(":MEAS:CURR?")[:-1])

    @property
    def power(self) -> float:
        return float(self._query(":MEAS:POW?")[:-1])

    @property
    def mode(self) -> Mode:
        return self.Mode(self._query(":FUNC?"))

    @mode.setter
    def mode(self, value: Mode):
        self._command(":FUNC " + value.value)
