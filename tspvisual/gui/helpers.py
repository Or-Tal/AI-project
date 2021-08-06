import wx


def borders(borders):
    """Helper for setting wx borders flags.

    Parameter string may consist of four letters, each meaning border on
    different side of the control: t - top, r - right, b - bottom, l - left.

    :param string borders: Borders string.
    :return: wx border flags.
    :rtype: int
    """

    flags = 0

    if 't' in borders:
        flags |= wx.TOP
    if 'r' in borders:
        flags |= wx.RIGHT
    if 'b' in borders:
        flags |= wx.BOTTOM
    if 'l' in borders:
        flags |= wx.LEFT

    return flags
