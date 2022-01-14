from src.manager import Agent 
from src.solver import Server
from src.solver import Model
from src.manager import TaskRunner
from time import sleep

if __name__ == '__main__':
    timestep = 0.2
    # Define the model for the agent
    model = Model(2,1,20,timestep)
    print(model._name)
    agent = Agent(model)
    agent.connect()
    # Make server obj
    S = Server(model)
    # Server must first be built and then created
    S.build_server()
    S.run_server()

    T = TaskRunner(agent, S, timestep, True)
    # Main loop

    print("Running")
    T.set_run()

    T._agent.update_setpoint([0.1, 0])

    T.thread_start()
    for i in range(5):
        print("Waiting another second, at ", i)
        sleep(1)
    T.stop_run()
    T.thread_stop()

    T._server.down()
    T._agent.disconnect()
    sleep(2)
    print(f"Agent connected: {T._agent._cf.is_connected()}")
    print("Done")
