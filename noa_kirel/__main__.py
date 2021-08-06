import argparse
from multiprocessing import freeze_support

import wx

from gui.tspvisual import TSPVisual


def parse_args():
    parser = argparse.ArgumentParser(
        prog='noa_kirel',
        description='Program visualising process of solving of the Travelling \
            Salesman Problem.'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    app = wx.App()
    TSPVisual()
    app.MainLoop()


if __name__ == '__main__':
    freeze_support()
    main()
