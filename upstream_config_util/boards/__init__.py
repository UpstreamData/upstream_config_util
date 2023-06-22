import datetime
import ipaddress
from base64 import b64decode
from io import BytesIO
from copy import copy

import cairosvg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from reportlab.graphics import renderPDF
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

from pyasic.miners.miner_factory import MinerFactory
from upstream_config_util.decorators import disable_buttons
from upstream_config_util.imgs import IMAGE_SELECTION_MATRIX, LOGO
from upstream_config_util.tables import TableManager
from xml.etree import ElementTree
from typing import List


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
<svg id="miner_base" width="250" height="250" version="1.1" viewBox="0 0 100 100">
    <defs>
        <linearGradient id="background_gradient" x1="100" x2="47.686" y1="100" y2="46.963" gradientUnits="userSpaceOnUse">
            <stop stop-color="#000080" offset="0"/>
            <stop stop-color="#008080" offset="1"/>
        </linearGradient>
        <filter id="blur_filter" x="-.075" y="-.075" width="1.15" height="1.15" color-interpolation-filters="sRGB">
            <feGaussianBlur stdDeviation="3.125"/>
        </filter>
    </defs>
    <g id="background">
        <rect id="Gradient" x="9.5911e-8" width="100" height="100" fill="url(#background_gradient)" filter="url(#blur_filter)" stroke-width=".18428" style="mix-blend-mode:normal"/>
    </g>
    <g id="fan" fill="none" stroke="#000">
        <g id="Fan" stroke-width="5">
            <g id="Outer">
                <path id="Outer_Lines" d="m2.6291 97.371 23.282-23.282m48.193-48.193 23.267-23.267m-94.742-4e-7 23.282 23.282m48.178 48.178 23.282 23.282"/>
                <path id="Outer_Circle" d="m85 50a35 35 0 0 1-35 35 35 35 0 0 1-35-35 35 35 0 0 1 35-35 35 35 0 0 1 35 35z" stroke-linecap="round" stroke-linejoin="round" style="paint-order:markers stroke fill"/>
            </g>
            <g id="Inner" transform="matrix(.33644 0 0 .33644 33.183 33.173)">
                <path id="Inner_Lines" d="m2.6291 97.371 23.282-23.282m48.193-48.193 23.267-23.267m-94.742-4e-7 23.282 23.282m48.178 48.178 23.282 23.282"/>
                <path id="Inner_Circle" d="m85 50a35 35 0 0 1-35 35 35 35 0 0 1-35-35 35 35 0 0 1 35-35 35 35 0 0 1 35 35z" stroke-linecap="round" stroke-linejoin="round" style="paint-order:markers stroke fill"/>
            </g>
            <g id="Mid" transform="matrix(.66139 0 0 .66139 16.93 16.93)">
                <path id="Mid_Lines" d="m2.6291 97.371 23.282-23.282m48.193-48.193 23.267-23.267m-94.742-4e-7 23.282 23.282m48.178 48.178 23.282 23.282"/>
                <path id="Mid_Circle" d="m85 50a35 35 0 0 1-35 35 35 35 0 0 1-35-35 35 35 0 0 1 35-35 35 35 0 0 1 35 35z" stroke-linecap="round" stroke-linejoin="round" style="paint-order:markers stroke fill"/>
            </g>
        </g>
        <path id="Outline" d="m2.6291 2.6291h94.742v94.742h-94.742zm13.847 7.6e-6h67.048c7.6712 0 13.847 6.1757 13.847 13.847v67.048c0 7.6712-6.1757 13.847-13.847 13.847h-67.048c-7.6712 0-13.847-6.1757-13.847-13.847v-67.048c0-7.6712 6.1757-13.847 13.847-13.847zm81.024 47.371a47.5 47.5 0 0 1-47.5 47.5 47.5 47.5 0 0 1-47.5-47.5 47.5 47.5 0 0 1 47.5-47.5 47.5 47.5 0 0 1 47.5 47.5z" stroke-linecap="round" stroke-width="5.2582" style="paint-order:markers stroke fill"/>
    </g>
</svg>
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
    table_manager = TableManager()

    data = copy(table_manager.data)

    for ip in data:
        if isinstance(data[ip]["hashrate"], str):
            data[ip]["hashrate"] = float(data[ip]["hashrate"].replace("TH/s", "").strip())

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
            if board["chips"] < (board["expected_chips"] * CHIP_PCT_IDEAL):
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
        # repeatRows=1,
        # rowHeights=[4 * inch],
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
                est_total_wattage = list_data_item["wattage"]
                est_total_hashrate = list_data_item["hashrate"]
                power_limit = list_data_item["wattage_limit"]
        est_wattage[len(data[item])] += est_total_wattage
        est_missing_wattage[len(data[item])] += power_limit - est_total_wattage
        est_hashrate[len(data[item])] += round(est_total_hashrate)
    for idx in range(4):
        efficiency[idx] = f"{round(est_wattage[idx]/(est_hashrate[idx]+1))} W/TH"
        if not idx == 0 and not idx == 3:
            est_missing_hashrate[idx] = round(
                est_missing_wattage[idx]
                / ((round(est_wattage[idx] / (est_hashrate[idx] + 1) + 1)))
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
            if board["chips"] < (board["expected_chips"] * CHIP_PCT_IDEAL):
                miner_bad_boards += 1

        table_data.append(
            [
                miner["ip"],
                miner["model"],
                miner["total_chips"],
                miner["ideal_chips"],
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
    t = Table(table_data, repeatRows=1, colWidths='*')
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
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
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
        png_data = cairosvg.svg2png(bytestring=create_board_svg(data[ip]))
        png_buffer = BytesIO(png_data)
        img = Image(png_buffer)
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
                "height": str(SVG_HEIGHT-10),
                "fill": board_color,
            },
        )

        background_group.append(board)

    root.attrib["xmlns"] = "http://www.w3.org/2000/svg"

    return ElementTree.tostring(root).decode()
