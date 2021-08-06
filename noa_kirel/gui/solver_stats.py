import wx
from pubsub import pub
from wx.lib.plot import PlotCanvas, PlotGraphics, PolyLine


class SolverStats(wx.Panel):
    """Displays solver statistics.
    """

    def __init__(self, parent):
        super(SolverStats, self).__init__(parent)

        # Solver states to plot
        self.results = []

        self._init_ui()

    def _init_ui(self):
        """Builds GUI.
        """

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.best_canvas = PlotCanvas(self)
        self.best_canvas.useScientificNotation = True
        self.current_canvas = PlotCanvas(self)
        self.current_canvas.useScientificNotation = True
        sizer.Add(self.best_canvas, 1, wx.EXPAND)
        sizer.Add(self.current_canvas, 1, wx.EXPAND)
        self._plot()

        self.SetSizer(sizer)

        pub.subscribe(self._on_solver_state_end, 'SOLVER_STATE_END')
        pub.subscribe(self._on_solver_state_reset, 'SOLVER_STATE_RESET')

    def _plot(self):
        """Plots best and current paths data.
        """

        self.best_canvas.Clear()
        self.current_canvas.Clear()

        if len(self.results) > 0:
            x_max = self.results[-1].time
            self.best_canvas.xSpec = (0, x_max)
            self.current_canvas.xSpec = (0, x_max)

        best_points = [(r.time, r.best.distance) for r in self.results
                       if r.best is not None and
                       isinstance(r.best.distance, int)]
        best_line = PolyLine(best_points)
        best_plot = PlotGraphics([best_line],
                                 title='Best path distance over time',
                                 xLabel='Time [ns]', yLabel='Distance')

        current_points = [(r.time, r.current.distance) for r in self.results
                          if r.current is not None and
                          isinstance(r.current.distance, int)]
        current_line = PolyLine(current_points)
        current_plot = PlotGraphics([current_line],
                                    title='Current path distance over time',
                                    xLabel='Time [ns]', yLabel='Distance')

        self.best_canvas.Draw(best_plot)
        self.current_canvas.Draw(current_plot)

    def reset(self):
        """Resets this control to its initial state.
        """

        self.results = []
        self._plot()

    def _on_solver_state_end(self, results):
        """Handles end of solving message.
        """

        self.results = results
        self._plot()

    def _on_solver_state_reset(self):
        """Handles SOLVER_STATE_RESET message.
        """

        self.reset()
