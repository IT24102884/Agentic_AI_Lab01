# simulator.py
from grid_game import GridHuntGame
from agent import SimpleReflexAgent, ModelBasedAgent


def run_agent_simulation(agent_cls, name):
    env = GridHuntGame()
    agent = agent_cls()

    print(f"\n=== Simulation: {name} ===")
    while not env.is_done():
        percept = env.get_percept(agent)
        action = agent.sense_and_act(percept)
        env.execute_action(agent, action)
        print(f"Step {env.steps:2d} | Percept: wall_ahead={percept.get('wall_ahead')}, food_here={percept.get('food_here')} | Action: {action:5s} | Score: {env.score:3d} | Food Left: {percept['remaining_food']}")

    print(f"End {name}: Final Score: {env.score} after {env.steps} steps.")


if __name__ == "__main__":
    print("=== Lab 02 Agent Simulation ===")
    run_agent_simulation(SimpleReflexAgent, "SimpleReflexAgent (No Memory)")
    run_agent_simulation(ModelBasedAgent, "ModelBasedAgent (With Internal Memory State)")