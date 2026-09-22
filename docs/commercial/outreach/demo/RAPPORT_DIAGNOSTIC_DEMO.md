# RAPPORT DE DIAGNOSTIC — QUALITÉ DES RÉFÉRENTIELS CLIENTS
### Exemple de démonstration (données 100 % fictives) — format identique au rapport réel

> **Fichier analysé :** DEMO_20_FICHES.csv · **20 fiches** · **Contrôles effectués :** format & clé SIREN, longueur SIRET, cohérence SIREN↔SIRET, format & unicité TVA intracommunautaire, doublons exacts et quasi-doublons, normalisation adresses/villes, présence des champs obligatoires de routage.
>
> **Délai réel de livraison : 24 h après réception du fichier.**

---

## 1. Synthèse

| Indicateur | Avant | Après corrections proposées |
|---|---:|---:|
| Fiches analysées | 20 | 20 |
| Fiches comportant au moins un défaut | **11 (55 %)** | 0 |
| Défauts détectés (unités) | **9 catégories ci-dessous** | corrigés ou arbitrés |
| Score de qualité (pondéré routage/rejet) | **49 / 100** | **≈ 98 / 100** |
| Risque estimé de rejet de facture sur cette base | élevé | résiduel |

## 2. Défauts détectés, par criticité

### 🔴 Critique — provoque un rejet immédiat de la facture (à corriger avant tout envoi)

| Fiche | Défaut | Détail | Action proposée |
|---|---|---|---|
| 01 | SIREN invalide | `123456789` — clé de contrôle incorrecte | Corriger auprès du client ; fichier bloqué en l'état |
| 10 | Entité radiée | TRANSPORTS DUPONT — société radiée du SIRENE | **Retirer de la base active** (décision de conservation à votre main) |
| 09, 14 | TVA intracom manquante | champ vide | Compléter : clé = f(SIREN) ; validation VIES si assujetti confirmé |
| 06 | TVA mal formée | `FR 12 3903881245` — espaces + clé erronée | Reformater en `FR` + clé 2 caractères + SIREN |
| 18 | SIRET longueur invalide | `8992013340001` (13 chiffres au lieu de 14) | Compléter le suffixe établissement |

### 🟠 Majeur — doublons : factures en double ou routage incertain

| Fiches | Défaut | Détail | Action proposée |
|---|---|---|---|
| 03 / 04 | Doublon exact | Même SIREN+SIRET (`803245672…00021`), libellés et casses différents | Fusionner — fiche consolidée proposée |
| 12 / 13 | Doublon avec SIRET divergents | Même SIREN, deux SIRET (`…00018` / `…00026`) | **Décision requise chez vous** : établissement facturé ? Je prépare les deux variantes, vous tranchez |

### 🟡 Mineur — qualité & normalisation (n'affecte pas le rejet, dégrade la correspondance)

| Fiche | Défaut | Détail | Action proposée |
|---|---|---|---|
| 16 | Ville non normalisée | `TOULOUSEE` | Correction orthographique + normalisation casse |
| 03/04, 12/13, 16 | Normalisation adresses | abréviations `av.` / `PLACE`, majuscules incohérentes | Uniformisation (format adresse postale FR) |

## 3. Répartition des fiches

```text
Fiches saines ..................... 9  ██████████████░░░░░░ 45%
Fiches avec défauts critiques ..... 5  (01, 06, 09, 10, 14, 18 → 6)
Fiches en doublon ................. 4  (03, 04, 12, 13)
Fiches normalisation seule ........ 1  (16)
```

## 4. Ce que je corrige / ce qui requiert votre décision

- **Je corrige directement :** formats, clés, normalisation, reformattage TVA (sur la base d'identifiants légaux vérifiés contre les sources publiques).
- **Vous décidez :** fusions de doublons, choix de l'établissement facturé, retrait des entités radiées, toute donnée comptable ou fiscale.
- **Je ne touche jamais à :** la comptabilité, la fiscalité, les montants — votre cabinet garde la main complète.

## 5. Livrables de la mission réelle (identiques à cette démo)

1. Fichier clients nettoyé, **prêt à importer** dans votre outil (format au choix — MEG, Pennylane, Sage, export CSV/XLSX neutre) ;
2. Ce rapport avant/après avec score de qualité ;
3. Liste des décisions requises de votre part ;
4. **Piste d'audit complète** : chaque modification tracée (valeur avant → valeur après → source) ;
5. Confirmation écrite de suppression de vos données chez moi après livraison.

---
*Rapport de démonstration établi sur données fictives — aucune entreprise réelle n'est identifiée. Méthode de contrôle : sources publiques SIRENE (INSEE) et règles de format DGFiP.*
