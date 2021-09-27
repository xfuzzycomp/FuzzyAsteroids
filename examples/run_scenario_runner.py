from src.fuzzy_asteroids.fuzzy_controller import *


from src.fuzzy_asteroids.runner import ScenarioRunner, Scenario


class FuzzyController1(ControllerBase):
    @property
    def name(self) -> str:
        return "Controller 1"

    @staticmethod
    def final_controller():
        return FuzzyController1()

    def actions(self, ship: SpaceShip, input_data: Dict[str, Any]) -> None:
        pass


class FuzzyController2(ControllerBase):
    @property
    def name(self) -> str:
        return "Controller 2"

    @staticmethod
    def final_controller():
        return FuzzyController2()

    def actions(self, ship: SpaceShip, input_data: Dict[str, Any]) -> None:
        pass

portfolio = [
    Scenario(num_asteroids=3, time_limit=0.5),
    Scenario(num_asteroids=4, time_limit=1),
]


if __name__ == "__main__":
    controllers = {
        "controller1": FuzzyController1.final_controller(),
        "controller2": FuzzyController2.final_controller(),
    }
    additional_options = {

    }

    # Instantiate an instance of TrainerEnvironment.
    # The default settings should be sufficient, but check out the documentation for more information
    runner = ScenarioRunner(controllers, portfolio)

    # Run all scenarios with graphics
    runner.run_all_controllers(graphics_on=True)

    # Run all scenarios without graphics
    # runner.run_all_controllers(graphics_on=False)
