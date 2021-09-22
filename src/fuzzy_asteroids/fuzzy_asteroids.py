"""
Asteroid Smasher Game

Shoot space rocks in this demo program created with
Python and the Arcade library.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.asteroid_smasher
"""
import math
import arcade
import time
import statistics
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import contextmanager
from typing import List, Any, Tuple, Dict

from .game import AsteroidGame, ShipSprite, Score, Scenario, StoppingCondition
from .fuzzy_controller import SpaceShip, ControllerBase
from .settings import *


class FuzzyAsteroidGame(AsteroidGame):
    """
    Modified version of the Asteroid Smasher game which accepts a Fuzzy Controller
    """
    def __init__(self, settings: Dict[str, Any] = None, track_compute_cost: bool = False, controller_timeout: bool = True,
                 ignore_exceptions: bool = False):
        """
        Create a an FuzzyAsteroidGame environment which extends AsteroidGame, but
        enables a user-defined controller class (which is passed via ``start_new_game()``)

        This constructor also changes the user-defined settings to be better suited for autonomous fuzzy controller,
        by overriding the "allow_key_presses" key to False.

        :param settings: Dictionary of settings which are passed to the parent constructor (with modification)
        :param track_compute_cost: Whether to track the evaluation costs
        :param controller_timeout: Whether to timeout the controller if evaluation takes too long
        :param ignore_exceptions: True allows the program to ignore exceptions, False means exceptions exit the program
        """
        self.controller = None

        # Check and modify settings
        _settings = settings if settings else dict()

        # Turn off key presses to ensure the controller is doing what it should
        _settings.update({"allow_key_presses": False})

        # Call constructor of AsteroidGame to set up the environment
        super().__init__(settings=_settings)

        # Used to track time elapsed for checking computational performance of the controller
        self.track_eval_time = track_compute_cost
        self.controller_timeout = controller_timeout
        self.ignore_exceptions = ignore_exceptions
        self.time_elapsed = 0
        self.evaluation_times = []
        self.num_asteroids = []
        self.total_controller_evaluation_time = 0

        # used for graphics traccking
        self.timed_out = False
        self.exceptioned_out = False

        # Create threadpool executor to run tasks in, we have access to 2 threadpools which should allow enough overhead
        # for evaluation times ~2 times operating frequency
        self.executor = ThreadPoolExecutor(4)
        self.loop = asyncio.get_event_loop()

    @property
    def data(self) -> Dict[str, Any]:
        # Getting data via this "getter" method will be read-only and un-assignable
        return {
            "frame": int(self.score.frame_count),
            "time": int(self.score.time),
            "stopping_condition": self.score.stopping_condition,
            "map_dimensions": tuple(self.get_size()),
            "asteroids": tuple(sprite.state for sprite in self.asteroid_list),
            "bullets": tuple(sprite.state for sprite in self.asteroid_list),
        }

    def start_new_game(self, controller: ControllerBase = None, scenario: Scenario = None, score: Score = None) -> None:
        """
        Set up the environment for a new game, storing the given arguments which configure how this game will run

        :param controller: object that is subclass of ControllerBase
        :param scenario: optional Scenario
        :param score: optional Score (should inherit from ``Score``)
        """
        # Store controller
        self.controller = controller

        # Check to see if user has given the fuzzy asteroid game a valid controller
        if not controller:
            raise ValueError("No controller object given to the FuzzyAsteroid() constructor")
        elif not isinstance(controller, ControllerBase):
            raise TypeError(f"Controller object given to {self.__class__}.start_new_game() must be a sub class"
                            f"of type ControllerBase.")
        elif not hasattr(self.controller, "actions"):
            raise TypeError("Controller class given to FuzzyAsteroidGame doesn't have a method called"
                            "``actions()`` which is used to control the Ship")

        # Call start new game
        AsteroidGame.start_new_game(self, scenario=scenario, score=score)

    @asyncio.coroutine
    def coro(self, loop, ship):
        # Run the controller actions in an thread pool executor as an async coroutine
        # This allows the controller to be timed out and the environment to proceed with no inputs
        yield from loop.run_in_executor(self.executor, self.controller.actions, ship, self.data)

    def call_stored_controller(self) -> None:
        """
        Call the stored controller (if it exists)
        """
        if self.controller:
            # Build list of controllable ships
            ships = tuple(SpaceShip(ship_sprite) for ship_sprite in self.player_sprite_list)

            # Within the timer_interface context manager (optional time measurement), run the controller
            # If the controller exceeds the loop time, then there will be control dropout with some minor slowdowns due
            # to not taking the environment processing loop into account
            # This prevents major slowdowns and encourages better algorithm design.
            with self.timer_interface():
                if self.controller_timeout:
                    self.loop.run_until_complete(asyncio.wait_for(self.coro(self.loop, ships),
                                                                  timeout=(1.0 / self.frequency)))
                else:
                    self.controller.actions(ships, self.data)

            # Convert the commands from the controller back to the environment
            for idx, ship in enumerate(ships):
                # Take controller actions and send them back to the environment
                self.player_sprite_list[idx].turn_rate = float(ship.turn_rate) if ship.turn_rate is not None else self.player_sprite_list[idx].turn_rate
                self.player_sprite_list[idx].thrust = float(ship.thrust) if ship.thrust is not None else self.player_sprite_list[idx].thrust

                # Fire bullet if the user has ordered the ship to shoot
                if bool(ship.fire_bullet) and ship.fire_bullet is not None:
                    self.fire_bullet(self.player_sprite_list[idx])

    def draw_extra(self):
        meter_x = self.get_size()[0] - 50
        y_top = 200

        if self.controller_name:
            output = f"Controller: {self.controller_name}"
            arcade.draw_text(output, 10, self.map.height - 45, WHITE_COLOR, FONT_SIZE2)

        # Draw that an exception was triggered
        if self.exceptioned_out:
            red_fill = (255, 50, 50, 150)
            arcade.draw_rectangle_filled(center_x=meter_x - 40, center_y=y_top+10, width=60 + 100, height=30, color=red_fill)
            arcade.draw_text(f"Controller Exception", meter_x - 40, y_top + 10,
                             WHITE_COLOR, FONT_SIZE2, anchor_x="center", anchor_y="center")

        # Draw the eval timer
        if self.track_eval_time:
            # Draw a red background if the eval time dictated by the environment clock is exceeded by the controller
            orange_fill = (255, 150, 50, 150 if self.timed_out else 0)
            arcade.draw_rectangle_filled(center_x=meter_x - 40, center_y=y_top+40, width=60 + 100, height=30, color=orange_fill)

            # Draw the eval time live
            arcade.draw_text(f"Eval Time:{'':4}{float(1E3) * self.time_elapsed:3.3f} ms", meter_x - 40, y_top + 40,
                             WHITE_COLOR, FONT_SIZE2, anchor_x="center", anchor_y="center")

    def on_update(self, delta_time: float = 1/60) -> None:
        if not self.active_key_presses and self.game_over == StoppingCondition.none:
            self.call_stored_controller()

        # Call on_update() of AsteroidGame parent
        AsteroidGame.on_update(self, delta_time)

        # If the game is over add the information pertaining to the controller
        # computation performance
        if self.game_over != StoppingCondition.none and self.track_eval_time:
            self.score.num_asteroids = self.num_asteroids.copy()
            self.score.evaluation_times = self.evaluation_times.copy()
            self.score.mean_eval_time = statistics.mean(self.evaluation_times)
            self.score.median_eval_time = statistics.median(self.evaluation_times)
            self.score.min_eval_time = min(self.evaluation_times)
            self.score.max_eval_time = max(self.evaluation_times)

            self.num_asteroids.clear()
            self.evaluation_times.clear()

    @contextmanager
    def timer_interface(self):
        """
        Use the function to wrap code within a timer interface (for performance debugging)

        You can also use your favorite IDE's profiling tools to accomplish the same thing.
        """
        t0 = time.perf_counter()
        self.timed_out = False
        self.exceptioned_out = False

        # If time tracking is not desired, simply yield the context and skip time measurement
        if not self.track_eval_time:
            yield

        else:
            try:
                yield

            except asyncio.TimeoutError as e:
                # If there was a timeout, track it and move on
                self.timed_out = True
                self.score.timeouts += 1

            except BaseException as e:
                # Track anything exceptions that extend the BaseException
                if self.ignore_exceptions:
                    self.exceptioned_out = True
                    self.score.exceptions += 1
                else:
                    raise e

            finally:
                # At this point, always log the time
                t1 = time.perf_counter()
                self.time_elapsed = t1 - t0

                # Store the evaluation time
                self.num_asteroids.append(len(self.asteroid_list))
                self.evaluation_times.append(self.time_elapsed)


class TrainerEnvironment(FuzzyAsteroidGame):
    def __init__(self, settings: Dict[str, Any] = None, track_compute_cost: bool = False,
                 controller_timeout: bool = False, ignore_exceptions: bool = False):
        """
        The TrainerEnvironment class extends behaviors built into FuzzyAsteroidGame, with simplifications focused
        on making it easier to perform training.

        This overrides settings options to guarantee the best possible training behavior.
        :param settings: Settings dictionary passed to parent class
        :param track_compute_cost: Whether to track the evaluation costs
        :param controller_timeout: Whether to timeout the controller if evaluation takes too long
        :param ignore_exceptions: True allows the program to ignore exceptions, False means exceptions exit the program
        """
        _settings = dict(settings) if settings else dict()

        # Override with desired settings for training
        _settings.update({
            "sound_on": False,
            "graphics_on": False,
            "real_time_multiplier": 0,
            "prints": False,
            "allow_key_presses": False,
            "full_dashboard": True,
        })

        # Call constructor of FuzzyAsteroidGame
        super().__init__(settings=_settings,
                         track_compute_cost=track_compute_cost,
                         controller_timeout=controller_timeout,
                         ignore_exceptions=ignore_exceptions)

    def on_key_press(self, symbol, modifiers) -> None:
        """Turned off during training"""
        pass

    def on_key_release(self, symbol, modifiers) -> None:
        """Turned off during training"""
        pass
