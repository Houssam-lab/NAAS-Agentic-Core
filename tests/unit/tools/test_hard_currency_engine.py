#!/usr/bin/env python3
"""
Tests unitaires pour la suite Hard Currency Engine (HCE).
Couvre la validation France, Belgique Peppol, CBAM, ZATCA, EAA et CRM.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.hard_currency_engine.belgium_validator import (
    audit_belgian_csv,
    export_cleaned_belgian_csv,
    format_peppol_id,
    validate_bce_modulo97,
    validate_belgian_vat,
)
from tools.hard_currency_engine.cbam_calculator import (
    calculate_cbam,
    calculate_cbam_batch,
    generate_cbam_xml,
    generate_sensitivity_table,
)
from tools.hard_currency_engine.crm_dispatcher import (
    generate_personalized_dispatch,
)
from tools.hard_currency_engine.eaa_scanner import (
    audit_html_content,
    generate_declaration_accessibilite,
)
from tools.hard_currency_engine.france_validator import (
    audit_french_csv,
    compute_french_vat_key,
    export_cleaned_french_csv,
    luhn_ok,
    siren_check,
    siret_check,
    tva_fr_check,
)
from tools.hard_currency_engine.zatca_validator import (
    GENESIS_PIH,
    audit_zatca_batch,
    canonical_invoice_hash,
    decode_zatca_tlv,
    encode_zatca_tlv,
    repair_zatca_chain,
    validate_uuid_v4,
    validate_zatca_vat_number,
)


class TestFranceValidator(unittest.TestCase):
    def test_luhn_algorithm(self):
        self.assertTrue(luhn_ok("501058812"))
        self.assertTrue(luhn_ok("443061841"))
        self.assertFalse(luhn_ok("501058813"))

    def test_siren_and_siret(self):
        ok, clean, _msg = siren_check("501 058 812")
        self.assertTrue(ok)
        self.assertEqual(clean, "501058812")

        ok_bad, _, _ = siren_check("12345")
        self.assertFalse(ok_bad)

        ok_st, clean_st, _ = siret_check("50105881210005")
        self.assertTrue(ok_st)
        self.assertEqual(clean_st, "50105881210005")

    def test_french_vat_derivation(self):
        ok, formatted, _ = tva_fr_check("FR64443061841")
        self.assertTrue(ok)
        self.assertEqual(formatted, "FR64443061841")

        computed = compute_french_vat_key("443061841")
        self.assertEqual(computed, "FR64443061841")

        ok_wrong, _, msg = tva_fr_check("FR99443061841")
        self.assertFalse(ok_wrong)
        self.assertIn("Clé erronée", msg)

    def test_french_audit_and_export_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "test_tiers.csv"
            csv_out = Path(tmpdir) / "test_clean.csv"
            # Encode with ISO-8859-1 (common Sage export)
            content = (
                "Raison_sociale;SIREN;SIRET;Num_TVA_intracom;Code_postal\n"
                "Google France;443061841;44306184100047;FR64443061841;75009\n"
                "Fausse Entité;123456789;12345678900012;FR40123456789;31000\n"
            )
            csv_in.write_bytes(content.encode("iso-8859-1"))

            res = audit_french_csv(csv_in)
            self.assertEqual(res["total"], 2)
            self.assertEqual(res["valides"], 1)

            export_cleaned_french_csv(res, csv_out)
            self.assertTrue(csv_out.exists())
            out_txt = csv_out.read_text(encoding="utf-8-sig")
            self.assertIn("STATUT_RFE", out_txt)
            self.assertIn("FR64443061841", out_txt)


class TestBelgiumValidator(unittest.TestCase):
    def test_bce_modulo97(self):
        ok, formatted, _msg = validate_bce_modulo97("0123.456.749")
        self.assertTrue(ok)
        self.assertEqual(formatted, "0123.456.749")

        ok_bad, _, msg_bad = validate_bce_modulo97("0123.456.750")
        self.assertFalse(ok_bad)
        self.assertIn("Échec Modulo 97", msg_bad)

    def test_belgian_vat_and_peppol_id(self):
        ok, vat, _ = validate_belgian_vat("BE0123456749")
        self.assertTrue(ok)
        self.assertEqual(vat, "BE0123456749")

        peppol_id = format_peppol_id("0123.456.749")
        self.assertEqual(peppol_id, "0208:0123456749")

    def test_belgian_audit_and_export_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_in = Path(tmpdir) / "test_be.csv"
            csv_out = Path(tmpdir) / "test_be_clean.csv"
            content = (
                "Raison_sociale;Numero_BCE;Numero_TVA;Code_postal\n"
                "Société Conforme;0123.456.749;BE0123456749;1000\n"
            )
            csv_in.write_bytes(content.encode("cp1252"))

            res = audit_belgian_csv(csv_in)
            self.assertEqual(res["total"], 1)
            self.assertEqual(res["valides"], 1)

            export_cleaned_belgian_csv(res, csv_out)
            self.assertTrue(csv_out.exists())
            out_txt = csv_out.read_text(encoding="utf-8-sig")
            self.assertIn("0208:0123456749", out_txt)
            self.assertIn("COMPATIBLE", out_txt)


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

    def test_cbam_batch_and_sensitivity(self):
        rows = [
            {"code_hs": "72071114", "tonnes": 5000},
            {"code_hs": "31021000", "tonnes": 3000},
        ]
        b_res = calculate_cbam_batch(rows, cert_price=80.0)
        self.assertEqual(b_res["nb_lignes"], 2)
        self.assertEqual(b_res["total_tonnes"], 8000.0)
        self.assertGreater(b_res["economie_globale_eur"], 5000.0)

        single = calculate_cbam("72071114", tonnes=1000)
        sens = generate_sensitivity_table(single)
        self.assertEqual(len(sens), 5)
        self.assertEqual(sens[0]["prix_co2"], 65.0)


class TestZATCAValidator(unittest.TestCase):
    def test_uuid_v4(self):
        self.assertTrue(validate_uuid_v4("c2b9a8f4-7e3d-4c8e-a9b1-5d2f6e8a7c3b"))
        self.assertFalse(validate_uuid_v4("not-a-uuid"))

    def test_vat_validation(self):
        ok, _ = validate_zatca_vat_number("300000000000003")
        self.assertTrue(ok)
        ok_bad, msg = validate_zatca_vat_number("100000000000002")
        self.assertFalse(ok_bad)
        self.assertIn("débuter", msg)

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

    def test_canonical_hash_and_chain_repair(self):
        ch = canonical_invoice_hash("<Invoice><ID>100</ID></Invoice>")
        self.assertEqual(len(ch), 44)

        # Broken chain: ICV jump from 1 to 3
        broken = [
            {
                "id": "INV-1",
                "icv": 1,
                "uuid": "c2b9a8f4-7e3d-4c8e-a9b1-5d2f6e8a7c3b",
                "pih": GENESIS_PIH,
                "invoice_hash": "47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=",
            },
            {
                "id": "INV-2",
                "icv": 3,
                "uuid": "invalid",
                "pih": "WRONG_PIH",
                "invoice_hash": "broken",
            },
        ]
        audit_before = audit_zatca_batch(broken)
        self.assertFalse(audit_before["est_valide"])

        repaired, actions = repair_zatca_chain(broken)
        self.assertTrue(len(actions) > 0)
        audit_after = audit_zatca_batch(repaired)
        self.assertTrue(audit_after["est_valide"])
        self.assertEqual(repaired[1]["icv"], 2)


class TestEAAScanner(unittest.TestCase):
    def test_html_audit_and_declaration(self):
        bad_html = "<html><body><img src='logo.png'><input type='text'></body></html>"
        res = audit_html_content(bad_html)
        self.assertFalse(res["est_conforme"])
        self.assertTrue(res["score_accessibilite"] < 100.0)
        self.assertTrue(len(res["guide_remediation"]) > 0)

        decl = generate_declaration_accessibilite(
            "SuperRetail",
            "SuperRetail.fr",
            "https://superretail.fr",
            taux_conformite=res["score_accessibilite"],
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
