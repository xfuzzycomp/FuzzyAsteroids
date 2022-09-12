import time
import random
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

from src.fuzzy_asteroids.fuzzy_controller import *
from src.fuzzy_asteroids.fuzzy_asteroids import FuzzyAsteroidGame, Scenario


def timeout(input_data):
    # Function for testing the timing out by the simulation environment
    wait_time = random.uniform(0.02, 0.03)
    time.sleep(wait_time)


class FuzzyController(ControllerBase):
    @property
    def name(self) -> str:
        return "Example Controller Name"

    def __init__(self):
        self.construct_fiss()

    def construct_fiss(self):
        input1 = ctrl.Antecedent(np.arange(-1, 1, 0.05), 'input1')
        input2 = ctrl.Antecedent(np.arange(-1, 1, 0.05), 'input2')
        turn_rate = ctrl.Consequent(np.arange(-1, 1, 0.05), 'turn_rate')

        # input1.automf(3)
        # input2.automf(3)

        input1['negative'] = fuzz.trimf(input1.universe, [-1.0, -1.0, 0.0])
        input1['zero'] = fuzz.trimf(input1.universe, [-1.0, 0.0, 1.0])
        input1['positive'] = fuzz.trimf(input1.universe, [0.0, 1.0, 1.0])

        input2['negative'] = fuzz.trimf(input2.universe, [-1.0, -1.0, 0.0])
        input2['zero'] = fuzz.trimf(input2.universe, [-1.0, 0.0, 1.0])
        input2['positive'] = fuzz.trimf(input2.universe, [0.0, 1.0, 1.0])

        turn_rate['negative'] = fuzz.trimf(turn_rate.universe, [-1.0, -1.0, 0.0])
        turn_rate['zero'] = fuzz.trimf(turn_rate.universe, [-1.0, 0.0, 1.0])
        turn_rate['positive'] = fuzz.trimf(turn_rate.universe, [0.0, 1.0, 1.0])

        rule1 = ctrl.Rule(input1['negative'] & input2['negative'], turn_rate['negative'])
        rule2 = ctrl.Rule(input1['negative'] & input2['zero'], turn_rate['negative'])
        rule3 = ctrl.Rule(input1['negative'] & input2['positive'], turn_rate['zero'])
        rule4 = ctrl.Rule(input1['zero'] & input2['negative'], turn_rate['negative'])
        rule5 = ctrl.Rule(input1['zero'] & input2['zero'], turn_rate['zero'])
        rule6 = ctrl.Rule(input1['zero'] & input2['positive'], turn_rate['positive'])
        rule7 = ctrl.Rule(input1['positive'] & input2['negative'], turn_rate['zero'])
        rule8 = ctrl.Rule(input1['positive'] & input2['zero'], turn_rate['positive'])
        rule9 = ctrl.Rule(input1['positive'] & input2['positive'], turn_rate['positive'])

        rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9]

        fis1_ctrl = ctrl.ControlSystem(rules)

        self.fis1 = ctrl.ControlSystemSimulation(fis1_ctrl)

    def get_closest_asteroid_distance(self, asteroids):
        pass

    def get_closest_asteroid_angle(self, asteroids) -> float:
        pass

    def actions(self, ships: Tuple[SpaceShip], input_data: Dict[str, Tuple]) -> None:
        timeout(input_data)

        asteroids = input_data["asteroids"]
        # print(asteroids[0]["angle"])

        for ship in ships:

            # self.get_closest_asteroid_distance(asteroids)
            # self.get_closest_asteroid_angle(asteroids)
            self.fis1.input["input1"] = asteroids[0]["angle"]/180.0
            self.fis1.input["input2"] = asteroids[1]["angle"]/180.0
            self.fis1.compute()
            ship.turn_rate = self.fis1.output["turn_rate"]*180.0
            # print(ship.turn_rate)
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
        "full_dashboard": True
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
