import time
import random

from src.fuzzy_asteroids.fuzzy_controller import *
from src.fuzzy_asteroids.fuzzy_asteroids import FuzzyAsteroidGame, Scenario


def test_timeout(input_data):
    # Function for testing the timing out by the simulation environment
    wait_time = random.uniform(0.02, 0.03)
    time.sleep(wait_time)


class FuzzyController(ControllerBase):
    pass

    def actions(self, ships: Tuple[SpaceShip], input_data: Dict[str, Tuple]) -> None:
        test_timeout(input_data)

        for ship in ships:
            ship.turn_rate = random.uniform(ship.turn_rate_range[0]/2.0, ship.turn_rate_range[1])
            ship.thrust = random.uniform(ship.thrust_range[0], ship.thrust_range[1])
            ship.fire_bullet = random.uniform(0.45, 1.0) < 0.5

if __name__ == "__main__":
    # Available settings
    settings = {
        "frequency": 60,
        "real_time_multiplier": 2,
        "graphics_on": True,
        "sound_on": False,
        "prints": True,
    }

    # Instantiate an instance of FuzzyAsteroidGame
    game = FuzzyAsteroidGame(settings=settings,
                             track_compute_cost=True,
                             controller_timeout=True,
                             ignore_exceptions=False)

    scenario_ship = Scenario(name="Multi-Ship",
                             num_asteroids=4,
                             ship_states=[{"position": (300, 500), "angle": 180, "lives": 1},
                                          {"position": (500, 300), "angle": 180, "lives": 5},
                                          {"position": (400, 300), "angle": 180, "lives": 3},
                                          ])

    score = game.run(controller=FuzzyController(), scenario=scenario_ship)
