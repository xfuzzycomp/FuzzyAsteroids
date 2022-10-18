"""
Asteroid Smasher

Shoot space rocks in this demo program created with
Python and the Arcade library.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.asteroids
"""

VOLUME = 0.05
SCALE = 0.5
OFFSCREEN_SPACE = 00
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "XFC 2022: ASTEROID SMASHER"
LEFT_LIMIT = 0
RIGHT_LIMIT = SCREEN_WIDTH
BOTTOM_LIMIT = 0
TOP_LIMIT = SCREEN_HEIGHT

# Settings related to drawing within the window (font sizes and colors)
FONT_SIZE1 = 15
FONT_SIZE2 = 13
WHITE_COLOR = (255, 255, 255, 255)
BLUE_COLOR = (150, 150, 255, 150)
