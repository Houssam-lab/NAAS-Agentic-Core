#!/usr/bin/env python3
"""
Hard Currency Engine (HCE) — Master Command Line Interface
Exécution unifiée des modules d'audit, de calcul carbone, de conformité et de prospection commerciale.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Assurer la résolution des imports relatifs et absolus
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.hard_currency_engine.belgium_validator import audit_belgian_csv, format_belgian_report
from tools.hard_currency_engine.cbam_calculator import (
    CBAM_CATALOG,
    calculate_cbam,
    generate_cbam_xml,
)
from tools.hard_currency_engine.crm_dispatcher import dispatch_campaign
from tools.hard_currency_engine.eaa_scanner import (
    audit_html_content,
    generate_declaration_accessibilite,
)
from tools.hard_currency_engine.france_validator import audit_french_csv, format_french_report
from tools.hard_currency_engine.zatca_validator import (
    decode_zatca_tlv,
    encode_zatca_tlv,
)


def cmd_france(args):
    path = Path(args.csv_file)
    res = audit_french_csv(path)
    report = format_french_report(res, path.name)
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"✅ Rapport France écrit dans : {args.out}")
    else:
        print(report)


def cmd_belgium(args):
    path = Path(args.csv_file)
    res = audit_belgian_csv(path)
    report = format_belgian_report(res, path.name)
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"✅ Rapport Belgique écrit dans : {args.out}")
    else:
        print(report)


def cmd_cbam(args):
    if args.list:
        print("Produits industriels CBAM configurés :")
        for k, v in CBAM_CATALOG.items():
            print(f"  - {k} : {v['nom']} ({v['secteur']}) -> Installation: {v['installation_nom']}")
        return

    if not args.hs or args.tonnes is None:
        print("Erreur : --hs et --tonnes sont obligatoires pour le calcul.", file=sys.stderr)
        sys.exit(1)

    res = calculate_cbam(args.hs, args.tonnes, args.see_actual, args.price)
    print("=" * 80)
    print(f"RAPPORT D'ARBITRAGE CBAM (UE 2025/2620) — {res['produit']}")
    print(f"Installation d'origine : {res['installation']} ({res['pays_origine']})")
    print(f"Volume : {res['tonnes']:,.0f} t | Prix CO2 : {res['prix_certificat']:.2f} €/t")
    print(f"Émission défaut UE (avec markup) : {res['see_default']:.3f} tCO2/t")
    print(
        f"Émission réelle mesurée Algérie  : {res['see_actual']:.3f} tCO2/t (-{(res['gain_carbone_tonne'] / res['see_default'] * 100):.1f}%)"
    )
    print(f"Coût certificats avec valeur par défaut : {res['cout_default']:,.2f} €")
    print(f"Coût certificats avec données réelles   : {res['cout_actual']:,.2f} €")
    print(
        f"💰 ÉCONOMIE NETTE POUR L'IMPORTATEUR    : {res['economie_totale']:,.2f} € ({res['economie_par_tonne']:.2f} €/t)"
    )
    print(f"🛡️  Pénalité réglementaire évitée (100€/t): {res['penalite_evitee']:,.2f} €")
    print("=" * 80)

    if args.xml:
        xml_content = generate_cbam_xml(res)
        Path(args.xml).write_text(xml_content, encoding="utf-8")
        print(f"✅ Fichier XML déclaratif généré dans : {args.xml}")


def cmd_zatca(args):
    if args.qr_encode:
        # Example format: "NomVendeur|TVA|Timestamp|Total|TVA_Montant"
        parts = args.qr_encode.split("|")
        if len(parts) < 5:
            print(
                "Format attendu pour --qr-encode : 'Vendeur|TVA15|ISO_Time|Total|TotalTVA'",
                file=sys.stderr,
            )
            sys.exit(1)
        b64 = encode_zatca_tlv(parts[0], parts[1], parts[2], parts[3], parts[4])
        print(f"TLV Base64 QR Code :\n{b64}")
    elif args.qr_decode:
        decoded = decode_zatca_tlv(args.qr_decode)
        print("QR Code TLV Décodé :")
        for tag, val in sorted(decoded.items()):
            print(f"  Tag {tag} : {val}")
    else:
        print("Utilisez --qr-encode ou --qr-decode.")


def cmd_eaa(args):
    html_text = (
        Path(args.html_file).read_text(encoding="utf-8")
        if Path(args.html_file).exists()
        else args.html_file
    )
    res = audit_html_content(html_text)
    print("=" * 80)
    print("AUDIT RAPIDE D'ACCESSIBILITÉ WEB (EAA / WCAG 2.1 AA)")
    print(
        f"Images : {res['total_images']} | Formulaires : {res['total_inputs']} | Liens : {res['total_liens']}"
    )
    print(
        f"Statut : {'🟢 Conforme' if res['est_conforme'] else '🔴 Non-conformités critiques détectées'}"
    )
    print("-" * 80)
    for niveau, ref, msg in res["anomalies"]:
        print(f"  [{niveau}] {ref} : {msg}")
    print("=" * 80)

    if args.declaration:
        decl = generate_declaration_accessibilite(
            args.company or "Entreprise E-commerce", "Boutique en ligne", "https://example.com"
        )
        Path(args.declaration).write_text(decl, encoding="utf-8")
        print(f"✅ Déclaration d'accessibilité légale générée : {args.declaration}")


def cmd_crm(args):
    csv_file = Path(args.targets_csv)
    out_dir = Path(args.output_dir)
    files = dispatch_campaign(csv_file, out_dir)
    print(
        f"✅ Campagne générée avec succès : {len(files)} messages prêts à l'envoi dans '{out_dir}'."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Hard Currency Engine — Suite d'outils d'exportation de services"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # France
    p_fr = subparsers.add_parser("france", help="Audit référentiels RFE France")
    p_fr.add_argument("csv_file", help="CSV de tiers à auditer")
    p_fr.add_argument("--out", help="Fichier rapport markdown de sortie")

    # Belgium
    p_be = subparsers.add_parser("belgium", help="Audit référentiels Peppol Belgique")
    p_be.add_argument("csv_file", help="CSV de tiers à auditer")
    p_be.add_argument("--out", help="Fichier rapport markdown de sortie")

    # CBAM
    p_cb = subparsers.add_parser("cbam", help="Calculateur d'économies CBAM")
    p_cb.add_argument("--hs", help="Code SH (ex: 72071114, 31021000)")
    p_cb.add_argument("--tonnes", type=float, help="Volume en tonnes")
    p_cb.add_argument("--see-actual", type=float, help="Valeur réelle d'émissions tCO2/t")
    p_cb.add_argument("--price", type=float, default=75.0, help="Prix du certificat ETS")
    p_cb.add_argument("--xml", help="Chemin du fichier XML de déclaration à exporter")
    p_cb.add_argument("--list", action="store_true", help="Lister les produits supportés")

    # ZATCA
    p_za = subparsers.add_parser("zatca", help="Validation et encodage ZATCA")
    p_za.add_argument(
        "--qr-encode", help="Encoder un QR TLV (format: Vendeur|TVA|Time|Total|TotalTVA)"
    )
    p_za.add_argument("--qr-decode", help="Décoder une chaîne QR Base64")

    # EAA
    p_ea = subparsers.add_parser("eaa", help="Scanner d'accessibilité EAA")
    p_ea.add_argument("html_file", help="Fichier HTML à auditer")
    p_ea.add_argument("--company", help="Nom de l'entreprise")
    p_ea.add_argument("--declaration", help="Fichier de sortie de la déclaration légale")

    # CRM
    p_cr = subparsers.add_parser("crm", help="Dispatch de campagne de prospection")
    p_cr.add_argument("targets_csv", help="CSV des cibles qualifiées")
    p_cr.add_argument(
        "--output-dir", default="outreach_campaign", help="Répertoire de sortie des emails"
    )

    args = parser.parse_args()

    if args.command == "france":
        cmd_france(args)
    elif args.command == "belgium":
        cmd_belgium(args)
    elif args.command == "cbam":
        cmd_cbam(args)
    elif args.command == "zatca":
        cmd_zatca(args)
    elif args.command == "eaa":
        cmd_eaa(args)
    elif args.command == "crm":
        cmd_crm(args)


if __name__ == "__main__":
    main()
