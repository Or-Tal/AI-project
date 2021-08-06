import argparse
from multiprocessing import freeze_support

import wx

from noa_kirel.gui.tspvisual import TSPVisual


def parse_args():
    parser = argparse.ArgumentParser(
        prog='noa_kirel',
        description='Program visualising process of solving of the Travelling \
            Salesman Problem.'
    )
    parser.add_argument('file', type=str, nargs='?', default=None,
                        help='TSP instance to open')
    return parser.parse_args()


def main():
    args = parse_args()
    app = wx.App()
    TSPVisual(args.file)
    app.MainLoop()


if __name__ == '__main__':
    freeze_support()
    main()
