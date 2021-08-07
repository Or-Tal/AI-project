import wx
import wx.adv
import wx.lib.inspection

import numpy as np
from pubsub import pub

from noa_kirel.gui.export import export_results, export_scr, export_tour
from noa_kirel.gui.helpers import borders
from noa_kirel.gui.solver_stats import SolverStats
from noa_kirel.gui.solver_view import SolverView
#from noa_kirel.gui.tsp_info import TSPInfo
from noa_kirel.tsp import TSP
from noa_kirel.partition import partition_1
from noa_kirel.city_selection import city_selection_1
from noa_kirel.constants import *


class TSPVisual(wx.Frame):
    """
    Main app window wrapping around everything else.
    """

    def __init__(self, file=None):
        super(TSPVisual, self).__init__(None, title='TSP Visual')

        # Solver results (for exporting)
        self._results = None
        # Current TSP instance

        # GUI
        self._init_ui()
        self.Show()
        self.SetSize(1200, 900)
        self.Centre()

        # Try to open TSP file if it's given
        if file:
            self.load_file(file)

    def _init_ui(self):
        """Builds GUI.
        """

        # Main layout
        self.panel = panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Tabs
        notebook = wx.Notebook(panel)
        self.solver_view = SolverView(notebook)
        self.solver_stats = SolverStats(notebook)
        #self.tsp_info = TSPInfo(notebook)
        notebook.AddPage(self.solver_view, 'Solver')
        notebook.AddPage(self.solver_stats, 'Stats')
        #notebook.AddPage(self.tsp_info, 'Info')
        sizer.Add(notebook, 1, wx.EXPAND | borders('lrb'), 10)

        panel.SetSizer(sizer)
        panel.Layout()
        self.Layout()

        # Event bindings
        pub.subscribe(self._on_tsp_change, 'TSP_CHANGE')
        pub.subscribe(self._on_solver_state_end, 'SOLVER_STATE_END')
        pub.subscribe(self._on_solver_state_reset, 'SOLVER_STATE_RESET')

    def load_file(self, file):
        """Tries to load specified TSP instance and sends message on success.
        Shows error dialog on fail.
        """

        try:
            tsp = TSP(file)
            pub.sendMessage('TSP_CHANGE', tsp=tsp)
            pub.sendMessage('SOLVER_STATE_RESET')
        except Exception as e:
            wx.MessageBox(str(e), 'Error', wx.ICON_ERROR | wx.OK)

    def _on_open(self, event):
        """Handles file opening.
        """

        # Present file picker and try to load selected instance
        with (wx.FileDialog(self, 'Open tsp instance.',
              wildcard='TSPLIB (*.tsp)|*.tsp',
              style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)) as file_dialog:

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return

            file = file_dialog.GetPath()
            self.load_file(file)

    def _on_close(self, event):
        """Handles file closing.
        """

        pub.sendMessage('TSP_CHANGE', tsp=None)
        pub.sendMessage('SOLVER_STATE_RESET')

    def _on_data_export(self, event):
        """Handles data export.
        """

        # Show error and return if there is no results
        if not self._results:
            wx.MessageBox('No data to export.', 'Error', wx.ICON_ERROR | wx.OK)
            return

        # Present file picker and try to load selected instance
        with (wx.FileDialog(self, 'Save solver data.',
              wildcard='CSV files (*.csv)|*.csv',
              style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)) as file_dialog:

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return

            file = file_dialog.GetPath()
            try:
                export_results(file, self._results)
                wx.MessageBox('Data exported successfully.', 'Success',
                              wx.ICON_INFORMATION | wx.OK)
            except Exception as e:
                wx.MessageBox(str(e), 'Error', wx.ICON_ERROR | wx.OK)

    def _on_graph_export(self, event):
        """Handles graphs export.
        """

        # Show error and return if there is no results
        if not self._results:
            wx.MessageBox('No graphs to export.', 'Error',
                          wx.ICON_ERROR | wx.OK)
            return

        if event.GetId() == self.export_b_graph_mi.GetId():
            graph = self.solver_stats.best_canvas
        elif event.GetId() == self.export_c_graph_mi.GetId():
            graph = self.solver_stats.current_canvas

        if graph.SaveFile():
            wx.MessageBox('Graph exported successfully.', 'Success',
                          wx.ICON_INFORMATION | wx.OK)
        else:
            wx.MessageBox('Error while exporting graph.', 'Error',
                          wx.ICON_ERROR | wx.OK)

    def _on_vis_export(self, event):
        """Handles exporting of the TSP visualisation.
        """

        # Show error and return if there is no visualisation
        if not self._tsp:
            wx.MessageBox('No visualisation to export.', 'Error',
                          wx.ICON_ERROR | wx.OK)
            return

        # I don't like this but it works
        panel_rect = self.panel.GetScreenRect()
        rect = self.solver_view.tsp_view.GetScreenRect()
        rect.x -= panel_rect.x
        rect.y -= panel_rect.y

        # Wildcards for the file picker
        image_wildcards = 'PNG files (*.png)|*.png|JPG files (*.jpg)|*.jpg|' \
                          'BMP files (*.bmp)|*.bmp'
        # Present file picker and try to load selected instance
        with (wx.FileDialog(self, 'Save solver data.',
              wildcard=image_wildcards,
              style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)) as file_dialog:

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return

            file = file_dialog.GetPath()

        try:
            export_scr(file, rect, self)
            wx.MessageBox('Data exported successfully.', 'Success',
                          wx.ICON_INFORMATION | wx.OK)
        except Exception as e:
            wx.MessageBox(str(e), 'Error', wx.ICON_ERROR | wx.OK)

    def _on_tour_export(self, event):
        """Handles tour export.
        """

        # Show error and return if there is no results
        if not self._results:
            wx.MessageBox('No tour to export.', 'Error', wx.ICON_ERROR | wx.OK)
            return

        # Present file picker and try to load selected instance
        with (wx.FileDialog(self, 'Save tour file.',
              wildcard='Tour files (*.tour)|*.tour',
              style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)) as file_dialog:

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return

            file = file_dialog.GetPath()
            try:
                export_tour(file, self._results[-1].best, self._tsp)
                wx.MessageBox('Tour exported successfully.', 'Success',
                              wx.ICON_INFORMATION | wx.OK)
            except Exception as e:
                wx.MessageBox(str(e), 'Error', wx.ICON_ERROR | wx.OK)

    def _on_about(self, event):
        """Shows about program box when.
        """

        desccription = 'TSP Visual is a program visualising TSP instances ' \
                       'and process of solving them for educational purposes.'

        license = '''MIT License

Copyright (c) 2019 Bazyli Cyran <bazyli.cyran@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

        about = wx.adv.AboutDialogInfo()
        about.SetName('TSP Visual')
        about.SetVersion('0.2.0')
        about.SetDescription(desccription)
        about.SetCopyright('(C) 2019 Bazyli Cyran')
        about.SetWebSite('https://bazylicyran.pl/')
        about.SetLicense(license)
        about.AddDeveloper('Bazyli Cyran')
        about.AddDocWriter('Bazyli Cyran')

        wx.adv.AboutBox(about)

    def _on_tsp_change(self, tsp):
        """Handles TSP change event.
        """

        if not tsp:
            self._tsp = None
            self.title.SetLabel(self.DEFAULT_TITLE)
        else:
            self._tsp = tsp
            self.title.SetLabel(f'Instance: {tsp.name}')

    def _on_solver_state_end(self, results):
        """Handles end of solving and stores reference to the results for
        future exporting.
        """

        self._results = results

    def _on_solver_state_reset(self):
        """Handles SOLVER_STATE_RESET message.
        """

        self._results = None
