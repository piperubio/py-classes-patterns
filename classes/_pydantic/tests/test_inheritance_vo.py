# pyright: reportGeneralTypeIssues=false

import unittest

import pydantic

from classes._pydantic import (
    AttenuationVO,
    NumberOfFilamentsVO,
    ConnectorTechSpecVO,
    CableTechSpecVO
)


class TestInheritanceConnectorPydanticVO(unittest.TestCase):
    def test_connector_tech_spec_instance(self):
        tech_spec = ConnectorTechSpecVO(
            attenuation_1310nm=AttenuationVO(value=0.5),
            attenuation_1550nm=AttenuationVO(value=0.6)
        )
        self.assertEqual(tech_spec.attenuation_1310nm.value, 0.5)
        self.assertEqual(tech_spec.attenuation_1550nm.value, 0.6)

    def test_connector_tech_spec_inmutable(self):
        tech_spec = ConnectorTechSpecVO(
            attenuation_1310nm=AttenuationVO(value=0.5),
            attenuation_1550nm=AttenuationVO(value=0.6)
        )
        # pydantic raises ValidationError when object is inmutable
        with self.assertRaises(pydantic.ValidationError):
            tech_spec.attenuation_1310nm = AttenuationVO(value=0.6)

    def test_connector_tech_spec_error_when_attenuation_default_is_invalid(self):
        with self.assertRaises(ValueError):
            ConnectorTechSpecVO(
                attenuation_1550nm=0.6,
            )

    def test_connector_tech_spec_error_when_attenuation_is_none(self):
        with self.assertRaises(ValueError):
            ConnectorTechSpecVO(
                attenuation_1310nm=None,
                attenuation_1550nm=0.6,
            )

    def test_connector_tech_spec_error_when_attenuation_is_zero(self):
        with self.assertRaises(ValueError):
            ConnectorTechSpecVO(
                attenuation_1310nm=AttenuationVO(value=0),
                attenuation_1550nm=AttenuationVO(value=0.6),
            )

    def test_connector_tech_spec_from_primitives(self):
        tech_spec = ConnectorTechSpecVO.from_primitives(
            {
                "attenuation_1310nm": {"value":  0.5},
                "attenuation_1550nm": {"value":  0.6}
            }
        )
        assert isinstance(tech_spec, ConnectorTechSpecVO)
        self.assertEqual(tech_spec.attenuation_1310nm.value, 0.5)
        self.assertEqual(tech_spec.attenuation_1550nm.value, 0.6)

    def test_connector_tech_spec_to_primitives(self):
        tech_spec = ConnectorTechSpecVO(
            attenuation_1310nm=AttenuationVO(value=0.5),
            attenuation_1550nm=AttenuationVO(value=0.6)
        )
        self.assertEqual(tech_spec.to_primitives(), {
            "attenuation_1310nm": {"value":  0.5},
            "attenuation_1550nm": {"value":  0.6}
        })


class TestInheritanceCablePydanticTypes(unittest.TestCase):
    def test_cable_tech_spec_instance(self):
        tech_spec = CableTechSpecVO(
            attenuation_1310nm=AttenuationVO(value=0.5),
            attenuation_1550nm=AttenuationVO(value=0.6),
            number_of_filaments=NumberOfFilamentsVO(value=1)
        )
        self.assertEqual(tech_spec.attenuation_1310nm.value, 0.5)
        self.assertEqual(tech_spec.attenuation_1550nm.value, 0.6)
        self.assertEqual(tech_spec.number_of_filaments.value, 1)

    def test_cable_tech_spec_error_when_attenuation_default_is_invalid(self):
        with self.assertRaises(ValueError):
            CableTechSpecVO(
                attenuation_1310nm=AttenuationVO(value=0),
                attenuation_1550nm=AttenuationVO(value=0.6),
            )

    def test_cable_tech_spec_error_when_attenuation_is_none(self):
        with self.assertRaises(ValueError):
            CableTechSpecVO(
                attenuation_1310nm=None,
                attenuation_1550nm=AttenuationVO(value=0.6),
                number_of_filaments=NumberOfFilamentsVO(value=1)
            )

    def test_cable_tech_spec_error_when_number_of_filaments_is_zero(self):
        with self.assertRaises(ValueError):
            CableTechSpecVO(
                attenuation_1310nm=None,
                attenuation_1550nm=AttenuationVO(value=0.6),
                number_of_filaments=NumberOfFilamentsVO(value=0)
            )

    def test_cable_tech_spec_from_primitives(self):
        tech_spec = CableTechSpecVO.from_primitives(
            {
                "attenuation_1310nm": {"value":  0.5},
                "attenuation_1550nm": {"value":  0.6},
                "number_of_filaments": {"value":  1}
            }
        )
        assert isinstance(tech_spec, CableTechSpecVO)
        self.assertEqual(tech_spec.attenuation_1310nm.value, 0.5)
        self.assertEqual(tech_spec.attenuation_1550nm.value, 0.6)
        self.assertEqual(tech_spec.number_of_filaments.value, 1)

    def test_cable_tech_spec_to_primitives(self):
        tech_spec = CableTechSpecVO(
            attenuation_1310nm=AttenuationVO(value=0.5),
            attenuation_1550nm=AttenuationVO(value=0.6),
            number_of_filaments=NumberOfFilamentsVO(value=1)
        )
        self.assertEqual(tech_spec.to_primitives(), {
            "attenuation_1310nm": {"value":  0.5},
            "attenuation_1550nm": {"value":  0.6},
            "number_of_filaments": {"value":  1}
        })
