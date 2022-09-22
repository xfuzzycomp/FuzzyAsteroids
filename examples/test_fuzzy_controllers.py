import time
import random

from src.fuzzy_asteroids.fuzzy_controller import *
from src.fuzzy_asteroids.fuzzy_asteroids import FuzzyAsteroidGame, Scenario


def timeout(input_data):
    # Function for testing the timing out by the simulation environment
    wait_time = random.uniform(0.02, 0.03)
    time.sleep(wait_time)

class T1Controller(ControllerBase):
    @property
    def name(self) -> str:
        return "Team 1 Controller"

    def actions(self, ship: SpaceShip, input_data: Dict[str, Tuple]) -> None:
        # timeout(input_data)
        if ship.team == 1:
            ship.turn_rate = random.uniform(ship.turn_rate_range[0]/2.0, ship.turn_rate_range[1])
            ship.thrust = random.uniform(ship.thrust_range[0], ship.thrust_range[1])
            ship.fire_bullet = random.uniform(0.45, 1.0) < 0.5
        else:
            ship.turn_rate = random.uniform(ship.turn_rate_range[0] / 2.0, ship.turn_rate_range[1])
            ship.thrust = random.uniform(ship.thrust_range[0], ship.thrust_range[1])
            ship.fire_bullet = random.uniform(0.0, 1.0) < 0.5


class T2Controller(ControllerBase):
    @property
    def name(self) -> str:
        return "Team 2 Controller"

    def actions(self, ship: SpaceShip, input_data: Dict[str, Tuple]) -> None:
        # timeout(input_data)

        if ship.team == 2:
            ship.turn_rate = random.uniform(-ship.turn_rate_range[0]/2.0, ship.turn_rate_range[1])
            ship.thrust = random.uniform(ship.thrust_range[0]/2.0, ship.thrust_range[1])
            ship.fire_bullet = random.uniform(0.0, 1.0) < 0.5
        else:
            ValueError("Wrong controller called, ship assigned team other than 2 but reached team 2 controller")
#
# class Controllers(ControllerBase):
#     @property
#     def name(self) -> str:
#         return "Main Controller Class"
#
#     def __int__(self, t1_controller, t2_controller):
#         self.team1 = t1_controller
#         self.team2 = t2_controller
#
#     @staticmethod
#     def team1_controller():
#         return T1Controller()
#
#     @staticmethod
#     def team2_controller():
#         return T2Controller()



if __name__ == "__main__":
    # Available settings
    settings = {
        "frequency": 60,
        "real_time_multiplier": 2,
        "graphics_on": True,
        "sound_on": False,
        "prints": True,
        "full_dashboard": True
    }

    # Instantiate an instance of FuzzyAsteroidGame
    game = FuzzyAsteroidGame(settings=settings,
                             track_compute_cost=True,
                             controller_timeout=True,
                             ignore_exceptions=False)

    scenario_ship = Scenario(name="Multi-Ship",
                             num_asteroids=4,
                             ship_states=[{"position": (300, 500), "angle": 180, "lives": 3, "team": 1},
                                          {"position": (500, 300), "angle": 180, "lives": 3, "team": 2},
                                          ])

    # controllers = [T1Controller(), T2Controller()]
    controllers = {1: T1Controller(), 2: T2Controller()}
    # cd = Controllers()
    # score = game.run(controller=FuzzyController(), scenario=scenario_ship)
    score = game.run(controller=controllers, scenario=scenario_ship)

