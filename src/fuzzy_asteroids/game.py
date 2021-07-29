"""
Asteroid Smasher

Shoot space rocks in this demo program created with
Python and the Arcade library.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.asteroids
"""
import pyglet
import arcade
import os
import time
import math
from typing import cast, Dict, Tuple, List, Any
from enum import Enum

from .sprites import AsteroidSprite, BulletSprite, ShipSprite
from .settings import *
from .util import Score, Scenario


# Stopping conditions for the Environment to communicate what the termination condition was
class StoppingCondition(str, Enum):
    none = "None"
    no_asteroids = "No Asteroids"
    no_lives = "No Lives"
    no_time = "No Time"


class AsteroidGame(arcade.Window):
    """
    Main application class.

    Based on Asteroid Smasher Example provided in arcade.examples/asteroids

    Shoot space rocks in this demo program created with
    Python and the Arcade library.

    Artwork from http://kenney.nl
    """
    def __init__(self, settings: Dict[str, Any] = None):
        _settings = settings if settings else dict()

        # Game starting state definition (map, asteroids)
        self.scenario = None

        # Store game settings
        self.frequency = _settings.get("frequency", 60)  # Hz
        self.real_time_multiplier = _settings.get("real_time_multiplier", 1)
        self.sound_on = _settings.get("sound_on", False)  # Whether sounds should play
        self.graphics_on = _settings.get("graphics_on", True)  # Whether graphics should be on
        self.time_limit = _settings.get("time_limit", 0)  # Number of starting lives
        self.lives = _settings.get("lives", 3)  # Number of starting lives
        self.prints = _settings.get("prints", True)
        self.allow_key_presses = _settings.get("allow_key_presses", True)
        self.number_of_ships = _settings.get("number_of_ships", 1)

        # Set the timestep to dictate the update rate for the environment
        if self.real_time_multiplier:
            self.timestep = (1 / float(self.frequency)) / float(self.real_time_multiplier)
        else:
            self.timestep = float(1E-9)

        # Set the time_limit to infinity if it is 0 or None
        self.time_limit = float("inf") if not self.time_limit else self.time_limit

        super().__init__(width=SCREEN_WIDTH,
                         height=SCREEN_HEIGHT,
                         title=SCREEN_TITLE, update_rate=self.timestep, visible=self.graphics_on)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        self.directory = os.path.dirname(os.path.abspath(__file__))

        # Sprite lists
        self.player_sprite_list = None
        self.asteroid_list = None
        self.bullet_list = None
        self.ship_life_list = None

        # Set up the game instance
        self.game_over = None
        self.player_sprite = None
        self.text_sprite_list = None

        # Evaluation analytics
        self.score = None

        # Track active keys (from eligible controls)
        self.available_keys = (arcade.key.SPACE, arcade.key.LEFT, arcade.key.RIGHT, arcade.key.UP, arcade.key.DOWN)
        self.active_key_presses = list()

        # Register sounds within the game
        self.laser_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound1 = arcade.load_sound(":resources:sounds/explosion1.wav")
        self.hit_sound2 = arcade.load_sound(":resources:sounds/explosion2.wav")
        self.hit_sound3 = arcade.load_sound(":resources:sounds/hit1.wav")
        self.hit_sound4 = arcade.load_sound(":resources:sounds/hit2.wav")

    def _play_sound(self, sound):
        # Private sound playing function (checks stored sound_on) using globally specified volume
        if self.sound_on:
            sound.play(VOLUME)

    def _print_terminal(self, msg: str):
        if self.prints:
            print(msg)

    @property
    def color_text(self):
        return arcade.color.WHITE

    @property
    def color_lines(self):
        return ()

    @property
    def color_fill(self):
        return ()

    def start_new_game(self, scenario: Scenario = None, score: Score = None, **kwargs) -> None:
        """
        Start a new game within the current environment

        :param scenario: optional, Scenario object (includes asteroid starting states and Map)
        :param score: optional Score (should inherit from ``Score``
        """
        if not isinstance(scenario, Scenario) and scenario is not None:
            raise TypeError("scenario argument given to start_new_game() must be a subclass of fuzzy_asteroids.util.Scenario")

        if not isinstance(score, Score) and score is not None:
            raise TypeError("score argument given to start_new_game() must be a subclass of fuzzy_asteroids.util.Score")

        # Store scenario (if it exists, otherwise use default)
        self.scenario = scenario if scenario else Scenario(num_asteroids=3)

        # Instantiate blank score (from optional user-defined score)
        self.score = score if score else Score()

        # Update score parameter
        self.score.max_asteroids = self.scenario.max_asteroids

        # Set trackers used for game over checks
        self.game_over = StoppingCondition.none

        # Sprite lists
        self.player_sprite_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        # Set up the players
        self.player_sprite_list.extend(self.scenario.ships(self.frequency))


        # Information dashboard
        self.text_sprite_list = arcade.SpriteList()

        # Set up the little icons that represent the player lives.
        if self.graphics_on:
            self.text_sprite_list.append(arcade.draw_text("Lives", SCREEN_WIDTH / 2.0, 50, self.color_text, 13, anchor_x="center", align="center"))

            cur_pos = SCREEN_WIDTH / 2.0 - 33 * self.scenario.ship_lives/ 1.5
            for i in range(self.scenario.ship_lives):
                life = arcade.Sprite(":resources:images/space_shooter/playerLife1_orange.png", SCALE*2.0)
                life.alpha = 150
                life.center_x = cur_pos + life.width
                life.center_y = life.height + 5
                cur_pos += life.width
                self.ship_life_list.append(life)

        # Get the asteroids from the Scenario (which builds them based on the Scenario settings)
        self.asteroid_list.extend(self.scenario.asteroids(self.frequency))

        # This will resize the window if the dimensions are different from global
        # This behavior is not tested well
        if self.scenario.game_map.default_dimensions != (SCREEN_WIDTH, SCREEN_HEIGHT):
            self.set_size(self.scenario.game_map.width, self.scenario.game_map.height)

    def on_draw(self) -> None:
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.asteroid_list.draw()
        self.ship_life_list.draw()
        self.bullet_list.draw()
        self.player_sprite_list.draw()
        self.text_sprite_list.draw()

        if self.scenario.name:
            output = f"Scenario: {self.scenario.name}"
            arcade.draw_text(output, 10, SCREEN_HEIGHT - 25, self.color_text, 13)

        # if self.controller_name:
        #     output = f"Controller: {self.controller_name}"
        #     arcade.draw_text(output, 10, SCREEN_HEIGHT - 45, self.color_text, 13)

        # Put the text on the screen.
        output = f"Time Limit: {self.time_limit if not self.time_limit == float('inf') else None}"
        arcade.draw_text(output, 10, 110, self.color_text, 13)

        output = f"Time: {self.score.time:.1f}"
        arcade.draw_text(output, 10, 90, self.color_text, 13)

        output = f"Score: {self.score.asteroids_hit}"
        arcade.draw_text(output, 10, 70, self.color_text, 13)

        output = f"Bullets Fired: {self.score.bullets_fired}"
        arcade.draw_text(output, 10, 50, self.color_text, 13)

        output = f"Accuracy (%): {int(100.0 * self.score.accuracy)}"
        arcade.draw_text(output, 10, 30, self.color_text, 13)

        output = f"Asteroid Count: {len(self.asteroid_list)}"
        arcade.draw_text(output, 10, 10, self.color_text, 13)

        # Throttle and Turning Rate Info
        color_lines = (255, 255, 255)
        color_fill = (150, 150, 255, 150)
        meter_x = SCREEN_WIDTH - 50
        # This is just viewing pleasure, so for now it is just for ship 1
        # TODO: does this need fixing
        thrust = self.player_sprite_list[0].thrust
        norm_thrust = thrust / max(self.player_sprite_list[0].thrust_range)
        arcade.draw_text(f"Throttle\n{thrust:.1f}", meter_x - 80, 70, self.color_text, 13, anchor_x="center", anchor_y="center", align="right")
        arcade.draw_line(start_x=meter_x, end_x=meter_x, start_y=50, end_y=90, color=color_lines)
        arcade.draw_rectangle_outline(center_x=meter_x, center_y=70, width=80, height=30, color=color_lines)
        arcade.draw_rectangle_filled(center_x=meter_x + (20 * norm_thrust), center_y=70, width=40*math.fabs(norm_thrust), height=30-2, color=color_fill)

        turn_rate = self.player_sprite_list[0].turn_rate # TODO: does this need fixing
        norm_turn_rate = turn_rate / max(self.player_sprite_list[0].turn_rate_range)
        arcade.draw_text(f"Turn Rate\n{turn_rate:.1f}", meter_x - 80, 30, self.color_text, 13, anchor_x="center", anchor_y="center", align="right")
        arcade.draw_line(start_x=meter_x, end_x=meter_x, start_y=10, end_y=50, color=color_lines)
        arcade.draw_rectangle_outline(center_x=meter_x, center_y=30, width=80, height=30, color=color_lines)
        arcade.draw_rectangle_filled(center_x=meter_x + (20 * norm_turn_rate), center_y=30, width=40*math.fabs(norm_turn_rate), height=30-2, color=color_fill)

    def fire_bullet(self) -> None:
        """Call to fire a bullet"""

        # Check to see if the ship is allowed to fire based on its built in rate limiter
        if self.player_sprite.can_fire:
            self.score.bullets_fired += 1

            # Skip past the respawning timer
            self.player_sprite._respawning = 0

            self.bullet_list.append(self.player_sprite.fire_bullet())
            self._play_sound(self.laser_sound)

    def on_key_press(self, symbol, modifiers) -> None:
        """ Called whenever a key is pressed. """
        if self.allow_key_presses:
            # Track active keys
            if symbol in self.available_keys:
                self.active_key_presses.append(symbol)

            # Shoot if the player hit the space bar and we aren't respawning.
            if symbol == arcade.key.SPACE:
                self.fire_bullet()

            if symbol == arcade.key.LEFT:
                self.player_sprite.turn_rate = self.player_sprite.turn_rate_range[1]
            elif symbol == arcade.key.RIGHT:
                self.player_sprite.turn_rate = self.player_sprite.turn_rate_range[0]

            if symbol == arcade.key.UP:
                self.player_sprite.thrust = self.player_sprite.thrust_range[1]
            elif symbol == arcade.key.DOWN:
                self.player_sprite.thrust = self.player_sprite.thrust_range[0]

    def on_key_release(self, symbol, modifiers) -> None:
        """ Called whenever a key is released. """
        if self.allow_key_presses:

            # Remove released key from active keys list
            if symbol in self.available_keys:
                self.active_key_presses.pop(self.active_key_presses.index(symbol))

            if symbol == arcade.key.LEFT and arcade.key.RIGHT not in self.active_key_presses:
                self.player_sprite.turn_rate = 0
            elif symbol == arcade.key.RIGHT and arcade.key.LEFT not in self.active_key_presses:
                self.player_sprite.turn_rate = 0
            elif symbol == arcade.key.UP and arcade.key.DOWN not in self.active_key_presses:
                self.player_sprite.thrust = 0
            elif symbol == arcade.key.DOWN and arcade.key.UP not in self.active_key_presses:
                self.player_sprite.thrust = 0

    def split_asteroid(self, asteroid: AsteroidSprite) -> None:
        """ Split an asteroid into chunks. """
        # Add to score
        self.score.asteroids_hit += 1

        if asteroid.size == 4:
            self.asteroid_list.extend([AsteroidSprite(frequency=self.frequency, position=asteroid.position, size=asteroid.size-1) for i in range(3)])
            self._play_sound(self.hit_sound1)

        elif asteroid.size == 3:
            self.asteroid_list.extend([AsteroidSprite(frequency=self.frequency, position=asteroid.position, size=asteroid.size-1) for i in range(3)])
            self._play_sound(self.hit_sound2)

        elif asteroid.size == 2:
            self.asteroid_list.extend([AsteroidSprite(frequency=self.frequency, position=asteroid.position, size=asteroid.size-1) for i in range(3)])
            self._play_sound(self.hit_sound3)

        elif asteroid.size == 1:
            self._play_sound(self.hit_sound4)

        # Remove asteroid from sprites
        asteroid.remove_from_sprite_lists()

    def on_update(self, delta_time: float = 1/60) -> None:
        """
        Move everything

        :param delta_time: Time since last time step
        """
        # Check to see if there any asteroids/time left
        if len(self.asteroid_list) == 0:
            self.game_over = StoppingCondition.no_asteroids
        elif self.score.time >= self.time_limit:
            self.game_over = StoppingCondition.no_time
        else:
            # If there are no stopping conditions, update the time/frame count
            self.score.frame_count += 1
            self.score.time = self.score.frame_count / float(self.frequency)

        # Check if the game is over
        if self.game_over == StoppingCondition.none:
            # Update all sprites
            self.asteroid_list.on_update(delta_time)
            self.bullet_list.on_update(delta_time)
            self.player_sprite_list.on_update(delta_time)

            # Check for collisions between bullets and asteroids
            for bullet in self.bullet_list:
                asteroids = arcade.check_for_collision_with_list(bullet, self.asteroid_list)

                # Break up and remove asteroids if there are bullet-asteroid collisions
                for asteroid in asteroids:
                    self.split_asteroid(cast(AsteroidSprite, asteroid))  # expected AsteroidSprite, got Sprite instead
                    bullet.remove_from_sprite_lists()

            # Perform checks on the player sprite if it is not respawning
            for player_sprite in self.player_sprite_list:
                if not player_sprite.respawn_time_left:
                    self.score.distance_travelled += (player_sprite.change_x**2+player_sprite.change_y**2)**0.5 # meters

                    # Check for collisions with the asteroids (returns collisions)
                    asteroids = arcade.check_for_collision_with_list(player_sprite, self.asteroid_list)

                    # Check if there are ship-asteroid collisions detected
                    if len(asteroids) > 0:
                        self.score.deaths += 1
                        self._print_terminal(f"Crashed at {player_sprite.position}, t={self.score.time:.3f} seconds")

                        if player_sprite.lives > 1:
                            player_sprite.destroy()
                            player_sprite.respawn(self.scenario.game_map.center)
                            self.split_asteroid(cast(AsteroidSprite, asteroids[0]))

                            if self.graphics_on:
                                self.ship_life_list.pop().remove_from_sprite_lists()
                        else:
                            self.game_over = StoppingCondition.no_lives
                            self.score.max_distance = self.score.frame_count * player_sprite.max_speed

        # Run final/time step score update
        if self.game_over == StoppingCondition.none:
            self.score.timestep_update(environment=self)
        else:
            # Final time step update
            self.score.final_update(environment=self)
            self.score.stopping_condition = self.game_over

            self._print_terminal("**********************************************************")
            self._print_terminal(f"Scenario: {self.scenario.name}")
            self._print_terminal(f"Game over at {self.score.time:.3f} seconds | ({self.game_over})")
            self._print_terminal("**********************************************************")

            if self.graphics_on:
                pyglet.app.exit()

    def enable_consistent_randomness(self, seed: int = 0) -> None:
        """
        Call this before environment evaluation to seed the random number generator to provide consistent results

        See [Python ``random`` docs] (https://docs.python.org/3/library/random.html) to learn more

        :param seed: Integer seed value
        """
        self.scenario.seed = seed

    def run(self, **kwargs) -> Score:
        """
        Run a full game, based on the settings passed in as keyword arguments (**kwargs)

        :param kwargs: optional keyword arguments passed to ``start_new_game()``
        :return: Score object which defines final score of the environment

        :Keyword Arguments:
        * *controller* (``ControllerBase``) --
            controller object that subclasses ControllerBase
        * *scenario* (``Scenario``) --
            optional environment scenario definition
        * *score* (``Score``) --
            optional score object which should subclass ``Score``
        """
        # Set up the environment with a new version of the game
        self.start_new_game(**kwargs)

        # Run the environment based off of the graphics settings
        if self.graphics_on:
            # Run the environment through the event loop if graphics are on
            self.center_window()
            arcade.run()
        else:
            # Run the environment frame-by-frame explicitly without graphics
            while self.game_over is StoppingCondition.none:
                self.on_update(1 / self.frequency)

        # Return the final score (Score object)
        return self.score
