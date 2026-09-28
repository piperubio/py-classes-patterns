# pyright: reportGeneralTypeIssues=false

import unittest

import pydantic

from classes._pydantic import ConnectorTechSpecStrictType, CableTechSpecStrictType


class TestInheritanceConnectorPydanticStrictTypes(unittest.TestCase):
    def test_connector_tech_spec_instance(self):
        tech_spec = ConnectorTechSpecStrictType(
            attenuation_1310nm=0.5,
            attenuation_1550nm=0.6
        )
        self.assertEqual(tech_spec.attenuation_1310nm, 0.5)
        self.assertEqual(tech_spec.attenuation_1550nm, 0.6)

    def test_connector_tech_spec_inmutable(self):
        tech_spec = ConnectorTechSpecStrictType(
            attenuation_1310nm=0.5,
            attenuation_1550nm=0.6
        )
        # pydantic raises ValidationError when object is inmutable
        with self.assertRaises(pydantic.ValidationError):
            tech_spec.attenuation_1310nm = 0.5

    def test_connector_tech_spec_error_when_attenuation_default_is_invalid(self):
        with self.assertRaises(ValueError):
            ConnectorTechSpecStrictType(
                attenuation_1550nm=0.6,
            )

    def test_connector_tech_spec_error_when_attenuation_is_none(self):
        with self.assertRaises(ValueError):
            ConnectorTechSpecStrictType(
                attenuation_1310nm=None,
                attenuation_1550nm=0.6,
            )

    def test_connector_tech_spec_error_when_attenuation_is_zero(self):
        with self.assertRaises(ValueError):
            ConnectorTechSpecStrictType(
                attenuation_1310nm=0,
                attenuation_1550nm=0.6,
            )

    def test_connector_tech_spec_from_primitives(self):
        tech_spec = ConnectorTechSpecStrictType.from_primitives(
            {
                "attenuation_1310nm": 0.5,
                "attenuation_1550nm": 0.6
            }
        )
        assert isinstance(tech_spec, ConnectorTechSpecStrictType)
        self.assertEqual(tech_spec.attenuation_1310nm, 0.5)
        self.assertEqual(tech_spec.attenuation_1550nm, 0.6)

    def test_connector_tech_spec_to_primitives(self):
        tech_spec = ConnectorTechSpecStrictType(
            attenuation_1310nm=0.5,
            attenuation_1550nm=0.6
        )
        self.assertEqual(tech_spec.to_primitives(), {
            "attenuation_1310nm": 0.5,
            "attenuation_1550nm": 0.6
        })


class TestInheritanceCablePydanticStrictTypes(unittest.TestCase):
    def test_cable_tech_spec_instance(self):
        tech_spec = CableTechSpecStrictType(
            attenuation_1310nm=0.5,
            attenuation_1550nm=0.6,
            number_of_filaments=1
        )
        self.assertEqual(tech_spec.attenuation_1310nm, 0.5)
        self.assertEqual(tech_spec.attenuation_1550nm, 0.6)
        self.assertEqual(tech_spec.number_of_filaments, 1)

    def test_cable_tech_spec_error_when_attenuation_default_is_invalid(self):
        with self.assertRaises(ValueError):
            CableTechSpecStrictType(
                attenuation_1310nm=0.5,
                attenuation_1550nm=0.6,
            )

    def test_cable_tech_spec_error_when_attenuation_is_none(self):
        with self.assertRaises(ValueError):
            CableTechSpecStrictType(
                attenuation_1310nm=None,
                attenuation_1550nm=0.6,
                number_of_filaments=1
            )

    def test_cable_tech_spec_error_when_number_of_filaments_is_zero(self):
        with self.assertRaises(ValueError):
            CableTechSpecStrictType(
                attenuation_1310nm=1,
                attenuation_1550nm=0.6,
                number_of_filaments=0
            )

    def test_cable_tech_spec_from_primitives(self):
        tech_spec = CableTechSpecStrictType.from_primitives(
            {
                "attenuation_1310nm": 0.5,
                "attenuation_1550nm": 0.6,
                "number_of_filaments": 1
            }
        )
        assert isinstance(tech_spec, CableTechSpecStrictType)
        self.assertEqual(tech_spec.attenuation_1310nm, 0.5)
        self.assertEqual(tech_spec.attenuation_1550nm, 0.6)
        self.assertEqual(tech_spec.number_of_filaments, 1)

    def test_cable_tech_spec_to_primitives(self):
        tech_spec = CableTechSpecStrictType(
            attenuation_1310nm=0.5,
            attenuation_1550nm=0.6,
            number_of_filaments=1
        )
        self.assertEqual(tech_spec.to_primitives(), {
            "attenuation_1310nm": 0.5,
            "attenuation_1550nm": 0.6,
            "number_of_filaments": 1
        })
