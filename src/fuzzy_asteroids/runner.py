import os
import json
from typing import List, Tuple, Dict, Any

import arcade

from .fuzzy_asteroids import AsteroidGame, FuzzyAsteroidGame
from .util import Scenario, Score
from .fuzzy_controller import ControllerBase

from enum import Enum


class Mode(Enum):
    HUMAN = 0
    CONTROLLER_VISIBLE = 1
    CONTROLLER_HIDDEN = 2


class CompetitionScore(Score):
    def __init__(self):
        super().__init__()

        self._last_num_deaths = 0

        self.death_times = []
        self.accuracy_over_time = []
        self.asteroids_over_time = []

    def timestep_update(self, environment) -> None:
        # Call parent score class update
        super().timestep_update(environment)


        if self.deaths != self._last_num_deaths:
            self._last_num_deaths = self.deaths
            self.death_times.append(self.time)

        self.accuracy_over_time.append(self.accuracy)
        self.asteroids_over_time.append(self.asteroids_hit)

    def final_update(self, environment) -> None:
        super().final_update(environment)

    def header(self) -> List:
        return list(key for key in self.__dict__.keys())

    def row(self) -> List:
        return list(self.__dict__[key] for key in self.header())


class ScenarioRunner:
    """
    `ScenarioRunner` is meant to be used to run all controllers through a specified portfolio
    against a common scoring function, and save the results
    """
    def __init__(self, controller_build_fcns: Dict[str, Any] = None, portfolio: List[Scenario] = None):
        # Portfolio to loop through
        self.portfolio = portfolio

        self.game = None

        # What directory to save the runner information in
        self.directory = os.path.abspath(os.path.curdir)

        # Settings for running the environments in different scenarios
        self.hidden_settings = {"real_time_multiplier": 0, "graphics_on": False, "prints": False}
        self.visible_settings = {"real_time_multiplier": 1, "graphics_on": True, "prints": True}

        if controller_build_fcns:
            self.builder_fcns = controller_build_fcns
            self.scores = {key: None for key in controller_build_fcns.keys()}
            self.data = {key: None for key in controller_build_fcns.keys()}

    def save_file(self, file_name: str, data: Dict[str, Any]) -> None:
        with open(os.path.join(self.directory, file_name), "w") as file:
            json.dump(data, file, indent=2)

    def load_file(self, file_name: str) -> Dict[str, Any]:
        with open(os.path.join(self.directory, file_name), "r") as file:
            data = json.load(file)
        return data

    def run_human(self, name: str = "Human", score: Score = None) -> Dict[str, Dict]:
        settings = {"real_time_multiplier": 1, "graphics_on": True, "prints": False}
        game = self.create_environment(settings, human_test=True)
        scores = self._run_all_scenarios(game, None, self.portfolio, score)
        return {name: scores}

    def run_all_controllers(self, score: Score = None, graphics_on: bool = True,
                            opt_settings: Dict = None) -> Dict[str, Dict]:
        all_data = {}

        # Run each controller over the whole portfolio
        for key, controller in self.builder_fcns.items():
            data = self.run_one_controller(controller=controller,
                                           score=score,
                                           graphics_on=graphics_on,
                                           opt_settings=opt_settings)

            all_data.update(**data)
        return all_data

    def run_one_controller(self, controller: ControllerBase, score: Score=None, graphics_on: bool = True,
                           opt_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        settings = self.visible_settings if graphics_on else self.hidden_settings
        settings.update(opt_settings if opt_settings else {})

        # Create environment only if one has not been created already
        self.game = self.create_environment(settings) if not self.game else self.game

        scores = self._run_all_scenarios(self.game, controller, self.portfolio, score)
        return {controller.name: scores}

    @staticmethod
    def create_environment(settings: Dict[str, Any], human_test: bool = False) -> AsteroidGame:
        """
        Static function for creating an Environment, based on user input
        :param settings: Settings dictionary that is given directly to the environment
        :param human_test: Whether this environment is used for human performance evaluation
        :return: game environment (one of `AsteroidGame`, `FuzzyAsteroidGame`)
        """
        if human_test:
            return AsteroidGame(settings=settings)
        else:
            return FuzzyAsteroidGame(settings=settings,
                                     track_compute_cost=True,
                                     ignore_exceptions=True,
                                     controller_timeout=True)

    @classmethod
    def _run_all_scenarios(cls, game: AsteroidGame, controller: ControllerBase,
                           portfolio: List[Scenario], score: Score = None) -> Any:
        data = {}

        if not game.graphics_on:
            print(f"{controller.name} ", end="")

        for scenario in portfolio:
            score = cls._run_one_scenario(game, controller=controller, scenario=scenario, score=score)

            # Print dots for monitoring evaluation in headless more
            if not game.graphics_on:
                print(".", end="" if scenario is not portfolio[-1] else "\n")

            data[scenario.name] = score.__dict__

        return data

    @classmethod
    def _run_one_scenario(cls, game: AsteroidGame, controller: ControllerBase, scenario: Scenario, score: Score) -> Score:
        """
        Function runs a game with the competition score class
        :param game: Game instance
        :param controller: ControllerBase instance
        :param scenario: Scenario object to run over
        :param score: Score object
        :return: Score object result
        """
        return game.run(controller=controller, scenario=scenario, score=score if score else CompetitionScore())


