import casadi.casadi as cs

class Model:
    """ Dynamic model for the optimization problem at hand.
    Implements mapping x(t+1) = f(x(t)) + u where f may be a nonlinear function describing the state transition dynamics 
    Provides the define_cost method which returns required casadi functions for OpEn to build a server
    """
    def __init__(self,
                 num_states : int,
                 num_inputs : int,
                 horizon : int,
                 sampling_time : float,
                 name : str ="base"):
        self._num_states = num_states
        self._num_inputs = num_inputs
        self._horizon = horizon
        self._t_sample = sampling_time
        self._name = name
        pass

    def _dyn_ct(self,x,u):
        """
        Dynamics (cont.)
        """
        dx1 = x[1]
        dx2 = u
        return [dx1,dx2]

    def _dynamics(self,x,u):
        """
        Dynamics in discrete format for the cascadi optimization problem
        """
        dx = self._dyn_ct(x,u)
        return [x[i] + self._t_sample*dx[i] for i in range(self._num_states)]

    def define_cost(self):
        """
        Define the cost function for this model.
        Returns what you need to build the OpEn Problem (optimization vars, state vars, cost summation)
        """
        u_seq = [cs.MX.sym('u' + str(i), self._num_inputs) for i in range(self._horizon)]
        state_seq = cs.MX.sym("x", self._num_states)
        states = state_seq
        total_cost = 0
        for n in range(0,self._horizon):
            total_cost += self._stage_cost(state_seq,u_seq[n])
            state_seq = self._dynamics(state_seq,u_seq[n])
        total_cost += self._terminal_cost(state_seq)
        return [cs.vertcat(*u_seq), states, total_cost] 
        
    def _stage_cost(self,x,u,Q=10,R=50):
        """ Stage cost is the (quadratic) cost function for an individual step.
        Each step of the sequence has cost roughly defined by Qx^2 + Ru^2
        """
        return Q*4*x[0]**2 + Q*x[1]**2 + R*u**2

    def _terminal_cost(self,x,Qs=10):
        """ Cost of offset from target (regulation) at the end of the optimization problem.
        """
        return Qs*x[0]**2 + Qs*x[1]**2
