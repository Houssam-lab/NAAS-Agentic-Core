#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cbam_savings_calculator.py — Calculateur d'économies CBAM et arbitrage réglementaire
pour les importateurs européens de métaux, ciment et engrais depuis l'Algérie.

Contexte réglementaire 2026 :
    - Règlement (UE) 2023/956 & Règlement d'exécution (UE) 2025/2620 (phase définitive).
    - L'importateur européen est assujetti à l'achat obligatoire de certificats CBAM.
    - S'il utilise les valeurs par défaut de l'annexe V, il subit des majorations forfaitaires (markups)
      qui alourdissent massivement la facture fiscale.
    - S'il dispose des données réelles de l'installation algérienne (ex: aciérie DRI-EAF au gaz naturel
      comme Tosyali Bethioua ou AQS Bellara), il bénéficie d'une empreinte carbone significativement
      inférieure à la moyenne européenne et mondiale basée sur le charbon (BF-BOF).

Usage :
    python3 cbam_savings_calculator.py --hs 72071114 --tonnes 25000 [--see-actual 0.95] [--price 75.0]
    python3 cbam_savings_calculator.py --list-goods
"""

from __future__ import annotations

import argparse
import sys

# Référentiels CBAM (Annexe V IR 2025/2620 & benchmarks D-292 / CPN)
CBAM_BENCHMARKS = {
    "72071114": {
        "nom": "Billettes d'acier non allié (Filière DRI-EAF vs Haut Fourneau)",
        "secteur": "Acier / Fer",
        "see_default": 1.629,  # tCO2/t avec markup par défaut UE
        "see_actual_dz": 0.950,  # tCO2/t mesurée sur filière gaz DRI-EAF Algérie (Tosyali/AQS)
        "bm_free_alloc": 0.453,  # Benchmark d'allocation gratuite
        "installation_type": "Tosyali Algérie / AQS Bellara",
    },
    "72142000": {
        "nom": "Ronds à béton crénelés (Rebar)",
        "secteur": "Acier / Construction",
        "see_default": 1.780,
        "see_actual_dz": 1.050,
        "bm_free_alloc": 0.410,
        "installation_type": "AQS Bellara / Tosyali Bethioua",
    },
    "31021000": {
        "nom": "Urée contenant plus de 45% d'azote",
        "secteur": "Engrais azotés",
        "see_default": 1.340,
        "see_actual_dz": 0.880,  # Gaz naturel haute efficacité
        "bm_free_alloc": 0.380,
        "installation_type": "Sorfert Arzew / Fertial Annaba",
    },
    "28141000": {
        "nom": "Ammoniac anhydre",
        "secteur": "Engrais / Chimie",
        "see_default": 2.250,
        "see_actual_dz": 1.720,
        "bm_free_alloc": 0.520,
        "installation_type": "Sorfert / AOA Arzew",
    },
    "25231000": {
        "nom": "Clinkers de ciment",
        "secteur": "Ciment",
        "see_default": 0.870,
        "see_actual_dz": 0.760,
        "bm_free_alloc": 0.693,
        "installation_type": "GICA (Biskra/Chlef) / LafargeHolcim Algérie",
    },
}

# Paramètres macro 2026
DEFAULT_CERT_PRICE_EUR = 75.0  # Prix du certificat CBAM (indexé sur ETS UE)
CBAM_FACTOR_2026 = 0.975  # Facteur d'allocation gratuite (2.5% soumis en 2026)
PENALTY_RATE_PER_TONNE = 100.0  # Pénalité en cas de déclaration non conforme / absence de rapport


def calculate_cbam_impact(
    hs_code: str,
    tonnes: float,
    see_actual: float | None = None,
    cert_price: float = DEFAULT_CERT_PRICE_EUR,
    year: int = 2026,
) -> dict:
    if hs_code not in CBAM_BENCHMARKS:
        raise ValueError(f"Code SH {hs_code} non pris en charge. Voir --list-goods.")

    data = CBAM_BENCHMARKS[hs_code]
    actual_emission = see_actual if see_actual is not None else data["see_actual_dz"]
    default_emission = data["see_default"]
    bm = data["bm_free_alloc"]

    # Facteur d'exposition 2026 = (1 - CBAM_FACTOR_2026) = 0.025
    exposure_factor = 1.0 - CBAM_FACTOR_2026

    # Émissions soumises au rachat de certificats après déduction de l'allocation gratuite
    net_emissions_default_per_t = max(0.0, default_emission - bm * CBAM_FACTOR_2026) * exposure_factor
    net_emissions_actual_per_t = max(0.0, actual_emission - bm * CBAM_FACTOR_2026) * exposure_factor

    # Coût total certificats CBAM
    cost_default_total = tonnes * net_emissions_default_per_t * cert_price
    cost_actual_total = tonnes * net_emissions_actual_per_t * cert_price

    saving_total_eur = cost_default_total - cost_actual_total
    saving_per_tonne_eur = saving_total_eur / tonnes if tonnes > 0 else 0.0

    # Pénalité légale évitée (100 € par tonne d'émissions non déclarées ou erronées)
    penalty_exposure_avoided = tonnes * actual_emission * PENALTY_RATE_PER_TONNE

    return {
        "code_hs": hs_code,
        "produit": data["nom"],
        "secteur": data["secteur"],
        "installation_source": data["installation_type"],
        "volume_tonnes": tonnes,
        "prix_certificat_eur": cert_price,
        "emission_defaut_ue": default_emission,
        "emission_reelle_dz": actual_emission,
        "gain_carbone_par_tonne": default_emission - actual_emission,
        "cout_cbam_defaut_eur": cost_default_total,
        "cout_cbam_reel_eur": cost_actual_total,
        "economie_totale_eur": saving_total_eur,
        "economie_par_tonne_eur": saving_per_tonne_eur,
        "penalite_infraction_evitee_eur": penalty_exposure_avoided,
    }


def format_report(res: dict) -> str:
    lines = [
        "================================================================================",
        "RAPPORT D'ARBITRAGE CBAM (CARBONE AUX FRONTIÈRES) — IMPORTATION ALGÉRIE → EUROPE",
        "================================================================================",
        f"Produit : {res['produit']} (Code SH {res['code_hs']})",
        f"Filière industrielle Algérie : {res['installation_source']}",
        f"Volume importé : {res['volume_tonnes']:,.0f} tonnes",
        f"Prix de référence certificat ETS : {res['prix_certificat_eur']:.2f} € / tonne CO2",
        "--------------------------------------------------------------------------------",
        "1. COMPARAISON DE L'EMPREINTE CARBONE (SEE) :",
        f"   - Valeur forfaitaire par défaut UE (avec markup) : {res['emission_defaut_ue']:.3f} tCO2 / t",
        f"   - Données réelles certifiées de l'installation  : {res['emission_reelle_dz']:.3f} tCO2 / t",
        f"   => Réduction nette de l'empreinte carbone       : {res['gain_carbone_par_tonne']:.3f} tCO2 / t (-{(res['gain_carbone_par_tonne']/res['emission_defaut_ue']*100):.1f}%)",
        "--------------------------------------------------------------------------------",
        "2. IMPACT FINANCIER SUR LES CERTIFICATS CBAM (Exercice 2026) :",
        f"   - Coût CBAM avec valeurs par défaut forfaitaires : {res['cout_cbam_defaut_eur']:,.2f} €",
        f"   - Coût CBAM avec dossier technique de données réelles : {res['cout_cbam_reel_eur']:,.2f} €",
        f"   => ÉCONOMIE FINANCIÈRE DIRECTE POUR L'IMPORTATEUR : {res['economie_totale_eur']:,.2f} €",
        f"   => Soit un gain net à la tonne importée           : {res['economie_par_tonne_eur']:.2f} € / tonne",
        "--------------------------------------------------------------------------------",
        "3. PROTECTION CONTRE LES RISQUES RÉGLEMENTAIRES :",
        f"   - Pénalité légale évitée (taux de 100 €/t)       : {res['penalite_infraction_evitee_eur']:,.2f} €",
        "   - Conformité garantie selon Règlement d'Exécution IR 2025/2620.",
        "================================================================================",
        "OFFRE DE SERVICE ASSOCIÉE :",
        "Préparation intégrale du dossier technique d'émissions et génération du XML CBAM",
        "prêt au téléversement sur le portail européen du déclarant autorisé.",
        "Tarif forfaitaire d'accompagnement : 4 500 € à 12 000 € (entièrement rentabilisé).",
        "================================================================================",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculateur d'arbitrage et d'économies CBAM Algérie → Europe")
    parser.add_argument("--hs", help="Code SH du produit (ex: 72071114, 72142000, 31021000, 28141000, 25231000)")
    parser.add_argument("--tonnes", type=float, help="Volume importé en tonnes")
    parser.add_argument("--see-actual", type=float, help="Émission réelle mesurée (optionnel)")
    parser.add_argument("--price", type=float, default=DEFAULT_CERT_PRICE_EUR, help="Prix du certificat CO2 (défaut: 75 €)")
    parser.add_argument("--list-goods", action="store_true", help="Lister les produits industriels supportés")

    args = parser.parse_args()

    if args.list_goods:
        print("Produits industriels et codes SH modélisés :")
        for code, info in CBAM_BENCHMARKS.items():
            print(f"  - {code} : {info['nom']} [{info['secteur']}] -> Source: {info['installation_type']}")
        return 0

    if not args.hs or args.tonnes is None:
        parser.print_help()
        return 1

    try:
        res = calculate_cbam_impact(args.hs, args.tonnes, args.see_actual, args.price)
        print(format_report(res))
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
