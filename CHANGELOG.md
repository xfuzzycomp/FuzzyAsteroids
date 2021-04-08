# Changelog

## [1.2.1] - 8 April 2021

- Default accuracy value changed to 0% not 100%
- Improved print statements for end of scenario to say what scenario was evaluated
- Resolved crash which would occur when turn_rate/thrust given to SpaceShip are NaN

## [1.2.0] - 5 April 2021

- Added `turn rate` + `thrust` control meters to the graphics and moved lives to center/bottom
- Added more evaluation metrics to the default score class (evaluation times and exception tracking)
- Changed the intrinsic type of the `fuzzy_asteroids.game.StoppingCondition` enum to string for better readability

## [1.1.9] - 1 April 2021

- Updated the `arcade` dependency to version 2.5.6, resolves some speed/memory issues.

## [1.1.8] - 30 March 2021

- Fixed the logic that v1.1.7 introduced which was incorrect, where the FuzzyAsteroids class
  would not call the controller


## [1.1.7] - 29 March 2021

- Resolved error where controller may be called when the game is over, causing crash because the ship controller
  is expecting objects to be there that aren't (ex. no asteroids)

## [1.1.6] - 15 March 2021

- Ship/Asteroid sprites `angle` property will now be capped to (-180.0, 180.0) to simplify calculations
  on the controller side
- Resolved issue with sign convention of starting angle of Asteroids, now should correctly match
  the global angle conventions
- Resolved error in Scenario where ``count_asteroids()`` only counted correctly for 
  asteroids of size=4. This affected the ``max_asteroids()`` calc used in the Score class
- Map class properly uses the global settings as the default

## [1.1.5] - 15 March 2021

- Scenario can be labeled now, example: ``Scenario(name="random_asteroids")``
- Resolved issue where the environment would skipp counting the last death as a death

## [1.1.4] - 09 March 2021

- Fixed trig calc in Asteroid starting velocity to match map coordinate system.

## [1.1.3] - 09 March 2021

- Enabled specification of starting position/angle/lives of the ShipSprite
- Enabled the tracking of lives within the ShipSprite, rather than in the Game environment
- Crash printouts now state crash time and position

## [1.1.2] - 08 March 2021

- Resolved error where the final ship crash is not printed
- Resolved crash in completion of game mode, where the StoppingCondition enum
  could not be converted to an int

## [1.1.1] - 10 February 2021

- Resolved error in AsteroidGame where game would end immediately due to while loop conditional
  not being properly updated for new StoppingCondition enum
- Added Exceptions for incorrect user Score/Scenario inputs to run()/start_new_game()

## [1.1.0] - 08 February 2021

- Added StopCondition enum to highlight the game completion reason
- Added "time_limit" setting to the environment settings dictionary
- Time limit stop condition included, added time tracking to the graphics window
- Score now tracks time and stopping condition
- Fixed error where the ship was given an extra life. 
- Added computational cost tracking (evaluation time) to FuzzyAsteroidsGame via ``track_compute_cost`` kwarg, off by default

## [1.0.0] - 15 January 2021

- First official release of the Fuzzy Asteroids Simulation Environment

