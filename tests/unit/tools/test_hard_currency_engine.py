#!/usr/bin/env python3
"""
Tests unitaires pour la suite Hard Currency Engine (HCE).
Couvre la validation France, Belgique Peppol, CBAM, ZATCA, EAA et CRM.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.hard_currency_engine.belgium_validator import (
    format_peppol_id,
    validate_bce_modulo97,
    validate_belgian_vat,
)
from tools.hard_currency_engine.cbam_calculator import (
    calculate_cbam,
    generate_cbam_xml,
)
from tools.hard_currency_engine.crm_dispatcher import (
    generate_personalized_dispatch,
)
from tools.hard_currency_engine.eaa_scanner import (
    audit_html_content,
    generate_declaration_accessibilite,
)
from tools.hard_currency_engine.france_validator import (
    luhn_ok,
    siren_check,
    siret_check,
    tva_fr_check,
)
from tools.hard_currency_engine.zatca_validator import (
    GENESIS_PIH,
    audit_zatca_batch,
    decode_zatca_tlv,
    encode_zatca_tlv,
    validate_uuid_v4,
)


class TestFranceValidator(unittest.TestCase):
    def test_luhn_algorithm(self):
        # 501058812 (Balagué) -> valid Luhn
        self.assertTrue(luhn_ok("501058812"))
        # 443061841 (Google France) -> valid Luhn
        self.assertTrue(luhn_ok("443061841"))
        # Invalid
        self.assertFalse(luhn_ok("501058813"))

    def test_siren_and_siret(self):
        ok, clean, _msg = siren_check("501 058 812")
        self.assertTrue(ok)
        self.assertEqual(clean, "501058812")

        # Wrong length
        ok_bad, _, _ = siren_check("12345")
        self.assertFalse(ok_bad)

        # SIRET
        ok_st, clean_st, _ = siret_check("50105881210005")
        self.assertTrue(ok_st)
        self.assertEqual(clean_st, "50105881210005")

    def test_french_vat_derivation(self):
        # Google France: 443061841 -> Key = (12 + 3 * (443061841 % 97)) % 97 = 64
        ok, formatted, _ = tva_fr_check("FR64443061841")
        self.assertTrue(ok)
        self.assertEqual(formatted, "FR64443061841")

        # Wrong key
        ok_wrong, _, msg = tva_fr_check("FR99443061841")
        self.assertFalse(ok_wrong)
        self.assertIn("Clé erronée", msg)


class TestBelgiumValidator(unittest.TestCase):
    def test_bce_modulo97(self):
        # 0123.456.749 -> 1234567 % 97 = 48 -> 97 - 48 = 49 -> Valid!
        ok, formatted, _msg = validate_bce_modulo97("0123.456.749")
        self.assertTrue(ok)
        self.assertEqual(formatted, "0123.456.749")

        # Bad checksum
        ok_bad, _, msg_bad = validate_bce_modulo97("0123.456.750")
        self.assertFalse(ok_bad)
        self.assertIn("Échec Modulo 97", msg_bad)

    def test_belgian_vat_and_peppol_id(self):
        ok, vat, _ = validate_belgian_vat("BE0123456749")
        self.assertTrue(ok)
        self.assertEqual(vat, "BE0123456749")

        peppol_id = format_peppol_id("0123.456.749")
        self.assertEqual(peppol_id, "0208:0123456749")


class TestCBAMCalculator(unittest.TestCase):
    def test_cbam_steel_savings(self):
        res = calculate_cbam("72071114", tonnes=10000)
        self.assertEqual(res["code_hs"], "72071114")
        self.assertGreater(res["economie_totale"], 10000.0)
        self.assertGreater(res["penalite_evitee"], 900000.0)

    def test_cbam_xml_generation(self):
        res = calculate_cbam("31021000", tonnes=5000)
        xml = generate_cbam_xml(res, declarant_eori="FR98765432100011")
        self.assertIn("<CBAMDeclaration", xml)
        self.assertIn("<CNCode>31021000</CNCode>", xml)
        self.assertIn("<EORINumber>FR98765432100011</EORINumber>", xml)
        self.assertIn("Sorfert", xml)


class TestZATCAValidator(unittest.TestCase):
    def test_uuid_v4(self):
        self.assertTrue(validate_uuid_v4("c2b9a8f4-7e3d-4c8e-a9b1-5d2f6e8a7c3b"))
        self.assertFalse(validate_uuid_v4("not-a-uuid"))

    def test_tlv_encode_decode(self):
        seller = "Tosyali Algérie"
        vat = "300000000000003"
        timestamp = "2026-09-24T12:00:00Z"
        total = "10000.00"
        vat_amount = "1500.00"

        b64 = encode_zatca_tlv(seller, vat, timestamp, total, vat_amount)
        self.assertTrue(len(b64) > 20)

        decoded = decode_zatca_tlv(b64)
        self.assertEqual(decoded[1], seller)
        self.assertEqual(decoded[2], vat)
        self.assertEqual(decoded[3], timestamp)
        self.assertEqual(decoded[4], total)
        self.assertEqual(decoded[5], vat_amount)

    def test_batch_continuity(self):
        # 2 chained invoices
        h1 = "47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU="
        h2 = "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY="

        invoices = [
            {
                "id": "INV-001",
                "icv": 1,
                "uuid": "c2b9a8f4-7e3d-4c8e-a9b1-5d2f6e8a7c3b",
                "pih": GENESIS_PIH,
                "invoice_hash": h1,
            },
            {
                "id": "INV-002",
                "icv": 2,
                "uuid": "d3c0b9a5-8e4d-4d9f-b0c2-6e3f7f9b8d4c",
                "pih": h1,
                "invoice_hash": h2,
            },
        ]
        res = audit_zatca_batch(invoices)
        self.assertTrue(res["est_valide"])
        self.assertEqual(len(res["anomalies"]), 0)


class TestEAAScanner(unittest.TestCase):
    def test_html_audit_and_declaration(self):
        bad_html = "<html><body><img src='logo.png'><input type='text'></body></html>"
        res = audit_html_content(bad_html)
        self.assertFalse(res["est_conforme"])
        self.assertTrue(any("lang" in item[2] for item in res["anomalies"]))
        self.assertTrue(any("alt" in item[2] for item in res["anomalies"]))

        decl = generate_declaration_accessibilite(
            "SuperRetail", "SuperRetail.fr", "https://superretail.fr"
        )
        self.assertIn("Déclaration d’accessibilité", decl)
        self.assertIn("SuperRetail", decl)


class TestCRMDispatcher(unittest.TestCase):
    def test_dispatch_generation(self):
        target = {
            "id": "1",
            "corridor": "FR_PDP",
            "nom_entite": "Pennylane",
            "role_cible": "Head of Partnerships",
            "contact_cible": "partenaires@pennylane.com",
            "hook_accroche": "Rejets Factur-X massifs constatés",
        }
        res = generate_personalized_dispatch(target)
        self.assertEqual(res["id"], "1")
        self.assertIn("Pennylane", res["objet"])
        self.assertIn("Houssam Benmerah", res["corps"])
        self.assertIn("h.benmerah@univ-eltarf.dz", res["corps"])


if __name__ == "__main__":
    unittest.main()
