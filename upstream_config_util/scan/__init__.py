import asyncio
import logging

from pyasic.miners.miner_factory import MinerFactory
from pyasic.network import MinerNetwork
from upstream_config_util.decorators import disable_buttons
from upstream_config_util.layout import window, update_prog_bar, TABLE_HEADERS
from upstream_config_util.tables import clear_tables, TableManager, DATA_HEADER_MAP


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ScanManager(metaclass=Singleton):
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


progress_bar_len = 0


DEFAULT_DATA = set()

for table in TABLE_HEADERS:
    for header in TABLE_HEADERS[table]:
        DEFAULT_DATA.add(TABLE_HEADERS[table][header])


async def scan_cancel():
    await ScanManager().cancel()


async def btn_all():
    tbl = "scan_table"
    window[tbl].update(select_rows=([row for row in range(len(window[tbl].Values))]))


async def btn_scan(scan_ip: str):
    network = MinerNetwork("192.168.1.0")
    if scan_ip:
        if "/" in scan_ip:
            ip, mask = scan_ip.split("/")
            network = MinerNetwork(ip, mask=mask)
        else:
            network = MinerNetwork(scan_ip)
    asyncio.create_task(ScanManager().scan_miners(network))


@disable_buttons("Scanning")
async def _scan_miners(network: MinerNetwork):
    """Scan the given network for miners, get data, and fill in the table."""
    # clear the tables on the config tool to prepare for new miners
    clear_tables()

    # clear miner factory cache to make sure we are getting correct miners
    MinerFactory().clear_cached_miners()

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
            if miner:
                miners.append(miner)

                # sort the list of miners by IP
                miners.sort()

                # generate default data for the table manager
                _data = {}
                for key in DEFAULT_DATA:
                    _data[key] = ""
                _data["ip"] = str(miner.ip)
                TableManager().update_item(_data)

                # create a task to get data, and save it to ensure it finishes
                data_tasks.append(asyncio.create_task(_get_miner_data(miner)))

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

    TableManager().update_item(await _get_data(miner))

    progress_bar_len += 1
    await update_prog_bar(progress_bar_len)


async def _get_data(miner):
    return (
        await miner.get_data(
            data_to_get=[
                "model",
                "fw_ver",
                "hostname",
                "hashrate",
                "nominal_hashrate",
                "hashboards",
                "wattage",
                "wattage_limit",
                "fault_light",
                "pools",
            ]
        )
    ).asdict()
