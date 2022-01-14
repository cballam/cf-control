import opengen as og

class Server:
    """ Allows interactions with the OpEn server to solve optimization problems.
    Requires the model of dynamic system in question to specify the problem, and solves to a desired tolerance.
    """
    def __init__(self, model):
        # Guess I'll have a model that I pass to this?
        self._model = model
        # Want status based on the last call
        self.status = 'OK'
        # set connection to nonetype for now
        self.connection = None
        # Last input is by default an empty list
        self._last_input = []
        self._state_traj = []

    def build_server(self, desired_tolerance = 1e-4, initial_tolerance = 1e-2):
        """
        Build the server. Uses the model passed to the system to generate a server
        """
        # Want to offload most of these things to the model class
        problem = og.opengen.builder.Problem(*self._model.define_cost())
        # Standard build directory (ignored by .gitignore)
        build_conf = og.opengen.config.BuildConfiguration() \
            .with_build_directory("python_build") \
            .with_tcp_interface_config()
        # Metadata is another standard one
        meta = og.opengen.config.OptimizerMeta().with_optimizer_name(self._model._name)
        solver_conf = og.opengen.config.SolverConfiguration()\
            .with_tolerance(desired_tolerance)\
            .with_initial_tolerance(initial_tolerance)
        # Build, but needs to use slightly modified OpEn repo to do so due to rust potential erroring out in some areas.
        builder = og.opengen.builder.OpEnOptimizerBuilder(problem, meta, build_conf, solver_conf)
        builder.build()

    def run_server(self) -> bool:
        """
        Sets up server
        """
        # Currently testing this, should be changing to model name again
        self.connection = og.opengen.tcp.OptimizerTcpManager("python_build/" + self._model._name)
        #self.connection = og.opengen.tcp.OptimizerTcpManager("python_build/" + 'a')
        self.connection.start()
        resp = self.connection.ping()
        # If you ping the server, you should get back "Pong" response
        return resp['Pong'] == 1

    def down(self) -> bool:
        """
        Kills the OpEn server
        """
        if type(self.connection) is type(None):
            return False
        else:
            self.connection.kill()
            return True
        
    def solve(self, state) -> list:
        """
        Solve the server's optimization problem and get the resulting input to the system
        """
        if type(self.connection) is not type(None):
            resp = self.connection.call(state)
            if not resp.is_ok():
                print("Failed to find solution")
            else:
                input = resp["solution"]
                self._last_input = input
                input = input[0:self._model._num_inputs]
                return input

        # fail by returning no input as default
        return [0 for _ in range(self._model._num_inputs)]

    def eval_traj(self, init_state : list) -> None:
        """ Given an initial state and the (known) inputs found from solving optimization problem, create expected trajectory
        """
        state_traj = [init_state]
        for inputs in zip(*[iter(self._last_input)]*self._model._num_inputs):
            new_state = self._model._dynamics(state_traj[-1], *inputs)
            state_traj.append(new_state)
        print(state_traj)
        self._state_traj = state_traj
