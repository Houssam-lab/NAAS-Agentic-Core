#!/usr/bin/env python3
"""
Module CRM Dispatcher — Hard Currency Engine
Moteur de génération et personnalisation des campagnes d'outreach direct à partir de la base de prospects qualifiés.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


def load_targets(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Fichier de cibles introuvable : {csv_path}")

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def generate_personalized_dispatch(target: dict) -> dict:
    """Génère le texte final personnalisé pour une cible donnée."""
    nom = target.get("nom_entite", "Cher Partenaire")
    corridor = target.get("corridor", "")
    role = target.get("role_cible", "Direction")
    email = target.get("contact_cible", "")
    hook = target.get("hook_accroche", "")

    # Sélection de la signature et de l'objet
    if corridor in ("FR_PDP", "FR_VULN_SECTOR"):
        subject = f"Vos rejets Factur-X : fiabilisation référentiels — {nom}"
        body = f"""Bonjour,

Votre structure {nom} prépare activement l'échéance de la facturation électronique.

Constat terrain direct : {hook}

Je prends en charge la fiabilisation intégrale de vos fichiers clients/fournisseurs :
- Détection des SIREN invalides et radiés.
- Validation des clés de TVA intracommunautaire.
- Dédoublonnage et normalisation d'adresses.

Test gratuit : vous m'adressez un échantillon de 20 fiches, je vous livre le diagnostic d'erreurs sous 24h.

Puis-je vous adresser ce premier rapport type ?

Bien cordialement,

Houssam Benmerah
Consultant Référentiels Données & Facturation Électronique
h.benmerah@univ-eltarf.dz
"""
    elif corridor == "BE_PEPPOL":
        subject = f"Peppol Belgique : mise en conformité des bases clients — {nom}"
        body = f"""Monsieur le Responsable,

Depuis janvier 2026, l'obligation Peppol B2B est entrée en vigueur en Belgique et les amendes administratives (1 500 à 5 000 €) s'appliquent désormais.

Constat : {hook}

Notre cabinet réalise l'audit d'intégrité de vos bases tiers :
- Contrôle Modulo 97 des numéros BCE / KBO.
- Attribution et validation des Participant IDs Peppol (0208:0xxxxxxxx).
- Normalisation des points d'accès électroniques.

Je vous propose un audit gratuit de 20 fiches sous 24h, sans aucun engagement.

Seriez-vous ouvert à ce que je vous transmette ce diagnostic ?

Cordialement,

Houssam Benmerah
Consultant Référentiels Peppol & Comptabilité
h.benmerah@univ-eltarf.dz
"""
    elif corridor == "EU_CBAM":
        subject = f"CBAM 2026 : optimisation carbone de vos imports Algérie — {nom}"
        body = f"""Madame, Monsieur le Responsable Douane & Achats,

Dans le cadre de la phase définitive du CBAM et de la surtaxe liée aux valeurs par défaut :
{hook}

Notre équipe d'ingénierie et conformité assure :
- Le calcul précis des émissions réelles selon le Règlement d'Exécution (UE) 2025/2620.
- La génération du fichier XML prêt pour le registre déclaratif CBAM.
- L'arbitrage financier réduisant immédiatement le volume de certificats à acheter.

Disponible pour une démonstration d'arbitrage sur l'une de vos lignes d'importation.

Bien cordialement,

Houssam Benmerah
Analyste Conformité Industrielle & CBAM
h.benmerah@univ-eltarf.dz
"""
    elif corridor == "SAUDI_ZATCA":
        subject = f"معالجة فواتير الزكاة (المرحلة 2 الموجة 24) — {nom}"
        body = f"""السلام عليكم ورحمة الله وبركاته،

الأستاذ الفاضل في {nom}،

مع بدء تطبيق غرامات الموجة 24 للمنشآت بعد انتهاء مهلة الإعفاء:
{hook}

نقدم لمكتبكم دعماً تقنياً برمجياً مستقلاً:
1. إصلاح أخطاء الترابط التشفيري وسلاسل الهاش (PIH / ICV) المرفوضة في منصة فاتورة.
2. تدقيق ملفات XML وتوليد الأختام الرقمية (ECDSA) والأكواد المتوافقة.

يسعدنا إجراء فحص تجريبي مجاني لعينة من 20 فاتورة تواجه مشكلات اعتماد وتقديم التقرير خلال 24 ساعة.

وتفضلوا بقبول فائق الاحترام،

حسام بن مراح
استشاري تدقيق البيانات والأنظمة السحابية
h.benmerah@univ-eltarf.dz
"""
    elif corridor == "EU_EAA":
        subject = f"EAA & accessibilité numérique : audit express — {nom}"
        body = f"""Bonjour,

L'European Accessibility Act (EAA) s'applique désormais à tout site marchand.
{hook}

Nous vous livrons sous 48h :
- L'audit des points de blocage critiques (panier, paiement, formulaires).
- La Déclaration d'Accessibilité légale prête à publication (évitant l'amende de 25 000 €).

Puis-je vous transmettre les premiers résultats d'audit sur votre tunnel d'achat ?

Bien à vous,

Houssam Benmerah
Auditeur Accessibilité Web EAA
h.benmerah@univ-eltarf.dz
"""
    elif corridor == "GLOBAL_AI_LABS":
        subject = f"Multilingual AI Evaluation Specialist Application — {nom}"
        body = f"""Dear Hiring Team at {nom},

I am submitting my profile as a dedicated multilingual AI evaluation engineer (Arabic, French, Darija, Python).

Value proposition: {hook}

Available 20-30h/week with daily availability on CET/UTC timezones. Ready for skill assessments immediately.

Best regards,

Houssam Benmerah
h.benmerah@univ-eltarf.dz
"""
    else:
        subject = f"Opportunité de collaboration B2B — {nom}"
        body = f"""Bonjour,

Dans le cadre de nos activités d'ingénierie et d'exportation de services : {hook}

Disponible pour un court échange technique.

Cordialement,
Houssam Benmerah
h.benmerah@univ-eltarf.dz
"""

    return {
        "id": target.get("id"),
        "destinataire": nom,
        "email": email,
        "corridor": corridor,
        "role": role,
        "objet": subject,
        "corps": body.strip(),
    }


def dispatch_campaign(csv_path: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    targets = load_targets(csv_path)
    generated_files = []

    for t in targets:
        packet = generate_personalized_dispatch(t)
        tid = packet["id"]
        safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", packet["destinataire"])
        filename = f"{int(tid):02d}_{packet['corridor']}_{safe_name}.txt"
        file_path = output_dir / filename

        content = f"""TO: {packet["email"]}
SUBJECT: {packet["objet"]}
DESTINATAIRE: {packet["destinataire"]} ({packet["role"]})
CORRIDOR: {packet["corridor"]}
================================================================================
{packet["corps"]}
"""
        file_path.write_text(content, encoding="utf-8")
        generated_files.append(file_path)

    return generated_files
