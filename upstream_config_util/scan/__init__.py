import asyncio
import logging

from pyasic.miners.miner_factory import miner_factory
from pyasic.network import MinerNetwork
from upstream_config_util import tables
from upstream_config_util.decorators import disable_buttons
from upstream_config_util.general import btn_all, btn_web, btn_refresh
from upstream_config_util.layout import update_prog_bar, TABLE_HEADERS
from upstream_config_util.layout import window
from upstream_config_util.record import record_ui
from upstream_config_util.tables import clear_tables
import settings

TABLE = "scan_table"


async def handle_event(event, value):
    if event == "scan_all":
        btn_all(TABLE, value[TABLE])
    if event == "scan_web":
        btn_web(TABLE, value[TABLE])
    if event == "scan_refresh":
        asyncio.create_task(btn_refresh(TABLE, value[TABLE]))
    if event == "btn_scan":
        asyncio.create_task(btn_scan(value["scan_ip"]))
    if event == "scan_cancel":
        asyncio.create_task(scan_cancel())
    if event == "record":
        if value[TABLE]:
            ips = [window[TABLE].Values[row][0] for row in value[TABLE]]
        else:
            ips = [
                window[TABLE].Values[row][0] for row in range(len(window[TABLE].Values))
            ]
        asyncio.create_task(record_ui(ips))


class ScanTabManager:
    def __init__(self):
        self.scan_task = None

    async def scan_miners(self, network: MinerNetwork):
        self.scan_task = asyncio.create_task(_scan_miners(network))
        window["scan_cancel"].update(visible=True)
        await self.scan_task
        window["scan_cancel"].update(visible=False)

    async def cancel(self):
        self.scan_task.cancel()
        window["scan_cancel"].update(visible=False)
        while not self.scan_task.done():
            await asyncio.sleep(0.1)


progress_bar_len = 0
DEFAULT_DATA = set()
SCAN_TAB_MANAGER = ScanTabManager()

for table in TABLE_HEADERS:
    for header in TABLE_HEADERS[table]:
        DEFAULT_DATA.add(TABLE_HEADERS[table][header])


async def scan_cancel():
    await SCAN_TAB_MANAGER.cancel()


async def btn_scan(scan_ip: str = None):
    if scan_ip is not None:
        if "/" in scan_ip:
            ip, mask = scan_ip.split("/")
            network = MinerNetwork(ip, mask=mask)
        else:
            network = MinerNetwork(scan_ip)
    else:
        network = MinerNetwork("192.168.1.0")
    asyncio.create_task(SCAN_TAB_MANAGER.scan_miners(network))


@disable_buttons("Scanning")
async def _scan_miners(network: MinerNetwork):
    """Scan the given network for miners, get data, and fill in the table."""
    # clear the tables on the config tool to prepare for new miners
    clear_tables()

    # clear miner factory cache to make sure we are getting correct miners
    miner_factory.clear_cached_miners()

    # create async generator to scan network for miners
    scan_generator = network.scan_network_generator()

    # set progress bar length to 2x network size and reset it to 0
    global progress_bar_len
    progress_bar_len = 0
    network_size = len(network)
    await update_prog_bar(progress_bar_len, _max=(2 * network_size))

    #  asynchronously get each miner scanned by the generator
    miners = []
    data_tasks = []
    try:
        async for miner in scan_generator:
            # if the generator yields a miner, add it to our list
            if miner is not None:
                miners.append(miner)

                # sort the list of miners by IP
                miners.sort()

                # generate default data for the table manager
                _data = {"ip": str(miner.ip)}
                tables.update_item(_data)

                # create a task to get data, and save it to ensure it finishes
                data_tasks.append(asyncio.create_task(_get_miner_data(miner)))
            else:
                progress_bar_len += 1

            # update progress bar to indicate scanned miners
            progress_bar_len += 1
            await update_prog_bar(progress_bar_len)
    except asyncio.CancelledError:
        logging.info("Cancelled scan.")
        await update_prog_bar(progress_bar_len)

    # make sure all getting data has finished
    await asyncio.gather(*data_tasks)

    # finish updating progress bar
    await update_prog_bar(100, 100)


async def _get_miner_data(miner):
    global progress_bar_len

    tables.update_item(await _get_data(miner))

    progress_bar_len += 1
    await update_prog_bar(progress_bar_len)


async def _get_data(miner):
    return (await miner.get_data(include=settings.get("include"))).asdict()
