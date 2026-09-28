# pyright: reportGeneralTypeIssues=false

import unittest

import pydantic

from classes._pydantic import ConnectorTechSpecType, CableTechSpecType


class TestInheritanceConnectorPydanticTypes(unittest.TestCase):
    def test_connector_tech_spec_instance(self):
        tech_spec = ConnectorTechSpecType(
            attenuation_1310nm=0.5,
            attenuation_1550nm=0.6
        )
        self.assertEqual(tech_spec.attenuation_1310nm, 0.5)
        self.assertEqual(tech_spec.attenuation_1550nm, 0.6)

    def test_connector_tech_spec_inmutable(self):
        tech_spec = ConnectorTechSpecType(
            attenuation_1310nm=0.5,
            attenuation_1550nm=0.6
        )
        # pydantic raises ValidationError when object is inmutable
        with self.assertRaises(pydantic.ValidationError):
            tech_spec.attenuation_1310nm = 0.5

    def test_connector_tech_spec_error_when_attenuation_default_is_invalid(self):
        with self.assertRaises(ValueError):
            ConnectorTechSpecType(
                attenuation_1550nm=0.6,
            )

    def test_connector_tech_spec_error_when_attenuation_is_none(self):
        with self.assertRaises(ValueError):
            ConnectorTechSpecType(
                attenuation_1310nm=None,
                attenuation_1550nm=0.6,
            )

    def test_connector_tech_spec_error_when_attenuation_is_zero(self):
        with self.assertRaises(ValueError):
            ConnectorTechSpecType(
                attenuation_1310nm=0,
                attenuation_1550nm=0.6,
            )

    def test_connector_tech_spec_from_primitives(self):
        tech_spec = ConnectorTechSpecType.from_primitives(
            {
                "attenuation_1310nm": 0.5,
                "attenuation_1550nm": 0.6
            }
        )
        assert isinstance(tech_spec, ConnectorTechSpecType)
        self.assertEqual(tech_spec.attenuation_1310nm, 0.5)
        self.assertEqual(tech_spec.attenuation_1550nm, 0.6)

    def test_connector_tech_spec_to_primitives(self):
        tech_spec = ConnectorTechSpecType(
            attenuation_1310nm=0.5,
            attenuation_1550nm=0.6
        )
        self.assertEqual(tech_spec.to_primitives(), {
            "attenuation_1310nm": 0.5,
            "attenuation_1550nm": 0.6
        })


class TestInheritanceCablePydanticTypes(unittest.TestCase):
    def test_cable_tech_spec_instance(self):
        tech_spec = CableTechSpecType(
            attenuation_1310nm=0.5,
            attenuation_1550nm=0.6,
            number_of_filaments=1
        )
        self.assertEqual(tech_spec.attenuation_1310nm, 0.5)
        self.assertEqual(tech_spec.attenuation_1550nm, 0.6)
        self.assertEqual(tech_spec.number_of_filaments, 1)

    def test_cable_tech_spec_error_when_attenuation_default_is_invalid(self):
        with self.assertRaises(ValueError):
            CableTechSpecType(
                attenuation_1310nm=0.5,
                attenuation_1550nm=0.6,
            )

    def test_cable_tech_spec_error_when_attenuation_is_none(self):
        with self.assertRaises(ValueError):
            CableTechSpecType(
                attenuation_1310nm=None,
                attenuation_1550nm=0.6,
                number_of_filaments=1
            )

    def test_cable_tech_spec_error_when_number_of_filaments_is_zero(self):
        with self.assertRaises(ValueError):
            CableTechSpecType(
                attenuation_1310nm=1,
                attenuation_1550nm=0.6,
                number_of_filaments=0
            )

    def test_cable_tech_spec_from_primitives(self):
        tech_spec = CableTechSpecType.from_primitives(
            {
                "attenuation_1310nm": 0.5,
                "attenuation_1550nm": 0.6,
                "number_of_filaments": 1
            }
        )
        assert isinstance(tech_spec, CableTechSpecType)
        self.assertEqual(tech_spec.attenuation_1310nm, 0.5)
        self.assertEqual(tech_spec.attenuation_1550nm, 0.6)
        self.assertEqual(tech_spec.number_of_filaments, 1)

    def test_cable_tech_spec_to_primitives(self):
        tech_spec = CableTechSpecType(
            attenuation_1310nm=0.5,
            attenuation_1550nm=0.6,
            number_of_filaments=1
        )
        self.assertEqual(tech_spec.to_primitives(), {
            "attenuation_1310nm": 0.5,
            "attenuation_1550nm": 0.6,
            "number_of_filaments": 1
        })
