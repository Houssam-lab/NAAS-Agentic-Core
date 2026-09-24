#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module France Validator — Hard Currency Engine
Audit et assainissement des référentiels clients/fournisseurs pour la réforme de la facturation électronique française (RFE).
"""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm(s: str) -> str:
    s = strip_accents((s or "").upper())
    return re.sub(r"[^A-Z0-9]", "", s)


def luhn_ok(digits: str) -> bool:
    """Vérification de l'algorithme de Luhn officiel."""
    if not digits.isdigit():
        return False
    total, length = 0, len(digits)
    for i, ch in enumerate(digits):
        d = int(ch)
        if (length - i) % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def siren_check(siren: str) -> tuple[bool, str, str]:
    """Validation d'un SIREN (9 chiffres, Luhn)."""
    s = re.sub(r"\D", "", siren or "")
    if len(s) != 9:
        return False, s, f"Longueur {len(s)} ≠ 9"
    if not luhn_ok(s):
        return False, s, "Échec contrôle Luhn"
    return True, s, "OK"


def siret_check(siret: str) -> tuple[bool, str, str]:
    """Validation d'un SIRET (14 chiffres, Luhn)."""
    s = re.sub(r"\D", "", siret or "")
    if len(s) != 14:
        return False, s, f"Longueur {len(s)} ≠ 14"
    if not luhn_ok(s):
        return False, s, "Échec contrôle Luhn"
    return True, s, "OK"


def tva_fr_check(tva: str) -> tuple[bool, str, str]:
    """Validation du numéro de TVA intracommunautaire français (FR + clé 2 chiffres + SIREN)."""
    t = re.sub(r"[\s.]", "", (tva or "").upper())
    m = re.fullmatch(r"FR(\d{2})(\d{9})", t)
    if not m:
        return False, t, "Format invalide (attendu FR + 2 chiffres + 9 chiffres SIREN)"
    key, siren = m.group(1), m.group(2)
    expected_key = str((12 + 3 * (int(siren) % 97)) % 97).zfill(2)
    if key != expected_key:
        return False, t, f"Clé erronée ({key} ≠ attendu {expected_key})"
    return True, t, "OK"


def audit_french_csv(csv_path: Path) -> dict:
    """Audit complet d'un fichier CSV de tiers pour le marché français."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {csv_path}")

    results = {
        "total": 0,
        "valides": 0,
        "erreurs_siren": 0,
        "erreurs_siret": 0,
        "erreurs_tva": 0,
        "doublons": 0,
        "anomalies": [],
        "annotees": [],
    }

    seen_dedup: dict[str, int] = {}

    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        valid_lines = [line for line in f if not line.strip().startswith("#")]
        if not valid_lines:
            return results

        delimiter = ";" if ";" in valid_lines[0] else ","
        reader = csv.DictReader(valid_lines, delimiter=delimiter)
        fields = reader.fieldnames or []

        col_nom = next((c for c in fields if re.search(r"nom|raison|client|fournisseur", c, re.I)), None)
        col_siren = next((c for c in fields if re.search(r"siren", c, re.I)), None)
        col_siret = next((c for c in fields if re.search(r"siret", c, re.I)), None)
        col_tva = next((c for c in fields if re.search(r"tva|vat", c, re.I)), None)
        col_cp = next((c for c in fields if re.search(r"cp|postal|zip", c, re.I)), None)

        for line_no, row in enumerate(reader, start=2):
            results["total"] += 1
            line_errors = []

            nom_val = row.get(col_nom, "") if col_nom else ""
            siren_val = row.get(col_siren, "") if col_siren else ""
            siret_val = row.get(col_siret, "") if col_siret else ""
            tva_val = row.get(col_tva, "") if col_tva else ""
            cp_val = row.get(col_cp, "") if col_cp else ""

            # SIREN
            if siren_val:
                ok_s, _, err_s = siren_check(siren_val)
                if not ok_s:
                    results["erreurs_siren"] += 1
                    line_errors.append(f"SIREN_INVALID({err_s})")
            elif siret_val:
                siren_from_siret = re.sub(r"\D", "", siret_val)[:9]
                ok_s, _, err_s = siren_check(siren_from_siret)
                if not ok_s:
                    results["erreurs_siren"] += 1
                    line_errors.append(f"SIREN_DERIVE_INVALID({err_s})")
            else:
                results["erreurs_siren"] += 1
                line_errors.append("SIREN_MANQUANT")

            # SIRET
            if siret_val:
                ok_st, _, err_st = siret_check(siret_val)
                if not ok_st:
                    results["erreurs_siret"] += 1
                    line_errors.append(f"SIRET_INVALID({err_st})")

            # TVA
            if tva_val:
                ok_tva, _, err_tva = tva_fr_check(tva_val)
                if not ok_tva:
                    results["erreurs_tva"] += 1
                    line_errors.append(f"TVA_INVALID({err_tva})")

            # Doublons
            dedup_key = f"{norm(nom_val)}_{norm(cp_val)}"
            if dedup_key and len(dedup_key) > 5:
                if dedup_key in seen_dedup:
                    results["doublons"] += 1
                    line_errors.append(f"DOUBLON_AVEC_LIGNE_{seen_dedup[dedup_key]}")
                else:
                    seen_dedup[dedup_key] = line_no

            if line_errors:
                results["anomalies"].append({
                    "ligne": line_no,
                    "nom": nom_val,
                    "siren": siren_val or siret_val[:9] if siret_val else "",
                    "erreurs": line_errors,
                })
            else:
                results["valides"] += 1

            row_ann = dict(row)
            row_ann["ANOMALIES_RFE"] = "; ".join(line_errors) if line_errors else "CONFORME"
            results["annotees"].append(row_ann)

    return results


def format_french_report(results: dict, filename: str) -> str:
    total = results["total"]
    valides = results["valides"]
    pct = (valides / total * 100) if total > 0 else 0.0

    lines = [
        f"# Rapport d'Audit Référentiels RFE France — {filename}",
        f"**Date :** 2026-09-24 · **Cadre Réglementaire :** Réforme Facturation Électronique (DGFiP / Factur-X)",
        "",
        "## 1. Synthèse de Conformité",
        f"| Indicateur | Résultat | Statut |",
        f"|---|---|---|",
        f"| Fiches traitées | **{total}** | Base totale |",
        f"| Fiches prêtes à l'émission | **{valides}** ({pct:.1f}%) | "
        f"{'🟢 Excellent' if pct > 90 else '🔴 Blocages majeurs détectés'} |",
        f"| Erreurs SIREN / SIRET | **{results['erreurs_siren'] + results['erreurs_siret']}** | Rejet immédiat sur l'annuaire |",
        f"| Erreurs TVA intracommunautaire | **{results['erreurs_tva']}** | Risque d'invalidation fiscale |",
        f"| Doublons détectés | **{results['doublons']}** | Risque de multi-routage |",
        "",
        "## 2. Risques Financiers pour l'Entreprise",
        "- **Pénalités de conformité :** 50 € par facture non conforme (plafonnée à 15 000 €/an par assujetti).",
        f"- **Impact immédiat :** {total - valides} fiches tiers nécessitent une remédiation avant injection dans votre PDP.",
        "",
        "## 3. Plan d'Action Recommandé",
        "1. Correction algorithmique des SIREN et dérivation automatique des TVA conformes.",
        "2. Rapprochement avec la base INSEE Sirene via API publique.",
        "3. Fusion des fiches doublons.",
    ]

    if results["anomalies"]:
        lines.append("")
        lines.append("## 4. Échantillon des Anomalies")
        lines.append("| Ligne | Nom | SIREN | Erreurs Détectées |")
        lines.append("|---|---|---|---|")
        for item in results["anomalies"][:15]:
            lines.append(f"| {item['ligne']} | {item['nom']} | {item['siren']} | {', '.join(item['erreurs'])} |")

    return "\n".join(lines)
