import math
import arcade
import arcade.gui

from typing import cast, Dict, Tuple, List, Any

from .settings import *
from .sprites import ShipSprite


class Dashboard:
    def __init__(self, player_sprite_list: arcade.SpriteList, map_size,
                 full_dashboard: bool = True, graphics_on: bool=True):
        self.full_dashboard = full_dashboard
        self.graphics_on = graphics_on

        # GUI widgets
        self.player_sprite_list = player_sprite_list
        self.ship_life_list = arcade.SpriteList(is_static=True)
        self.static_batched_elements = arcade.ShapeElementList()

        # Get the starting point for the dash board elements, starting from the right
        self.meter_x = map_size[0] - 50

        # Starting point for the ship lives (creates offset in-case the control actions shouldn't be shown)
        self.life_y_offset = 80 if full_dashboard else 0

        if self.graphics_on:
            # Instantiate UI elements which can be drawn faster using batching
            self.create_ship_lives()

            # Create reusable dashboard elements (if desired)
            if full_dashboard:
                self.create_dashboard_elements()

    def x_pos(self, idx: int) -> int:
        # Method for spacing out the windows in each ship block
        return self.meter_x - (180 * idx)

    def create_ship_lives(self):
        """
        Build the sprite list which contains life counters for the ships
        """
        for idx, player_sprite in enumerate(self.player_sprite_list):
            x_pos = self.x_pos(idx)

            life = arcade.Sprite(":resources:images/space_shooter/playerLife1_orange.png", SCALE * 2.0)
            life.alpha = 150
            life.center_x = x_pos
            life.center_y = 35 + self.life_y_offset
            self.ship_life_list.append(life)

    def create_dashboard_elements(self):
        """
        Build the UI elements which represent the control actions meters
        """
        for idx, player_sprite in enumerate(self.player_sprite_list):
            x_pos = self.x_pos(idx)

            # Build two identical, vertically stacked control meters
            self.build_control_meter(x_pos, 30, width=80, height=30)
            self.build_control_meter(x_pos, 70, width=80, height=30)

    def build_control_meter(self, x_pos, y_pos, width, height):
        """
        Used for building elements which represent the control space of a given control action
        """
        self.static_batched_elements.append(
            arcade.create_line(start_x=x_pos, end_x=x_pos, start_y=y_pos-height/2-4, end_y=y_pos+height/2+4, color=WHITE_COLOR))
        self.static_batched_elements.append(
            arcade.create_rectangle_outline(center_x=x_pos, center_y=y_pos, width=width, height=height, color=WHITE_COLOR))

    def draw_dashboard(self):
        """
        Draw the dashboard every timestep
        """
        for idx, player_sprite in enumerate(self.player_sprite_list):
            # Get the x position for this player sprite control block
            x_pos = self.x_pos(idx)

            # Create Basic labels about ship id/lives
            arcade.draw_text(f"Ship {player_sprite.id}", x_pos - 40, 60 + self.life_y_offset, WHITE_COLOR, FONT_SIZE1,
                             anchor_x="center", anchor_y="center")
            arcade.draw_text(f"Lives:   {player_sprite.lives}", x_pos - 50, 30 + self.life_y_offset, WHITE_COLOR, FONT_SIZE2,
                             anchor_x="center", anchor_y="center")

            # if the user wants the full dash board, draw the turning rates as well
            if self.full_dashboard:
                self.draw_thrust(player_sprite, x_pos)
                self.draw_turn_rate(player_sprite, x_pos)

    def draw_turn_rate(self, player_sprite, x_pos):
        # thrust
        thrust = player_sprite.thrust
        norm_thrust = thrust / max(player_sprite.thrust_range)
        arcade.draw_text(f"Throttle\n{thrust:6.1f}", x_pos - 50, 70, WHITE_COLOR, FONT_SIZE2,
                         anchor_x="right", anchor_y="center", align="right", width=80)

        # Dynamic block for monitoring thrust
        arcade.draw_rectangle_filled(center_x=x_pos + (20 * norm_thrust), center_y=70,
                                     width=40 * math.fabs(norm_thrust), height=30 - 2, color=BLUE_COLOR)

    def draw_thrust(self, player_sprite, x_pos):
        # turn rate
        turn_rate = player_sprite.turn_rate
        norm_turn_rate = turn_rate / max(player_sprite.turn_rate_range)
        arcade.draw_text(f"Turn Rate\n{turn_rate:6.1f}", x_pos - 50, 30, WHITE_COLOR, FONT_SIZE2,
                         anchor_x="right", anchor_y="center", align="right", width=80)

        # Dynamic block for monitoring turn rate
        arcade.draw_rectangle_filled(center_x=x_pos + (20 * norm_turn_rate), center_y=30,
                                       width=40 * math.fabs(norm_turn_rate), height=30 - 2, color=BLUE_COLOR)

    def kill_ship(self):
        """
        When ship runs out of lives, remove its life tracker from the sprite list
        """
        # Pop a ship life
        if self.ship_life_list:
            self.ship_life_list.pop().remove_from_sprite_lists()

        # Pop the batched control elements
        if self.static_batched_elements:
            for item in self.static_batched_elements[-4:]:
                self.static_batched_elements.remove(item)

    def draw(self):
        # Draw the dashboard entries not included below
        self.draw_dashboard()

        # Draw the ship life sprites
        self.ship_life_list.draw()

        # Draw the batched elements which should be static until deleted
        if self.static_batched_elements:
            self.static_batched_elements.draw()
