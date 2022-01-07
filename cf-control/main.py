from manager import Agent 
#from solver import *
from solver import Server
from solver import Model
from manager import TaskRunner
from time import sleep

if __name__ == '__main__':
    timestep = 0.1
    # Define the model for the agent
    model = Model(2,1,10,0.1)
    print(model._name)
    agent = Agent(model)
    agent.connect()
    # Make server obj
    S = Server(model)
    # Server must first be built and then created
    S.build_server()
    S.run_server()
    print(S.solve([1.0, 0]))
    agent._state[0] = 1.0

    T = TaskRunner(agent, S, timestep)
    # Main loop

    print("Running")
    T.set_run()
#    while running:
#        # Want something every (configured) timestep to run
#        #schedule.every(0.1).seconds.do(pass, None)
#        # Call server for solution with
#        T.feedback()
#        print(T._agent._input)
#
#        running = False
#        sleep(1)

    #T.runner()
    T.thread_start()
    for i in range(10):
        print("Waiting another second, at ", i)
        sleep(1)
    T.stop_run()
    T.thread_stop()

    T._server.down()
    T._agent.disconnect()
    sleep(2)
    print(f"Agent connected: {T._agent._cf.is_connected()}")
    print("Done")
