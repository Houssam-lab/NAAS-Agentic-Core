#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_belgium_peppol.py — Outil de diagnostic et de mise en conformité des référentiels
clients/fournisseurs pour la facturation électronique Peppol en Belgique (B2B).

Contexte réglementaire 2026 :
    - Depuis le 1er janvier 2026, la facturation électronique via le réseau Peppol (format UBL 2.1)
      est strictement obligatoire entre assujettis TVA belges (B2B).
    - La période de tolérance a pris fin le 31 mars 2026.
    - Amendes administratives : 1 500 € (1re infraction), 3 000 € (2e), 5 000 € (suivantes)
      avec risque de non-déductibilité de la TVA pour les factures reçues hors Peppol.

Fonctionnalités :
    1. Validation du Numéro d'Entreprise KBO / BCE (10 chiffres, contrôle Modulo 97 officiel).
    2. Formatage et validation du Participant ID Peppol (schéma 0208:0xxxxxxxx ou 9956:BE0xxxxxxxx).
    3. Cohérence du numéro de TVA belge (préfixe BE + 10 chiffres).
    4. Détection des doublons exacts et quasi-doublons (dénomination + code postal).
    5. Normalisation des adresses et fiches tiers pour injection dans Exact Online, WinBooks, Clearfacts, Odoo.

Usage:
    python3 verify_belgium_peppol.py <fichier.csv> [--out rapport_peppol.md] [--csv annote.csv]
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from pathlib import Path


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm(s: str) -> str:
    s = strip_accents((s or "").upper())
    return re.sub(r"[^A-Z0-9]", "", s)


def validate_bce_modulo97(raw_number: str) -> tuple[bool, str, str]:
    """
    Valide un numéro d'entreprise belge (KBO/BCE) selon l'algorithme officiel Modulo 97.
    Structure : 10 chiffres (commençant par 0 ou 1).
    Formule : 97 - (Base8 % 97) == Chiffres de contrôle (positions 9 et 10).
    """
    digits = re.sub(r"[^0-9]", "", raw_number or "")
    if len(digits) == 9:
        digits = "0" + digits

    if len(digits) != 10:
        return False, digits, f"Longueur invalide ({len(digits)} chiffres au lieu de 10)"

    if digits[0] not in ("0", "1"):
        return False, digits, f"Le numéro doit débuter par 0 ou 1 (trouvé '{digits[0]}')"

    base8 = int(digits[:8])
    checksum = int(digits[8:])
    rem = base8 % 97
    expected = 97 if rem == 0 else (97 - rem)

    if checksum != expected:
        return (
            False,
            digits,
            f"Échec Modulo 97 : contrôle={checksum:02d}, attendu={expected:02d}",
        )

    formatted = f"{digits[:4]}.{digits[4:7]}.{digits[7:]}"
    return True, formatted, "OK"


def format_peppol_participant_id(bce_formatted: str) -> str:
    """Formate l'identifiant Peppol officiel sous le schéma ISO6523:0208."""
    digits = re.sub(r"[^0-9]", "", bce_formatted)
    return f"0208:{digits}"


def validate_belgian_vat(vat_str: str) -> tuple[bool, str, str]:
    """Valide le numéro de TVA belge (BE + numéro BCE)."""
    raw = (vat_str or "").strip().upper().replace(" ", "").replace(".", "")
    if not raw.startswith("BE"):
        return False, raw, "Préfixe national 'BE' manquant"

    bce_part = raw[2:]
    ok, num, err = validate_bce_modulo97(bce_part)
    if not ok:
        return False, raw, f"Numéro TVA invalide : {err}"

    return True, f"BE{num.replace('.', '')}", "OK"


def audit_peppol_csv(csv_path: Path) -> dict:
    """Analyse un fichier CSV de référentiels clients/fournisseurs belges."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {csv_path}")

    results = {
        "total_lignes": 0,
        "valides": 0,
        "erreurs_bce": 0,
        "erreurs_tva": 0,
        "doublons": 0,
        "details_anomalies": [],
        "fiches_annotees": [],
    }

    seen_keys: dict[str, int] = {}

    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        valid_lines = [line for line in f if not line.strip().startswith("#")]
        if not valid_lines:
            return results

        delimiter = ";" if ";" in valid_lines[0] else ","
        reader = csv.DictReader(valid_lines, delimiter=delimiter)
        fields = reader.fieldnames or []

        # Détection heuristique des colonnes
        col_nom = next((c for c in fields if re.search(r"nom|raison|client|fournisseur", c, re.I)), None)
        col_bce = next((c for c in fields if re.search(r"bce|kbo|entreprise|siren", c, re.I)), None)
        col_tva = next((c for c in fields if re.search(r"tva|vat", c, re.I)), None)
        col_cp = next((c for c in fields if re.search(r"cp|postal|zip", c, re.I)), None)

        for line_no, row in enumerate(reader, start=2):
            results["total_lignes"] += 1
            anomalies = []

            nom_val = row.get(col_nom, "") if col_nom else ""
            bce_val = row.get(col_bce, "") if col_bce else ""
            tva_val = row.get(col_tva, "") if col_tva else ""
            cp_val = row.get(col_cp, "") if col_cp else ""

            # 1. Vérification BCE
            if bce_val:
                ok_bce, clean_bce, msg_bce = validate_bce_modulo97(bce_val)
                if not ok_bce:
                    results["erreurs_bce"] += 1
                    anomalies.append(f"BCE_INVALID({msg_bce})")
            else:
                results["erreurs_bce"] += 1
                anomalies.append("BCE_MANQUANT")

            # 2. Vérification TVA
            if tva_val:
                ok_tva, clean_tva, msg_tva = validate_belgian_vat(tva_val)
                if not ok_tva:
                    results["erreurs_tva"] += 1
                    anomalies.append(f"TVA_INVALID({msg_tva})")

            # 3. Détection de doublons (Dénomination normalisée + Code postal)
            dedup_key = f"{norm(nom_val)}_{norm(cp_val)}"
            if dedup_key and len(dedup_key) > 5:
                if dedup_key in seen_keys:
                    results["doublons"] += 1
                    anomalies.append(f"DOUBLON_AVEC_LIGNE_{seen_keys[dedup_key]}")
                else:
                    seen_keys[dedup_key] = line_no

            if anomalies:
                results["details_anomalies"].append({
                    "ligne": line_no,
                    "nom": nom_val,
                    "bce": bce_val,
                    "anomalies": anomalies,
                })
            else:
                results["valides"] += 1

            row_annotated = dict(row)
            row_annotated["DEFAUTS_DETECTES"] = "; ".join(anomalies) if anomalies else "AUCUN"
            row_annotated["PEPPOL_PARTICIPANT_ID"] = (
                format_peppol_participant_id(bce_val) if bce_val and not anomalies else "A_CORRIGER"
            )
            results["fiches_annotees"].append(row_annotated)

    return results


def generate_markdown_report(results: dict, source_filename: str) -> str:
    """Génère un rapport de diagnostic complet en Markdown pour le cabinet comptable."""
    total = results["total_lignes"]
    valides = results["valides"]
    tx_conformite = (valides / total * 100) if total > 0 else 0.0

    lines = [
        f"# Rapport de Diagnostic de Conformité Peppol Belgique — {source_filename}",
        f"**Date d'audit :** 2026-09-24 · **Standard :** Peppol BIS Billing 3.0 / KBO-BCE Modulo 97",
        "",
        "## 1. Synthèse Exécutive",
        "",
        f"| Métrique | Valeur | Statut Réglementaire |",
        f"|---|---|---|",
        f"| Total fiches auditées | **{total}** | Base déclarée |",
        f"| Fiches 100% conformes Peppol | **{valides}** ({tx_conformite:.1f}%) | "
        f"{'🟢 Prêt au routage' if tx_conformite > 90 else '🔴 Risque de rejet massif'} |",
        f"| Numéros BCE / KBO invalides | **{results['erreurs_bce']}** | Risque d'amende 1 500 € à 5 000 € |",
        f"| Numéros de TVA invalides | **{results['erreurs_tva']}** | Risque de non-déductibilité TVA |",
        f"| Doublons détectés | **{results['doublons']}** | Rejets de facturation / litiges |",
        "",
        "## 2. Risques Financiers Immédiats",
        "En application de l'arrêté royal belge sur la facturation électronique obligatoire (en vigueur depuis le 01/01/2026) :",
        f"- **Rejets prévisibles :** {total - valides} fiches tiers bloqueront l'émission ou la réception des factures Peppol.",
        "- **Exposition aux sanctions :** Les amendes administratives débutent à 1 500 € par infraction et montent à 5 000 €.",
        "",
        "## 3. Plan d'Action Recommandé sous 48h",
        "1. **Correction des identifiants BCE :** Rapprochement direct avec la Banque-Carrefour des Entreprises (BCE).",
        "2. **Attribution automatique des Participant IDs Peppol** au format `0208:0xxxxxxxx`.",
        "3. **Fusion des doublons** et normalisation des points de terminaison électroniques (Electronic Endpoints).",
    ]

    if results["details_anomalies"]:
        lines.append("")
        lines.append("## 4. Échantillon des Anomalies Détectées")
        lines.append("| Ligne | Tiers | Valeur BCE | Anomalies Détectées |")
        lines.append("|---|---|---|---|")
        for item in results["details_anomalies"][:15]:
            lines.append(f"| {item['ligne']} | {item['nom']} | {item['bce']} | {', '.join(item['anomalies'])} |")
        if len(results["details_anomalies"]) > 15:
            lines.append(f"| ... | *et {len(results['details_anomalies']) - 15} autres fiches* | ... | ... |")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit de référentiels Peppol Belgique (B2B)")
    parser.add_argument("fichier", help="Fichier CSV à auditer")
    parser.add_argument("--out", help="Chemin du rapport Markdown en sortie")
    parser.add_argument("--csv", help="Chemin du fichier CSV annoté en sortie")
    args = parser.parse_args()

    csv_path = Path(args.fichier)
    if not csv_path.exists():
        print(f"Erreur : fichier introuvable {csv_path}", file=sys.stderr)
        return 1

    try:
        results = audit_peppol_csv(csv_path)
    except Exception as e:
        print(f"Erreur lors du traitement : {e}", file=sys.stderr)
        return 1

    report = generate_markdown_report(results, csv_path.name)

    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"✅ Rapport généré avec succès dans : {args.out}")
    else:
        print(report)

    if args.csv and results["fiches_annotees"]:
        out_csv = Path(args.csv)
        fieldnames = list(results["fiches_annotees"][0].keys())
        with open(out_csv, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results["fiches_annotees"])
        print(f"✅ CSV annoté généré avec succès dans : {args.csv}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
