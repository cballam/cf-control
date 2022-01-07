from time import sleep
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
        self._cf = Crazyflie(rw_cache='./cache') 
        
    def current_state(self):
        # Generic getter fn to get the state of the agent.
        return self._state

    def update_input(self, input: list, send_command: bool):
        """ Get a new input for the agent to send (through some channel) 
        """
        self._input = input
        if send_command:
            print("Sending actual command")
            self._cf.commander.send_velocity_world_setpoint(*input)

    def connect(self) -> None:
        """ Connect directly to the Crazyflie (make generic later if desired)
            Init all local control drivers (should get antenna)
        """ 
        crtp.init_drivers(enable_debug_driver=False)
        # Scan for crazyflie
        found = crtp.scan_interfaces()
        if len(found) > 0:
            print("Opening link to Crazyflie with uri: ", found[0][0])
            print("Found: ", found)
            # Note: scf should be instance of the actual Crazyflie class
            # Using regular async Crazyflie instead
            self._cf.open_link(found[0][0])
            self._cf.connected.add_callback(self._on_connect)

    def disconnect(self) -> None:
        """ Force disconnect from Crazyflie
        """
        print("Closing link")
        self._cf.close_link()

    def takeoff(self,bench_test : bool, height=0.4) -> None:
        """ Get the quad flying. Defaults to height of 0.4m, enough to be off the ground but not too high.
        Can also bench test this (does nothing)
        """
        if self._cf.is_connected() and not bench_test:
            self._home_base = self.current_state()
            # Turn props on for a short time so that the quad doesn't have any issues at the start
            self._cf.commander.send_velocity_world_setpoint(0,0,0.1,0)
            sleep(0.1)
            for i in range(15):
                self._cf.commander.send_position_setpoint(self._home_base[0], self._home_base[1], self._home_base[2] + (height/15)*i, 0)
                sleep(0.1)
        else:
            print("Bench test 'takeoff'")


    def _cf_logconf(self) -> LogConfig:
        # Set up the log config for the controller (async logs)
        log_config = LogConfig(name="State", period_in_ms=500)
        log_config.add_variable("stateEstimate.x",'float')
        log_config.add_variable("stateEstimate.y",'float')
        log_config.add_variable("stateEstimate.z",'float')
        return log_config

    def _on_connect(self, _):
        self._log =self._cf_logconf() 
        self._log.data_received_cb.add_callback(self._log_callback)
        #logconf.data_received_cb(print)
        self._cf.log.add_config(self._log)
        self._log.start()

    def _log_callback(self,timestep,data,logconf):
        self._state[0] = data['stateEstimate.x']
#        self._state[1] = data['stateEstimate.y']
#        self._state[2] = data['stateEstimate.z']
