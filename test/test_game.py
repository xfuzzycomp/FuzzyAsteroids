from src.fuzzy_asteroids.game import *

if __name__ == "__main__":
    # Settings dictionary
    settings = {
        "frequency": 60,
        "real_time_multiplier": 2,
        "time_limit": 100,
        "sound_on": False,
        "graphics_on": True,
        "lives": 3,
        "prints": False,
        "allow_key_presses": True,
        "number_of_ships": 3
    }

    # Creates the environment with
    # the specified settings
    window = AsteroidGame(settings)

    scenario_ship = Scenario(name="scenario_ship",
                             num_asteroids=4,
                             ship_states=[{"position": (300, 500), "angle": 180, "lives": 5},
                                          {"position": (500, 300), "angle": 180, "lives": 3},
                                          {"position": (400, 300), "angle": 180, "lives": 2},
                                          ])


    # The instantiated environment can be given:
    # * A Scenario to override the default Scenario
    # * A Score to override the default Score
    score = window.run(scenario=scenario_ship,
                       score=Score())

    print(f"score {score.__dict__}")
    # score = window.run(scenario=Scenario(num_asteroids=3))
    # score = window.run(scenario=Scenario(num_asteroids=3))
