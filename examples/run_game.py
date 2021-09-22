from src.fuzzy_asteroids.game import *

if __name__ == "__main__":
    # Settings dictionary
    settings = {
        "frequency": 60,
        "real_time_multiplier": 1,
        "time_limit": 100,
        "sound_on": False,
        "graphics_on": True,
        "prints": True,
        "allow_key_presses": True,
        "full_dashboard": True,
    }

    # Creates the environment with
    # the specified settings
    window = AsteroidGame(settings)

    scenario_ship = Scenario(name="Multi-Ship",
                             num_asteroids=4,
                             time_limit=100,
                             ship_states=[{"position": (300, 500), "angle": 180, "lives": 1},
                                          {"position": (500, 300), "angle": 180, "lives": 5},
                                          {"position": (400, 300), "angle": 180, "lives": 3},
                                          ])

    # The instantiated environment can be given:
    # * A Scenario to override the default Scenario
    # * A Score to override the default Score
    score = window.run(scenario=scenario_ship,
                       score=Score())
