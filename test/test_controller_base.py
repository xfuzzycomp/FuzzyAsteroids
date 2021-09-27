from unittest import TestCase

from typing import Tuple, Dict, Any
from src.fuzzy_asteroids.fuzzy_controller import ControllerBase, SpaceShip


class BadChild(ControllerBase):
    pass


class GoodChild(ControllerBase):
    @property
    def name(self) -> str:
        return "My name is Bob"

    @staticmethod
    def final_controller():
        # Specify your arguments within cls() constructor
        return GoodChild

    def actions(self, ships: Tuple[SpaceShip], input_data: Dict[str, Any]) -> None:
        self.updated = True


class TestControllerBase(TestCase):
    """
    Base class Tests
    """
    def test_base_class_name_error(self):
        controller = ControllerBase()
        self.assertRaises(NotImplementedError, getattr, controller, "name")

    def test_base_class_final_controller_error(self):
        self.assertRaises(NotImplementedError, ControllerBase.final_controller)

    def test_base_class_actions_error(self):
        controller = ControllerBase()
        self.assertRaises(NotImplementedError, controller.actions, [], {})

    """
    Bad Child Tests
    """
    def test_child_name_error(self):
        controller = BadChild()
        self.assertRaises(NotImplementedError, getattr, controller, "name")

    def test_child_final_controller_error(self):
        self.assertRaises(NotImplementedError, BadChild.final_controller)

    def test_child_actions_error(self):
        controller = BadChild()
        self.assertRaises(NotImplementedError, controller.actions, [], {})

    """
    Good Child Tests
    """
    def test_good_child_name(self):
        controller = GoodChild()
        self.assertRaises(NotImplementedError, getattr, controller, "name")

    def test_good_child_final_controller(self):
        self.assertTrue(GoodChild.final_controller())

    def test_good_child_actions(self):
        controller = GoodChild()
        controller.actions(None, {})
        self.assertTrue(controller.updated)

