import datetime
import ipaddress
from base64 import b64decode
from copy import copy
from io import BytesIO, StringIO
from typing import List
from xml.etree import ElementTree

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.lib.styles import (
    ParagraphStyle,
    TA_CENTER,  # noqa - not declared in __all__
)
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate,
    KeepInFrame,
    Table,
    Image,
    Paragraph,
    TableStyle,
    PageBreak,
    Spacer,
)
from svglib.svglib import svg2rlg

from upstream_config_util.decorators import disable_buttons
from upstream_config_util.imgs import LOGO
from upstream_config_util.tables import TABLE_MANAGER

CHIP_PCT_IDEAL = 0.9

IP_STYLE = ParagraphStyle(
    "IP Style",
    alignment=TA_CENTER,
    fontSize=7,
    fontName="Helvetica-Bold",
)
TITLE_STYLE = ParagraphStyle(
    "Title",
    alignment=TA_CENTER,
    fontSize=20,
    spaceAfter=40,
    fontName="Helvetica-Bold",
)
BOARD_WIDTH = 10
SVG_WIDTH = 100
SVG_HEIGHT = 100
BOARD_GOOD_COLOR = "#008000"
BOARD_BAD_COLOR = "#C00000"
OUTER_SPACING = 20
SVG = """
<svg id="miner_base" width="250" height="250" version="1.1" viewBox="0 0 100 100" xml:space="preserve" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="background"><image id="image1792" width="100" height="100" image-rendering="optimizeSpeed" preserveAspectRatio="none" xlink:href="data:image/png;base64,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 "/></g><g id="fan" fill="none" stroke="#000"><g id="Fan" stroke-width="5"><g id="Outer"><path id="Outer_Lines" d="m2.6291 97.371 23.282-23.282m48.193-48.193 23.267-23.267m-94.742-4e-7 23.282 23.282m48.178 48.178 23.282 23.282"/><path id="Outer_Circle" d="m85 50a35 35 0 0 1-35 35 35 35 0 0 1-35-35 35 35 0 0 1 35-35 35 35 0 0 1 35 35z" stroke-linecap="round" stroke-linejoin="round" style="paint-order:markers stroke fill"/></g><g id="Inner" transform="matrix(.33644 0 0 .33644 33.183 33.173)"><path id="Inner_Lines" d="m2.6291 97.371 23.282-23.282m48.193-48.193 23.267-23.267m-94.742-4e-7 23.282 23.282m48.178 48.178 23.282 23.282"/><path id="Inner_Circle" d="m85 50a35 35 0 0 1-35 35 35 35 0 0 1-35-35 35 35 0 0 1 35-35 35 35 0 0 1 35 35z" stroke-linecap="round" stroke-linejoin="round" style="paint-order:markers stroke fill"/></g><g id="Mid" transform="matrix(.66139 0 0 .66139 16.93 16.93)"><path id="Mid_Lines" d="m2.6291 97.371 23.282-23.282m48.193-48.193 23.267-23.267m-94.742-4e-7 23.282 23.282m48.178 48.178 23.282 23.282"/><path id="Mid_Circle" d="m85 50a35 35 0 0 1-35 35 35 35 0 0 1-35-35 35 35 0 0 1 35-35 35 35 0 0 1 35 35z" stroke-linecap="round" stroke-linejoin="round" style="paint-order:markers stroke fill"/></g></g><path id="Outline" d="m2.6291 2.6291h94.742v94.742h-94.742zm13.847 7.6e-6h67.048c7.6712 0 13.847 6.1757 13.847 13.847v67.048c0 7.6712-6.1757 13.847-13.847 13.847h-67.048c-7.6712 0-13.847-6.1757-13.847-13.847v-67.048c0-7.6712 6.1757-13.847 13.847-13.847zm81.024 47.371a47.5 47.5 0 0 1-47.5 47.5 47.5 47.5 0 0 1-47.5-47.5 47.5 47.5 0 0 1 47.5-47.5 47.5 47.5 0 0 1 47.5 47.5z" stroke-linecap="round" stroke-width="5.2582" style="paint-order:markers stroke fill"/></g></svg>
"""


def add_first_page_number(canvas, doc):
    canvas.saveState()
    canvas.drawString(letter[0] - 60, 20, "Page " + str(doc.page))
    canvas.restoreState()


def add_page_header(canvas, doc):
    canvas.saveState()
    canvas.drawCentredString(
        (letter[0] / 16) * 14,
        letter[1] - 57,
        datetime.datetime.now().strftime("%Y-%b-%d"),
    )
    img_dec = b64decode(LOGO)
    img = BytesIO(img_dec)
    img.seek(0)

    canvas.drawImage(
        ImageReader(img),
        30,
        letter[1] - 65,
        150,
        35,
    )
    canvas.drawString(letter[0] - 60, 20, "Page " + str(doc.page))
    canvas.restoreState()


@disable_buttons("Exporting Report")
async def boards_report(file_location):
    p1_logo, p1_title = create_first_page()
    table_manager = TABLE_MANAGER

    data = copy(table_manager.data)

    for ip in data:
        if isinstance(data[ip]["hashrate"], str):
            data[ip]["hashrate"] = float(
                data[ip]["hashrate"].replace("TH/s", "").strip()
            )

    list_data = []
    for ip in data.keys():
        new_data = data[ip]
        new_data["ip"] = ip
        list_data.append(new_data)

    list_data = sorted(
        list_data, reverse=False, key=lambda x: ipaddress.ip_address(x["ip"])
    )
    boards_data = {}
    for miner in list_data:
        boards_data[miner["ip"]] = []
        for board in miner["hashboards"]:
            chips = board.get("chips")
            if chips is None:
                chips = 0
            expected = board.get("expected_chips")
            if expected is None:
                expected = 0

            if chips < (expected * CHIP_PCT_IDEAL):
                boards_data[miner["ip"]].append(False)
            else:
                boards_data[miner["ip"]].append(True)

    doc = SimpleDocTemplate(
        file_location,
        pagesize=letter,
        topMargin=1 * inch,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        bottomMargin=1 * inch,
        title=f"Board Report {datetime.datetime.now().strftime('%Y/%b/%d')}",
    )

    pie_chart, board_table = create_boards_pie_chart(boards_data, list_data)

    table_data = get_table_data(boards_data)

    miner_img_table = Table(
        table_data,
        colWidths=0.8 * inch,
    )

    miner_img_table.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 0), (-1, 0)),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 0),
                ("TOPPADDING", (0, 1), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 20),
                ("TOPPADDING", (0, 0), (-1, 0), 20),
            ]
        )
    )
    elements = [
        p1_logo,
        p1_title,
        PageBreak(),
        pie_chart,
        Spacer(0, 60),
        board_table,
        PageBreak(),
        miner_img_table,
        PageBreak(),
        Paragraph(
            "Board Data",
            style=TITLE_STYLE,
        ),
        create_data_table(list_data),
        PageBreak(),
        # create_recommendations_page(),
    ]

    doc.build(
        elements,
        onFirstPage=add_first_page_number,
        onLaterPages=add_page_header,
    )


def create_boards_pie_chart(data, list_data: list):
    labels = ["All Working", "1 Bad Board", "2 Bad Boards", "3 Bad Boards"]
    num_bad_boards = [0, 0, 0, 0]
    est_wattage = [0, 0, 0, 0]
    est_missing_wattage = [0, 0, 0, 0]
    est_hashrate = [0, 0, 0, 0]
    est_missing_hashrate = [0, 0, 0, 0]
    efficiency = [0, 0, 0, 0]
    for item in data.keys():
        num_bad_boards[data[item].count(False)] += 1
        est_total_wattage = 0
        est_total_hashrate = 0
        power_limit = 0
        for list_data_item in list_data:
            if list_data_item["ip"] == item:
                est_total_wattage = list_data_item.get("wattage")
                if est_total_wattage is None:
                    est_total_wattage = 0
                est_total_hashrate = list_data_item.get("hashrate")
                if est_total_hashrate is None:
                    est_total_hashrate = 0
                power_limit = list_data_item.get("wattage_limit")
                if power_limit is None:
                    power_limit = 0

        est_wattage[data[item].count(False)] += est_total_wattage
        est_missing_wattage[data[item].count(False)] += power_limit - est_total_wattage
        est_hashrate[data[item].count(False)] += round(est_total_hashrate)
    for idx in range(4):
        efficiency[idx] = f"{round(est_wattage[idx]/(est_hashrate[idx]+1))} W/TH"
        if not idx == 0 and not idx == 3:
            est_missing_hashrate[idx] = round(
                est_missing_wattage[idx]
                / (round(est_wattage[idx] / (est_hashrate[idx] + 1) + 1))
            )
        if idx == 3:
            eff_data = [
                int(efficiency[0].replace(" W/TH", "")),
                int(efficiency[1].replace(" W/TH", "")),
                int(efficiency[2].replace(" W/TH", "")),
            ]
            avg_eff = sum(eff_data) / len(eff_data)
            est_missing_hashrate[idx] = 0
            if not avg_eff == 0:
                est_missing_hashrate[idx] = round(est_missing_wattage[idx] / avg_eff)

        if est_wattage[idx] > 10000:
            est_wattage[idx] = f"{round(est_wattage[idx]/1000, 2)} kW"
        else:
            est_wattage[idx] = f"{est_wattage[idx]} W"
        est_missing_wattage[idx] = f"{est_missing_wattage[idx]} W"
        est_hashrate[idx] = f"{est_hashrate[idx]} TH/s"
        est_missing_hashrate[idx] = f"{est_missing_hashrate[idx]} TH/s"
    idxs = []
    graph_labels = copy(labels)
    graph_num_bad_board = copy(num_bad_boards)
    for idx in range(len(num_bad_boards)):
        if num_bad_boards[idx] == 0:
            idxs.append(idx)
        idxs.sort(reverse=True)
    for idx in idxs:
        graph_labels.pop(idx)
        graph_num_bad_board.pop(idx)

    cmap = plt.get_cmap("Blues")
    cs = cmap(np.linspace(0.2, 0.8, num=len(graph_num_bad_board)))

    # fig, ax = plt.subplots() -> causes window resizing...
    fig = Figure()
    ax = fig.add_subplot()
    ax.pie(
        graph_num_bad_board,
        labels=graph_labels,
        autopct="%1.2f%%",
        shadow=True,
        startangle=180,
        colors=cs,
        pctdistance=0.8,
    )
    ax.axis("equal")
    ax.set_title("Miner Status", fontsize=24, pad=20)

    imgdata = BytesIO()
    fig.savefig(imgdata, format="svg")
    imgdata.seek(0)  # rewind the data
    drawing = svg2rlg(imgdata)
    imgdata.close()
    plt.close("all")
    pie_chart = KeepInFrame(375, 375, [Image(drawing)], hAlign="CENTER")
    table_data = [
        ["-", *labels],
        ["Miners", *num_bad_boards],
        ["Est. Watts", *est_wattage],
        ["Est. Missing Watts", *est_missing_wattage],
        ["Est. Hashrate", *est_hashrate],
        ["Est. Missing Hashrate", *est_missing_hashrate],
        ["Efficiency", *efficiency],
    ]

    t = Table(table_data)

    table_style = TableStyle(
        [
            # ("FONTSIZE", (0, 0), (-1, -1), 13),
            # line for below titles
            ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            # line for above totals
            ("LINEABOVE", (0, -1), (-1, -1), 2, colors.black),
            # line for beside unit #
            ("LINEAFTER", (0, 0), (0, -1), 2, colors.black),
            # gridlines and outline of table
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("BOX", (0, 0), (-1, -1), 2, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            # color the table
            ("TEXTCOLOR", (4, 1), (4, -1), colors.red),
            ("TEXTCOLOR", (3, 1), (3, -1), colors.orangered),
            ("TEXTCOLOR", (2, 1), (2, -1), colors.yellow),
            ("TEXTCOLOR", (1, 1), (1, -1), colors.green),
        ]
    )

    t.setStyle(table_style)

    # zebra stripes on table
    for each in range(len(table_data)):
        if each % 2 == 0:
            bg_color = colors.lightgrey
        else:
            bg_color = colors.darkgrey

        t.setStyle(TableStyle([("BACKGROUND", (0, each), (-1, each), bg_color)]))

    return pie_chart, t


def create_first_page():
    title_style = ParagraphStyle(
        "Title",
        alignment=TA_CENTER,
        fontSize=50,
        spaceAfter=40,
        spaceBefore=150,
        fontName="Helvetica-Bold",
    )

    img_dec = b64decode(LOGO)
    img = BytesIO(img_dec)
    img.seek(0)

    logo = KeepInFrame(450, 105, [Image(img)])
    title = Paragraph("Board Report", style=title_style)
    return logo, title


def create_data_table(data):
    table_data = []
    for miner in data:
        miner_bad_boards = 0
        for board in miner["hashboards"]:
            chips = board.get("chips")
            if chips is None:
                chips = 0
            expected = board.get("expected_chips")
            if expected is None:
                expected = 0

            if chips < (expected * CHIP_PCT_IDEAL):
                miner_bad_boards += 1

        table_data.append(
            [
                miner["ip"],
                miner["model"] if miner["model"] is not None else "?",
                miner["total_chips"] if miner["total_chips"] is not None else 0,
                miner["ideal_chips"] if miner["ideal_chips"] is not None else 0,
                miner_bad_boards,
            ]
        )

    table_data.append(
        [
            "Total",
            "-",
            sum([miner[2] for miner in table_data]),
            sum([miner[3] for miner in table_data]),
            sum([miner[4] for miner in table_data]),
        ]
    )

    table_data[:0] = (
        [
            "IP",
            "Model",
            "Total Chips",
            "Ideal Chips",
            "Failed Boards",
        ],
    )

    # create the table
    t = Table(table_data, repeatRows=1, colWidths="*")
    col_widths = [10, 10, 10, 10, 10]

    # generate a basic table style
    table_style = TableStyle(
        [
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            # line for below titles
            ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            # line for above totals
            ("LINEABOVE", (0, -1), (-1, -1), 2, colors.black),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            # line for beside unit #
            ("LINEAFTER", (0, 0), (0, -1), 2, colors.black),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            # gridlines and outline of table
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("BOX", (0, 0), (-1, -1), 2, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
    )

    for (
        row,
        values,
    ) in enumerate(table_data):
        if not row == 0 and not row == (len(table_data) - 1):
            failed_boards = values[4]
            if not failed_boards == 0:
                table_style.add("TEXTCOLOR", (6, row), (6, row), colors.red)

    # set the styles to the table
    t.setStyle(table_style)

    # zebra stripes on table
    for each in range(len(table_data)):
        if each % 2 == 0:
            bg_color = colors.lightgrey
        else:
            bg_color = colors.darkgrey

        t.setStyle(TableStyle([("BACKGROUND", (0, each), (-1, each), bg_color)]))

    return t


def get_table_data(data):
    table_elems = [[Paragraph("Hashboard Visual Representation", style=TITLE_STYLE)]]
    table_row = []
    table_style = TableStyle(
        [
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("BOX", (0, 0), (-1, -1), 2, colors.black),
        ]
    )
    table_width = 0.8 * inch
    for ip in data.keys():
        img = svg2rlg(StringIO(create_board_svg(data[ip])))
        image = KeepInFrame(table_width, table_width, [img])

        ip_para = Paragraph(ip, style=IP_STYLE)

        table_row.append(
            Table([[ip_para], [image]], colWidths=table_width, style=table_style)
        )

        # table_row.append(image)
        # table_row_txt.append(ip_para)

        if len(table_row) > 7:
            # table_elems.append(table_row_txt)
            # table_elems.append(table_row)
            table_elems.append(table_row)
            # table_row_txt = []
            table_row = []
    if not table_row == []:
        table_elems.append(table_row)
    return table_elems


def create_recommendations_page(data: list):
    return None


def create_board_svg(boards: List[bool]):
    root = ElementTree.fromstring(SVG)

    background_group = root.find(".//*[@id='background']")

    spacing = (SVG_WIDTH - (OUTER_SPACING * 2)) / (len(boards) - 1)

    for i, val in enumerate(boards):
        x = OUTER_SPACING + (i * spacing) - BOARD_WIDTH / 2
        board_color = BOARD_GOOD_COLOR if val else BOARD_BAD_COLOR

        board = ElementTree.Element(
            "rect",
            {
                "x": str(x),
                "y": str(5),
                "width": str(BOARD_WIDTH),
                "height": str(SVG_HEIGHT - 10),
                "fill": board_color,
            },
        )

        background_group.append(board)

    root.attrib["xmlns"] = "http://www.w3.org/2000/svg"

    return ElementTree.tostring(root).decode()
