import wx
from pubsub import pub

from tspvisual.gui.helpers import borders


class TSPInfo(wx.Panel):
    """Displays specification of the TSP instance and its optimal tour if it's
    available.
    """

    def __init__(self, parent):
        super(TSPInfo, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Builds GUI.
        """

        sizer = wx.BoxSizer(wx.VERTICAL)

        # TSP info box
        tsp_box = wx.StaticBox(self, label='TSP instance')
        tsp_box_sizer = wx.StaticBoxSizer(tsp_box, wx.VERTICAL)
        sizer.Add(tsp_box_sizer, 1, wx.EXPAND | wx.ALL, 10)
        # Tour info box
        tour_box = wx.StaticBox(self, label='Optimal tour')
        tour_box_sizer = wx.StaticBoxSizer(tour_box, wx.VERTICAL)
        sizer.Add(tour_box_sizer, 1, wx.EXPAND | borders('lrb'), 10)

        # TSP specification table
        self.tsp_table = wx.ListCtrl(tsp_box, style=wx.LC_REPORT)
        self.tsp_table.SetMinSize((1, 1))  # To avoid GTK errors
        self.tsp_table.InsertColumn(0, 'Key')
        self.tsp_table.InsertColumn(1, 'Value')
        tsp_box_sizer.Add(self.tsp_table, 1, wx.EXPAND | borders('lr'), 10)

        # Tour specification table
        self.tour_table = wx.ListCtrl(tour_box, style=wx.LC_REPORT)
        self.tour_table.SetMinSize((1, 1))  # To avoid GTK errors
        self.tour_table.InsertColumn(0, 'Key')
        self.tour_table.InsertColumn(1, 'Key')
        tour_box_sizer.Add(self.tour_table, 1, wx.EXPAND | borders('lr'), 10)

        self.SetSizer(sizer)

        pub.subscribe(self._on_tsp_change, 'TSP_CHANGE')

    def _on_tsp_change(self, tsp):
        """Populates table with given specification.
        """

        self.reset()

        if not tsp:
            return

        for key, value in tsp.specification.items():
            self.tsp_table.Append((key, value))

        if tsp.opt_tour:
            for key, value in tsp.opt_tour.specification.items():
                self.tour_table.Append((key, value))

            self.tour_table.Append(('TOUR', str(tsp.opt_tour.tour)))
            self.tour_table.Append(('DISTANCE', str(tsp.opt_path.distance)))

        # Not pretty but forces first columns of both tables to be of equal
        # width
        self.tsp_table.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.tour_table.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        width1 = self.tsp_table.GetColumnWidth(0)
        width2 = self.tour_table.GetColumnWidth(0)
        max_width = max([width1, width2])
        self.tsp_table.SetColumnWidth(0, max_width)
        self.tour_table.SetColumnWidth(0, max_width)
        self.tsp_table.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.tour_table.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def reset(self):
        """Resets this panel to empty state.
        """

        self.specification = {}
        self.tsp_table.DeleteAllItems()
        self.tour_table.DeleteAllItems()
