# Outil verify_referentiels — diagnostic SIREN/SIRET/TVA (outil du kit e-invoicing)

**Usage quand le client envoie son fichier (20 fiches ou plus) :**

```bash
# 1. Diagnostic local (clés, cohérence, doublons, normalisation) — sans réseau
python3 tools/fr_einvoicing/verify_referentiels.py fichier_client.csv --out rapport.md --csv annote.csv

# 2. Ajouter la vérification d'existence & d'état administratif (API publique SIRENE, gratuite)
python3 tools/fr_einvoicing/verify_referentiels.py fichier_client.csv --online --out rapport.md
```

- Sortie : rapport Markdown prêt à joindre au mail de livraison + CSV annoté (colonne `DEFAUTS_DETECTED`).
- Délai de livraison réel : **< 1 h** pour 20 fiches, < 2 h pour 500 fiches en `--online` (5 req/s max, limites API respectées).
- ⛔ Règles du dossier commercial : identifiants légaux uniquement (jamais d'e-mails de personnes physiques), aucune décision de fusion exécutée chez le client sans son arbitrage, suppression des données confirmée par écrit après livraison.
- Test validé le 2026-09-22 sur `docs/commercial/outreach/demo/DEMO_20_FICHES.csv` (offline + online).
