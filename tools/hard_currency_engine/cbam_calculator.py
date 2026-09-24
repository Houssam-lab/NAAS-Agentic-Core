#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module CBAM Calculator — Hard Currency Engine
Calculateur d'arbitrage carbone et générateur de déclarations XML pour le Mécanisme d'Ajustement Carbone aux Frontières (UE).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from xml.dom import minidom

CBAM_CATALOG = {
    "72071114": {
        "nom": "Billettes d'acier non allié (Filière DRI-EAF)",
        "secteur": "Acier / Fer",
        "see_default": 1.629,
        "see_actual_dz": 0.950,
        "bm_free_alloc": 0.453,
        "installation_nom": "Tosyali Iron Steel Industry Algerie SPA",
        "installation_pays": "DZ",
        "installation_coordonnees": "35.807, -0.278",
    },
    "72142000": {
        "nom": "Ronds à béton crénelés (Rebar)",
        "secteur": "Acier / Construction",
        "see_default": 1.780,
        "see_actual_dz": 1.050,
        "bm_free_alloc": 0.410,
        "installation_nom": "Algerian Qatari Steel (AQS)",
        "installation_pays": "DZ",
        "installation_coordonnees": "36.758, 6.042",
    },
    "31021000": {
        "nom": "Urée contenant plus de 45% d'azote",
        "secteur": "Engrais azotés",
        "see_default": 1.340,
        "see_actual_dz": 0.880,
        "bm_free_alloc": 0.380,
        "installation_nom": "Sorfert Algerie SPA",
        "installation_pays": "DZ",
        "installation_coordonnees": "35.815, -0.290",
    },
    "28141000": {
        "nom": "Ammoniac anhydre",
        "secteur": "Engrais / Chimie",
        "see_default": 2.250,
        "see_actual_dz": 1.720,
        "bm_free_alloc": 0.520,
        "installation_nom": "Fertial Annaba / Sorfert",
        "installation_pays": "DZ",
        "installation_coordonnees": "36.850, 7.760",
    },
    "25231000": {
        "nom": "Clinkers de ciment",
        "secteur": "Ciment",
        "see_default": 0.870,
        "see_actual_dz": 0.760,
        "bm_free_alloc": 0.693,
        "installation_nom": "GICA Biskra / LafargeHolcim Algérie",
        "installation_pays": "DZ",
        "installation_coordonnees": "34.850, 5.730",
    },
}

CBAM_FACTOR_2026 = 0.975
CERT_PRICE_DEFAULT = 75.0
PENALTY_RATE = 100.0


def calculate_cbam(hs_code: str, tonnes: float, see_override: float | None = None, cert_price: float = CERT_PRICE_DEFAULT) -> dict:
    if hs_code not in CBAM_CATALOG:
        raise ValueError(f"Code SH {hs_code} non répertorié.")

    item = CBAM_CATALOG[hs_code]
    see_act = see_override if see_override is not None else item["see_actual_dz"]
    see_def = item["see_default"]
    bm = item["bm_free_alloc"]

    exp_factor = 1.0 - CBAM_FACTOR_2026

    net_def_t = max(0.0, see_def - bm * CBAM_FACTOR_2026) * exp_factor
    net_act_t = max(0.0, see_act - bm * CBAM_FACTOR_2026) * exp_factor

    cost_def = tonnes * net_def_t * cert_price
    cost_act = tonnes * net_act_t * cert_price

    saving_total = cost_def - cost_act
    penalty_avoided = tonnes * see_act * PENALTY_RATE

    return {
        "code_hs": hs_code,
        "produit": item["nom"],
        "secteur": item["secteur"],
        "installation": item["installation_nom"],
        "pays_origine": item["installation_pays"],
        "tonnes": tonnes,
        "prix_certificat": cert_price,
        "see_default": see_def,
        "see_actual": see_act,
        "gain_carbone_tonne": see_def - see_act,
        "cout_default": cost_def,
        "cout_actual": cost_act,
        "economie_totale": saving_total,
        "economie_par_tonne": saving_total / tonnes if tonnes > 0 else 0.0,
        "penalite_evitee": penalty_avoided,
    }


def generate_cbam_xml(res: dict, declarant_eori: str = "FR12345678900012") -> str:
    """Génère un extrait XML conforme au portail déclaratif CBAM de la Commission Européenne."""
    root = ET.Element("CBAMDeclaration", attrib={
        "xmlns": "urn:eu:cbam:v1:declaration",
        "regulation": "EU-2023-956",
        "year": "2026",
    })

    declarant = ET.SubElement(root, "AuthorisedDeclarant")
    ET.SubElement(declarant, "EORINumber").text = declarant_eori
    ET.SubElement(declarant, "Role").text = "IMPORTER"

    goods_item = ET.SubElement(root, "ImportedGoodsItem")
    ET.SubElement(goods_item, "CNCode").text = res["code_hs"]
    ET.SubElement(goods_item, "Description").text = res["produit"]
    ET.SubElement(goods_item, "MassInTonnes").text = f"{res['tonnes']:.2f}"
    ET.SubElement(goods_item, "CountryOfOrigin").text = res["pays_origine"]

    installation = ET.SubElement(goods_item, "ProductionInstallation")
    ET.SubElement(installation, "Name").text = res["installation"]
    ET.SubElement(installation, "Country").text = res["pays_origine"]

    emissions = ET.SubElement(goods_item, "EmbeddedEmissions")
    ET.SubElement(emissions, "CalculationMethod").text = "ACTUAL_INSTALLATION_DATA"
    ET.SubElement(emissions, "SpecificDirectEmissions").text = f"{res['see_actual']:.4f}"
    ET.SubElement(emissions, "SpecificIndirectEmissions").text = "0.0000"
    ET.SubElement(emissions, "DefaultValueAvoided").text = f"{res['see_default']:.4f}"

    financial = ET.SubElement(goods_item, "FinancialImpact")
    ET.SubElement(financial, "TotalCertificatesRequired").text = f"{(res['cout_actual'] / res['prix_certificat']):.2f}"
    ET.SubElement(financial, "CarbonCostSavingsEUR").text = f"{res['economie_totale']:.2f}"

    rough_string = ET.tostring(root, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
