#!/usr/bin/env python3
"""
verify_referentiels.py — Outil de diagnostic des référentiels clients/fournisseurs
pour la facturation électronique française.

Usage:
    python3 verify_referentiels.py <fichier.csv> [--offline] [--out rapport.md]

Mode offline (par défaut si pas de réseau): validations locales uniquement
    - clé de contrôle SIREN (Luhn)
    - longueur & clé SIRET
    - cohérence SIREN ↔ SIRET
    - format & clé TVA intracommunautaire (FR + 2 + SIREN, clé mod 97)
    - doublons exacts et quasi-doublons (nom normalisé + code postal)
    - normalisation (villes, adresses, casse)

Mode online (--online): ajoute l'interrogation de l'API publique
    https://recherche-entreprises.api.gouv.fr (gratuite, sans clé)
    → existence de l'entité, état administratif (active/radiée),
      rapprochement de la dénomination.
    ⚠️ Limiter à ~5 requêtes/seconde ; n'envoyer que des identifiants légaux.

Sortie: rapport Markdown (console + fichier) + CSV annoté optionnel (--csv annoté.csv)

Aucune donnée personnelle n'est requise : ne jamais inclure d'e-mails de personnes
physiques dans les fichiers traités (règle DPA du dossier commercial).
"""

import argparse
import csv
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------- utilitaires


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm(s: str) -> str:
    s = strip_accents((s or "").upper())
    return re.sub(r"[^A-Z0-9]", "", s)


def luhn_ok(digits: str) -> bool:
    """Validation Luhn (utilisée par SIREN/SIRET)."""
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


def siren_ok(siren: str) -> bool:
    return bool(re.fullmatch(r"\d{9}", siren)) and luhn_ok(siren)


def siret_ok(siret: str) -> bool:
    return bool(re.fullmatch(r"\d{14}", siret)) and luhn_ok(siret)


def tva_check(tva: str) -> tuple:
    """Retourne (ok_format, ok_cle, attendu)."""
    t = re.sub(r"[\s.]", "", (tva or "").upper())
    m = re.fullmatch(r"FR(\d{2})(\d{9})", t)
    if not m:
        return False, False, ""
    key, siren = m.group(1), m.group(2)
    attendu = str((12 + 3 * (int(siren) % 97)) % 97).zfill(2)
    return True, key == attendu, attendu


def norm_address(s: str) -> str:
    s = strip_accents((s or "").upper())
    s = re.sub(r"\bAV(E|\.)?\b", "AVENUE", s)
    s = re.sub(r"\bRUE\b", "RUE", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip(" ,.")


KNOWN_CITY_FIX = {"TOULOUSEE": "TOULOUSE"}


# ---------------------------------------------------------------- lecture CSV


def load_rows(path: Path):
    raw = [
        ln
        for ln in path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]
    if not raw:
        sys.exit("Fichier vide.")
    sample = "\n".join(raw[:5])
    delim = ";" if sample.count(";") >= sample.count(",") else ","
    reader = csv.DictReader(raw, delimiter=delim)
    rows = list(reader)
    cols = {c.lower().strip(): c for c in (reader.fieldnames or [])}

    def find(*patterns):
        for pat in patterns:
            for lc, orig in cols.items():
                if re.search(pat, lc):
                    return orig
        return None

    mapping = {
        "id": find(r"^id$", r"^fiche"),
        "nom": find(r"raison", r"nom", r"societe", r"denomination"),
        "siren": find(r"siren"),
        "siret": find(r"siret"),
        "adresse": find(r"adresse"),
        "cp": find(r"code_postal", r"^cp$"),
        "ville": find(r"ville"),
        "tva": find(r"tva"),
    }
    return rows, mapping, delim


# ---------------------------------------------------------------- API publique

API_URL = "https://recherche-entreprises.api.gouv.fr/search"


def api_lookup(siren: str, timeout: int = 10) -> dict:
    q = urllib.parse.urlencode({"q": siren, "limit": 1})
    req = urllib.request.Request(f"{API_URL}?{q}", headers={"User-Agent": "referentiel-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
        res = data.get("results") or []
        if not res:
            return {"trouve": False}
        e = res[0]
        siege = e.get("siege", {}) or {}
        return {
            "trouve": True,
            "etat": e.get("etat_administratif") or "?",
            "nom_officiel": (e.get("nom_complet") or "").upper(),
            "siret_siege": siege.get("siret") or "",
            "actif": (e.get("etat_administratif") == "A"),
        }
    except Exception as exc:  # réseau indisponible → on dégrade proprement
        return {"trouve": None, "erreur": str(exc)[:120]}


# ---------------------------------------------------------------- analyse


def _check_siren_siret_tva(siren, siret, tva, rid):
    findings = []
    # SIREN
    if not siren:
        findings.append((rid, "CRITIQUE", "SIREN", "manquant", "compléter avant tout envoi"))
    elif not siren_ok(siren):
        findings.append(
            (rid, "CRITIQUE", "SIREN", f"clé invalide ({siren})", "vérifier contre SIRENE")
        )

    # SIRET
    if siret and not siret_ok(siret):
        if len(siret) != 14:
            findings.append(
                (rid, "CRITIQUE", "SIRET", f"longueur {len(siret)} ≠ 14", "compléter le suffixe")
            )
        else:
            findings.append(
                (rid, "CRITIQUE", "SIRET", f"clé invalide ({siret})", "correction requise")
            )
    if siren and siret and len(siret) == 14 and not siret.startswith(siren):
        findings.append(
            (rid, "CRITIQUE", "SIRET", "ne correspond pas au SIREN", "réassocier l'établissement")
        )

    # TVA
    if tva:
        okf, okk, attendu = tva_check(tva)
        if not okf:
            findings.append(
                (rid, "CRITIQUE", "TVA", f"format invalide ({tva})", "reformater FR+2+SIREN")
            )
        elif not okk:
            findings.append(
                (
                    rid,
                    "CRITIQUE",
                    "TVA",
                    f"clé erronée ({tva}) → attendu FR{attendu}{siren or '?'}",
                    "reformater",
                )
            )
    else:
        findings.append((rid, "CRITIQUE", "TVA", "manquante", "compléter (clé = f(SIREN))"))

    return findings


def _check_row_fields(r, mapping, idx, seen_exact, seen_quasi):
    def get_val(k):
        return (r.get(mapping[k]) or "").strip() if mapping[k] else ""

    rid, nom = get_val("id") or str(idx), get_val("nom")
    siren, siret = re.sub(r"\D", "", get_val("siren")), re.sub(r"\D", "", get_val("siret"))
    ville, cp, tva = get_val("ville"), get_val("cp"), get_val("tva")

    findings = _check_siren_siret_tva(siren, siret, tva, rid)

    # doublons exacts
    key = (siren, siret)
    if key in seen_exact and siren:
        findings.append(
            (
                rid,
                "MAJEUR",
                "DOUBLON",
                f"exact = fiche {seen_exact[key]} ({nom})",
                "fusion à arbitrer chez le client",
            )
        )
    else:
        seen_exact[key] = rid

    # quasi-doublons
    qk = (norm(nom), cp)
    if nom and qk in seen_quasi and qk != ("", ""):
        findings.append(
            (
                rid,
                "MAJEUR",
                "QUASI-DOUBLON",
                f"nom+CP = fiche {seen_quasi[qk]}",
                "fusion à arbitrer",
            )
        )
    else:
        seen_quasi[qk] = rid

    # normalisation
    if ville and ville.upper() in KNOWN_CITY_FIX:
        findings.append(
            (rid, "MINEUR", "VILLE", f"« {ville} » → {KNOWN_CITY_FIX[ville.upper()]}", "normaliser")
        )
    if re.search(r"[a-zà-ÿ]{3,}", ville or "") and ville != ville.upper():
        findings.append((rid, "MINEUR", "VILLE", "casse incohérente", "tout en majuscules"))

    return findings, rid, nom, siren


def analyse(rows, mapping, online=False, sleep=0.2):
    findings = []  # (fiche, criticite, champ, detail, action)
    seen_exact = {}  # (siren,siret) -> idx
    seen_quasi = {}  # (nom_norm,cp) -> idx
    api_cache = {}

    for idx, r in enumerate(rows, start=1):
        row_findings, rid, nom, siren = _check_row_fields(r, mapping, idx, seen_exact, seen_quasi)
        findings.extend(row_findings)

        # API publique
        if online and siren and siren_ok(siren):
            if siren in api_cache:
                info = api_cache[siren]
            else:
                info = api_lookup(siren)
                api_cache[siren] = info
                time.sleep(sleep)
            if info.get("trouve") is False:
                findings.append(
                    (
                        rid,
                        "CRITIQUE",
                        "SIRENE",
                        "entité introuvable",
                        "blocage : vérifier la saisie",
                    )
                )
            elif info.get("trouve") is True:
                if not info.get("actif"):
                    findings.append(
                        (
                            rid,
                            "CRITIQUE",
                            "SIRENE",
                            f"état administratif = {info.get('etat')} (radiée ?)",
                            "retirer de la base (décision client)",
                        )
                    )
                nom_off = norm(info.get("nom_officiel") or "")
                if nom and nom_off and nom[:12] not in nom_off and nom_off[:12] not in nom:
                    findings.append(
                        (
                            rid,
                            "MINEUR",
                            "DENOMINATION",
                            f"diffère de « {info.get('nom_officiel')} »",
                            "aligner sur la raison sociale officielle",
                        )
                    )
    return findings


# ---------------------------------------------------------------- rapport


def rapport(rows, findings, online_used: bool) -> str:
    n = len(rows)
    fiches_touchees = len({f[0] for f in findings})
    scores = {"CRITIQUE": 0, "MAJEUR": 0, "MINEUR": 0}
    for f in findings:
        scores[f[1]] += 1
    quality = max(0, 100 - scores["CRITIQUE"] * 5 - scores["MAJEUR"] * 3 - scores["MINEUR"] * 1)
    lines = []
    lines.append("# RAPPORT DE DIAGNOSTIC — RÉFÉRENTIELS CLIENTS\n")
    lines.append(
        f"**Fiches analysées :** {n} · **Fiches avec défauts :** {fiches_touchees} "
        f"({100 * fiches_touchees // max(n, 1)} %) · **Score de qualité : {quality}/100**\n"
    )
    lines.append(
        f"| Criticité | Nombre |\n|---|---|\n"
        f"| 🔴 Critique (rejet probable) | {scores['CRITIQUE']} |\n"
        f"| 🟠 Majeur (doublons / routage incertain) | {scores['MAJEUR']} |\n"
        f"| 🟡 Mineur (normalisation) | {scores['MINEUR']} |\n"
    )
    if findings:
        lines.append(
            "## Détail des défauts détectés\n\n"
            "| Fiche | Criticité | Champ | Constat | Action proposée |\n|---|---|---|---|---|"
        )
        for rid, crit, champ, detail, action in findings:
            lines.append(f"| {rid} | {crit} | {champ} | {detail} | {action} |")
    else:
        lines.append("Aucun défaut détecté — référentiel propre sur les contrôles appliqués.")
    lines.append("\n## Limites de ce contrôle\n")
    lines.append(
        "- Vérifications locales : clés SIREN/SIRET (Luhn), cohérence SIREN↔SIRET, format & clé TVA, doublons, normalisation."
    )
    lines.append(
        "- "
        + (
            "Existence & état administratif vérifiés contre l'API publique recherche-entreprises.api.gouv.fr."
            if online_used
            else "Mode OFFLINE : existence des entités NON vérifiée contre SIRENE (relancer avec --online)."
        )
    )
    lines.append(
        "- Les décisions de fusion/suppression restent à la main du client ; aucune donnée comptable ou fiscale n'est touchée."
    )
    return "\n".join(lines) + "\n"


def ecrire_csv_annote(rows, mapping, findings, out: Path):
    idx_map = (
        {r.get(mapping["id"], str(i + 1)): [] for i, r in enumerate(rows, start=1)}
        if mapping["id"]
        else {}
    )
    for rid, crit, champ, detail, _action in findings:
        idx_map.setdefault(rid, []).append(f"{crit}:{champ}:{detail}")
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow([*list(rows[0].keys()), "DEFAUTS_DETECTED"])
        for rid, r in zip(idx_map, rows, strict=False):
            w.writerow([*list(r.values()), " | ".join(idx_map[rid])])


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fichier")
    ap.add_argument("--online", action="store_true", help="interroger l'API publique SIRENE")
    ap.add_argument("--out", help="écrire le rapport Markdown dans ce fichier")
    ap.add_argument("--csv", help="écrire un CSV annoté (colonne DEFAUTS_DETECTED)")
    a = ap.parse_args()

    path = Path(a.fichier)
    rows, mapping, _ = load_rows(path)
    if not mapping["siren"] and not mapping["siret"]:
        sys.exit("Colonnes SIREN/SIRET introuvables dans l'en-tête.")

    findings = analyse(rows, mapping, online=a.online)
    md = rapport(rows, findings, online_used=a.online)
    print(md)
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8")
        print(f"→ rapport écrit : {a.out}")
    if a.csv:
        ecrire_csv_annote(rows, mapping, findings, Path(a.csv))
        print(f"→ CSV annoté écrit : {a.csv}")


if __name__ == "__main__":
    main()
