from copy import copy

from upstream_config_util.boards.report import create_board_report
from upstream_config_util.decorators import disable_buttons
from upstream_config_util.tables import TABLE_MANAGER

CHIP_PCT_IDEAL = 0.9


@disable_buttons("Exporting Report")
async def boards_report(file_location: str):
    table_manager = TABLE_MANAGER

    data = copy(table_manager.data)
    await create_board_report(data, file_location)
