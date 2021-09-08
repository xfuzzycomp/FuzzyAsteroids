import random
import math
import arcade

from typing import cast, Dict, Tuple, List, Any

from .settings import *


class BulletSprite(arcade.Sprite):
    """ Sprite that sets its angle to the direction it is traveling in. """
    def __init__(self, frequency: float, starting_angle: float, starting_position: Tuple[float, float]):
        """ Set up a bullet sprite. """
        # Call the parent Sprite constructor
        super().__init__(":resources:images/space_shooter/laserBlue01.png", SCALE)

        # Set GUID
        self.guid = "Bullet"

        # Bullet model
        self.frequency = frequency
        self.bullet_speed = 800

        # Set the starting state
        self.change_x = -math.sin(math.radians(starting_angle)) * self.bullet_speed / self.frequency
        self.change_y = math.cos(math.radians(starting_angle)) * self.bullet_speed / self.frequency
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))

        self.center_x, self.center_y = starting_position

        # Update the bullet sprite
        self.update()

    @property
    def state(self) -> Dict[str, Tuple[float, float]]:
        return {
            "frequency": float(self.frequency),
            "position": tuple(self.position),
            "velocity": tuple(self.velocity),
            "speed": float(self.bullet_speed),
            "angle": float(self.angle)
        }

    def on_update(self, delta_time: float = 1/60):
        # Call position update via parent
        super().update()

        if self.center_x < LEFT_LIMIT - self.width:
            self.remove_from_sprite_lists()
        elif self.center_x > SCREEN_WIDTH + self.width:
            self.remove_from_sprite_lists()

        if self.center_y < BOTTOM_LIMIT - self.height:
            self.remove_from_sprite_lists()
        elif self.center_y > SCREEN_HEIGHT + self.height:
            self.remove_from_sprite_lists()


class ShipSprite(arcade.Sprite):
    """
    Sprite that represents our space ship.

    Derives from arcade.Sprite.
    """
    def __init__(self, id: int, frequency: float, position: Tuple[float, float], angle: float = 0.0, lives: int = 3):
        """
        Instantiate a ShipSprite

        :param frequency: Frequency for rate based update mechanics
        :param position: Starting position of the
        :param angle: Starting angle of the ShipSprite
        :param lives: Number of starting lives
        """
        """ Set up the space ship. """

        # Call the parent Sprite constructor
        super().__init__(":resources:images/space_shooter/playerShip1_orange.png", SCALE)

        # State info
        self.id = id
        self.frequency = frequency
        self.thrust = 0
        self.speed = 0
        self.max_speed = 240  # Meters per second
        self.turn_rate = 0

        # Lives
        self.lives = lives

        # Limitations to controllers
        self.thrust_range = (-480.0, 480.0)  # m/s^2
        self.turn_rate_range = (-180.0, 180.0)  # Degrees per second

        # Manage drag via timer
        self.drag = 80.0  # m/s^2

        # Manage respawns/firing via timers
        self._respawning = 0
        self._respawn_time = 3      # seconds
        self._fire_limiter = 0
        self._fire_time = 1 / 10    # seconds

        # Mark that we are respawning.
        self.respawn(position, angle)

    @property
    def state(self) -> Dict[str, Any]:
        return {
            "is_respawning": True if self.is_respawning else False,
            "respawn_time_left": float(self.respawn_time_left),
            "frequency": float(self.frequency),
            "position": tuple(self.position),
            "velocity": tuple(self.velocity),
            "speed": float(self.speed),
            "angle": float(self.angle),
            "max_speed": float(self.max_speed)
        }

    @property
    def position_str(self) -> str:
        return f"({self.center_x:.3f}, {self.center_y:.3f})"

    @property
    def is_respawning(self) -> bool:
        return True if self._respawning else False

    @property
    def respawn_time_left(self) -> float:
        return self._respawning

    @property
    def respawn_time(self) -> float:
        return self._respawn_time

    @property
    def can_fire(self) -> bool:
        return not self._fire_limiter

    @property
    def fire_rate(self) -> float:
        return 1 / self._fire_time

    @property
    def fire_wait_time(self) -> float:
        return self._fire_limiter

    @property
    def half_width(self) -> float:
        return self.width / 2.0

    @property
    def half_height(self) -> float:
        return self.height / 2.0

    def destroy(self) -> None:
        """
        Destroys the current ship (reducing lives by one)
        """
        self.lives -= 1

    def respawn(self, position: Tuple[float, float], angle: float = 0.0) -> None:
        """
        Called when we die and need to make a new ship.
        'respawning' is an invulnerability timer.
        """
        # If we are in the middle of respawning, this is non-zero.
        self._respawning = self._respawn_time
        self.center_x, self.center_y = position
        self.speed = 0
        self.angle = angle

    def fire_bullet(self) -> BulletSprite:
        # Fire a bullet, starting at this sprite's position/angle
        self._fire_limiter = self._fire_time

        return BulletSprite(frequency=self.frequency,
                            starting_angle=self.angle,
                            starting_position=(self.center_x, self.center_y))

    def on_update(self, delta_time: float = 1/60):
        """
        Update our position and other particulars.
        """
        # Call position update via parent
        super().update()

        # Handle respawning
        if self._respawning:
            self._respawning -= (1/self.frequency)

        if self._respawning <= 0.0:
            self._respawning = 0
            self.alpha = 255
        else:
            self.alpha = 255 * (1 - self._respawning/self._respawn_time)

        if self._fire_limiter <= 0.0:
            self._fire_limiter = 0.0
        else:
            self._fire_limiter -= (1/self.frequency)

        # Apply drag
        if self.speed > 0:
            self.speed -= self.drag / self.frequency
            if self.speed < 0:
                self.speed = 0

        elif self.speed < 0:
            self.speed += self.drag / self.frequency
            if self.speed > 0:
                self.speed = 0

        # Apply thrust to speed
        self.speed += self.thrust / self.frequency

        # Bounds check the speed
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        elif self.speed < -self.max_speed:
            self.speed = -self.max_speed

        # Update the angle based on turning rate
        self.angle += self.turn_rate / self.frequency

        # Keep the angle within (-180, 180)
        if self.angle > 180.0:
            self.angle -= 360.0
        elif self.angle < -180.0:
            self.angle += 360.0

        # Use speed magnitude to get velocity vector
        self.change_x = -math.sin(math.radians(self.angle)) * self.speed / self.frequency
        self.change_y = math.cos(math.radians(self.angle)) * self.speed / self.frequency

        # Update the position based off the speed
        self.center_x += self.change_x / self.frequency
        self.center_y += self.change_y / self.frequency

        # If the ship goes off-screen, move it to the other side of the window
        if self.right < 0:
            self.left = SCREEN_WIDTH

        elif self.left > SCREEN_WIDTH:
            self.right = 0

        if self.bottom < BOTTOM_LIMIT:
            self.top = SCREEN_HEIGHT

        elif self.top > SCREEN_HEIGHT:
            self.bottom = BOTTOM_LIMIT


class AsteroidSprite(arcade.Sprite):
    """ Sprite that represents an asteroid. """
    def __init__(self, frequency: float, position: Tuple[float, float] = None,
                 speed: float = None, angle: float = None, size: float = None):
        """
        Constructor for Asteroid Sprite

        :param frequency: Operating frequency for rate based model dynamics
        :param position:  Optional Starting position (x, y) position
        :param speed: Optional Starting Speed
        :param angle: Optional Starting heading angle (degrees)
        :param size: Optional Starting size (1 to 4 inclusive)
        """
        if size:
            if 1 <= size <= 4:
                self.size = size
            else:
                raise ValueError("AsteroidSize can only be between 1 and 4")
        else:
            self.size = 4

        # Images dict for lookup/selection of sprite images
        images = {
            4: (":resources:images/space_shooter/meteorGrey_big1.png",
                ":resources:images/space_shooter/meteorGrey_big2.png",
                ":resources:images/space_shooter/meteorGrey_big3.png",
                ":resources:images/space_shooter/meteorGrey_big4.png"),
            3: (":resources:images/space_shooter/meteorGrey_med1.png",
                ":resources:images/space_shooter/meteorGrey_med2.png"),
            2: (":resources:images/space_shooter/meteorGrey_small1.png",
                ":resources:images/space_shooter/meteorGrey_small2.png"),
            1: (":resources:images/space_shooter/meteorGrey_tiny1.png",
                ":resources:images/space_shooter/meteorGrey_tiny2.png")
        }

        # Call Sprite constructor
        super().__init__(random.choice(images[self.size]), scale=SCALE*1.5)

        # Set GUID
        self.guid = "Asteroid"

        # Set random rotation angle for spinning
        self.frequency = frequency
        self.change_angle = (random.random() - 0.5) * 120 / self.frequency

        # Set initial speed based off of scaling factor
        speed_scaler = 2.0 + (4.0 - self.size) / 4.0
        self.max_speed = 60.0 * speed_scaler

        # Use options angle and speed arguments
        starting_angle = angle if angle is not None else random.random()*360.0 - 180.0
        starting_speed = speed if speed is not None else random.random()*self.max_speed - self.max_speed/2.0

        # Set constant starting velocity based on starting angle and speed
        self.change_x = -starting_speed * math.sin(math.radians(starting_angle)) / self.frequency
        self.change_y = starting_speed * math.cos(math.radians(starting_angle)) / self.frequency

        # Use parent position as starting point if this asteroid is starting form a parent
        # Otherwise use the position given
        self.center_x, self.center_y = position

    @property
    def state(self) -> Dict[str, Tuple[float, float]]:
        return {
            "frequency": float(self.frequency),
            "position": tuple(self.position),
            "velocity": tuple(self.velocity),
            "size": int(self.size),
            "angle": float(self.angle)
        }

    @property
    def half_width(self) -> float:
        return self.width / 2.0

    @property
    def half_height(self) -> float:
        return self.height / 2.0

    def on_update(self, delta_time: float = 1/60):
        """ Move the asteroid around. """
        # Call position update via parent
        super().update()

        # Keep the angle within (-180, 180)
        if self.angle > 180.0:
            self.angle -= 360.0
        elif self.angle < -180.0:
            self.angle += 360.0

        # Check right/left bounds
        if self.center_x < LEFT_LIMIT - self.half_width:
            self.center_x = RIGHT_LIMIT + self.half_width
        elif self.center_x > RIGHT_LIMIT + self.half_width:
            self.center_x = LEFT_LIMIT - self.half_width

        # Check top bottom bounds
        if self.center_y > TOP_LIMIT + self.half_height:
            self.center_y = BOTTOM_LIMIT - self.half_height
        elif self.center_y < BOTTOM_LIMIT - self.half_height:
            self.center_y = TOP_LIMIT + self.half_height
