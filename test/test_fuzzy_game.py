import time
import random

from src.fuzzy_asteroids.fuzzy_asteroids import *


def test_timeout(input_data):
    # Function for testing the timing out by the simulation environment
    wait_time = random.uniform(0.01, 0.02)
    time.sleep(wait_time)

class FuzzyController(ControllerBase):
    pass

    def actions(self, ship: SpaceShip, input_data: Dict[str, Tuple]) -> None:
        test_timeout(input_data)

        ship.turn_rate = random.randrange(ship.turn_rate_range[0]/2.0, ship.turn_rate_range[1])
        ship.thrust = random.randrange(ship.thrust_range[0], ship.thrust_range[1])



if __name__ == "__main__":
    # Available settings
    settings = {
        "frequency": 60,
        "real_time_multiplier": 2,
        "lives": 3,
        "time_limit": None,
        "graphics_on": True,
        "sound_on": False,
        "prints": True,
        "allow_key_presses": False
    }

    # Instantiate an instance of FuzzyAsteroidGame
    game = FuzzyAsteroidGame(settings=settings, track_compute_cost=True)

    score = game.run(controller=FuzzyController())
