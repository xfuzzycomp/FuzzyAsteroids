from src.fuzzy_asteroids.fuzzy_asteroids import *


class FuzzyController(ControllerBase):
    def actions(self, ship: SpaceShip, input_data: Dict[str, Any]) -> None:
        pass


if __name__ == "__main__":
    # Instantiate an instance of TrainerEnvironment.
    # The default settings should be sufficient, but check out the documentation for more information
    game = TrainerEnvironment()

    # Because of how the arcade library is implemented, there are memory leaks for instantiating the environment
    # too many times, keep instantiations to a small number and simply reuse the environment

    score = game.run(controller=FuzzyController())
    print(score)
