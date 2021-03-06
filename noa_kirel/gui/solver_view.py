from operator import itemgetter
from noa_kirel.constants import *

import wx
import wx.lib.agw.floatspin as Fs
import wx.propgrid as wxpg
from pubsub import pub

from noa_kirel.gui.helpers import borders
from noa_kirel.gui.solver_runner import SolverRunner
from noa_kirel.solver import Solver
from noa_kirel.solvers import greedy_solver, brute_force_solver, \
    genetic_solver
from noa_kirel.constants import *
from noa_kirel.partition import partition_1
from noa_kirel.city_selection import city_selection_1
import os

#from solvers import *  # noqa: F403, F401
# Weird solution for importing solvers when frozen with PyInstaller


class SolverView(wx.Panel):
    """Main view of the app, solver controls and tsp view.
    """

    def __init__(self, parent):
        super(SolverView, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """
        Builds GUI.
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

    def get_solver(self, solver_name, dset: dict, params: dict, ver: int=1):
        if solver_name == GEN:
            ret = self.solvers[solver_name](dset[CITIES],
                                             params[POP_SIZE],
                                             params[TOUR_LEN],
                                             partition_1,
                                             city_selection_1,
                                             np.inf,
                                             params[STEPS],
                                             params[MUT_RATE],
                                             params[NUM_ELITE],
                                             dset[COSTS], dset[REV], ver=ver)
        else:
            ret = self.solvers[solver_name](dset[CITIES], dset[COSTS], dset[REV], params[TOUR_LEN], ver=ver)
        return ret

    def __init__(self, parent):
        super(SolverControls, self).__init__(parent)

        # List of all available solvers
        # self.solvers = {s.name: s for s in Solver.__subclasses__()}
        self.solvers = {GREEDY: greedy_solver.GreedySolver, GEN: genetic_solver.GeneticSolver,
                        BF_SOL: brute_force_solver.BruteForceSolver}
        self.cur_solver = BF_SOL
        self.solver_names = sorted(list(self.solvers.keys()))

        # List of all number of cities
        self.cities = {}
        self.num_of_cities = NUM_OF_CITIES

        # Currently selected solver and tsp
        self.dset = load_dset_vis("./noa_kirel/datasets/3_cities.npy")

        self.params = {BF_SOL: {TOUR_LEN: 3},
                       GREEDY: {TOUR_LEN: 3},
                       GEN: {POP_SIZE: 5, TOUR_LEN: 3, STEPS: 20, MUT_RATE: 0.01, NUM_ELITE: 1}}
        self.solver = self.get_solver(BF_SOL, self.dset, self.params[BF_SOL])
        self.tsp = None

        # Current `SolverRunner`
        self.runner = None
        # Whether ther is currently running solver
        self.running = False
        self.best_sol = None
        self.best_score = np.NINF
        self.cur_sol = None
        self.cur_score = np.NINF

        self._init_ui()

    def get_cur_solver(self):
        return self.get_solver(self.cur_solver, self.dset, self.params[self.cur_solver])

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
        sizer.Add(props_box_sizer, 0, wx.EXPAND)

        # Properties box contents
        props_sizer = wx.GridBagSizer(10, 10)

        # Solver box contents
        solver_sizer = wx.GridBagSizer(10, 10)

        # Solver selection
        solver_select_label = wx.StaticText(solver_box,
                                            label='Solver selection')
        solver_sizer.Add(solver_select_label, (0, 0), (1, 1),
                         wx.EXPAND | borders('trl'), 10)
        self.solver_select = wx.Choice(solver_box, choices=self.solver_names)
        self.solver_select.SetSelection(0)
        solver_sizer.Add(self.solver_select, (1, 0), (1, 1),
                         wx.EXPAND | borders('rl'), 10)

        # Cities selection
        cities_select_label = wx.StaticText(solver_box,
                                            label='Cities selection')
        solver_sizer.Add(cities_select_label, (0, 1), (1, 1),
                         wx.EXPAND | borders('trl'), 10)
        self.cities_select = wx.Choice(solver_box, choices=self.num_of_cities)
        self.cities_select.SetSelection(0)
        solver_sizer.Add(self.cities_select, (1, 1), (1, 1),
                         wx.EXPAND | borders('rl'), 10)

        # Delay setting
        delay_label = wx.StaticText(solver_box, label='Delay [ms]')
        solver_sizer.Add(delay_label, (2, 0), (1, 2),
                         wx.EXPAND | borders('rl'), 10)
        self.delay = wx.Slider(solver_box, value=50, minValue=50, maxValue=600,
                                       style=wx.SL_LABELS)
        solver_sizer.Add(self.delay, (3, 0), (1, 2),
                         wx.EXPAND | borders('rl'), 10)

        # Solve button
        self.solve_button = wx.Button(solver_box,
                                      label=self.SOLVE_BTN_INACTIVE)
        solver_sizer.Add(self.solve_button, (4, 0), (1, 1),
                         wx.EXPAND | borders('l'), 10)
        # Reset button
        self.reset_button = wx.Button(solver_box, label='Reset')
        solver_sizer.Add(self.reset_button, (4, 1), (1, 1),
                         wx.EXPAND | borders('r'), 10)
        # Progress bar
        self.progress = wx.Gauge(solver_box, range=100)
        # self.progress.SetMaxSize((-1, 10))
        solver_sizer.Add(self.progress, (5, 0), (1, 2),
                         wx.EXPAND | borders('rbl'), 10)
        solver_box_sizer.Add(solver_sizer)

        # Result box contents
        # No idea why this panel and sizer are necessary but this was the only
        # way to avoid GTK warnings
        result_panel = wx.Panel(self)
        result_sizer = wx.GridBagSizer(10, 10)
        result_font = wx.Font(wx.FontInfo(10))
        # Score
        result_label = wx.StaticText(result_panel, label='Score:')
        result_sizer.Add(result_label, (0, 0), (0, 0),
                         wx.ALIGN_CENTER_VERTICAL | borders('tl'), 10)
        self.result = wx.StaticText(result_panel, label=self.DEFAULT_RESULT)
        self.result.SetFont(result_font)
        result_sizer.Add(self.result, (0, 1), (0, 0),
                         wx.ALIGN_CENTER_VERTICAL | borders('tr'), 10)

        result_panel.SetSizer(result_sizer)
        res_box_sizer.Add(result_panel, 1)


        # #Error
        # error_label = wx.StaticText(result_panel, label='Error:')
        # result_sizer.Add(error_label, (1, 0), (0, 1),
        #                  wx.ALIGN_CENTER_VERTICAL | borders('bl'), 10)
        # self.error = wx.StaticText(result_panel, label=self.DEFAULT_RESULT)
        # self.error.SetFont(result_font)
        # result_sizer.Add(self.error, (1, 1), (0, 1),
        #                  wx.ALIGN_CENTER_VERTICAL | borders('br'), 10)
        # result_panel.SetSizer(result_sizer)
        # res_box_sizer.Add(result_panel, 1)

        # mutation setting
        mutation_rate = wx.StaticText(props_box, label='Mutation rate')
        props_sizer.Add(mutation_rate, (0, 0), (1, 1),
                         wx.EXPAND | borders('l'), 10)
        self.mutation_rate = Fs.FloatSpin(props_box, value=0, min_val=0,
                        increment=0.01, max_val=1, style=wx.SL_LABELS)
        self.mutation_rate.SetDigits(digits=2)


        props_sizer.Add(self.mutation_rate, (1, 0), (1, 1),
                         wx.EXPAND | borders('l'), 10)

        # population size
        population_size = wx.StaticText(props_box, label='Population size')
        props_sizer.Add(population_size, (0, 1), (1, 1),
                        wx.EXPAND | borders('r'), 10)
        self.population_size = wx.Slider(props_box, value=5, minValue=5,
                                       maxValue=100,
                                       style=wx.SL_LABELS)
        props_sizer.Add(self.population_size, (1, 1), (1, 1),
                        wx.EXPAND | borders('r'), 10)

        # num elite
        num_elite = wx.StaticText(props_box, label='Num elite')
        props_sizer.Add(num_elite, (2, 0), (1, 1),
                        wx.EXPAND | borders('l'), 10)
        self.num_elite = wx.Slider(props_box, value=1, minValue=1,
                                         maxValue=1000,
                                         style=wx.SL_LABELS)
        props_sizer.Add(self.num_elite, (3, 0), (1, 1),
                        wx.EXPAND | borders('l'), 10)

        # num generations
        generations = wx.StaticText(props_box, label='Generations')
        props_sizer.Add(generations, (2, 1), (1, 1),
                        wx.EXPAND | borders('r'), 10)
        self.generations = wx.Slider(props_box, value=1, minValue=1,
                                   maxValue=1000, style=wx.SL_LABELS)
        props_sizer.Add(self.generations, (3, 1), (1, 1),
                        wx.EXPAND | borders('r'), 10)

        # tour len
        tour_len = wx.StaticText(props_box, label='Tour length')
        props_sizer.Add(tour_len, (4, 0), (1, 1),
                        wx.EXPAND | borders('l'), 10)
        self.tour_len = wx.Slider(props_box, value=3, minValue=3,
                                     maxValue=100, style=wx.SL_LABELS)
        props_sizer.Add(self.tour_len, (5, 0), (1, 1),
                        wx.EXPAND | borders('l'), 10)

        props_box_sizer.Add(props_sizer)
        self.SetSizer(sizer)

        # Event bindings
        self.cities_select.Bind(wx.EVT_CHOICE, self._on_select_number_cities)
        self.solver_select.Bind(wx.EVT_CHOICE, self._on_select_solver)
        self.solve_button.Bind(wx.EVT_BUTTON, self._on_solve)
        self.reset_button.Bind(wx.EVT_BUTTON, self._on_reset)
        self.delay.Bind(wx.EVT_SCROLL_CHANGED, self._on_delay_set)
        self.mutation_rate.Bind(Fs.EVT_FLOATSPIN, self._on_mutation_rate_set)
        self.population_size.Bind(wx.EVT_SCROLL_CHANGED,
                                  self._on_population_size_set)
        self.num_elite.Bind(wx.EVT_SCROLL_CHANGED, self._on_elite_size_set)
        self.generations.Bind(wx.EVT_SCROLL_CHANGED, self._on_generations_set)
        self.tour_len.Bind(wx.EVT_SCROLL_CHANGED, self._on_tour_len_set)


        pub.subscribe(self._on_number_of_cities_change, 'NUM_OF_CITIES_CHANGE')
        pub.subscribe(self._on_solver_change, 'SOLVER_CHANGE')
        pub.subscribe(self._on_tsp_change, 'TSP_CHANGE')
        pub.subscribe(self._on_solver_state_change, 'SOLVER_STATE_CHANGE')
        pub.subscribe(self._on_solver_state_reset, 'SOLVER_STATE_RESET')

        # Run solver selection event handler to create default solver
        self._on_select_solver(None)

    def _on_select_solver(self, event):
        """Handles selecting solver from solvers combobox.
        """
        solver_name = self.solver_names[self.solver_select.GetSelection()]
        self.solver = self.get_solver(solver_name, self.dset, self.params[solver_name])
        self.cur_solver = solver_name
        pub.sendMessage('SOLVER_CHANGE', solver=solver_name)

    def _on_select_number_cities(self, event):
        """Handles selecting num of cities from cities combobox.
        """
        self.dset = load_dset_vis(f"./noa_kirel/datasets/{event.String}_cities.npy")
        self.solver = self.get_solver(self.cur_solver, self.dset, self.params[self.cur_solver])
        pub.sendMessage('NUM_OF_CITIES_CHANGE', num_of_cities=self.dset[CITIES])

    def _on_solve(self, event):
        """Handles clicking 'solve' button - runs `SolverRunner` with currently
        set solver and tsp.
        """
        num_of_days = self.params[self.cur_solver][TOUR_LEN]
        num_of_cities = self.dset[CITIES]
        if self.cur_solver == GEN:
            population_size = self.params[self.cur_solver][POP_SIZE]
            num_of_elite = self.params[self.cur_solver][NUM_ELITE]
            if num_of_days * num_of_cities < population_size:
                wx.MessageBox('Population size is too big', 'Error',
                              wx.ICON_ERROR | wx.OK)
                return
            if num_of_days < num_of_elite:
                wx.MessageBox('Elitisim is too big', 'Error', wx.ICON_ERROR
                              | wx.OK)
                return

        num_of_days = self.params[self.cur_solver][TOUR_LEN]
        num_of_cities = self.dset[CITIES]
        if num_of_days > num_of_cities:
            wx.MessageBox('Tour length is too long', 'Error',
                          wx.ICON_ERROR | wx.OK)
            return

        if not self.running:

            # Create and start the solver runner
            self.runner = SolverRunner(self.get_cur_solver())
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

            #self._on_solver_state_reset()

    def _on_reset(self, event):
        """Handles clicking 'reset' button - sends reset message.
        """
        self.Parent.tsp_view.gen_coords()
        pub.sendMessage('SOLVER_STATE_CHANGE', state=None)
        pub.sendMessage('SOLVER_STATE_RESET')
        self.result.SetLabel(self.DEFAULT_RESULT)

    def _on_delay_set(self, event):
        """Handles setting 'delay' slider - if there is an active runner its
        delay to the value from slider.
        """

        if not self.running:
            return

        self.runner.delay = self.delay.GetValue() / 1000
        self.result.SetLabel(self.DEFAULT_RESULT)

    def _on_mutation_rate_set(self, event):
        """Handles setting 'mutation_rate' slider
        """
        val = event.EventObject.Value
        self.params[self.cur_solver][MUT_RATE] = val
        self.solver = self.get_solver(self.cur_solver, self.dset, self.params[
                                      self.cur_solver])
        self.result.SetLabel(self.DEFAULT_RESULT)

    def _on_population_size_set(self, event):
        """Handles setting 'population_size' slider
        """
        val = event.EventObject.Value
        self.params[self.cur_solver][POP_SIZE] = val
        self.solver = self.get_solver(self.cur_solver, self.dset, self.params[
                                      self.cur_solver])
        self.result.SetLabel(self.DEFAULT_RESULT)

    def _on_elite_size_set(self, event):
        """Handles setting 'elite_size' slider
        """
        val = event.EventObject.Value
        self.params[self.cur_solver][NUM_ELITE] = val
        self.solver = self.get_solver(self.cur_solver, self.dset, self.params[
                                      self.cur_solver])
        self.result.SetLabel(self.DEFAULT_RESULT)

    def _on_generations_set(self, event):
        """Handles setting number of 'generations' slider
        """
        val = event.EventObject.Value
        self.params[self.cur_solver][STEPS] = val
        self.solver = self.get_solver(self.cur_solver, self.dset, self.params[
                                      self.cur_solver])
        self.result.SetLabel(self.DEFAULT_RESULT)

    def _on_tour_len_set(self, event):
        """Handles setting 'tour len' slider
        """
        val = event.EventObject.Value
        for solvers in self.params.values():
            solvers[TOUR_LEN] = val
        # self.params[self.cur_solver][TOUR_LEN] = val
        self.solver = self.get_solver(self.cur_solver, self.dset, self.params[
                                      self.cur_solver])
        self.result.SetLabel(self.DEFAULT_RESULT)

    def _on_view_change(self, event):
        """Handles checking or unchecking one of view option checkboxes.
        """
        options = {}
        pub.sendMessage('VIEW_OPTION_CHANGE', **options)

    def _on_number_of_cities_change(self, num_of_cities):
        """Handles solver change event.
        """
        self.num_of_cities = num_of_cities
        self.dset = load_dset_vis(f"./noa_kirel/datasets/{num_of_cities}_cities.npy")
        self.solver = self.get_cur_solver()
        self._on_reset(None)
        self.result.SetLabel(self.DEFAULT_RESULT)

    def _on_solver_change(self, solver):
        """Handles solver change event.
        """
        self.solver = solver
        self.result.SetLabel(self.DEFAULT_RESULT)

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

        if state[-1]:
            self.progress.SetValue(state[-1] * 100)

        self.cur_sol = state[0]
        self.cur_score = state[1]

        if state[1] > self.best_score:
            self.best_sol = state[0]
            self.best_score = state[1]

        # If this is final result
        if state[-1] == 1:
            # Set state to not running
            self._set_running(False)
        self.result.SetLabel(self.DEFAULT_RESULT)

    def _on_solver_state_reset(self):
        """Handles solver state reset message - clears result, error and
        progress controls.
        """
        self.result.SetLabel(self.DEFAULT_RESULT)
        #self.result.SetLabel(str(self.best_score))
        #self.error.SetLabel(self.DEFAULT_RESULT)
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
            # self.runner.stop()
            # self._on_reset(None)
            # Unset running flag, change button text, enable reset button
            self.running = False
            self.solve_button.SetLabel(self.SOLVE_BTN_INACTIVE)
            self.result.SetLabel(str(self.best_score))
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

    def gen_coords(self):
        self._points = dict()
        n_cities = self.Parent.Parent.controls.dset[CITIES]
        seen = set()
        def get_coord():
            coord = (np.random.randint(30, 731), np.random.randint(30, 731))
            # coord = (np.random.randint(0, 501), np.random.randint(0, 501))
            while coord in seen:
                coord = (np.random.randint(30, 731), np.random.randint(30, 731))
                # coord = (np.random.randint(0, 501), np.random.randint(0, 490))
            seen.add(coord)
            return coord

        cities = [get_coord() for _ in range(n_cities)]

        # Calculate for all points
        for i, c in enumerate(cities):
            # Note the inverted y axis
            self._points[i] = (c[0], c[1])


    def __init__(self, parent):
        super(TSPView, self).__init__(parent)

        # Cities list
        self._tsp = None
        self._points = None
        self.gen_coords()
        # self._points = None
        # Solver state
        self._state = None
        # Whether to show the best path
        self.show_best = True
        self.show_current = True

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
        pub.subscribe(self._on_solver_state_change, 'SOLVER_STATE_CHANGE')
        pub.subscribe(self._on_tsp_change, 'TSP_CHANGE')
        pub.subscribe(self._on_view_option_change, 'VIEW_OPTION_CHANGE')

    def _on_paint(self, event):
        """Paints currently set cities and paths.
        """

        # Create and clear drawing context
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()

        # Skip if there are no points
        if len(self._points) == 0:
            return

        # Draw state if it's defined
        if self._state:
            # Draw current path if there's no best even if it's disabled
            self._draw_path(dc, self._state[-3], self.BEST_COLOR)
            b = np.nonzero(np.array(self._state[-3]) - np.array(self._state[0]))[0]
            if len(b) > 1:
                self._draw_path(dc, self._state[0], self.CURRENT_COLOR)

        # Draw cities
        dc.SetPen(wx.Pen(self.CITY_COLOR))
        dc.SetBrush(wx.Brush(self.CITY_COLOR))
        for c in self._points.values():
            dc.DrawCircle(c[0], c[1], self.CITY_RADIUS)

    def _draw_path(self, dc, path, color):
        """Utility method to draw a path on the given device context.
        """

        dc.SetPen(wx.Pen(color, width=self.PATH_WIDTH))
        for i in range(len(path) - 1):
            if path[i] == -1 or path[i + 1] == -1:
                continue
            dc.DrawLine(self._points[path[i]], self._points[path[i + 1]])

    def _on_resize(self, event):
        """Handles resize event.
        """

        # self.calculate_points()

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

        self.Refresh()

    @property
    def tsp(self):
        """Returns current tsp instance.
        """

        return self._tsp

    @tsp.setter
    def tsp(self, tsp):
        """
        Sets tsp instance, triggers point calculation and repaint.
        """

        self._tsp = tsp
        # self.calculate_points()
        self.Refresh()

    def set_state(self, state):
        """Sets `SolverState` object and triggers repaint.
        """

        self._state = state
        self.Refresh()

    def calculate_points(self):
        """
        Calculates positions of points representing cities.
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
            x, y = (c[0] * side + exp), (h - (c[1] * side + eyp))
            self._points.append((x, y))

    def reset(self):
        """
        Resets this control to its initial empty state.
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

        # # Skip if there is no solver or solver has no properties
        # if not self.solver or not self.solver.properties:
        #     return

        # # For each property
        # for i, p in enumerate(self.solver.properties):
        #     # Create property object with appropriate type
        #     if p.type is int:
        #         prop = wxpg.IntProperty()
        #     elif p.type is float:
        #         prop = wxpg.FloatProperty()
        #     elif issubclass(p.type, Enum):
        #         prop = wxpg.EnumProperty()
        #         labels = list(map(lambda c: c.name, p.type))
        #         values = list(map(lambda c: c.value, p.type))
        #         prop_choices = wxpg.PGChoices(labels=labels, values=values)
        #         prop.SetChoices(prop_choices)
        #
        #     # Set label and value
        #     prop.SetLabel(p.name)
        #     prop.SetValue(p.default)
        #     prop.SetDefaultValue(p.default)
        #     prop.SetAttribute('property_idx', i)
        #
        #     # And append the property object
        #     self.Append(prop)

        # Fit columns and layout the parent
        self.FitColumns()
        self.GetParent().Layout()

    def reset(self):
        """Resets control to initial state.
        """

        self.Clear()
