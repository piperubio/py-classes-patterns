# pyright: reportGeneralTypeIssues=false

import unittest

import pydantic

from classes._pydantic import ID


class TestVOPydantic(unittest.TestCase):
    def test_id_instance(self):
        id_instance = ID(value="test-id")
        assert isinstance(id_instance, ID)
        assert isinstance(id_instance.value, str)
        assert id_instance.value == "test-id"

    def test_id_generate_instance(self):
        id_generate_instance = ID.generate(size=8)
        assert isinstance(id_generate_instance, ID)
        assert isinstance(id_generate_instance.value, str)
        assert len(id_generate_instance.value) == 8

    def test_id_instance_from_primitive(self):
        id_instance = ID(**{"value": "test-id"})
        assert isinstance(id_instance, ID)
        assert isinstance(id_instance.value, str)
        assert id_instance.value == "test-id"

    def test_id_instance_to_primitive(self):
        id_instance = ID(value="test-id")
        assert id_instance.to_primitives() == {"value": "test-id"}

    def test_equals(self):
        id_instance = ID(value="test-id")
        id_instance_2 = ID(value="test-id")
        assert id_instance == id_instance_2

    def test_not_equals(self):
        id_instance = ID(value="test-id")
        id_instance_2 = ID(value="test-id-2")
        assert id_instance != id_instance_2

    def test_hash(self):
        id_instance = ID(value="test-id")
        id_instance_2 = ID(value="test-id")
        assert hash(id_instance) == hash(id_instance_2)

    def test_raise_error_when_try_change_value(self):
        id_instance = ID(value="test-id")
        # pydantic use ValidationError instead of AttributeError
        with self.assertRaises(pydantic.ValidationError):
            id_instance.value = "test-id-2"

    def test_raise_error_when_try_delete_value(self):
        id_instance = ID(value="test-id")
        with self.assertRaises(pydantic.ValidationError):
            del id_instance.value

    def test_raise_error_when_try_delete_value_attr(self):
        id_instance = ID(value="test-id")
        with self.assertRaises(pydantic.ValidationError):
            delattr(id_instance, "value")

    def test_raise_error_when_value_is_not_str(self):
        """ pydantic use ValidationError(ValueError) instead of TypeError,
            pydantic v2 does not parse int to str (v1 did: 1 -> "1")
        """
        with self.assertRaises(ValueError):
            _ = ID(value=1)

    def test_raise_error_when_value_is_an_empty_str(self):
        with self.assertRaises(ValueError):
            _ = ID(value="")

    def test_raise_error_when_value_has_more_than_36_characters(self):
        with self.assertRaises(ValueError):
            _ = ID(value="3213213131312321312312312321321321312312312321")
