"""
Asteroid Smasher Game

Shoot space rocks in this demo program created with
Python and the Arcade library.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.asteroid_smasher
"""
import arcade
import time
from contextlib import contextmanager
from typing import List, Any, Tuple, Dict

from .game import AsteroidGame, ShipSprite, Score, Scenario
from .fuzzy_controller import SpaceShip, ControllerBase


class FuzzyAsteroidGame(AsteroidGame):
    """
    Modified version of the Asteroid Smasher game which accepts a Fuzzy Controller
    """
    def __init__(self, settings: Dict[str, Any] = None):
        self.controller = None

        # Check and modify settings
        _settings = settings if settings else dict()

        # Turn off key presses to ensure the controller is doing what it should
        _settings.update({"allow_key_presses": False})

        # Call constructor of AsteroidGame to set up the environment
        super().__init__(settings=settings)

        # Used to track time elapsed for checking computational performance of the controller
        self.time_elapsed = 0

    @property
    def data(self) -> Dict[str, Tuple]:
        # Getting data via this "getter" method will be read-only and un-assignable
        return {
            "frame": int(self.score.frame_count),
            "map_dimensions": tuple(self.get_size()),
            "asteroids": tuple(sprite.state for sprite in self.asteroid_list),
            "bullets": tuple(sprite.state for sprite in self.asteroid_list),
        }

    def start_new_game(self, controller: ControllerBase=None, scenario: Scenario=None, score: Score=None) -> None:
        """

        :param controller: object that is subclass of ControllerBase
        :param scenario: optional Scenario
        :param score: optional Score (should inherit from ``Score``)
        """
        # Store controller
        self.controller = controller

        # Check to see if user has given the fuzzy asteroid game a valid controller
        if not controller:
            raise ValueError("No controller object given to the FuzzyAsteroid() constructor")
        elif not hasattr(self.controller, "actions"):
            raise TypeError("Controller class given to FuzzyAsteroidGame doesn't have a method called"
                            "``actions()`` which is used to control the Ship")

        # Call start new game
        AsteroidGame.start_new_game(self, scenario=scenario, score=score)

    def call_stored_controller(self) -> None:
        """
        Call the stored controller (if it exists)
        """
        if self.controller:
            # Use the space ship class as an intermediary between the user and the environment
            # to limit cheating/abuse of the environment
            ship = SpaceShip(self.player_sprite)

            # Use the defined controller
            self.controller.actions(ship, self.data)

            # Take controller actions and send them back to the environment
            self.player_sprite.turn_rate = float(ship.turn_rate)
            self.player_sprite.thrust = float(ship.thrust)

            # Fire bullet if the user has ordered the ship to shoot
            if bool(ship.fire_bullet):
                self.fire_bullet()

    def on_update(self, delta_time: float=1/60) -> None:
        if not self.active_key_presses:
            self.call_stored_controller()

        # Call on_update() of AsteroidGame parent
        AsteroidGame.on_update(self, delta_time)

    @contextmanager
    def _timer_interface(self):
        """
        Use the function to wrap code within a timer interface (for performance debugging)

        You can also use your favorite IDE's profiling tools to accomplish the same thing.
        """
        t0 = time.perf_counter()

        try:
            yield
        except Exception as e:
            # Handle exceptions raised
            print(e, " ignored in ", self.controller.__class__, "actions() function evaluation")
        finally:
            t1 = time.perf_counter()
            self.time_elapsed = t1 - t0 / float(1E6)
            print("Time to evaluate", __class__, "actions() function", (t1 - t0) * float(1E6), "micro seconds")

    @contextmanager
    def evaluation_manager(self):
        yield self

    def evaluate_complexity(self):
        pass


class TrainerEnvironment(FuzzyAsteroidGame):
    def __init__(self, settings: Dict[str, Any] = None):
        _settings = dict(settings) if settings else dict()

        # Override with desired settings for training
        _settings.update({
            "sound_on": False,
            "graphics_on": False,
            "real_time_multiplier": 0,
            "prints": False,
            "allow_key_presses": False
        })

        # Call constructor of FuzzyAsteroidGame
        super().__init__(settings=_settings)

    def on_key_press(self, symbol, modifiers) -> None:
        """Turned off during training"""
        pass

    def on_key_release(self, symbol, modifiers) -> None:
        """Turned off during training"""
        pass

    def on_draw(self) -> None:
        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw message reminding the
        output = f"Running in Training Mode"
        arcade.draw_text(output, start_x=self.get_size()[0]/2.0, start_y=self.get_size()[1]/2.0,
                         color=arcade.color.WHITE, font_size=16, align="center", anchor_x="center")
