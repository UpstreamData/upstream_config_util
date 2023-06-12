import asyncio
import webbrowser

from pyasic.miners.miner_factory import MinerFactory, miner_factory
from upstream_config_util.decorators import disable_buttons
from upstream_config_util.layout import TABLE_KEYS
from upstream_config_util.layout import window, update_prog_bar, TABLE_HEADERS
from upstream_config_util.tables import TableManager, DATA_HEADER_MAP
from settings import DATA_TO_GET

progress_bar_len = 0

DEFAULT_DATA = set()
headers = []
for table in TABLE_HEADERS:
    for header in TABLE_HEADERS[table]:
        headers.append(headers)
        DEFAULT_DATA.add(TABLE_HEADERS[table][header])


def btn_all(table, selected):
    if table in TABLE_KEYS["table"]:
        if len(selected) == len(window[table].Values):
            window[table].update(select_rows=())
        else:
            window[table].update(
                select_rows=([row for row in range(len(window[table].Values))])
            )

    if table in TABLE_KEYS["tree"]:
        if len(selected) == len(window[table].Widget.get_children()):
            _tree = window[table]
            _tree.Widget.selection_set([])
        else:
            _tree = window[table]
            rows_to_select = [i for i in _tree.Widget.get_children()]
            _tree.Widget.selection_set(rows_to_select)


def btn_web(table, selected):
    for row in selected:
        webbrowser.open("http://" + window[table].Values[row][0])


@disable_buttons("Refreshing")
async def btn_refresh(table, selected):
    ips = [window[table].Values[row][0] for row in selected]
    if not len(selected) > 0:
        ips = [window[table].Values[row][0] for row in range(len(window[table].Values))]

    await update_miners_data(ips)


async def update_miners_data(miners: list):
    data = []
    for miner in miners:
        _data = {}
        for key in DEFAULT_DATA:
            _data[key] = ""
        _data["ip"] = str(miner)
        data.append(_data)

    TableManager().update_data(data)

    global progress_bar_len
    progress_bar_len = 0
    await update_prog_bar(progress_bar_len, _max=len(miners))
    _miners = []
    async for miner in miner_factory.get_miner_generator(miners):
        _miners.append(miner)

    data_generator = asyncio.as_completed([_get_data(miner) for miner in _miners])
    for all_data in data_generator:
        data = await all_data
        TableManager().update_item(data)
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)


async def _get_data(miner):
    return (
        await miner.get_data(data_to_get=DATA_TO_GET)
    ).asdict()
