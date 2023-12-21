import PySimpleGUI as sg

from .imgs import WINDOW_ICON, TkImages

import asyncio

WINDOW_COLOR = "#DFDFDF"
TABLE_BG = "#FFFFFF"
ACCENT_COLOR = "#04AEFF"
TABLE_HIGHLIGHT = ("#000000", ACCENT_COLOR)
TAB_PAD = 0
BTN_BORDER = 1
POOLS_TABLE_PAD = 0
TABLE_BORDER = 1
TABLE_HEADER_BORDER = 3
TABLE_PAD = 0
SCROLLBAR_WIDTH = 20
SCROLLBAR_ARROW_WIDTH = 20
SCROLLBAR_RELIEF = sg.RELIEF_RAISED
POOLS_TABLE_BORDER = 1
POOLS_TABLE_HEADER_BORDER = 3

THEME = "Default1"
sg.LOOK_AND_FEEL_TABLE[THEME]["BACKGROUND"] = WINDOW_COLOR
sg.LOOK_AND_FEEL_TABLE[THEME]["PROGRESS_DEPTH"] = 1

sg.theme(THEME)

TABLE_HEADERS = {
    "SCAN": {
        "IP": "ip",
        "Model": "model",
        "Hostname": "hostname",
        "Hashrate": "hashrate",
        "Temp": "temperature_avg",
        "Pool 1 User": "pool_1_user",
        "Wattage": "wattage",
    },
    "BOARDS": {
        "IP": "ip",
        "Model": "model",
        "Ideal": "expected_chips",
        "Total": "total_chips",
        "Chip %": "percent_expected_chips",
        "Board 1": "board_1_chips",
        "Board 2": "board_2_chips",
        "Board 3": "board_3_chips",
        "Board 4": "board_4_chips",
    },
    "CMD": {"IP": "ip", "Model": "model", "Version": "fw_ver", "Output": "output"},
    "POOLS_ALL": {
        "IP": "ip",
        "Quota": "pool_split",
        "Pool 1 User": "pool_1_user",
        "Pool 2 User": "pool_2_user",
        "Pool 3 User": "pool_3_user",
    },
    "POOLS_1": {
        "IP": "ip",
        "Quota": "pool_split",
        "Pool 1": "pool_1_url",
        "Pool 1 User": "pool_1_user",
    },
    "POOLS_2": {
        "IP": "ip",
        "Quota": "pool_split",
        "Pool 2": "pool_2_url",
        "Pool 2 User": "pool_2_user",
    },
    "POOLS_3": {
        "IP": "ip",
        "Quota": "pool_split",
        "Pool 3": "pool_3_url",
        "Pool 3 User": "pool_3_user",
    },
    "CONFIG": {
        "IP": "ip",
        "Model": "model",
        "Pool 1 User": "pool_1_user",
        "Power Limit": "wattage_limit",
    },
    "ERRORS": {
        "IP": "ip",
        "Code": "error_code",
        "Description": "error_desc",
    },
}

TABLE_KEYS = {
    "table": [
        "scan_table",
        "boards_table",
        "errors_table",
        "pools_table",
        "pools_1_table",
        "pools_2_table",
        "cfg_table",
    ],
    "tree": ["cmd_table"],
}

MINER_COUNT_BUTTONS = [
    "miner_count",
]

HASHRATE_TOTAL_BUTTONS = [
    "total_hashrate",
]

BUTTON_KEYS = [
    "btn_scan",
    "btn_cmd",
    "scan_all",
    "scan_refresh",
    "scan_web",
    "boards_report",
    "boards_all",
    "boards_refresh",
    "boards_web",
    "cmd_all",
    "cmd_light",
    "cmd_reboot",
    "cmd_backend",
    "pools_all",
    "pools_refresh",
    "pools_web",
    "cfg_import",
    "cfg_config",
    "cfg_generate",
    "cfg_all",
    "cfg_web",
    "cmd_listen",
    "cmd_wm_unlock",
    "record",
]

TABLE_HEIGHT = 27

IMAGE_COL_WIDTH = 10
IP_COL_WIDTH = 17
MODEL_COL_WIDTH = 15
HOST_COL_WIDTH = 15
HASHRATE_COL_WIDTH = 12
TEMP_COL_WIDTH = 8
USER_COL_WIDTH = 33
WATTAGE_COL_WIDTH = 10
SPLIT_COL_WIDTH = 8
TOTAL_CHIP_WIDTH = 9
expected_CHIP_WIDTH = 9
CHIP_PERCENT_WIDTH = 10
POWER_LIMIT_WIDTH = 12
SCAN_COL_WIDTHS = [
    IP_COL_WIDTH,
    MODEL_COL_WIDTH,
    HOST_COL_WIDTH,
    HASHRATE_COL_WIDTH,
    TEMP_COL_WIDTH,
    USER_COL_WIDTH,
    WATTAGE_COL_WIDTH,
]
TABLE_TOTAL_WIDTH = sum(SCAN_COL_WIDTHS)


async def update_prog_bar(count: int, _max: int = None):
    bar = window["progress_bar"]
    bar.update_bar(count, max=_max)
    if _max:
        bar.maxlen = _max
    if not hasattr(bar, "maxlen"):
        if not _max:
            _max = 100
        bar.maxlen = _max

    percent_done = 100 * (count / bar.maxlen)
    window["progress_percent"].Update(f"{round(percent_done, 2)} %")
    if percent_done == 100:
        await asyncio.sleep(1)
        await update_prog_bar(0)
        window["progress_percent"].Update("")


def get_scan_layout():
    scan_layout = [
        [
            sg.Text(
                "Scan IP",
                pad=((0, 5), (1, 1)),
            ),
            sg.InputText(key="scan_ip", size=(31, 1), focus=True),
            sg.Button(
                "Scan",
                key="btn_scan",
                border_width=BTN_BORDER,
                bind_return_key=True,
            ),
            sg.Button(
                "Cancel",
                key="scan_cancel",
                border_width=BTN_BORDER,
                visible=False,
            ),
        ],
        [
            sg.Button(
                "ALL",
                key="scan_all",
                border_width=BTN_BORDER,
                pad=((0, 5), (1, 1)),
            ),
            sg.Button(
                "REFRESH DATA",
                key="scan_refresh",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "OPEN IN WEB",
                key="scan_web",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "RECORD DATA",
                key="record",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "STOP LISTENING",
                key="scan_cancel_listen",
                border_width=BTN_BORDER,
                visible=False,
            ),
        ],
        [
            sg.Table(
                values=[],
                headings=[heading for heading in TABLE_HEADERS["SCAN"]],
                auto_size_columns=False,
                max_col_width=15,
                justification="center",
                key="scan_table",
                background_color=TABLE_BG,
                selected_row_colors=TABLE_HIGHLIGHT,
                text_color=TABLE_HIGHLIGHT[0],
                col_widths=SCAN_COL_WIDTHS,
                border_width=TABLE_BORDER,
                header_border_width=TABLE_HEADER_BORDER,
                sbar_width=SCROLLBAR_WIDTH,
                sbar_arrow_width=SCROLLBAR_ARROW_WIDTH,
                sbar_relief=SCROLLBAR_RELIEF,
                size=(TABLE_TOTAL_WIDTH, TABLE_HEIGHT),
                expand_x=True,
                expand_y=True,
                enable_click_events=True,
                pad=TABLE_PAD,
            )
        ],
    ]
    return scan_layout


def get_boards_layout():
    BOARDS_COL_WIDTHS = [
        IP_COL_WIDTH,
        MODEL_COL_WIDTH,
        TOTAL_CHIP_WIDTH,
        expected_CHIP_WIDTH,
        CHIP_PERCENT_WIDTH,
    ]
    add_length = TABLE_TOTAL_WIDTH - sum(BOARDS_COL_WIDTHS)
    for i in range(3):
        BOARDS_COL_WIDTHS.append(round(add_length / 4))
    boards_layout = [
        [
            sg.Input(visible=False, enable_events=True, key="boards_report_file"),
            sg.SaveAs(
                "Create Report",
                key="boards_report",
                file_types=(("PDF Files", "*.pdf"),),
                target="boards_report_file",
                pad=((0, 5), (6, 0)),
            ),
        ],
        [
            sg.Button(
                "ALL",
                key="boards_all",
                border_width=BTN_BORDER,
                pad=((0, 5), (1, 1)),
            ),
            sg.Button(
                "REFRESH DATA",
                key="boards_refresh",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "OPEN IN WEB",
                key="boards_web",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "STOP LISTENING",
                key="boards_cancel_listen",
                border_width=BTN_BORDER,
                visible=False,
            ),
        ],
        [
            sg.Table(
                values=[],
                headings=[heading for heading in TABLE_HEADERS["BOARDS"]],
                auto_size_columns=False,
                max_col_width=15,
                justification="center",
                key="boards_table",
                background_color=TABLE_BG,
                selected_row_colors=TABLE_HIGHLIGHT,
                text_color=TABLE_HIGHLIGHT[0],
                col_widths=BOARDS_COL_WIDTHS,
                border_width=TABLE_BORDER,
                header_border_width=TABLE_HEADER_BORDER,
                sbar_width=SCROLLBAR_WIDTH,
                sbar_arrow_width=SCROLLBAR_ARROW_WIDTH,
                sbar_relief=SCROLLBAR_RELIEF,
                size=(TABLE_TOTAL_WIDTH, TABLE_HEIGHT),
                expand_x=True,
                expand_y=True,
                enable_click_events=True,
                pad=TABLE_PAD,
            )
        ],
    ]
    return boards_layout


def get_command_layout():
    data = sg.TreeData()
    col_widths = [
        IP_COL_WIDTH,
        MODEL_COL_WIDTH,
        MODEL_COL_WIDTH,
        TABLE_TOTAL_WIDTH
        - (IP_COL_WIDTH + MODEL_COL_WIDTH + MODEL_COL_WIDTH + IMAGE_COL_WIDTH + 4),
    ]

    command_layout = [
        [
            sg.Text(
                "Custom Command",
                pad=((0, 1), (1, 1)),
            ),
            sg.InputText(key="cmd_txt", expand_x=True),
            sg.Button(
                "Send Command",
                key="btn_cmd",
                border_width=BTN_BORDER,
            ),
        ],
        [
            sg.Button(
                "ALL",
                key="cmd_all",
                border_width=BTN_BORDER,
                pad=((0, 5), (1, 1)),
            ),
            sg.Button(
                "LIGHT",
                key="cmd_light",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "REBOOT",
                key="cmd_reboot",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "RESTART BACKEND",
                key="cmd_backend",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "WM UNLOCK",
                key="cmd_wm_unlock",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "LISTEN",
                key="cmd_listen",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "STOP LISTENING",
                key="cmd_cancel_listen",
                border_width=BTN_BORDER,
                visible=False,
            ),
        ],
        [
            sg.Tree(
                data,
                headings=[heading for heading in TABLE_HEADERS["CMD"]],
                auto_size_columns=False,
                max_col_width=15,
                justification="center",
                key="cmd_table",
                background_color=TABLE_BG,
                selected_row_colors=TABLE_HIGHLIGHT,
                text_color=TABLE_HIGHLIGHT[0],
                col_widths=col_widths,
                border_width=TABLE_BORDER,
                header_border_width=TABLE_HEADER_BORDER,
                sbar_width=SCROLLBAR_WIDTH,
                sbar_arrow_width=SCROLLBAR_ARROW_WIDTH,
                sbar_relief=SCROLLBAR_RELIEF,
                expand_x=True,
                expand_y=True,
                col0_heading="Light",
                col0_width=IMAGE_COL_WIDTH,
                enable_events=True,
                pad=TABLE_PAD,
            )
        ],
    ]
    return command_layout


def get_pools_layout():
    pool_col_width = int((TABLE_TOTAL_WIDTH - (IP_COL_WIDTH + SPLIT_COL_WIDTH)) / 3)
    col_widths = [
        IP_COL_WIDTH,
        SPLIT_COL_WIDTH,
        pool_col_width,
        pool_col_width,
        pool_col_width,
    ]
    pools_layout = [
        [
            sg.Button(
                "ALL",
                key="pools_all",
                border_width=BTN_BORDER,
                pad=((0, 5), (6, 7)),
            ),
            sg.Button(
                "REFRESH DATA",
                key="pools_refresh",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "OPEN IN WEB",
                key="pools_web",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "STOP LISTENING",
                key="pools_cancel_listen",
                border_width=BTN_BORDER,
                visible=False,
            ),
        ],
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab(
                            "All",
                            [
                                [
                                    sg.Table(
                                        values=[],
                                        headings=[
                                            heading
                                            for heading in TABLE_HEADERS["POOLS_ALL"]
                                        ],
                                        auto_size_columns=False,
                                        max_col_width=15,
                                        justification="center",
                                        key="pools_table",
                                        background_color=TABLE_BG,
                                        selected_row_colors=TABLE_HIGHLIGHT,
                                        text_color=TABLE_HIGHLIGHT[0],
                                        border_width=POOLS_TABLE_BORDER,
                                        header_border_width=POOLS_TABLE_HEADER_BORDER,
                                        sbar_width=SCROLLBAR_WIDTH,
                                        sbar_arrow_width=SCROLLBAR_ARROW_WIDTH,
                                        sbar_relief=SCROLLBAR_RELIEF,
                                        col_widths=col_widths,
                                        size=(0, TABLE_HEIGHT),
                                        expand_x=True,
                                        expand_y=True,
                                        enable_click_events=True,
                                        pad=POOLS_TABLE_PAD,
                                    )
                                ]
                            ],
                            pad=TAB_PAD,
                        )
                    ],
                    [
                        sg.Tab(
                            "Pool 1",
                            [
                                [
                                    sg.Table(
                                        values=[],
                                        headings=[
                                            heading
                                            for heading in TABLE_HEADERS["POOLS_1"]
                                        ],
                                        auto_size_columns=False,
                                        max_col_width=15,
                                        justification="center",
                                        key="pools_1_table",
                                        background_color=TABLE_BG,
                                        selected_row_colors=TABLE_HIGHLIGHT,
                                        text_color=TABLE_HIGHLIGHT[0],
                                        border_width=POOLS_TABLE_BORDER,
                                        header_border_width=POOLS_TABLE_HEADER_BORDER,
                                        sbar_width=SCROLLBAR_WIDTH,
                                        sbar_arrow_width=SCROLLBAR_ARROW_WIDTH,
                                        sbar_relief=SCROLLBAR_RELIEF,
                                        col_widths=col_widths,
                                        size=(0, TABLE_HEIGHT),
                                        expand_x=True,
                                        expand_y=True,
                                        enable_click_events=True,
                                        pad=POOLS_TABLE_PAD,
                                    )
                                ]
                            ],
                        )
                    ],
                    [
                        sg.Tab(
                            "Pool 2",
                            [
                                [
                                    sg.Table(
                                        values=[],
                                        headings=[
                                            heading
                                            for heading in TABLE_HEADERS["POOLS_2"]
                                        ],
                                        auto_size_columns=False,
                                        max_col_width=15,
                                        justification="center",
                                        key="pools_2_table",
                                        background_color=TABLE_BG,
                                        selected_row_colors=TABLE_HIGHLIGHT,
                                        text_color=TABLE_HIGHLIGHT[0],
                                        border_width=POOLS_TABLE_BORDER,
                                        header_border_width=POOLS_TABLE_HEADER_BORDER,
                                        sbar_width=SCROLLBAR_WIDTH,
                                        sbar_arrow_width=SCROLLBAR_ARROW_WIDTH,
                                        sbar_relief=SCROLLBAR_RELIEF,
                                        col_widths=col_widths,
                                        size=(0, TABLE_HEIGHT),
                                        expand_x=True,
                                        expand_y=True,
                                        enable_click_events=True,
                                        pad=POOLS_TABLE_PAD,
                                    )
                                ]
                            ],
                        )
                    ],
                    [
                        sg.Tab(
                            "Pool 3",
                            [
                                [
                                    sg.Table(
                                        values=[],
                                        headings=[
                                            heading
                                            for heading in TABLE_HEADERS["POOLS_3"]
                                        ],
                                        auto_size_columns=False,
                                        max_col_width=15,
                                        justification="center",
                                        key="pools_3_table",
                                        background_color=TABLE_BG,
                                        selected_row_colors=TABLE_HIGHLIGHT,
                                        text_color=TABLE_HIGHLIGHT[0],
                                        border_width=POOLS_TABLE_BORDER,
                                        header_border_width=POOLS_TABLE_HEADER_BORDER,
                                        sbar_width=SCROLLBAR_WIDTH,
                                        sbar_arrow_width=SCROLLBAR_ARROW_WIDTH,
                                        sbar_relief=SCROLLBAR_RELIEF,
                                        col_widths=col_widths,
                                        size=(0, TABLE_HEIGHT),
                                        expand_x=True,
                                        expand_y=True,
                                        enable_click_events=True,
                                        pad=POOLS_TABLE_PAD,
                                    )
                                ]
                            ],
                        )
                    ],
                ],
                background_color=WINDOW_COLOR,
                selected_background_color=WINDOW_COLOR,
                border_width=0,
                tab_border_width=2,
                pad=TAB_PAD,
                expand_x=True,
                expand_y=True,
            )
        ],
    ]
    return pools_layout


def get_config_layout():
    CFG_COL_WIDTHS = [
        IP_COL_WIDTH,
        MODEL_COL_WIDTH,
        TABLE_TOTAL_WIDTH - ((30 * 2) + (6 + POWER_LIMIT_WIDTH)),
        POWER_LIMIT_WIDTH,
    ]
    config_layout = [
        [
            sg.Button(
                "IMPORT",
                key="cfg_import",
                border_width=BTN_BORDER,
                pad=((0, 5), (6, 0)),
            ),
            sg.Button(
                "CONFIG",
                key="cfg_config",
                border_width=BTN_BORDER,
                pad=((0, 5), (6, 0)),
            ),
            sg.Button(
                "GENERATE",
                key="cfg_generate",
                border_width=BTN_BORDER,
                pad=((0, 5), (6, 0)),
            ),
            sg.Button(
                "STOP LISTENING",
                key="cfg_cancel_listen",
                border_width=BTN_BORDER,
                pad=((0, 5), (6, 0)),
                visible=False,
            ),
        ],
        [
            sg.Button(
                "ALL",
                key="cfg_all",
                border_width=BTN_BORDER,
                pad=((0, 5), (1, 0)),
            ),
            sg.Button(
                "OPEN IN WEB",
                key="cfg_web",
                border_width=BTN_BORDER,
                pad=((5, 5), (3, 2)),
            ),
            sg.Push(),
            sg.Checkbox(
                "Append IP to Username",
                key="cfg_append_ip",
                pad=((5, 5), (3, 2)),
                checkbox_color=TABLE_BG,
            ),
        ],
        [
            sg.Table(
                values=[],
                headings=[heading for heading in TABLE_HEADERS["CONFIG"]],
                auto_size_columns=False,
                max_col_width=15,
                justification="center",
                key="cfg_table",
                background_color=TABLE_BG,
                selected_row_colors=TABLE_HIGHLIGHT,
                text_color=TABLE_HIGHLIGHT[0],
                header_border_width=TABLE_HEADER_BORDER,
                border_width=TABLE_BORDER,
                sbar_width=SCROLLBAR_WIDTH,
                sbar_arrow_width=SCROLLBAR_ARROW_WIDTH,
                sbar_relief=SCROLLBAR_RELIEF,
                col_widths=CFG_COL_WIDTHS,
                size=(0, TABLE_HEIGHT),
                expand_x=True,
                expand_y=True,
                enable_click_events=True,
                pad=TABLE_PAD,
            ),
            sg.Multiline(
                size=(30, TABLE_HEIGHT + 3),
                key="cfg_config_txt",
                font=("Noto Mono", 9),
                sbar_width=SCROLLBAR_WIDTH,
                sbar_arrow_width=SCROLLBAR_ARROW_WIDTH,
                sbar_relief=SCROLLBAR_RELIEF,
                expand_y=True,
                expand_x=True,
            ),
        ],
    ]
    return config_layout


def get_errors_layout():
    ERRORS_COL_WIDTHS = [IP_COL_WIDTH, 15, TABLE_TOTAL_WIDTH - (15 + IP_COL_WIDTH)]
    errors_layout = [
        [
            sg.Button(
                "ALL",
                key="errors_all",
                border_width=BTN_BORDER,
                pad=((0, 5), (1, 0)),
            ),
            sg.Button(
                "REFRESH DATA",
                key="errors_refresh",
                border_width=BTN_BORDER,
            ),
            sg.Button(
                "OPEN IN WEB",
                key="errors_web",
                border_width=BTN_BORDER,
                pad=((5, 5), (3, 2)),
            ),
        ],
        [
            sg.Table(
                values=[],
                headings=[heading for heading in TABLE_HEADERS["ERRORS"]],
                auto_size_columns=False,
                max_col_width=15,
                justification="center",
                key="errors_table",
                background_color=TABLE_BG,
                selected_row_colors=TABLE_HIGHLIGHT,
                text_color=TABLE_HIGHLIGHT[0],
                header_border_width=TABLE_HEADER_BORDER,
                border_width=TABLE_BORDER,
                sbar_width=SCROLLBAR_WIDTH,
                sbar_arrow_width=SCROLLBAR_ARROW_WIDTH,
                sbar_relief=SCROLLBAR_RELIEF,
                col_widths=ERRORS_COL_WIDTHS,
                size=(0, TABLE_HEIGHT),
                expand_x=True,
                expand_y=True,
                enable_click_events=True,
                pad=TABLE_PAD,
            ),
        ],
    ]
    return errors_layout


layout = [
    [
        sg.Text("", size=(20, 1), key="status"),
        sg.ProgressBar(
            max_value=100,
            size_px=(0, 20),
            bar_color=(ACCENT_COLOR, TABLE_BG),
            expand_x=True,
            key="progress_bar",
        ),
        sg.Text("", size=(20, 1), key="progress_percent", justification="r"),
    ],
    [
        sg.Push(),
        sg.Button(
            "Hashrate: 0 TH/s",
            disabled=True,
            button_color=("black", "white smoke"),
            disabled_button_color=("black", "white smoke"),
            key="total_hashrate",
        ),
        sg.Button(
            "Miners: 0",
            disabled=True,
            button_color=("black", "white smoke"),
            disabled_button_color=("black", "white smoke"),
            key="miner_count",
        ),
        sg.Push(),
    ],
    [
        sg.TabGroup(
            [
                [
                    sg.Tab(
                        "Scan",
                        get_scan_layout(),
                        pad=TAB_PAD,
                    )
                ],
                [
                    sg.Tab(
                        "Boards",
                        get_boards_layout(),
                        pad=TAB_PAD,
                    )
                ],
                [
                    sg.Tab(
                        "Errors",
                        get_errors_layout(),
                        pad=TAB_PAD,
                    )
                ],
                [
                    sg.Tab(
                        "Pools",
                        get_pools_layout(),
                        pad=TAB_PAD,
                    )
                ],
                [
                    sg.Tab(
                        "Configure",
                        get_config_layout(),
                        pad=TAB_PAD,
                    )
                ],
                [
                    sg.Tab(
                        "Command",
                        get_command_layout(),
                        pad=TAB_PAD,
                    )
                ],
            ],
            background_color=WINDOW_COLOR,
            selected_background_color=WINDOW_COLOR,
            border_width=0,
            tab_border_width=2,
            expand_y=True,
            expand_x=True,
        ),
    ],
]

window = sg.Window("Upstream Config Util", layout, icon=WINDOW_ICON, resizable=True)
