from dataclasses import dataclass
from enum import Enum
from typing import Optional


class StatusCode(Enum):
    def __init__(self, code: int, label: str):
        self.code = code
        self.label = label

    def __str__(self):
        return self.label

    @classmethod
    def from_code(cls, code: int):
        for state in cls:
            if code == state.code:
                return state
        raise ValueError(f"Unrecognized code when parsing {cls}: {code}")


class MachineState(StatusCode):
    IDLE = (1, "Idle")
    RUNNING = (2, "Running")
    PAUSED = (3, "Paused")
    DELAYED_START_SELECTION = (4, "Delayed start selection")
    DELAYED_START_PROGRAMMED = (5, "Delayed start programmed")
    ERROR = (6, "Error")
    FINISHED1 = (7, "Finished")
    FINISHED2 = (8, "Finished")


class WashProgramState(StatusCode):
    STOPPED = (0, "Stopped")
    PRE_WASH = (1, "Pre-wash")
    WASH = (2, "Wash")
    RINSE = (3, "Rinse")
    LAST_RINSE = (4, "Last rinse")
    END = (5, "End")
    DRYING = (6, "Drying")
    ERROR = (7, "Error")
    STEAM = (8, "Steam")
    GOOD_NIGHT = (9, "Spin - Good Night")  # TODO: GN pause?
    SPIN = (10, "Spin")


@dataclass
class WashingMachineStatus:
    machine_state: MachineState
    program_state: WashProgramState
    program: int
    temp: int
    spin_speed: int
    remaining_minutes: int
    remote_control: bool
    fill_percent: Optional[int]  # 0...100

    @classmethod
    def from_json(cls, json):
        return cls(
            machine_state=MachineState.from_code(int(json["MachMd"])),
            program_state=WashProgramState.from_code(int(json["PrPh"])),
            program=int(json["Pr"]) if "Pr" in json else int(json["PrNm"]),
            temp=int(json["Temp"]),
            spin_speed=int(json["SpinSp"]) * 100,
            remaining_minutes=round(int(json["RemTime"]) / 60),
            remote_control=json["WiFiStatus"] == "1",
            fill_percent=int(json["FillR"]) if "FillR" in json else None,
        )


class DryerProgramState(StatusCode):
    STOPPED = (0, "Stopped")
    RUNNING = (2, "Running")
    END = (3, "End")


class DryerCycleState(StatusCode):
    LEVEL_NONE = (0, "No Dry")
    LEVEL_IRON = (1, "Iron Dry")
    LEVEL_HANG = (2, "Hang Dry")
    LEVEL_STORE = (3, "Store Dry")
    LEVEL_BONE = (4, "Bone Dry")


@dataclass
class TumbleDryerStatus:
    machine_state: MachineState
    program_state: DryerProgramState
    cycle_state: DryerCycleState
    program: int
    remaining_minutes: int
    remote_control: bool
    dry_level: int
    dry_level_selected: int
    refresh: bool
    need_clean_filter: bool
    water_tank_full: bool
    door_closed: bool

    @classmethod
    def from_json(cls, json):
        return cls(
            machine_state=MachineState.from_code(int(json["StatoTD"])),
            program_state=DryerProgramState.from_code(int(json["PrPh"])),
            cycle_state=DryerCycleState.from_code(int(json["DryLev"])),
            program=int(json["Pr"]),
            remaining_minutes=int(json["RemTime"]),
            remote_control=json["StatoWiFi"] == "1",
            dry_level=int(json["DryLev"]),
            dry_level_selected=int(json["DryingManagerLevel"]),
            refresh=json["Refresh"] == "1",
            need_clean_filter=json["CleanFilter"] == "1",
            water_tank_full=json["WaterTankFull"] == "1",
            door_closed=json["DoorState"] == "1",
        )


class DishwasherState(StatusCode):
    """
    Dishwashers have a single state combining the machine state and program state
    """

    IDLE = (0, "Idle")
    PRE_WASH = (1, "Pre-wash")
    WASH = (2, "Wash")
    RINSE = (3, "Rinse")
    DRYING = (4, "Drying")
    FINISHED = (5, "Finished")


@dataclass
class DishwasherStatus:
    machine_state: DishwasherState
    program: str
    remaining_minutes: int
    delayed_start_hours: Optional[int]
    door_open: bool
    door_open_allowed: Optional[bool]
    eco_mode: bool
    remote_control: bool
    salt_empty: bool
    rinse_aid_empty: bool

    @classmethod
    def from_json(cls, json):
        return cls(
            machine_state=DishwasherState.from_code(int(json["StatoDWash"])),
            program=DishwasherStatus.parse_program(json),
            remaining_minutes=int(json["RemTime"]),
            delayed_start_hours=int(json["DelayStart"])
            if json["DelayStart"] != "0"
            else None,
            door_open=json["OpenDoor"] != "0",
            door_open_allowed=json["OpenDoorOpt"] == "1"
            if "OpenDoorOpt" in json
            else None,
            eco_mode=json["Eco"] != "0",
            remote_control=json["StatoWiFi"] == "1",
            salt_empty=json["MissSalt"] == "1",
            rinse_aid_empty=json["MissRinse"] == "1",
        )

    @staticmethod
    def parse_program(json) -> str:
        """
        Parse final program label, like P1, P1+, P1-
        """
        program = json["Program"]
        # Some dishwashers don't include the OpzProg field
        option = json.get("OpzProg")
        if option == "p":
            return program + "+"
        elif option == "m":
            return program + "-"
        else:
            # Third OpzProg value is 0
            return program


class OvenState(StatusCode):
    IDLE = (0, "Idle")
    HEATING = (1, "Heating")


class OvenSelection(StatusCode):
    IDLE = (0, "Idle")
    CONVECTION = (3, "Convection")
    ON_DIFFERENT_LEVELS = (5, "On differend levels")
    CONVECTION_AND_FAN = (7, "Convection and fan")
    DEFROSTING = (8, "Defrosting")
    HEATING = (9, "Heating")
    GRILL = (11, "Grill")
    PIZZA = (13, "Pizza")
    BOTTOM_HEATER = (14, "Bottom heater")
    GRILL_AND_FAN = (19, "Grill and fan")


@dataclass
class OvenStatus:
    machine_state: OvenState
    program: int
    selection: OvenSelection
    temp: float
    tempSet: float
    temp_reached: bool
    program_length_minutes: Optional[int]
    remote_control: bool

    @classmethod
    def from_json(cls, json):
        return cls(
            machine_state=OvenState.from_code(int(json["StartStop"])),
            program=int(only_numerics(json["Program"])),
            selection=OvenSelection.from_code(int(only_numerics(json["Selettore"]))),
            temp=round(fahrenheit_to_celsius(int(json["TempRead"])))
            if not json["Program"].startswith("P")
            else int(json["TempRead"]) / 10,
            tempSet=round(fahrenheit_to_celsius(int(json["TempSet"])))
            if not json["Program"].startswith("P")
            else int(json["TempSet"]) / 10,
            temp_reached=json["TempSetRaggiunta"] == "1",
            program_length_minutes=int(json["TimeProgr"])
            if "TimeProgr" in json
            else None,
            remote_control=json["StatoWiFi"] == "1",
        )


class HobState(StatusCode):
    IDLE = (0, "Idle")
    HEATING = (1, "Heating")
    COOLING_DOWN = (2, "Cooling down")


@dataclass
class HobHeaterStatus:
    heater_state: HobState
    status: bool
    pan: bool
    hot: bool
    low: bool
    combi: bool
    power: int
    timer_minutes: Optional[int]

    @classmethod
    def from_json(cls, json, index):
        return cls(
            heater_state=HobHeaterStatus.parse_state(
                json["Z" + index + "status"], json["Z" + index + "hot"]
            ),
            status=json["Z" + index + "status"] == "1",
            pan=json["Z" + index + "pan"] == "1",
            hot=json["Z" + index + "hot"] == "1",
            low=json["Z" + index + "low"] == "1",
            combi=json["Z" + index + "combi"] == "1",
            power=int(json["Z" + index + "power"]),
            timer_minutes=int(json["Z" + index + "timeh"]) * 60
            + int(json["Z" + index + "timem"])
            if json["Z" + index + "status"] == "1"
            and (
                int(json["Z" + index + "timeh"]) > 0
                or int(json["Z" + index + "timem"]) > 0
            )
            else None,
        )

    @staticmethod
    def parse_state(status, hot) -> str:
        """
        Parse Hob status
        """
        if status == "1":
            return HobState.HEATING

        if hot == "1":
            return HobState.COOLING_DOWN
        else:
            return HobState.IDLE


@dataclass
class HobStatus:
    machine_state: HobState
    heater1: Optional[HobHeaterStatus]
    heater2: Optional[HobHeaterStatus]
    heater3: Optional[HobHeaterStatus]
    heater4: Optional[HobHeaterStatus]
    lock: bool
    remote_control: bool

    @classmethod
    def from_json(cls, json):
        return cls(
            machine_state=HobStatus.parse_state(json),
            heater1=HobHeaterStatus.from_json(json, "1")
            if "Z1status" in json
            else None,
            heater2=HobHeaterStatus.from_json(json, "2")
            if "Z2status" in json
            else None,
            heater3=HobHeaterStatus.from_json(json, "3")
            if "Z3status" in json
            else None,
            heater4=HobHeaterStatus.from_json(json, "4")
            if "Z4status" in json
            else None,
            lock=json["lock"] == "1",
            remote_control=json["StatoWiFi"] == "1",
        )

    @staticmethod
    def parse_state(json) -> str:
        """
        Parse Hob status
        """
        if (
            json["Z1status"] == "1"
            or json["Z2status"] == "1"
            or json["Z3status"] == "1"
            or json["Z4status"] == "1"
        ):
            return HobState.HEATING

        if (
            json["Z1hot"] == "1"
            or json["Z2hot"] == "1"
            or json["Z3hot"] == "1"
            or json["Z4hot"] == "1"
        ):
            return HobState.COOLING_DOWN
        else:
            return HobState.IDLE


class HoodState(StatusCode):
    IDLE = (0, "Idle")
    FAN = (1, "Fan")
    LIGHT = (2, "Light")
    FAN_LIGHT = (3, "Fan & Light")


@dataclass
class HoodStatus:
    machine_state: HoodState
    light: bool
    fan: bool
    grease_filter: bool
    carbon_Filter: bool
    warning: bool
    remote_control: bool

    @classmethod
    def from_json(cls, json):
        return cls(
            machine_state=HoodStatus.parse_state(json),
            light=json["Light"] == "1",
            fan=int(json["Fan"]) > 0,
            grease_filter=json["GreaseFilter"] == "1",
            carbon_Filter=json["CarbonFilter"] == "1",
            warning=json["Warning"] == "1",
            remote_control=json["WiFiStatus"] == "1",
        )

    @staticmethod
    def parse_state(json) -> str:
        """
        Parse Hood status
        """
        if int(json["Fan"]) > 0 and json["Light"] == "1":
            return HoodState.FAN_LIGHT

        if int(json["Fan"]) > 0:
            return HoodState.FAN

        if json["Light"] == "1":
            return HoodState.LIGHT
        else:
            return HoodState.IDLE


class FridgeState(StatusCode):
    NORMAL = (0, "Normal")
    ECO = (1, "Eco")
    SUPER_FREEZING = (2, "Super freezing")
    SMART_COOLING = (3, "Smart cooling")
    SUPER_FREEZING_COOLING = (4, "Super freezing & cooling")
    ERROR = (5, "Error")


@dataclass
class FridgeStatus:
    machine_state: HobState
    cooling_temperature: bool
    freezing_temperature: bool
    eco_mode: bool
    super_freezing_mode: bool
    smart_cooling_mode: bool
    door_locked: bool
    door_open: bool
    fan: int
    error: Optional[int]
    remote_control: bool

    @classmethod
    def from_json(cls, json):
        return cls(
            machine_state=FridgeStatus.parse_state(json),
            cooling_temperature=int(json["FrSet"]),
            freezing_temperature=int(json["FzSet"]),
            eco_mode=json["Eco"] == "1",
            super_freezing_mode=json["Spr"] == "1",
            smart_cooling_mode=json["Ice"] == "1",
            door_locked=json["Lck"] == "1",
            door_open=json["Door"] == "1",
            fan=int(json["Fan"]),
            error=int(json["Error"]) if int(json["Error"]) != 0 in json else None,
            remote_control=json["WiFi"] == "1",
        )

    @staticmethod
    def parse_state(json) -> str:
        """
        Parse Fridge status
        """

        if json["Error"] != "0":
            return FridgeState.ERROR

        if json["Eco"] == "1":
            return FridgeState.ECO

        if json["Ice"] == "1" and json["Spr"] == "1":
            return FridgeState.SUPER_FREEZING_COOLING

        if json["Ice"] == "1":
            return FridgeState.SUPER_FREEZING

        if json["Spr"] == "1":
            return FridgeState.SMART_COOLING
        else:
            return FridgeState.NORMAL


def only_numerics(seq):
    seq_type = type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5.0 / 9.0
