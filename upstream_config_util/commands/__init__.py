from pyasic.miners.miner_factory import miner_factory
from pyasic.miners.miner_listener import MinerListener
from pyasic.miners.makes import WhatsMiner
from upstream_config_util.general import btn_all
from upstream_config_util.layout import window, update_prog_bar, WINDOW_ICON
from upstream_config_util.tables import TableManager, TABLE_MANAGER
from upstream_config_util.decorators import disable_buttons
import settings
from typing import Tuple

import PySimpleGUI as sg

import asyncio


async def handle_event(event, value):
    # commands tab
    if event == "cmd_all":
        _table = "cmd_table"
        btn_all(_table, value[_table])
    if event == "cmd_light":
        _table = "cmd_table"
        _ips = value[_table]
        asyncio.create_task(btn_light(_ips))
    if event == "cmd_wm_unlock":
        _table = "cmd_table"
        _ips = value[_table]
        asyncio.create_task(btn_wm_unlock(_ips))
    if event == "cmd_reboot":
        _table = "cmd_table"
        _ips = value[_table]
        asyncio.create_task(btn_reboot(_ips))
    if event == "cmd_backend":
        _table = "cmd_table"
        _ips = value[_table]
        asyncio.create_task(btn_backend(_ips))
    if event == "btn_cmd":
        _table = "cmd_table"
        _ips = value[_table]
        asyncio.create_task(btn_command(_ips, value["cmd_txt"]))
    if event == "cmd_listen":
        asyncio.create_task(btn_listen())
    if not isinstance(event, tuple):
        if event.endswith("cancel_listen"):
            asyncio.create_task(btn_cancel_listen())


@disable_buttons("Flashing Lights")
async def btn_light(ip_idxs: list):
    _table = window["cmd_table"].Widget
    iids = _table.get_children()
    tasks = []
    vals = {}
    for idx in ip_idxs:
        item = _table.item(iids[idx])
        ip = item["values"][0]
        new_light_val = not TABLE_MANAGER.data[ip]["fault_light"]
        tasks.append(_fault_light(ip, new_light_val))
        vals[ip] = new_light_val

    for task in asyncio.as_completed(tasks):
        ip, success = await task
        ip = str(ip)
        if success:
            TABLE_MANAGER.data[ip]["fault_light"] = vals[ip]
            TABLE_MANAGER.data[ip]["output"] = "Fault Light command succeeded."
        else:
            TABLE_MANAGER.data[ip]["output"] = "Fault Light command failed."
        TABLE_MANAGER.update_tables()


@disable_buttons("Unlocking")
async def btn_wm_unlock(ip_idxs: list):
    prog_bar_len = 0
    await update_prog_bar(prog_bar_len, len(ip_idxs))
    _table = window["cmd_table"].Widget
    miners = []
    iids = _table.get_children()
    for idx in ip_idxs:
        item = _table.item(iids[idx])
        ip = item["values"][0]
        miner = await miner_factory.get_miner(ip)
        if isinstance(miner, WhatsMiner):
            miners.append(miner)

    if miners:
        p_bar_len = 0
        await update_prog_bar(0, _max=(len(miners)))
        sent = wm_unlock_generator(miners)
        async for done in sent:
            success = done["Status"]
            if success:
                TABLE_MANAGER.data[str(done["IP"])][
                    "output"
                ] = "Unlock command succeeded."
            else:
                TABLE_MANAGER.data[str(done["IP"])]["output"] = "Unlock command failed."
            p_bar_len += 1
            await update_prog_bar(p_bar_len)
            TABLE_MANAGER.update_tables()
    else:
        await update_prog_bar(100, _max=100)


async def wm_unlock_generator(miners: list):
    loop = asyncio.get_event_loop()
    unlock_tasks = []
    for miner in miners:
        if len(unlock_tasks) >= settings.get("config_threads", 300):
            cmd_sent = asyncio.as_completed(unlock_tasks)
            unlock_tasks = []
            for done in cmd_sent:
                yield await done
        unlock_tasks.append(loop.create_task(_wm_unlock(miner)))
    cmd_sent = asyncio.as_completed(unlock_tasks)
    for done in cmd_sent:
        yield await done


async def _wm_unlock(miner):
    try:
        proc = await miner._reset_api_pwd_to_admin("root")
        return {"IP": miner.ip, "Status": proc}
    except:
        return {"IP": miner.ip, "Status": False}


async def _fault_light(ip: str, on: bool) -> Tuple[str, bool]:
    miner = await miner_factory.get_miner(ip)
    if on:
        success = await miner.fault_light_on()
    else:
        success = await miner.fault_light_off()
    return miner.ip, success


@disable_buttons("Rebooting")
async def btn_reboot(ip_idxs: list):
    _table = window["cmd_table"].Widget
    iids = _table.get_children()
    miners = []
    for idx in ip_idxs:
        item = _table.item(iids[idx])
        ip = item["values"][0]
        miner = await miner_factory.get_miner(ip)
        miners.append(miner)
        for idx in ip_idxs:
            item = _table.item(iids[idx])
            ip = item["values"][0]
            miner = await miner_factory.get_miner(ip)
            miners.append(miner)

        sent = reboot_generator(miners)
        async for done in sent:
            success = done["Status"]
            if success:
                TABLE_MANAGER.data[ip]["output"] = "Reboot command succeeded."
            else:
                TABLE_MANAGER.data[ip]["output"] = "Reboot command failed."
            TABLE_MANAGER.update_tables()


async def reboot_generator(miners: list):
    loop = asyncio.get_event_loop()
    reboot_tasks = []
    for miner in miners:
        if len(reboot_tasks) >= settings.get("reboot_threads", 300):
            cmd_sent = asyncio.as_completed(reboot_tasks)
            reboot_tasks = []
            for done in cmd_sent:
                yield await done
        reboot_tasks.append(loop.create_task(_reboot(miner)))
    cmd_sent = asyncio.as_completed(reboot_tasks)
    for done in cmd_sent:
        yield await done


async def _reboot(miner):
    proc = await miner.reboot()
    return {"IP": miner.ip, "Status": proc}


@disable_buttons("Restarting Backend")
async def btn_backend(ip_idxs: list):
    _table = window["cmd_table"].Widget
    iids = _table.get_children()
    for idx in ip_idxs:
        item = _table.item(iids[idx])
        ip = item["values"][0]
        miner = await miner_factory.get_miner(ip)
        success = await miner.restart_backend()
        if success:
            TABLE_MANAGER.data[ip]["output"] = "Restart Backend command succeeded."
        else:
            TABLE_MANAGER.data[ip]["output"] = "Restart Backend command failed."
    TABLE_MANAGER.update_tables()


@disable_buttons("Sending Command")
async def btn_command(ip_idxs: list, command: str):
    prog_bar_len = 0
    await update_prog_bar(prog_bar_len, len(ip_idxs))
    _table = window["cmd_table"].Widget
    miners = []
    iids = _table.get_children()
    for idx in ip_idxs:
        item = _table.item(iids[idx])
        ip = item["values"][0]
        miner = await miner_factory.get_miner(ip)
        miners.append(miner)

    sent = send_command_generator(miners, command)
    async for done in sent:
        success = done["Status"]
        if not isinstance(done["Status"], str):
            success = f"Command {command} failed."
        TABLE_MANAGER.data[done["IP"]]["output"] = success
        prog_bar_len += 1
        TABLE_MANAGER.update_tables()
        await update_prog_bar(prog_bar_len, len(ip_idxs))


async def send_command_generator(miners: list, command: str):
    loop = asyncio.get_event_loop()
    command_tasks = []
    for miner in miners:
        if len(command_tasks) >= settings.get("config_threads", 300):
            cmd_sent = asyncio.as_completed(command_tasks)
            command_tasks = []
            for done in cmd_sent:
                yield await done
        command_tasks.append(loop.create_task(_send_ssh_command(miner, command)))
    cmd_sent = asyncio.as_completed(command_tasks)
    for done in cmd_sent:
        yield await done


async def _send_ssh_command(miner, command: str):
    proc = await miner.send_ssh_command(command)
    return {"IP": miner.ip, "Status": proc}


CANCEL_LISTEN_BTNS = [
    "cmd_cancel_listen",
    "pools_cancel_listen",
    "boards_cancel_listen",
    "scan_cancel_listen",
    "cfg_cancel_listen",
]

LISTENER = MinerListener()


@disable_buttons("Listening for Miner")
async def btn_listen():
    window["cmd_listen"].update(visible=False)
    for btn in CANCEL_LISTEN_BTNS:
        window[btn].update(visible=True)
    async for miner in LISTENER.listen():
        sg.popup(
            f"IP: {miner['IP']}, MAC: {miner['MAC']}",
            title="Found Miner",
            keep_on_top=True,
            icon=WINDOW_ICON,
        )


async def btn_cancel_listen():
    await LISTENER.cancel()
    window["cmd_listen"].update(visible=True)
    for btn in CANCEL_LISTEN_BTNS:
        window[btn].update(visible=False)
