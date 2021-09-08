import math
from typing import Tuple, Dict, Any, List

from .sprites import ShipSprite


class SpaceShip:
    """
    Space Ship class to be used to interact with the ShipSprite in the environment

    At each time step the user's controller class will receive a SpaceShip object which limits the amount of
    information/controls the user can access. This SpaceShip class is built directly from the sprite
    """
    def __init__(self, sprite: ShipSprite):
        # Instantiate the ship based on the Sprite used to represent the ship in the environment
        self.id = sprite.id
        self.angle = sprite.angle
        self.change_x = sprite.change_x
        self.change_y = sprite.change_y
        self.center_x = sprite.center_x
        self.center_y = sprite.center_y
        self.is_respawning = sprite.is_respawning
        self.respawn_time_left = sprite.respawn_time_left
        self.fire_wait_time = sprite.fire_wait_time
        self.max_speed = sprite.max_speed
        self.drag = sprite.drag

        # Limitations to output_space
        self.thrust_range = sprite.thrust_range
        self.turn_rate_range = sprite.turn_rate_range

        # Create blank outputs
        self._turn_rate = None
        self._thrust = None
        self._fire_bullet = None

    @property
    def output_space(self) -> Dict[str, Tuple[float, float]]:
        return {
            "turn_rate": self.turn_rate_range,
            "thrust": self.thrust_range,
            "fire_bullet": (False, True),
        }

    @property
    def position(self) -> Tuple[float, float]:
        return self.center_x, self.center_y

    @property
    def velocity(self) -> Tuple[float, float]:
        return self.change_x, self.change_y

    @property
    def turn_rate(self) -> float:
        return self._turn_rate

    @turn_rate.setter
    def turn_rate(self, turn_rate: float):
        if turn_rate < self.output_space["turn_rate"][0]:
            turn_rate = self.output_space["turn_rate"][0]
        elif turn_rate > self.output_space["turn_rate"][1]:
            turn_rate = self.output_space["turn_rate"][1]
        elif math.isnan(turn_rate):
            raise ValueError("value given to SpaceShip.turn_rate.setter() cannot be NaN")

        self._turn_rate = turn_rate

    @property
    def thrust(self) -> float:
        return self._thrust

    @thrust.setter
    def thrust(self, thrust: float):
        if thrust < self.output_space["thrust"][0]:
            thrust = self.output_space["thrust"][0]
        elif thrust > self.output_space["thrust"][1]:
            thrust = self.output_space["thrust"][1]
        elif math.isnan(thrust):
            raise ValueError("value given to SpaceShip.thrust.setter() cannot be NaN")

        self._thrust = thrust

    @property
    def fire_bullet(self) -> bool:
        return self._fire_bullet

    @fire_bullet.setter
    def fire_bullet(self, fire: bool):
        self._fire_bullet = fire

    def shoot(self):
        self._fire_bullet = True


class ControllerBase:
    """
    Abstract class used to manage the control of the AsteroidSmasher ship.

    Note: Users must define a __init__() for the class to instantiate correctly
    """
    def actions(self, ships: Tuple[SpaceShip], input_data: Dict[str, Any]) -> None:
        """
        Compute control actions of the ship. Perform all command actions via the ``ship``
        argument. This class acts as an intermediary between the controller and the environment.

        The environment looks for this function when calculating control actions for the Ship sprite.
        An instance of this class must be given to the environment to evaluate correctly.

        :param ships: Object to use when controlling the SpaceShip
        :param input_data: Input data which describes the current state of the environment
        """
        raise NotImplementedError(f"{self.__class__} does not have an actions() method defined. Your controller class"
                                  f"needs to have an actions() method defined for it to work properly with the "
                                  f"Fuzzy Asteroids game environment.")
