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
        "allow_key_presses": True
    }

    # Creates the environment with
    # the specified settings
    window = AsteroidGame(settings)

    # The instantiated environment can be given a Scenario
    # to override the default Scenario
    score = window.run(scenario=Scenario(num_asteroids=3))

    print(f"score {score.__dict__}")
    # score = window.run(scenario=Scenario(num_asteroids=3))
    # score = window.run(scenario=Scenario(num_asteroids=3))
