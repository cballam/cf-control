from time import sleep
from time import time
import numpy as np
import cflib.crtp as crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig

class Agent:
    """ Handles communications and direct control with the actual robot.
    This is currently hard-coded for the Crazyflie, ideally it would be more of a template to allow you to implement your own comms.
    Holds agent state, allows for connection to be established, input to be updated, state to be read directly
    """
    # I would prefer if this were platform independant, but for now it is easier to hard-code Crazyflie-specific functions
    def __init__(self, model):
        self._state = np.zeros(model._num_states)
        self._home_base = self._state
        self._setpoint = self._state
        self._cf = Crazyflie(rw_cache='./cache') 
        self._ready = False
        self._start = time()
        
    def current_state(self) -> list:
        """ Agent's stored state
        """
        # Generic getter fn to get the state of the agent.
        return self._state

    def state_setpoint_diff(self) -> list:
        """ In case I want to do setpoint based control - may change in future
        """
        return self._state - self._setpoint

    def update_input(self, input: list, send_command: bool):
        """ Get a new input for the agent to send (through some channel) 
        """
        self._input = input
        #print(f"{time() - self._start}: Input should be: {input}")
        if self._ready and send_command:
            self._cf.commander.send_velocity_world_setpoint(input[0], 0, 0, 0)

    def update_setpoint(self, setpoint: list):
        """ Get new setpoint direction
        """
        self._setpoint = setpoint

    def connect(self) -> None:
        """ Connect directly to the Crazyflie (make generic later if desired)
            Init all local control drivers (should get antenna)
        """ 
        crtp.init_drivers(enable_debug_driver=False)
        # Scan for crazyflie
        found = crtp.scan_interfaces()
        if len(found) > 0:
            print("Opening link to Crazyflie with uri: ", found[0][0])
            # Note: scf should be instance of the actual Crazyflie class
            # Using regular async Crazyflie instead
            self._cf.open_link(found[0][0])
            self._cf.connected.add_callback(self._on_connect)

    def disconnect(self) -> None:
        """ Force disconnect from Crazyflie
        """
        print("Closing link")
        self._cf.close_link()

    def takeoff(self,fly: bool = False, height : float = 0.4) -> None:
        """ Get the quad flying. Defaults to height of 0.4m, enough to be off the ground but not too high.
        Can also bench test this (does nothing)
        """
        if self._cf.is_connected() and fly:
            # Wait until properly connected
            while not self._ready:
                pass
            self._reset_estimation()
            self._log.start()
            print("Reset!")
            self._home_base = self.current_state()
            # Turn props on for a short time so that the quad doesn't have any issues at the start
            self._cf.commander.send_velocity_world_setpoint(0,0,0.1,0)
            sleep(0.1)
            for i in range(15):
                self._cf.commander.send_position_setpoint(0, 0, (height/15)*i, 0)
                sleep(0.1)
        else:
            print("Bench test 'takeoff'")
            self._reset_estimation()
            self._log.start()
            sleep(0.4)

        self._start = time()

    def land(self,fly: bool = False, height : float = 0.4):
        """ Land the Crazyflie by descending (currently hard coded to assume height in 10ths of a meter)
        Lazy descent to 0.1m before cutting motors, might be nicer way to do this but 10cm probably fine to drop
        """
        if self._cf.is_connected() and fly:
            # get down to 0.1m before cutting motors
            for h in range(int(height*10) -1):
                self._cf.commander.send_position_setpoint(self._state[0], self._state[1], height - h, 0)
                sleep(0.2)

            self._cf.commander.send_stop_setpoint()
            self._log.stop()
            print("Stopped")
        else:
            print("Landing sequence reached, not flying")

    def _cf_logconf(self) -> LogConfig:
        # Set up the log config for the controller (async logs)
        log_config = LogConfig(name="State", period_in_ms=50)
        #log_config.add_variable("stateEstimate.x",'float')
        #log_config.add_variable("stateEstimate.x",'float')
        log_config.add_variable("kalman.stateX",'float')
        log_config.add_variable("kalman.statePX",'float')
        #log_config.add_variable("stateEstimate.y",'float')
        #log_config.add_variable("stateEstimate.z",'float')
        return log_config

    def _on_connect(self, _) -> None:
        print("Connecting")
        self._log =self._cf_logconf() 
        self._log.data_received_cb.add_callback(self._log_callback)
        self._cf.log.add_config(self._log)
        #self._log.start()
        print("Connected to CF and called log.start")
        sleep(0.4)
        self._ready = True

    def _reset_estimation(self) -> None:
        """ Reset the Kalman filter so current position is zeroed
        """
        print("Reset the kalman filter")
        self._cf.param.set_value('kalman.resetEstimation', '1')
        print("Set resetEstimation = 1")
        sleep(0.5)
        self._cf.param.set_value('kalman.resetEstimation', '0')
        print("Set resetEstimation = 0")
        sleep(0.1)

    def _log_callback(self,timestep,data,logconf):
        """ What is to be done with the Crazyflie state data (should be stored)
        """
        #self._x = data['kalman.stateX']
        self._state[0], self._state[1] = data['kalman.stateX'], data['kalman.statePX']
        #self._vx = data['kalman.statePX']
        #print(f"Callback, data: {data}")
#        self._state[1] = data['stateEstimate.y']
#        self._state[2] = data['stateEstimate.z']
