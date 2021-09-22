"""
Asteroid Smasher

Shoot space rocks in this demo program created with
Python and the Arcade library.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.asteroids
"""
import random
from typing import Any, Dict, List, Tuple

from .sprites import AsteroidSprite, ShipSprite
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Score:
    """
    Class which is used to keep track of various scoring metrics

    This class can be inherited to create custom subclasses for extending the Scoring behavior, useful
    for competitors to create their own scoring metrics. If you inherit this class make sure to override the
    following methods
    *  timestep_update()
    *  final_update()
    """

    def __init__(self):
        """
        Default constructor requires no arguments as all values are initialized to default values, which
        are modified by the game environment over the span of each game
        """
        self.asteroids_hit = 0
        self.bullets_fired = 0
        self.distance_travelled = 0
        self.deaths = 0

        # Maximum values (used for normalizing)
        self.max_asteroids = 0
        self.max_distance = 0

        # The amount of time steps the score has been counted for
        self.frame_count = 0
        self.time = 0

        # Stopping condition
        self.stopping_condition = 0

        # For tracking controller performance
        self.timeouts = 0
        self.exceptions = 0
        self.mean_eval_time = 0
        self.median_eval_time = 0
        self.min_eval_time = 0
        self.max_eval_time = 0
        self.evaluation_times = []
        self.num_asteroids = []

    def __repr__(self):
        return str(self.__dict__)

    @property
    def accuracy(self) -> float:
        return 0.0 if not self.bullets_fired else self.asteroids_hit / self.bullets_fired

    @property
    def fraction_total_asteroids_hit(self):
        return 0.0 if not self.asteroids_hit else self.asteroids_hit / self.max_asteroids

    @property
    def fraction_distance_travelled(self):
        return 0.0 if not self.max_distance else self.distance_travelled / self.max_distance

    def timestep_update(self, environment) -> None:
        """
        Function that is called at the end of each time step.

        User can override this function to add/update scoring parameters which should be updated
        at the end of each time step

        :param environment: Environment object
        """
        pass

    def final_update(self, environment) -> None:
        """
        Function that is called at the end of each game (when game over).

        User can override this function to add/update scoring parameters which should be updated
        at the end of a game

        :param environment: Environment object
        """
        pass


class Map:
    """
    Class to be used to customize the game map
    """

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        """
        Class for specifying the Map dimensions (visible + otherwise)

        :param width: Width in pixels of the visible map
        :param height: Height in pixels of the visible map
        """
        self.width = width if width else Map.default_width()
        self.height = height if width else Map.default_height()

        # Set limits of the map (outside of the visible window)
        self.LEFT_LIMIT = 0
        self.RIGHT_LIMIT = self.width
        self.BOTTOM_LIMIT = 0
        self.TOP_LIMIT = self.height

    @property
    def center(self) -> Tuple[float, float]:
        return self.width / 2.0, self.height / 2.0

    @staticmethod
    def default_width() -> float:
        return SCREEN_WIDTH

    @staticmethod
    def default_height() -> float:
        return SCREEN_HEIGHT

    @staticmethod
    def default_dimensions() -> Tuple[float, float]:
        return Map.default_width(), Map.default_height()

    @staticmethod
    def default_map_center() -> Tuple[float, float]:
        dims = Map.default_dimensions()
        return dims[0] / 2.0, dims[1] / 2.0


class Scenario:
    def __init__(self, name: str = "Unnamed", num_asteroids: int = 0, asteroid_states: List[Dict[str, Any]] = None,
                 ship_states: List[Dict[str, Any]] = None, game_map: Map = None, seed: int = None,
                 time_limit: float = float("inf")):
        """
        Specify the starting state of the environment, including map dimensions and optional features

        Make sure to only set either ``num_asteroids`` or ``asteroid_states``. If neither are set, the
        Scenario defaults to 3 randomly placed asteroids

        :param name: Optional, name of the scenario
        :param num_asteroids: Optional, Number of asteroids
        :param asteroid_states: Optional, Asteroid Starting states
        :param ship_states: Optional, Ship Starting states (list of dictionaries)
        :param game_map: Game Map using ``Map`` object
        :param seed: Optional seeding value to pass to random.seed() which is called before asteroid creation
        :param time_limit: Optional seeding value to pass to random.seed() which is called before asteroid creation
        """
        self.name = name

        # Store Map
        self.game_map = game_map if game_map else Map()

        # Store ship states if not None, otherwise, create one ship at center
        self.ship_states = ship_states if ship_states else [{"position": self.game_map.center}]

        # Set the time_limit to infinity if it is 0 or None
        self.time_limit = time_limit

        # Store random seed
        self.seed = seed

        # Will be built later
        self.asteroid_states = list()

        # Check for mismatch between explicitly defined number of asteroids and Tuple of states
        if num_asteroids and asteroid_states:
            raise ValueError("Both `num_asteroids` and `asteroid_positions` are specified for Scenario() constructor."
                             "Make sure to only define one of these arguments")

        # Store asteroid states
        elif asteroid_states:
            self.asteroid_states = asteroid_states
        elif num_asteroids:
            self.asteroid_states = [dict() for _ in range(num_asteroids)]
        else:
            raise (ValueError("User should define `num_asteroids` or `asteroid_states` to create "
                              "valid custom starting states for the environment"))

    @property
    def num_starting_asteroids(self) -> float:
        return len(self.asteroid_states)

    @property
    def is_random(self) -> bool:
        return not all(state for state in self.asteroid_states) if self.asteroid_states else True

    @property
    def max_asteroids(self) -> int:
        return sum([Scenario.count_asteroids(asteroid.size) for asteroid in self.asteroids(60)])

    @staticmethod
    def count_asteroids(asteroid_size) -> float:
        # Counting based off of each asteroid making 3 children when destroyed
        return sum([3 ** (size - 1) for size in range(1, asteroid_size + 1)])

    def asteroids(self, frequency: float) -> List[AsteroidSprite]:
        """
        Create asteroid sprites
        :param frequency: Operating frequency of the game
        :return: List of ShipSprites
        """
        asteroids = list()

        # Seed the random number generator via an optionally defined user seed
        if self.seed is not None:
            random.seed(self.seed)

        # Loop through and create AsteroidSprites based on starting state
        for asteroid_state in self.asteroid_states:
            if asteroid_state:
                asteroids.append(AsteroidSprite(frequency, **asteroid_state))
            else:
                asteroids.append(
                    AsteroidSprite(frequency,
                                   position=(
                                       random.randrange(self.game_map.LEFT_LIMIT, self.game_map.RIGHT_LIMIT),
                                       random.randrange(self.game_map.BOTTOM_LIMIT, self.game_map.TOP_LIMIT)),
                                   ))

        return asteroids

    def ships(self, frequency: float) -> List[ShipSprite]:
        """
        Create ship sprites
        :param frequency: Operating frequency of the game
        :return: List of ShipSprites
        """
        # Loop through and create ShipSprites based on starting state
        return [ShipSprite(idx+1, frequency, **ship_state) for idx, ship_state in enumerate(self.ship_states)]
