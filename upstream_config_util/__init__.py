import asyncio
import sys
import logging
import PySimpleGUI as sg

from .ui import ui

# # Fix bug with some whatsminers and asyncio because of a socket not being shut down:
# if (
#     sys.version_info[0] == 3
#     and sys.version_info[1] >= 8
#     and sys.platform.startswith("win")
# ):
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#
#
# def handle_exception(loop, context):
#     # context["message"] will always be there; but context["exception"] may not
#     msg = context.get("exception", context["message"])
#     logging.error(f"Caught exception: {msg}")
#     try:
#         sg.popup_error_with_traceback("An error occurred.  Please give the maintainer this information.", msg)
#     except SystemExit:
#         loop.stop()
#         loop.close()
#         sys.exit()


def main():
    from logger import init_logger

    init_logger()

    loop = asyncio.get_event_loop()

    # loop.set_exception_handler(handle_exception)

    loop.run_until_complete(ui())


if __name__ == "__main__":
    main()
