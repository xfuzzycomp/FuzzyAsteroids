from src.fuzzy_asteroids.util import *

if __name__ == "__main__":
    scenario2 = Scenario(game_map=Map(), asteroid_states=[{"position": (100, 100)}])

    # assert not scenario2
    # print("states", Scenario(Map(), num_asteroids=3).asteroid_states)

    print("num_starting_asteroids", scenario2.num_starting_asteroids)
    print("max_asteroids", scenario2.max_asteroids)
