from upstream_config_util.layout import (
    MINER_COUNT_BUTTONS,
    HASHRATE_TOTAL_BUTTONS,
    TABLE_KEYS,
    TABLE_HEADERS,
    window,
    WATTAGE_TOTAL_BUTTONS,
)
from upstream_config_util.imgs import LIGHT, FAULT_LIGHT
import PySimpleGUI as sg
import ipaddress

DATA_PARSE_MAP = {
    "IP": {
        "parser": lambda x: x["ip"],
        "default": str,
        "sorter": ipaddress.ip_address,
    },
    "Model": {
        "parser": lambda x: x["model"],
        "default": str,
    },
    "Hostname": {
        "parser": lambda x: x["hostname"],
        "default": str,
    },
    "Hashrate": {
        "parser": lambda x: x["hashrate"],
        "formatter": lambda x: format(
            round(float(x if x is not None else 0), 2), ".2f"
        ).rjust(6, " "),
        "default": float,
        "suffix": " TH/s",
        "sorter": lambda x: float(x.replace(" ", "") if isinstance(x, str) else x),
    },
    "Temp": {
        "parser": lambda x: x["temperature_avg"],
        "default": int,
        "suffix": None,
    },
    "Wattage": {
        "parser": lambda x: x["wattage"],
        "default": int,
    },
    "Ideal": {
        "parser": lambda x: x["expected_chips"],
        "default": int,
    },
    "Board 1": {
        "parser": lambda x: x["hashboards"][0]["chips"],
        "default": int,
    },
    "Board 2": {
        "parser": lambda x: x["hashboards"][1]["chips"],
        "default": int,
    },
    "Board 3": {
        "parser": lambda x: x["hashboards"][2]["chips"],
        "default": int,
    },
    "Board 4": {
        "parser": lambda x: x["hashboards"][3]["chips"],
        "default": int,
    },
    "Total": {
        "parser": lambda x: x["total_chips"],
        "default": int,
    },
    "Nominal": {
        "parser": lambda x: x["nominal"],
        "default": int,
    },
    "Quota": {
        "parser": lambda x: x["config"]["pools"]["groups"][0]["quota"],
        "default": str,
    },
    "Pool 1": {
        "parser": lambda x: x["config"]["pools"]["groups"][0]["pools"][0]["url"],
        "default": str,
    },
    "Pool 1 User": {
        "parser": lambda x: x["config"]["pools"]["groups"][0]["pools"][0]["user"],
        "default": str,
    },
    "Pool 2": {
        "parser": lambda x: x["config"]["pools"]["groups"][0]["pools"][1]["url"],
        "default": str,
    },
    "Pool 2 User": {
        "parser": lambda x: x["config"]["pools"]["groups"][0]["pools"][1]["user"],
        "default": str,
    },
    "Pool 3": {
        "parser": lambda x: x["config"]["pools"]["groups"][0]["pools"][2]["url"],
        "default": str,
    },
    "Pool 3 User": {
        "parser": lambda x: x["config"]["pools"]["groups"][0]["pools"][2]["user"],
        "default": str,
    },
    "Chip %": {
        "parser": lambda x: x["percent_expected_chips"],
        "default": int,
        "suffix": "%",
    },
    "Power Limit": {
        "parser": lambda x: x["wattage_limit"],
        "default": str,
    },
    "Light": {
        "parser": lambda x: x["fault_light"],
        "default": str,
    },
    "Output": {
        "parser": lambda x: x["output"],
        "default": str,
    },
    "Version": {
        "parser": lambda x: x["fw_ver"],
        "default": str,
    },
    "Description": {"default": str},
    "Code": {"default": int},
}


def update_miner_count(count):
    for button in MINER_COUNT_BUTTONS:
        window[button].update(f"Miners: {count}")


def update_total_hr(hashrate: float, expected_hashrate: float):
    if expected_hashrate > 999:
        hashrate = f"{round(hashrate/1000, 2)}/{round(expected_hashrate/1000, 2)} PH/s"
    else:
        hashrate = f"{round(hashrate)}/{round(expected_hashrate)} TH/s"
    for button in HASHRATE_TOTAL_BUTTONS:
        window[button].update(f"Hashrate: {hashrate}")


def update_total_wattage(wattage: float, expected_wattage: float):
    wattage = f"{round(wattage)}/{round(expected_wattage)} W"
    for button in WATTAGE_TOTAL_BUTTONS:
        window[button].update(f"Wattage: {wattage}")


class TableManager:
    def __init__(self):
        self.data = {}
        self.sort_key = "IP"
        self.sort_reverse = False

    def update_data(self, data: list):
        if not data:
            return

        for line in data:
            self.update_item(line)

    def update_sort_key(self, sort_key: str):
        if "▲" in sort_key or "▼" in sort_key:
            sort_key = sort_key[:-1]
        if self.sort_key == sort_key:
            self.sort_reverse = not self.sort_reverse
        self.sort_key = sort_key
        self.update_tables()

    def update_item(self, data: dict):
        if not data or data == {} or not data.get("ip"):
            return

        if not data["ip"] in self.data.keys():
            self.data[data["ip"]] = {}

        if not data.get("fault_light") and not self.data[data["ip"]].get("fault_light"):
            data["fault_light"] = False

        for key in data.keys():
            self.data[data["ip"]][key] = data[key]

        self.update_tables()

    def update_tables(self):
        tables = {
            "SCAN": [["" for _ in TABLE_HEADERS["SCAN"]] for _ in self.data],
            "CMD": [["" for _ in TABLE_HEADERS["CMD"]] for _ in self.data],
            "BOARDS": [["" for _ in TABLE_HEADERS["BOARDS"]] for _ in self.data],
            "POOLS_ALL": [["" for _ in TABLE_HEADERS["POOLS_ALL"]] for _ in self.data],
            "POOLS_1": [["" for _ in TABLE_HEADERS["POOLS_1"]] for _ in self.data],
            "POOLS_2": [["" for _ in TABLE_HEADERS["POOLS_2"]] for _ in self.data],
            "POOLS_3": [["" for _ in TABLE_HEADERS["POOLS_3"]] for _ in self.data],
            "CONFIG": [["" for _ in TABLE_HEADERS["CONFIG"]] for _ in self.data],
            "ERRORS": [],
        }

        ip_sorted_keys = sorted(self.data.keys(), key=lambda x: ipaddress.ip_address(x))
        sorted_keys = sorted(
            ip_sorted_keys, reverse=self.sort_reverse, key=lambda x: self._get_sort(x)
        )

        table_names = {
            "SCAN": "scan_table",
            "BOARDS": "boards_table",
            "POOLS_ALL": "pools_table",
            "POOLS_1": "pools_1_table",
            "POOLS_2": "pools_2_table",
            "POOLS_3": "pools_3_table",
            "CONFIG": "cfg_table",
            "CMD": "cmd_table",
            "ERRORS": "errors_table",
        }

        for table in TABLE_HEADERS:
            widget = window[table_names[table]].Widget
            for idx, header in enumerate(TABLE_HEADERS[table]):
                _header = header
                if header == self.sort_key:
                    if self.sort_reverse:
                        _header = f"{header}▼"
                    else:
                        _header = f"{header}▲"
                widget.heading(idx, text=_header)

        # reset light
        window["cmd_table"].Widget.heading("#0", text="Light")

        # handle light sort key
        if self.sort_key == "Light":
            widget = window["cmd_table"].Widget
            idx = "#0"
            if self.sort_reverse:
                _header = f"Light▼"
            else:
                _header = f"Light▲"
            widget.heading(idx, text=_header)

        for data_idx, ip in enumerate(sorted_keys):
            item = self.data[ip]
            headers = {**TABLE_HEADERS}
            del headers["ERRORS"]
            for table in headers:
                for idx, header in enumerate(TABLE_HEADERS[table]):
                    parse_map = DATA_PARSE_MAP.get(header)
                    if parse_map is None:
                        continue
                    try:
                        val = parse_map["parser"](item)
                    except (LookupError, TypeError):
                        continue
                    if val is None:
                        val = parse_map["default"]()

                    if parse_map.get("formatter") is not None:
                        val = parse_map["formatter"](val)
                    if parse_map.get("suffix") is not None:
                        val = f"{val}{parse_map['suffix']}"
                    tables[table][data_idx][idx] = val

        for data_idx, ip in enumerate(sorted_keys):
            item = self.data[ip]
            for err in item.get("errors", []):
                msg_val = err.get("error_message")
                code_val = str(err.get("error_code"))

                val = [item["ip"], code_val, msg_val]
                tables["ERRORS"].append(val)

        window["scan_table"].update(tables["SCAN"])
        window["boards_table"].update(tables["BOARDS"])
        window["pools_table"].update(tables["POOLS_ALL"])
        window["pools_1_table"].update(tables["POOLS_1"])
        window["pools_2_table"].update(tables["POOLS_2"])
        window["pools_3_table"].update(tables["POOLS_3"])
        window["cfg_table"].update(tables["CONFIG"])

        window["errors_table"].update(tables["ERRORS"])

        treedata = sg.TreeData()
        for idx, item in enumerate(tables["CMD"]):
            ico = LIGHT
            status = " Off"
            if self.data[item[0]]["fault_light"]:
                ico = FAULT_LIGHT
                status = " On"
            treedata.insert("", idx, status, item, icon=ico)

        window["cmd_table"].update(treedata)

        update_miner_count(len(self.data))
        total_hr = 0
        total_expected_hr = 0
        total_wattage = 0
        total_expected_wattage = 0
        for key in self.data.keys():
            hashrate = 0
            expected_hashrate = 0
            wattage = 0
            expected_wattage = 0
            if self.data[key].get("hashrate") is not None:
                hashrate = self.data[key]["hashrate"]
            if self.data[key].get("expected_hashrate") is not None:
                expected_hashrate = self.data[key]["expected_hashrate"]
            if self.data[key].get("wattage") is not None:
                wattage = self.data[key]["wattage"]
            if self.data[key].get("wattage_limit") is not None:
                expected_wattage = self.data[key]["wattage_limit"]
            total_hr += float(hashrate)
            total_expected_hr += float(expected_hashrate)
            total_wattage += float(wattage)
            total_expected_wattage += float(expected_wattage)
        update_total_hr(round(total_hr), round(total_expected_hr))
        update_total_wattage(round(total_wattage), round(total_expected_wattage))

    def _get_sort(self, data_key: str):
        try:
            value = DATA_PARSE_MAP[self.sort_key]["parser"](self.data[data_key])
        except LookupError:
            value = DATA_PARSE_MAP[self.sort_key]["default"]()

        if DATA_PARSE_MAP[self.sort_key].get("suffix") is not None:
            try:
                value = value.replace(
                    f"{DATA_PARSE_MAP[self.sort_key]['suffix']}", ""
                ).strip()
            except AttributeError:
                pass

        if DATA_PARSE_MAP[self.sort_key].get("sorter") is not None:
            return DATA_PARSE_MAP[self.sort_key]["sorter"](value)
        if value is not None:
            return DATA_PARSE_MAP[self.sort_key]["default"](value)
        return DATA_PARSE_MAP[self.sort_key]["default"]()

    def clear_tables(self):
        self.data = {}
        window["total_hashrate"].update("Hashrate: 0/0 TH/s")
        window["total_wattage"].update("Wattage: 0/0 W")
        window["miner_count"].update("Miners: 0")
        for table in TABLE_KEYS["table"]:
            window[table].update([])
        for tree in TABLE_KEYS["tree"]:
            window[tree].update(sg.TreeData())
        update_miner_count(0)


TABLE_MANAGER = TableManager()


def update_tables(data: list or None = None):
    TABLE_MANAGER.update_data(data)


def update_item(data: dict):
    TABLE_MANAGER.update_item(data)


def clear_tables():
    TABLE_MANAGER.clear_tables()


def update_sort_key(sort_key: str):
    TABLE_MANAGER.update_sort_key(sort_key)
