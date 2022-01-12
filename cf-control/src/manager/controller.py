from .comms import Agent
from ..solver.server import Server
import schedule
from time import sleep
from time import time
import threading

class TaskRunner:
    """
    This is the class to actually control the agent itself. 
    Runs optimizations with the server and communicates to Crazyflie to actually implement solutions
    """
    def __init__(self,agent: Agent,server: Server, timestep: float, bench_test : bool = True):
        self._agent = agent
        self._server = server
        self._ts = timestep
        # default to False/off
        self._running = False
        self._send_cmd = not bench_test
        print(f"Bench test: {bench_test}, sending command: {self._send_cmd}")
        # Throws error at times, but this does allow for subsecond scheduling and not just 1-second intervals
        schedule.every(self._ts).seconds.do(self.feedback)
        
    def set_run(self):
        """ Start a run. Must call before starting the runner.
        """
        self._running = True
        self._agent.takeoff(self._send_cmd)

    def stop_run(self):
        """ Stop a run.
        """
        self._running = False
        self._agent.land(self._send_cmd)

    def feedback(self):
        """ Runs the feedback control problem for a given agent/server
        """
        state = self._agent.state_setpoint_diff()
        input = self._server.solve(state)
        print(f"{time() - self._agent._start} Current state: {self._agent.current_state()}")
        self._agent.update_input(input, self._send_cmd)

    def loop(self):
        """ Task loop to run for control. Runs the feedback function. Not sure if I need this now
        """
        self.feedback()


    def thread_start(self):
        self._task_thread = threading.Thread(target=self.runner)
        print("Started")
        self._task_thread.start()

    def thread_stop(self):
        self._task_thread.join()
        print("Stopped")

    def runner(self):
        """ Runs the task and sleep, simple thread
        """
        while self._running:
            # Note: probably unable to access class variable inside of thread.
            schedule.run_pending()   
            sleep(self._ts/10)
