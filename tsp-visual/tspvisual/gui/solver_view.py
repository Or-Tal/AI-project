from enum import Enum
from operator import itemgetter

import wx
import wx.propgrid as wxpg
from pubsub import pub

from tspvisual.gui.helpers import borders
from tspvisual.gui.solver_runner import SolverRunner
from tspvisual.solver import Solver
from tspvisual.solvers import *  # noqa: F403, F401
# Weird solution for importing solvers when frozen with PyInstaller
from tspvisual.solvers import bf, bnb, sa, ts, ga  # noqa: F401


class SolverView(wx.Panel):
    """Main view of the app, solver controls and tsp view.
    """

    def __init__(self, parent):
        super(SolverView, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Builds GUI.
        """

        # Panel sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Solver controls and TSP view
        self.controls = SolverControls(self)
        tsp_view_box = wx.StaticBox(self, label='Visualisation')
        tsp_view_box_sizer = wx.StaticBoxSizer(tsp_view_box)
        self.tsp_view = TSPView(tsp_view_box)
        tsp_view_box_sizer.Add(self.tsp_view, 1, wx.EXPAND)
        sizer.Add(self.controls, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(tsp_view_box_sizer, 1, wx.EXPAND | borders('trb'), 10)

        self.SetSizer(sizer)


class SolverControls(wx.Panel):
    """Solver selection and controls.
    """

    DEFAULT_RESULT = 'N/A'
    SOLVE_BTN_INACTIVE = 'Solve'
    SOLVE_BTN_ACTIVE = 'Stop'

    def __init__(self, parent):
        super(SolverControls, self).__init__(parent)

        # List of all available solvers
        self.solvers = {s.name: s for s in Solver.__subclasses__()}
        self.solver_names = sorted(list(self.solvers.keys()))

        # Currently selected solver and tsp
        self.solver = None
        self.tsp = None

        # Current `SolverRunner`
        self.runner = None
        # Whether ther is currently running solver
        self.running = False

        self._init_ui()

    def _init_ui(self):
        """Builds GUI.
        """

        # Static boxes
        sizer = wx.BoxSizer(wx.VERTICAL)
        # Solver box
        solver_box = wx.StaticBox(self, label='Solving')
        solver_box_sizer = wx.StaticBoxSizer(solver_box)
        sizer.Add(solver_box_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)
        # Result box
        res_box = wx.StaticBox(self, label='Result')
        res_box_sizer = wx.StaticBoxSizer(res_box)
        sizer.Add(res_box_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)
        # Properties box
        props_box = wx.StaticBox(self, label='Solver Properties')
        props_box_sizer = wx.StaticBoxSizer(props_box)
        sizer.Add(props_box_sizer, 1, wx.EXPAND)

        # Solver box contents
        solver_sizer = wx.GridBagSizer(10, 10)

        # Solver selection
        solver_select_label = wx.StaticText(solver_box,
                                            label='Solver selection')
        solver_sizer.Add(solver_select_label, (0, 0), (1, 2),
                         wx.EXPAND | borders('trl'), 10)
        self.solver_select = wx.Choice(solver_box, choices=self.solver_names)
        self.solver_select.SetSelection(0)
        solver_sizer.Add(self.solver_select, (1, 0), (1, 2),
                         wx.EXPAND | borders('rl'), 10)
        # Delay setting
        delay_label = wx.StaticText(solver_box, label='Delay [ms]')
        solver_sizer.Add(delay_label, (2, 0), (1, 2),
                         wx.EXPAND | borders('rl'), 10)
        self.delay = wx.Slider(solver_box, value=0, minValue=0, maxValue=1000,
                               style=wx.SL_LABELS)
        solver_sizer.Add(self.delay, (3, 0), (1, 2),
                         wx.EXPAND | borders('rl'), 10)
        # Show best path checkbox
        self.show_best = wx.CheckBox(solver_box,
                                     label='Show the best found path')
        self.show_best.SetValue(True)
        solver_sizer.Add(self.show_best, (4, 0), (1, 2),
                         wx.EXPAND | borders('rl'), 10)
        # Show current path checkbox
        self.show_current = wx.CheckBox(solver_box,
                                        label='Show current working path')
        self.show_current.SetValue(True)
        solver_sizer.Add(self.show_current, (5, 0), (1, 2),
                         wx.EXPAND | borders('rl'), 10)
        # Show optimal path checkbox
        self.show_opt = wx.CheckBox(solver_box, label='Show optimal path')
        self.show_opt.SetValue(True)
        solver_sizer.Add(self.show_opt, (6, 0), (1, 2),
                         wx.EXPAND | borders('rl'), 10)
        # Solve button
        self.solve_button = wx.Button(solver_box,
                                      label=self.SOLVE_BTN_INACTIVE)
        solver_sizer.Add(self.solve_button, (7, 0), (1, 1),
                         wx.EXPAND | borders('l'), 10)
        # Reset button
        self.reset_button = wx.Button(solver_box, label='Reset')
        solver_sizer.Add(self.reset_button, (7, 1), (1, 1),
                         wx.EXPAND | borders('r'), 10)
        # Progress bar
        self.progress = wx.Gauge(solver_box, range=100)
        # self.progress.SetMaxSize((-1, 10))
        solver_sizer.Add(self.progress, (8, 0), (1, 2),
                         wx.EXPAND | borders('rbl'), 10)
        solver_box_sizer.Add(solver_sizer)

        # Result box contents
        # No idea why this panel and sizer are necessary but this was the only
        # way to avoid GTK warnings
        result_panel = wx.Panel(self)
        result_sizer = wx.GridBagSizer(10, 10)
        result_font = wx.Font(wx.FontInfo(16))
        # Distance
        result_label = wx.StaticText(result_panel, label='Distance:')
        result_sizer.Add(result_label, (0, 0), (0, 1),
                         wx.ALIGN_CENTER_VERTICAL | borders('tl'), 10)
        self.result = wx.StaticText(result_panel, label=self.DEFAULT_RESULT)
        self.result.SetFont(result_font)
        result_sizer.Add(self.result, (0, 1), (0, 1),
                         wx.ALIGN_CENTER_VERTICAL | borders('tr'), 10)
        # Error
        error_label = wx.StaticText(result_panel, label='Error:')
        result_sizer.Add(error_label, (1, 0), (0, 1),
                         wx.ALIGN_CENTER_VERTICAL | borders('bl'), 10)
        self.error = wx.StaticText(result_panel, label=self.DEFAULT_RESULT)
        self.error.SetFont(result_font)
        result_sizer.Add(self.error, (1, 1), (0, 1),
                         wx.ALIGN_CENTER_VERTICAL | borders('br'), 10)
        result_panel.SetSizer(result_sizer)
        res_box_sizer.Add(result_panel, 1)

        # Properties box contents
        self.solver_properties = SolverProperties(self)
        props_box_sizer.Add(self.solver_properties, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)

        # Event bindings
        self.solver_select.Bind(wx.EVT_CHOICE, self._on_select)
        self.solve_button.Bind(wx.EVT_BUTTON, self._on_solve)
        self.reset_button.Bind(wx.EVT_BUTTON, self._on_reset)
        self.delay.Bind(wx.EVT_SCROLL_CHANGED, self._on_delay_set)
        self.show_best.Bind(wx.EVT_CHECKBOX, self._on_view_change)
        self.show_current.Bind(wx.EVT_CHECKBOX, self._on_view_change)
        self.show_opt.Bind(wx.EVT_CHECKBOX, self._on_view_change)
        pub.subscribe(self._on_solver_change, 'SOLVER_CHANGE')
        pub.subscribe(self._on_tsp_change, 'TSP_CHANGE')
        pub.subscribe(self._on_solver_state_change, 'SOLVER_STATE_CHANGE')
        pub.subscribe(self._on_solver_state_reset, 'SOLVER_STATE_RESET')

        # Run solver selection event handler to create default solver
        self._on_select(None)

    def _on_select(self, event):
        """Handles selecting solver from solvers combobox.
        """

        solver_name = self.solver_names[self.solver_select.GetSelection()]
        solver_class = self.solvers[solver_name]
        solver = solver_class()

        pub.sendMessage('SOLVER_CHANGE', solver=solver)

    def _on_solve(self, event):
        """Handles clicking 'solve' button - runs `SolverRunner` with currently
        set solver and tsp.
        """

        if not self.running:
            # Make sure there is loaded instance and selected solver
            if not self.tsp:
                wx.MessageBox('No TSP instance loaded.', 'Error',
                              wx.ICON_ERROR | wx.OK)
                return
            if not self.solver:
                wx.MessageBox('No solver selected.', 'Error',
                              wx.ICON_ERROR | wx.OK)
                return

            # Create and start the solver runner
            self.runner = SolverRunner(self.solver, self.tsp)
            self.runner.delay = self.delay.GetValue() / 1000
            self.runner.daemon = True
            self.runner.start()
            # Set state to running
            self._set_running(True)
        else:
            # Stop the runner
            self.runner.stop()
            # Set state to not running
            self._set_running(False)

    def _on_reset(self, event):
        """Handles clicking 'reset' button - sends reset message.
        """

        pub.sendMessage('SOLVER_STATE_CHANGE', state=None)
        pub.sendMessage('SOLVER_STATE_RESET')

    def _on_delay_set(self, event):
        """Handles setting 'delay' slider - if there is an active runner its
        delay to the value from slider.
        """

        if not self.running:
            return

        self.runner.delay = self.delay.GetValue() / 1000

    def _on_view_change(self, event):
        """Handles checking or unchecking one of view option checkboxes.
        """

        options = {}
        options['show_best'] = self.show_best.GetValue()
        options['show_current'] = self.show_current.GetValue()
        options['show_opt'] = self.show_opt.GetValue()

        pub.sendMessage('VIEW_OPTION_CHANGE', **options)

    def _on_solver_change(self, solver):
        """Handles solver change event.
        """

        self.solver = solver

    def _on_tsp_change(self, tsp):
        """Handles TSP change event.
        """

        self.tsp = tsp

    def _on_solver_state_change(self, state):
        """Handles solver state change - displays length of the currently best
        path in the result area.

        :param SolverState state: New solver state.
        """

        if not state:
            return

        if state.progress:
            self.progress.SetValue(state.progress * 100)

        if state.best:
            result = state.best.distance
            self.result.SetLabel(str(result))

            if self.tsp.opt_path:
                opt = self.tsp.opt_path.distance
                error = round((result - opt) / opt * 100, 2)
                self.error.SetLabel(str(error) + '%')

        # If this is final result
        if state.final:
            # Set state to not running
            self._set_running(False)

    def _on_solver_state_reset(self):
        """Handles solver state reset message - clears result, error and
        progress controls.
        """

        self.result.SetLabel(self.DEFAULT_RESULT)
        self.error.SetLabel(self.DEFAULT_RESULT)
        self.progress.SetValue(0)

    def _set_running(self, state):
        """Adjusts the UI to the current state of the solver runner.
        """

        if state:
            # Set running flag, change button text, disbale reset button
            self.running = True
            self.solve_button.SetLabel(self.SOLVE_BTN_ACTIVE)
            self.reset_button.Disable()
        else:
            # Wait for the runner to actually stop
            self.runner.join()
            # Unset running flag, change button text, enable reset button
            self.running = False
            self.solve_button.SetLabel(self.SOLVE_BTN_INACTIVE)
            self.reset_button.Enable()


class TSPView(wx.Panel):
    """Visualisation of the TSP instance.
    """

    PADDING = 20
    CITY_RADIUS = 3
    CITY_COLOR = 'black'
    CURRENT_COLOR = 'black'
    BEST_COLOR = 'red'
    OPT_COLOR = 'light gray'
    PATH_WIDTH = 2

    def __init__(self, parent):
        super(TSPView, self).__init__(parent)

        # Cities list
        self._tsp = None
        self._points = []
        # Solver state
        self._state = None
        # Whether to show the best path
        self.show_best = True
        self.show_current = True
        self.show_opt = True

        # GUI
        self._init_ui()

    def _init_ui(self):
        """Builds GUI.
        """

        # Background style
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Event bindings
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_resize)
        pub.subscribe(self._on_tsp_change, 'TSP_CHANGE')
        pub.subscribe(self._on_solver_state_change, 'SOLVER_STATE_CHANGE')
        pub.subscribe(self._on_view_option_change, 'VIEW_OPTION_CHANGE')

    def _on_paint(self, event):
        """Paints currently set cities and paths.
        """

        # Create and clear drawing context
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()

        # Skip if there are no points
        if not self._points:
            return

        # Draw the optimal path
        if self.show_opt and self._tsp.opt_path:
            self._draw_path(dc, self._tsp.opt_path, self.OPT_COLOR)

        # Draw state if it's defined
        if self._state:
            # Draw current path if there's no best even if it's disabled
            draw_current = (
                self._state.current and
                (self.show_current or not self._state.best)
            )
            draw_best = (
                (self._state.best or self._state.final) and
                self.show_best
            )
            # Draw paths
            if draw_best:
                self._draw_path(dc, self._state.best, self.BEST_COLOR)
            if draw_current:
                self._draw_path(dc, self._state.current, self.CURRENT_COLOR)

        # Draw cities
        dc.SetPen(wx.Pen(self.CITY_COLOR))
        dc.SetBrush(wx.Brush(self.CITY_COLOR))
        for c in self._points:
            dc.DrawCircle(c[0], c[1], self.CITY_RADIUS)

    def _draw_path(self, dc, path, color):
        """Utility method to draw a path on the given device context.
        """

        dc.SetPen(wx.Pen(color, width=self.PATH_WIDTH))
        for i in range(len(path) - 1):
            if path[i] == -1 or path[i + 1] == -1:
                continue
            dc.DrawLine(*self._points[path[i]], *self._points[path[i + 1]])

    def _on_resize(self, event):
        """Handles resize event.
        """

        self.calculate_points()

    def _on_tsp_change(self, tsp):
        """Handles TSP change event.
        """

        self.reset()

        if not tsp:
            return

        if not tsp.display:
            wx.MessageBox('This instance does not have display data',
                          'Warning', wx.OK | wx.ICON_WARNING)
            return

        self.tsp = tsp

    def _on_solver_state_change(self, state):
        """Handles solver state change event.
        """

        self.set_state(state)

    def _on_view_option_change(self, show_best=None, show_current=None,
                               show_opt=None):
        """Handles view option change - enables or disables displaying of the
        best, current or optimal path.
        """

        if show_best is not None:
            self.show_best = show_best

        if show_current is not None:
            self.show_current = show_current

        if show_best is not None:
            self.show_opt = show_opt

        self.Refresh()

    @property
    def tsp(self):
        """Returns current tsp instance.
        """

        return self._tsp

    @tsp.setter
    def tsp(self, tsp):
        """Sets tsp instance, triggers point calculation and repaint.
        """

        self._tsp = tsp
        self.calculate_points()
        self.Refresh()

    def set_state(self, state):
        """Sets `SolverState` object and triggers repaint.
        """

        self._state = state
        self.Refresh()

    def calculate_points(self):
        """Calculates positions of points representing cities.
        """

        # Skip if no cities are set
        if not self._tsp or not self._tsp.display:
            return

        cities = self._tsp.display

        # Clear current points
        self._points.clear()

        # Find max x and y value
        max_x = max(cities, key=itemgetter(0))[0]
        max_y = max(cities, key=itemgetter(1))[1]
        # Drawing area size
        w, h = self.GetClientSize()
        # Usable area
        uw, uh = (w - self.PADDING * 2), (h - self.PADDING * 2)
        # Size of the drawing if it was scaled to fit the longer area side
        vw, vh = (uw / max_x), (uh / max_y)
        # Shorter side
        side = min(vw, vh)
        # Effective padding
        exp, eyp = ((w - side * max_x) / 2), ((h - side * max_y) / 2)

        # Calculate for all points
        for c in cities:
            # Note the inverted y axis
            x, y = (c[0] * side + exp),  (h - (c[1] * side + eyp))
            self._points.append((x, y))

    def reset(self):
        """Resets this control to its initial empty state.
        """

        self._cities = []
        self._points = []
        self._state = None
        self.Refresh()


class SolverProperties(wx.propgrid.PropertyGrid):
    """Panel for configuring solver-specific options.
    """

    def __init__(self, parent):
        super(SolverProperties, self).__init__(parent,
                                               style=wxpg.PG_HIDE_MARGIN |
                                               wxpg.PG_BOLD_MODIFIED |
                                               wxpg.PG_TOOLTIPS)

        # Currently selected solver
        self.solver = None

        self._init_ui()

    def _init_ui(self):
        """Builds GUI.
        """

        # Event bindings
        self.Bind(wxpg.EVT_PG_CHANGED, self._on_changed)
        pub.subscribe(self._on_solver_change, 'SOLVER_CHANGE')

    def _on_changed(self, event):
        """Applies current properties values to the currently set solver.
        """

        for prop in self.Properties:
            prop_idx = prop.GetAttribute('property_idx')
            solver_prop = self.solver.properties[prop_idx]
            value = solver_prop.type(prop.GetValue())
            setattr(self.solver, solver_prop.field, value)

    def _on_solver_change(self, solver):
        """Handles solver change event.
        """

        self.set_solver(solver)

    def set_solver(self, solver):
        """Sets current solver and builds UI basing on its properties.

        :param Solver solver: Solver to show properties of.
        """

        # Set the solver
        self.solver = solver

        # Reset the properties
        self.reset()

        # Skip if there is no solver or solver has no properties
        if not self.solver or not self.solver.properties:
            return

        # For each property
        for i, p in enumerate(self.solver.properties):
            # Create property object with appropriate type
            if p.type is int:
                prop = wxpg.IntProperty()
            elif p.type is float:
                prop = wxpg.FloatProperty()
            elif issubclass(p.type, Enum):
                prop = wxpg.EnumProperty()
                labels = list(map(lambda c: c.name, p.type))
                values = list(map(lambda c: c.value, p.type))
                prop_choices = wxpg.PGChoices(labels=labels, values=values)
                prop.SetChoices(prop_choices)

            # Set label and value
            prop.SetLabel(p.name)
            prop.SetValue(p.default)
            prop.SetDefaultValue(p.default)
            prop.SetAttribute('property_idx', i)

            # And append the property object
            self.Append(prop)

        # Fit columns and layout the parent
        self.FitColumns()
        self.GetParent().Layout()

    def reset(self):
        """Resets control to initial state.
        """

        self.Clear()
