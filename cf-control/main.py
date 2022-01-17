import threading
from src.manager import Agent 
from src.solver import Server
from src.solver import Model
from src.manager import TaskRunner
from time import sleep

# Setup
timestep = 0.1
# Define the model for the agent
model = Model(2,1,50,timestep)

#app = Flask(__name__)
S = Server(model)
from src.web import *

# Note: very dodgy way to do things, but it works. Should find better way to do it.
@app.route('/trajectory')
def state():
    return jsonify({'state' : S._state_traj})

if __name__ == '__main__':
    t = threading.Thread(target= lambda: app.run(port=3000, debug = True, use_reloader= False))
    t.start()
    agent = Agent(model)
    agent.connect()
    # Make server obj
    #S = Server(model)
    # Server must first be built and then created
    S.build_server()
    S.run_server()

    T = TaskRunner(agent, S, timestep, True)
    # Main loop

    print("Running")
    T.set_run()

    T._agent.update_setpoint([0.5, 0])

    T.thread_start()
    for i in range(30):
        print("Waiting another second, at ", i)
        sleep(1)
    T.stop_run()
    T.thread_stop()

    T._server.down()
    T._agent.disconnect()
    sleep(2)
    print(f"Agent connected: {T._agent._cf.is_connected()}")
    print("Done")
    t.join(5)
