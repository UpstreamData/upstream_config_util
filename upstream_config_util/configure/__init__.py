import asyncio

import FreeSimpleGUI as sg
import yaml

from pyasic.config import MinerConfig
from pyasic.miners.factory import miner_factory
import settings
from upstream_config_util.decorators import disable_buttons
from upstream_config_util.general import update_miners_data, btn_all, btn_web
from upstream_config_util.imgs import WINDOW_ICON
from upstream_config_util.layout import window, update_prog_bar, TABLE_BG

progress_bar_len = 0


async def handle_event(event, value):
    # configure tab
    if event == "cfg_all":
        _table = "cfg_table"
        btn_all(_table, value[_table])
    if event == "cfg_web":
        _table = "cfg_table"
        btn_web(_table, value[_table])
    if event == "cfg_generate":
        await generate_config_ui()
    if event == "cfg_import":
        _table = "cfg_table"
        asyncio.create_task(btn_import(_table, value[_table]))
    if event == "cfg_config":
        _table = "cfg_table"
        asyncio.create_task(
            btn_config(
                _table,
                value[_table],
                value["cfg_config_txt"],
                value["cfg_append_ip"],
            )
        )


@disable_buttons("Importing")
async def btn_import(table, selected):
    if not len(selected) > 0:
        return
    ip = [window[table].Values[row][0] for row in selected][0]
    miner = await miner_factory.get_miner(ip)
    config = await miner.get_config()
    if config:
        window["cfg_config_txt"].update(yaml.dump(config.as_dict(), sort_keys=False))


@disable_buttons("Configuring")
async def btn_config(table, selected, config: str, last_oct_ip: bool):
    ips = [window[table].Values[row][0] for row in selected]
    await send_config(ips, config, last_oct_ip)


async def send_config(ips: list, config: str, last_octet_ip: bool):
    global progress_bar_len
    progress_bar_len = 0
    await update_prog_bar(progress_bar_len, _max=(2 * len(ips)))
    get_miner_genenerator = miner_factory.get_miner_generator(ips)
    all_miners = []
    async for miner in get_miner_genenerator:
        all_miners.append(miner)
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)

    config_sender_generator = send_config_generator(
        all_miners, config, last_octet_ip_user=last_octet_ip
    )
    async for _config_sender in config_sender_generator:
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)
    await asyncio.sleep(3)
    await update_miners_data(ips)


async def send_config_generator(miners: list, config, last_octet_ip_user: bool):
    loop = asyncio.get_event_loop()
    config_tasks = []
    config = MinerConfig.from_dict(yaml.full_load(config))
    for miner in miners:
        if len(config_tasks) >= settings.get("config_threads", 300):
            configured = asyncio.as_completed(config_tasks)
            config_tasks = []
            for sent_config in configured:
                yield await sent_config
        if last_octet_ip_user:
            suffix = f"x{miner.ip.split('.')[-1]}"
            config_tasks.append(
                loop.create_task(miner.send_config(config, user_suffix=suffix))
            )
        else:
            config_tasks.append(loop.create_task(miner.send_config(config)))
    configured = asyncio.as_completed(config_tasks)
    for sent_config in configured:
        yield await sent_config


def generate_config(
    username: str,
    workername: str,
    v2_allowed: bool,
    advanced_cfg: bool,
    autotuning_wattage: int,
    manual_fan_control: bool,
    manual_fan_speed: int,
    min_fans: int,
    target_temp: int,
    hot_temp: int,
    dangerous_temp: int,
    dps_enabled: bool,
    dps_power_step: int,
    dps_min_power: int,
    dps_shutdown_enabled: bool,
    dps_shutdown_duration: int,
):
    if username and workername:
        user = f"{username}.{workername}"
    elif username and not workername:
        user = username
    else:
        return

    if v2_allowed:
        url_1 = "stratum2+tcp://v2.us-east.stratum.braiins.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt"
        url_2 = "stratum2+tcp://v2.stratum.braiins.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt"
        url_3 = "stratum+tcp://stratum.braiins.com:3333"
    else:
        url_1 = "stratum+tcp://ca.stratum.braiins.com:3333"
        url_2 = "stratum+tcp://us-east.stratum.braiins.com:3333"
        url_3 = "stratum+tcp://stratum.braiins.com:3333"
    if not advanced_cfg:
        config = {
            "pools": {
                "groups": [
                    {
                        "name": "group",
                        "quota": 1,
                        "pool": [
                            {"url": url_1, "user": user, "password": "123"},
                            {"url": url_2, "user": user, "password": "123"},
                            {"url": url_3, "user": user, "password": "123"},
                        ],
                    }
                ]
            },
            "temperature": {
                "target": 80.0,
                "hot": 90.0,
                "danger": 120.0,
            },
            "mining_mode": {
                "mode": "power_tuning",
                "power": 1000,
            },
        }
    else:
        config = {
            "pools": {
                "groups": [
                    {
                        "name": "group",
                        "quota": 1,
                        "pool": [
                            {"url": url_1, "user": user, "password": "123"},
                            {"url": url_2, "user": user, "password": "123"},
                            {"url": url_3, "user": user, "password": "123"},
                        ],
                    }
                ]
            },
            "temperature": {
                "target": float(target_temp),
                "hot": float(hot_temp),
                "danger": float(dangerous_temp),
            },
            "mining_mode": {
                "mode": "power_tuning",
                "power": autotuning_wattage,
            },
        }
        if manual_fan_control:
            config["fan_mode"] = {
                "mode": "manual",
                "minimum_fans": min_fans,
                "speed": manual_fan_speed,
            }
        if dps_enabled:
            config["power_scaling"] = {
                "mode": "enabled" if dps_enabled else "disabled",
                "power_step": dps_power_step,
                "minimum_power": dps_min_power,
            }
            if dps_shutdown_enabled:
                config["power_scaling"]["shutdown_enabled"] = {
                    "mode": "enabled",
                    "duration": dps_shutdown_duration,
                }
            else:
                config["power_scaling"]["shutdown_enabled"] = {
                    "mode": "disabled",
                    "duration": dps_shutdown_duration,
                }

    cfg = MinerConfig.from_dict(dict_conf=config)

    window["cfg_config_txt"].update(yaml.dump(cfg.as_dict(), sort_keys=False))


async def generate_config_ui():
    generate_config_window = sg.Window(
        "Generate Config", generate_config_layout(), modal=True, icon=WINDOW_ICON
    )
    while True:
        event, values = generate_config_window.read()
        if event in (None, "Close", sg.WIN_CLOSED):
            break
        if event == "generate_config_window_generate":
            if values["generate_config_window_username"]:
                generate_config(
                    values["generate_config_window_username"],
                    values["generate_config_window_workername"],
                    values["generate_config_window_allow_v2"],
                    values["show_advanced_options"],
                    values["autotuning_wattage"],
                    values["manual_fan_control"],
                    values["manual_fan_speed"],
                    values["min_fans"],
                    values["target_temp"],
                    values["hot_temp"],
                    values["danger_temp"],
                    values["dps_enabled"],
                    values["dps_power_step"],
                    values["dps_min_power"],
                    values["dps_shutdown_enabled"],
                    values["dps_shutdown_duration"],
                )
                generate_config_window.close()
                break
        if event == "show_advanced_options":
            generate_config_window["advanced_options"].update(
                visible=values["show_advanced_options"]
            )

        if event == "autotuning_enabled":
            generate_config_window["autotuning_wattage"].update(
                disabled=not values["autotuning_enabled"]
            )
        if event == "manual_fan_control":
            generate_config_window["manual_fan_speed"].update(
                disabled=not values["manual_fan_control"]
            )
            generate_config_window["min_fans"].update(
                disabled=not values["manual_fan_control"]
            )
        if event == "dps_enabled":
            for elem in ["dps_power_step", "dps_min_power", "dps_shutdown_enabled"]:
                generate_config_window[elem].update(disabled=not values["dps_enabled"])
            if not values["dps_enabled"]:
                generate_config_window["dps_shutdown_duration"].update(disabled=True)
            if values["dps_enabled"] and values["dps_shutdown_enabled"]:
                generate_config_window["dps_shutdown_duration"].update(disabled=False)
        if event == "dps_shutdown_enabled":
            if values["dps_enabled"]:
                generate_config_window["dps_shutdown_duration"].update(
                    disabled=not values["dps_shutdown_enabled"]
                )


def generate_config_layout():
    config_layout = [
        [sg.Text("Enter your pool username and password below to generate a config.")],
        [sg.Text("")],
        [
            sg.Text("Username:", size=(19, 1)),
            sg.InputText(
                key="generate_config_window_username", do_not_clear=True, size=(45, 1)
            ),
        ],
        [
            sg.Text("Worker Name (OPT):", size=(19, 1)),
            sg.InputText(
                key="generate_config_window_workername", do_not_clear=True, size=(45, 1)
            ),
        ],
        [
            sg.Text("Allow Stratum V2?:", size=(19, 1)),
            sg.Checkbox(
                "",
                key="generate_config_window_allow_v2",
                default=True,
                checkbox_color=TABLE_BG,
            ),
        ],
        [
            sg.Push(),
            sg.Checkbox(
                "Advanced Options",
                enable_events=True,
                key="show_advanced_options",
                checkbox_color=TABLE_BG,
            ),
        ],
        [
            sg.pin(
                sg.Column(
                    [
                        [
                            sg.Text("Autotuning Enabled:", size=(19, 1)),
                            sg.Text("Power Limit:"),
                            sg.Spin(
                                [i for i in range(100, 5001, 100)],
                                initial_value=900,
                                size=(5, 1),
                                key="autotuning_wattage",
                                disabled=True,
                            ),
                        ],
                        [
                            sg.Text("Manual Fan Control:", size=(19, 1)),
                            sg.Checkbox(
                                "",
                                key="manual_fan_control",
                                enable_events=True,
                                checkbox_color=TABLE_BG,
                            ),
                            sg.Text("Speed:"),
                            sg.Spin(
                                [i for i in range(5, 101, 5)],
                                initial_value=100,
                                size=(5, 1),
                                key="manual_fan_speed",
                                disabled=True,
                            ),
                            sg.Text("Min Fans:"),
                            sg.Spin(
                                [i for i in range(5)],
                                initial_value=1,
                                size=(5, 1),
                                key="min_fans",
                                disabled=True,
                            ),
                        ],
                        [
                            sg.Text("Target Temp:", size=(19, 1)),
                            sg.Spin(
                                [i for i in range(5, 101, 5)],
                                initial_value=80,
                                size=(5, 1),
                                key="target_temp",
                            ),
                        ],
                        [
                            sg.Text("Hot Temp:", size=(19, 1)),
                            sg.Spin(
                                [i for i in range(5, 111, 5)],
                                initial_value=90,
                                size=(5, 1),
                                key="hot_temp",
                            ),
                        ],
                        [
                            sg.Text("Dangerous Temp:", size=(19, 1)),
                            sg.Spin(
                                [i for i in range(5, 131, 5)],
                                initial_value=100,
                                size=(5, 1),
                                key="danger_temp",
                            ),
                        ],
                        [
                            sg.Text("Dynamic Power Scaling:"),
                            sg.Checkbox(
                                "",
                                key="dps_enabled",
                                enable_events=True,
                                checkbox_color=TABLE_BG,
                            ),
                            sg.Text("Power Step:"),
                            sg.Spin(
                                [i for i in range(50, 301, 5)],
                                initial_value=100,
                                size=(5, 1),
                                key="dps_power_step",
                                disabled=True,
                            ),
                            sg.Text("Min Power:"),
                            sg.Spin(
                                [i for i in range(100, 5001, 100)],
                                initial_value=800,
                                size=(5, 1),
                                key="dps_min_power",
                                disabled=True,
                            ),
                        ],
                        [
                            sg.Text("DPS Shutdown:"),
                            sg.Checkbox(
                                "",
                                key="dps_shutdown_enabled",
                                enable_events=True,
                                disabled=True,
                                checkbox_color=TABLE_BG,
                            ),
                            sg.Text("Shutdown Duration (H):"),
                            sg.Spin(
                                [i for i in range(1, 11, 1)],
                                initial_value=3,
                                size=(5, 1),
                                key="dps_shutdown_duration",
                                disabled=True,
                            ),
                        ],
                    ],
                    key="advanced_options",
                    visible=False,
                    pad=0,
                )
            )
        ],
        [sg.Button("Generate", key="generate_config_window_generate")],
    ]
    return config_layout
