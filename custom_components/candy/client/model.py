from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MachineState(Enum):
    IDLE = 1
    RUNNING = 2
    PAUSED = 3
    DELAYED_START_SELECTION = 4
    DELAYED_START_PROGRAMMED = 5
    ERROR = 6
    FINISHED = 7

    def __str__(self):
        if self == MachineState.IDLE:
            return "Idle"
        elif self == MachineState.RUNNING:
            return "Running"
        elif self == MachineState.PAUSED:
            return "Paused"
        elif self == MachineState.DELAYED_START_SELECTION:
            return "Delayed start selection"
        elif self == MachineState.DELAYED_START_PROGRAMMED:
            return "Delayed start programmed"
        elif self == MachineState.ERROR:
            return "Error"
        elif self == MachineState.FINISHED:
            return "Finished"
        else:
            return "%s" % self


class ProgramState(Enum):
    STOPPED = 0
    PRE_WASH = 1
    WASH = 2
    RINSE = 3
    LAST_RINSE = 4
    END = 5
    DRYING = 6
    ERROR = 7
    STEAM = 8
    GOOD_NIGHT = 9  # TODO: GN pause?
    SPIN = 10

    def __str__(self):
        if self == ProgramState.STOPPED:
            return "Stopped"
        elif self == ProgramState.PRE_WASH:
            return "Pre-wash"
        elif self == ProgramState.WASH:
            return "Wash"
        elif self == ProgramState.RINSE:
            return "Rinse"
        elif self == ProgramState.LAST_RINSE:
            return "Last rinse"
        elif self == ProgramState.END:
            return "End"
        elif self == ProgramState.DRYING:
            return "Drying"
        elif self == ProgramState.ERROR:
            return "Error"
        elif self == ProgramState.STEAM:
            return "Steam"
        elif self == ProgramState.GOOD_NIGHT:
            return "Spin - Good Night"
        elif self == ProgramState.SPIN:
            return "Spin"
        else:
            return "%s" % self


@dataclass
class MachineStatus:
    machine_state: MachineState
    program_state: ProgramState
    program: int
    temp: int
    spin_speed: int
    remaining_minutes: int
    remote_control: bool
    fill_percent: Optional[int]  # 0...100

    @classmethod
    def from_json(cls, json):
        return cls(
            machine_state=MachineState(int(json["MachMd"])),
            program_state=ProgramState(int(json["PrPh"])),
            program=int(json["Pr"]),
            temp=int(json["Temp"]),
            spin_speed=int(json["SpinSp"]) * 100,
            remaining_minutes=round(int(json["RemTime"]) / 60),
            remote_control=json["WiFiStatus"] == "1",
            fill_percent=int(json["FillR"]) if "FillR" in json else None
        )
