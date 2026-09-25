# Rapport d'Audit Référentiels RFE France — DEMO_20_FICHES.csv
**Date :** 2026-09-24 · **Cadre Réglementaire :** Réforme Facturation Électronique (DGFiP / Factur-X)

## 1. Synthèse de Conformité
| Indicateur | Résultat | Statut |
|---|---|---|
| Fiches traitées | **20** | Base totale |
| Fiches prêtes à l'émission | **0** (0.0%) | 🔴 Blocages majeurs détectés |
| Erreurs SIREN / SIRET | **36** | Rejet immédiat sur l'annuaire |
| Erreurs TVA intracommunautaire | **18** | Risque d'invalidation fiscale |
| Doublons détectés | **1** | Risque de multi-routage |

## 2. Risques Financiers pour l'Entreprise
- **Pénalités de conformité :** 50 € par facture non conforme (plafonnée à 15 000 €/an par assujetti).
- **Impact immédiat :** 20 fiches tiers nécessitent une remédiation avant injection dans votre PDP.

## 3. Plan d'Action Recommandé
1. Correction algorithmique des SIREN et dérivation automatique des TVA conformes.
2. Rapprochement avec la base INSEE Sirene via API publique.
3. Fusion des fiches doublons.

## 4. Échantillon des Anomalies
| Ligne | Nom | SIREN | Erreurs Détectées |
|---|---|---|---|
| 2 | STE EXEMPLE BETA | 123456789 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Clé erronée (40 ≠ attendu 32)) |
| 3 | GARAGE DUPONT & FILS | 804556219 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Clé erronée (40 ≠ attendu 15)) |
| 4 | BOULANGERIE MARTIN | 803245672 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Clé erronée (40 ≠ attendu 75)) |
| 5 | Boulangerie Martin SAS | 803245672 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Clé erronée (40 ≠ attendu 75)) |
| 6 | MENUISERIE LEBRUN | 902133458 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Clé erronée (40 ≠ attendu 88)) |
| 7 | SARL TECH SOLUTIONS | 903881245 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Format invalide (attendu FR + 2 chiffres + 9 chiffres SIREN)) |
| 8 | PHARMACIE CENTRALE | 509447112 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Clé erronée (50 ≠ attendu 36)) |
| 9 | CABINET MOREL CONSEIL | 752290884 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Clé erronée (40 ≠ attendu 48)) |
| 10 | FLEURISTE LA ROSE | 821993507 | SIREN_INVALID(Échec contrôle Luhn) |
| 11 | TRANSPORTS DUPONT (radiée) | 891004437 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Clé erronée (40 ≠ attendu 37)) |
| 12 | RESTAURANT LE GOURMET | 843712609 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Clé erronée (40 ≠ attendu 51)) |
| 13 | AGENCE IMMO HORIZON | 884520331 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Clé erronée (40 ≠ attendu 02)) |
| 14 | Agence Immo Horizon | 884520331 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Clé erronée (40 ≠ attendu 02)), DOUBLON_AVEC_LIGNE_13 |
| 15 | PRESSING NETPLUS | 875601442 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn) |
| 16 | AUTO-ECOLE CONDUITE+ | 853940221 | SIREN_INVALID(Échec contrôle Luhn), SIRET_INVALID(Échec contrôle Luhn), TVA_INVALID(Clé erronée (40 ≠ attendu 41)) |