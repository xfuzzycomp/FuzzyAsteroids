from src.fuzzy_asteroids.fuzzy_asteroids import *


class FuzzyController(ControllerBase):
    def actions(self, ship: SpaceShip, input_data: Dict[str, Any]) -> None:
        pass


if __name__ == "__main__":
    # Available settings
    settings = {
        "frequency": 60,
        "real_time_multiplier": 0,
        "sound_on": False,
        "prints": True,
        "allow_key_presses": False
    }

    # Instantiate an instance of FuzzyAsteroidGame
    game = TrainerEnvironment(settings=settings)

    score = game.run(controller=FuzzyController())
    print(score)
