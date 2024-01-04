import asyncio
import sys
import tkinter as tk

import PySimpleGUI as sg
import pyperclip

from upstream_config_util import scan, boards, configure
from upstream_config_util import tables
from upstream_config_util.general import btn_all, btn_web, btn_refresh
from upstream_config_util.imgs import TkImages
from upstream_config_util.layout import window, TABLE_KEYS
from upstream_config_util.tables import update_selected_miners_total


def _tree_header_click_handler(event, table):
    region = table.Widget.identify("region", event.x, event.y)
    if region == "heading":
        col = int(table.Widget.identify_column(event.x)[1:]) - 1

        if col == -1:
            # handle the "Light" column, which needs a key of #0
            col = "#0"

        heading = table.Widget.heading(col)["text"]

        tables.update_sort_key(heading)


def _table_copy(table):
    selection = window[table].Widget.selection()
    _copy_values = []
    for each in selection:
        try:
            value = window[table].Widget.item(each)["values"]
            values = []
            for item in value:
                values.append(str(item).strip())
            _copy_values.append(values)
        except Exception:
            pass

    copy_values = []
    for item in _copy_values:
        copy_values.append(", ".join(item))
    copy_string = "\n".join(copy_values)
    pyperclip.copy(copy_string)


def _table_select_all(table):
    btn_all(table, window[table].SelectedRows)


def bind_copy(key):
    widget = window[key].Widget
    widget.bind("<Control-Key-c>", lambda x: _table_copy(key))


def bind_ctrl_a(key):
    widget = window[key].Widget
    widget.bind("<Control-Key-a>", lambda x: _table_select_all(key))


async def ui():
    window.read(1)
    tables.update_tables()

    for key in [*TABLE_KEYS["table"], *TABLE_KEYS["tree"]]:
        bind_copy(key)
        bind_ctrl_a(key)

    # create images used in the table, they will not show if not saved here
    tk_imgs = TkImages()  # noqa - need to save this in memory to hold images

    # left justify hostnames
    window["scan_table"].Widget.column(2, anchor=tk.W)

    # cmd table sort event
    window["cmd_table"].Widget.bind(
        "<Button-1>", lambda x: _tree_header_click_handler(x, window["cmd_table"])
    )
    window["cmd_table"].Widget.column("#0", stretch=tk.NO, anchor=tk.CENTER)

    while True:
        event, value = window.read(0.001)
        if event in (None, "Close", sg.WIN_CLOSED):
            sys.exit()

        if isinstance(event, tuple):
            if event[0].endswith("_table"):
                if event[2][0] == -1:
                    table = window[event[0]].Widget
                    tables.update_sort_key(table.heading(event[2][1])["text"])

        await scan.handle_event(event, value)

        await boards.handle_event(event, value)

        await configure.handle_event(event, value)

        # pools tab
        if event == "pools_all":
            _table = "pools_table"
            btn_all(_table, value[_table])
        if event == "pools_web":
            _table = "pools_table"
            btn_web(_table, value[_table])
        if event == "pools_refresh":
            _table = "pools_table"
            asyncio.create_task(btn_refresh(_table, value[_table]))

        # errors tab
        if event == "errors_all":
            _table = "pools_table"
            btn_all(_table, value[_table])
        if event == "errors_web":
            _table = "pools_table"
            btn_web(_table, value[_table])
        if event == "errors_refresh":
            _table = "pools_table"
            asyncio.create_task(btn_refresh(_table, value[_table]))

        if "+CLICKED+" in event:
            if "_table" in event[0]:
                update_selected_miners_total(event[0], value[event[0]])
        elif event == "cmd_table":
            update_selected_miners_total(event, value[event])

        if event == "__TIMEOUT__":
            await asyncio.sleep(0.001)


if __name__ == "__main__":
    asyncio.run(ui())
