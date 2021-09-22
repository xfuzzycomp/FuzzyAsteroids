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
import math
from typing import cast, Dict, Tuple, List, Any
from enum import Enum

from .sprites import AsteroidSprite, BulletSprite, ShipSprite
from .settings import *
from .util import Score, Scenario
from .dashboard import Dashboard


# # image for dead ship
# here = os.path.dirname(os.path.abspath(__file__))
# filename_death = os.path.join(here, 'SC.png')
# death_image = Image.open(filename_death)
# death_image.show()

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

    Artwork from https://kenney.nl
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
        self.prints = _settings.get("prints", True)
        self.allow_key_presses = _settings.get("allow_key_presses", True)
        self.full_dashboard = _settings.get("full_dashboard", False)

        # Set the timestep to dictate the update rate for the environment
        if self.real_time_multiplier:
            self.timestep = (1 / float(self.frequency)) / float(self.real_time_multiplier)
        else:
            self.timestep = float(1E-9)

        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE,
                         update_rate=self.timestep, visible=self.graphics_on)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        self.directory = os.path.dirname(os.path.abspath(__file__))

        # Sprite lists
        self.player_sprite_list = None
        self.asteroid_list = None
        self.bullet_list = None

        # Other UI elements
        self.dashboard = None

        # Set up the game instance
        self.game_over = None
        self.controller_name = None

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

        self.hit_sounds = [self.hit_sound1, self.hit_sound2, self.hit_sound3, self.hit_sound4]

    def _play_sound(self, sound):
        # Private sound playing function (checks stored sound_on) using globally specified volume
        if self.sound_on:
            sound.play(VOLUME)

    def _print_terminal(self, msg: str):
        if self.prints:
            print(msg)

    def start_new_game(self, scenario: Scenario = None, score: Score = None, **kwargs) -> None:
        """
        Start a new game within the current environment

        :param scenario: optional, Scenario object (includes asteroid starting states and Map)
        :param score: optional Score (should inherit from ``Score``
        """
        if not isinstance(scenario, Scenario) and scenario is not None:
            raise TypeError(
                "scenario argument given to start_new_game() must be a subclass of fuzzy_asteroids.util.Scenario")

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

        # Set up the players
        self.player_sprite_list.extend(self.scenario.ships(self.frequency))

        # Build the dashboard if it should be drawn
        self.dashboard = Dashboard(self.player_sprite_list, self.get_size(), full_dashboard=self.full_dashboard)

        # Get the asteroids from the Scenario (which builds them based on the Scenario settings)
        self.asteroid_list.extend(self.scenario.asteroids(self.frequency))

        # This will resize the window if the dimensions are different from global
        # This behavior is not tested well
        if self.scenario.game_map.default_dimensions != (SCREEN_WIDTH, SCREEN_HEIGHT):
            self.set_size(self.scenario.game_map.width, self.scenario.game_map.height)

        self._print_terminal("**********************************************************")
        self._print_terminal(f"Scenario: {self.scenario.name}")
        self._print_terminal(f"- - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    def draw_extra(self) -> None:
        """
        This function is overridden in child classes to extend window UI plotting behaviors
        """
        pass

    def on_draw(self) -> None:
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.asteroid_list.draw()
        self.bullet_list.draw()
        self.player_sprite_list.draw()

        # Put text on the screen.
        if self.scenario.name:
            output = f"Scenario: {self.scenario.name}"
            arcade.draw_text(output, 10, SCREEN_HEIGHT - 25, WHITE_COLOR, FONT_SIZE2)

        arcade.draw_text(f"Frequency: {self.frequency:.0f} Hz", 10, 110, WHITE_COLOR, FONT_SIZE2)

        time_limit_str = f" / {self.scenario.time_limit}" if not self.scenario.time_limit == float('inf') else ""
        time_str = f"Time: {self.score.time:.1f}{time_limit_str} sec"
        arcade.draw_text(time_str, 10, 90, WHITE_COLOR, FONT_SIZE2)

        score_str = f"Score: {self.score.asteroids_hit}"
        arcade.draw_text(score_str, 10, 70, WHITE_COLOR, FONT_SIZE2)

        bullet_str = f"Bullets Fired: {self.score.bullets_fired}"
        arcade.draw_text(bullet_str, 10, 50, WHITE_COLOR, FONT_SIZE2)

        accuracy_str = f"Accuracy (%): {int(100.0 * self.score.accuracy)}"
        arcade.draw_text(accuracy_str, 10, 30, WHITE_COLOR, FONT_SIZE2)

        asteroid_str = f"Asteroid Count: {len(self.asteroid_list)}"
        arcade.draw_text(asteroid_str, 10, 10, WHITE_COLOR, FONT_SIZE2)

        # Draw the stored dashboard
        self.dashboard.draw()

        # Pin the Ship IDs to the ship as it moves
        for idx, player_sprite in enumerate(self.player_sprite_list):
            arcade.draw_text(f"{player_sprite.id}", player_sprite.position[0] + 30, player_sprite.position[1],
                             WHITE_COLOR, FONT_SIZE1, anchor_x="center", anchor_y="center")

        # Draw extra sprites (used by children)
        self.draw_extra()

    def fire_bullet(self, player_sprite) -> None:
        """Call to fire a bullet"""

        # Check to see if the ship is allowed to fire based on its built in rate limiter
        if player_sprite.can_fire:
            self.score.bullets_fired += 1

            # Skip past the respawning timer
            player_sprite._respawning = 0

            self.bullet_list.append(player_sprite.fire_bullet())
            self._play_sound(self.laser_sound)

    def on_key_press(self, symbol, modifiers) -> None:
        """ Called whenever a key is pressed. """
        if self.allow_key_presses:
            # Track active keys
            if symbol in self.available_keys:
                self.active_key_presses.append(symbol)

            # Shoot if the player hit the space bar and we aren't respawning.
            if symbol == arcade.key.SPACE:
                for player_sprite in self.player_sprite_list:
                    self.fire_bullet(player_sprite)

            # Loop through each player ship and apply the same control action
            for player_sprite in self.player_sprite_list:
                if symbol == arcade.key.LEFT:
                    player_sprite.turn_rate = player_sprite.turn_rate_range[1]
                elif symbol == arcade.key.RIGHT:
                    player_sprite.turn_rate = player_sprite.turn_rate_range[0]

                if symbol == arcade.key.UP:
                    player_sprite.thrust = player_sprite.thrust_range[1]
                elif symbol == arcade.key.DOWN:
                    player_sprite.thrust = player_sprite.thrust_range[0]

    def on_key_release(self, symbol, modifiers) -> None:
        """ Called whenever a key is released. """
        if self.allow_key_presses:

            # Remove released key from active keys list
            if symbol in self.available_keys:
                self.active_key_presses.pop(self.active_key_presses.index(symbol))

            # Update the ships with different control actions
            for player_sprite in self.player_sprite_list:
                if symbol == arcade.key.LEFT and arcade.key.RIGHT not in self.active_key_presses:
                    player_sprite.turn_rate = 0
                elif symbol == arcade.key.RIGHT and arcade.key.LEFT not in self.active_key_presses:
                    player_sprite.turn_rate = 0
                elif symbol == arcade.key.UP and arcade.key.DOWN not in self.active_key_presses:
                    player_sprite.thrust = 0
                elif symbol == arcade.key.DOWN and arcade.key.UP not in self.active_key_presses:
                    player_sprite.thrust = 0

    def split_asteroid(self, asteroid: AsteroidSprite) -> None:
        """ Split an asteroid into chunks. """
        # Add to score
        self.score.asteroids_hit += 1

        if asteroid.size > 1:
            self.asteroid_list.extend(
                [AsteroidSprite(frequency=self.frequency, position=asteroid.position, size=asteroid.size - 1) for _ in
                 range(3)])

        # Play sound via index lookup
        self._play_sound(self.hit_sounds[asteroid.size-1])

        # Remove asteroid from sprites
        asteroid.remove_from_sprite_lists()

    def kill_ship(self, ship: ShipSprite) -> None:
        """
        Kill the given ship sprite, and manage respawn if there are lives leftover
        :param ship: ShipSprite object that will die
        """
        # Destroy decrements the ship lives by 1
        ship.destroy()

        # If there are lives left, then respawn, otherwise pop the ship sprites
        if ship.lives > 0:
            ship.respawn(self.scenario.game_map.center)
        else:
            ship.remove_from_sprite_lists()

            # If graphics are on, remove the ship life indicator
            if self.graphics_on:
                self.dashboard.kill_ship()

    def on_update(self, delta_time: float) -> None:
        """
        Move everything

        :param delta_time: Time since last time step
        """
        # Check for stopping conditions
        self.check_stopping_conditions()

        # Run final/time step score update
        if self.game_over == StoppingCondition.none:
            # Update all sprites
            self.asteroid_list.on_update(delta_time)
            self.bullet_list.on_update(delta_time)
            self.player_sprite_list.on_update(delta_time)

            # Check for collisions between bullets and asteroids
            self.check_bullet_asteroid_collisions()

            # Check for ship to asteroid collisions
            self.check_asteroid_ship_collisions()

            # Check for ship to ship collisions
            self.check_ship_ship_collisions()

            # Run the timestep score update function after the environment has updated
            self.score.timestep_update(environment=self)

        else:
            # Final time step update
            self.score.max_distance = sum(self.score.frame_count * sprite.max_speed for sprite in self.player_sprite_list)
            self.score.stopping_condition = self.game_over
            self.score.final_update(environment=self)

            self._print_terminal(f"- - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
            self._print_terminal(f"Game over at {self.score.time:.3f} seconds | ({self.game_over})")
            self._print_terminal(f"Score: {self.score.__dict__}")
            self._print_terminal("**********************************************************\n")

            if self.graphics_on:
                pyglet.app.exit()

    def check_stopping_conditions(self):
        # Check to see for termination conditions
        if not self.asteroid_list:
            self.game_over = StoppingCondition.no_asteroids
        elif not self.player_sprite_list:
            self.game_over = StoppingCondition.no_lives
        elif self.score.time >= self.scenario.time_limit:
            self.game_over = StoppingCondition.no_time
        else:
            # If there are no stopping conditions, update the time/frame count
            self.score.frame_count += 1
            self.score.time = self.score.frame_count / float(self.frequency)

            # Update the total distance travelled tracker
            self.score.distance_travelled += sum((sprite.change_x ** 2 + sprite.change_y ** 2) ** 0.5
                                                 for sprite in self.player_sprite_list)  # meters

    def check_bullet_asteroid_collisions(self):
        # Check for collisions between bullets and asteroids
        for bullet in self.bullet_list:
            asteroids = arcade.check_for_collision_with_list(bullet, self.asteroid_list)

            # Break up and remove asteroids if there are bullet-asteroid collisions
            for asteroid in asteroids:
                self.split_asteroid(cast(AsteroidSprite, asteroid))  # expected AsteroidSprite, got Sprite instead
                bullet.remove_from_sprite_lists()

    def check_asteroid_ship_collisions(self):
        # Perform checks on the player sprite if it is not respawning
        for idx, sprite in enumerate(self.player_sprite_list):
            if not sprite.respawn_time_left:
                self.score.distance_travelled += (sprite.change_x ** 2 + sprite.change_y ** 2) ** 0.5  # meters

                # Check for collisions with the asteroids (returns collisions)
                asteroids = arcade.check_for_collision_with_list(sprite, self.asteroid_list)

                # Check if there are ship-asteroid collisions detected
                if len(asteroids) > 0:
                    self.score.deaths += 1

                    self._print_terminal(f"Ship {sprite.id} crashed into asteroid: at {sprite.position_str}, t={self.score.time:.3f} seconds")

                    self.split_asteroid(cast(AsteroidSprite, asteroids[0]))
                    self.kill_ship(sprite)

    def check_ship_ship_collisions(self):
        # Perform checks on the player sprite if it is not respawning
        for idx, sprite in enumerate(self.player_sprite_list):
            if not sprite.respawn_time_left:

                # Check for collisions with other ships (returns list of sprites that collided with `sprite`)
                collided_ships = arcade.check_for_collision_with_list(sprite, self.player_sprite_list)

                # Filter out collisions if the target ship is still respawning
                valid_collided_ships = [ship for ship in collided_ships if not cast(ShipSprite, ship).respawn_time_left]

                # Check if there are ship-ship collisions detected
                if len(valid_collided_ships) > 0:
                    self.score.deaths += len(valid_collided_ships) + 1

                    # Loop through collided ships (and current sprite), trigger deaths and respawns in applicable
                    for ship in valid_collided_ships + [sprite]:
                        ship = cast(ShipSprite, ship)  # Cast the ship object to ShipSprite for type hinting

                        self._print_terminal(f"Ship {ship.id} crashed into other ship: at {ship.position_str}, t={self.score.time:.3f} seconds")
                        self.kill_ship(ship)

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
