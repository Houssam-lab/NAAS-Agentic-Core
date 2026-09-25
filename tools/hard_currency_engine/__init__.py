"""
Hard Currency Engine (HCE) — Production Suite
=============================================
Moteur d'exécution, d'audit réglementaire et de génération de devises fortes depuis l'Algérie.
Conçu pour les 9 corridors d'exportation de services, de données et d'ingénierie (2026).

Modules :
    - france_validator : Validation des référentiels SIREN / SIRET / TVA / Factur-X (RFE France).
    - belgium_validator : Validation KBO / BCE (Modulo 97) & Peppol BIS 3.0 (Belgique).
    - cbam_calculator : Arbitrage carbone et calcul d'économies CBAM / XML (Afrique du Nord -> UE).
    - zatca_validator : Intégrité تشفيرية وفحص سلاسل فواتير زاتكا السعودية (ZATCA Wave 24).
    - eaa_scanner : Audit d'accessibilité web WCAG 2.1 AA / Déclaration d'accessibilité (EAA).
    - crm_dispatcher : Génération et personnalisation des campagnes de prospection ciblées.
"""

__version__ = "1.0.0"
__author__ = "Houssam Benmerah"
