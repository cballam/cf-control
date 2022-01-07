import opengen as og

class Server:
    def __init__(self, model):
        # Guess I'll have a model that I pass to this?
        self._model = model
        # Want status based on the last call
        self.status = 'OK'
        # set connection to nonetype for now
        self.connection = None

    def build_server(self):
        """
        Build the server. Uses the model passed to the system to generate a server
        """
        # Want to offload most of these things to the model class
        problem = og.opengen.builder.Problem(*self._model.define_cost())
        build_conf = og.opengen.config.BuildConfiguration() \
            .with_build_directory("python_build") \
            .with_tcp_interface_config()
        meta = og.opengen.config.OptimizerMeta().with_optimizer_name(self._model._name)
        solver_conf = og.opengen.config.SolverConfiguration()\
            .with_tolerance(1e-4)\
            .with_initial_tolerance(1e-2)
        builder = og.opengen.builder.OpEnOptimizerBuilder(problem, meta, build_conf, solver_conf)
        builder.build()

    def run_server(self) -> bool:
        """
        Sets up server
        """
        self.connection = og.opengen.tcp.OptimizerTcpManager("python_build/" + self._model._name)
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
                input = input[0:self._model._num_inputs]
                return input

        # fail by returning no input as default
        return [0 for _ in range(self._model._num_inputs)]
