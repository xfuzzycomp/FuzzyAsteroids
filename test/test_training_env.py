from src.fuzzy_asteroids.fuzzy_asteroids import *


class FuzzyController(ControllerBase):
    pass


if __name__ == "__main__":
    # Available settings
    settings = {
        "frequency": 60,
        "real_time_multiplier": 3,
        "lives": 3,
        "time_limit": None,
        "graphics_on": True,
        "sound_on": False,
        "prints": True,
        "allow_key_presses": False
    }

    # Instantiate an instance of FuzzyAsteroidGame
    game = TrainerEnvironment(settings=settings)

    score = game.run(controller=FuzzyController())
