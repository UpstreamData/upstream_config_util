from copy import copy

import asyncio

from upstream_config_util.boards.report import create_board_report
from upstream_config_util.decorators import disable_buttons
from upstream_config_util.general import btn_all, btn_web, btn_refresh
from upstream_config_util.layout import window
from upstream_config_util.tables import TABLE_MANAGER

CHIP_PCT_IDEAL = 0.9


@disable_buttons("Exporting Report")
async def boards_report(file_location: str):
    table_manager = TABLE_MANAGER

    data = copy(table_manager.data)
    await create_board_report(data, file_location)


async def handle_event(event, value):
    # boards tab
    if event == "boards_all":
        _table = "boards_table"
        btn_all(_table, value[_table])
    if event == "boards_web":
        _table = "boards_table"
        btn_web(_table, value[_table])
    if event == "boards_refresh":
        _table = "boards_table"
        asyncio.create_task(btn_refresh(_table, value[_table]))
    if event == "boards_report_file":
        if not value["boards_report_file"] == "":
            asyncio.create_task(boards_report(value["boards_report_file"]))
            window["boards_report_file"].update("")
