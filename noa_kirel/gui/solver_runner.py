import multiprocessing
import threading
import time

import wx
from pubsub import pub


class SolverRunner(threading.Thread):
    """Separate thread for running solver. It spawns SolverProcess, reads
    solver states from the queue respecting set delay and send pubsub messages
    to the GUI with new states.
    """

    def __init__(self, solver, tsp):
        """Creates new SolverRunner for given solver and TSP instance.

        :param Solver solver: TSP solver instance.
        :param TSP tsp: TSP instance.
        """

        threading.Thread.__init__(self)

        # Results queue
        self._queue = multiprocessing.Queue()

        # Results list
        self.results = []

        # Solver and TSP instance
        self._solver = solver
        self._tsp = tsp

        # Event signalling this thread to stop
        self._stop_event = threading.Event()

        # Delay between messages to GUI
        self.delay = 0
        # How many messages per second can be sent to GUI
        self.message_limit = 60

        # Reset message subscribtion
        pub.subscribe(self._on_solver_state_reset, 'SOLVER_STATE_RESET')

    def run(self):
        """Creates a process wich runs the solver.
        """

        # Start solver process
        self.solver_process = SolverProcess(
            self._solver, self._tsp, self._queue)
        self.solver_process.daemon = True
        self.solver_process.start()

        # Mesage can be sent after this interval from sending the previous one
        message_interval = 1 / self.message_limit
        # Timestamp after which next message can be sent
        next_message_time = time.time()

        # Start reading SolverState objects from the queue
        while not self._stop_event.is_set():
            state = self._queue.get()
            self.results.append(state)

            if time.time() > next_message_time:
                # Send message with the new state to GUI
                wx.CallAfter(pub.sendMessage, 'SOLVER_STATE_CHANGE',
                             state=state)
                # Calculate when next message can be sent
                next_message_time = time.time() + message_interval

            # Break out of the loop if it's the final state
            if state.final:
                break

            # Sleep specified amount of itme
            time.sleep(self.delay)

        # Always send the final state
        wx.CallAfter(pub.sendMessage, 'SOLVER_STATE_CHANGE', state=state)
        # Send information that solving has ended
        wx.CallAfter(pub.sendMessage, 'SOLVER_STATE_END', results=self.results)

        # Make sure the queue is empty
        while not self._queue.empty():
            self._queue.get_nowait()

        # This is necessary only Windows, worked fine on Linux
        self.solver_process.terminate()

        # Wait for the solver process
        self.solver_process.join()

    def stop(self):
        """Terminates the solver process.
        """

        self.solver_process.stop()
        self._stop_event.set()

    def _on_solver_state_reset(self):
        """Handles solver state reset.
        """

        self.results = []


class SolverProcess(multiprocessing.Process):
    """Separate process for running solver so it can have as much CPU power as
    it wants without interfering with GUI.
    """

    def __init__(self, solver, tsp, queue):
        multiprocessing.Process.__init__(self)

        # Queue for storing queue
        self._solver = solver
        self._tsp = tsp
        self._queue = queue

        # Signal to stop the process
        self._stop_event = multiprocessing.Event()

    def run(self):
        """Runs the solver in loop, stops on event.
        """

        for state in self._solver.solve(self._tsp):
            self._queue.put_nowait(state)

            if self._stop_event.is_set():
                break

        self._queue.close()

    def stop(self):
        """Sets the stop event.
        """

        self._stop_event.set()
