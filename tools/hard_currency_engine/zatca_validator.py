#!/usr/bin/env python3
"""
Module ZATCA Validator — Hard Currency Engine
Vérification تشفيرية وفحص سلاسل الفواتير الإلكترونية لهيئة الزكاة والضريبة والجمارك (المملكة العربية السعودية - المرحلة 2 الموجة 24).
"""

from __future__ import annotations

import base64
import hashlib
import re
import uuid

GENESIS_PIH = (
    "NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI4NjExN2Q2NDhkNzg1ZTZmMw=="
)


def validate_uuid_v4(val: str) -> bool:
    try:
        u = uuid.UUID((val or "").strip(), version=4)
        return str(u) == (val or "").strip().lower()
    except (ValueError, AttributeError):
        return False


def validate_zatca_vat_number(vat_str: str) -> tuple[bool, str]:
    """Validation du numéro fiscal saoudien (15 chiffres, début et fin = 3)."""
    s = re.sub(r"\D", "", vat_str or "")
    if len(s) != 15:
        return False, f"Longueur {len(s)} ≠ 15 chiffres"
    if not (s.startswith("3") and s.endswith("3")):
        return False, "Doit débuter et se terminer par 3"
    return True, "OK"


def canonical_invoice_hash(xml_content: str) -> str:
    """Calcule le hash SHA-256 canonique en Base64 d'une facture XML ZATCA."""
    clean_xml = re.sub(r">\s+<", "><", (xml_content or "").strip())
    digest = hashlib.sha256(clean_xml.encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


def is_valid_base64_sha256(hash_str: str) -> bool:
    s = (hash_str or "").strip()
    if len(s) != 44:  # 32 bytes base64 encoded = 44 chars ending in = or ==
        return False
    try:
        raw = base64.b64decode(s, validate=True)
        return len(raw) == 32
    except Exception:
        return False


def encode_zatca_tlv(
    seller_name: str,
    vat_number: str,
    timestamp_iso: str,
    total_with_vat: str,
    vat_amount: str,
    invoice_hash: str = "",
    crypto_stamp: str = "",
    public_key: str = "",
    stamp_signature: str = "",
) -> str:
    """
    Encode un QR Code TLV (Tag-Length-Value) officiel ZATCA en Base64.
    Tags 1-5 sont obligatoires pour B2C simplifié. Tags 6-9 pour Phase 2 B2B.
    """
    tags = [
        (1, seller_name.encode("utf-8")),
        (2, vat_number.encode("utf-8")),
        (3, timestamp_iso.encode("utf-8")),
        (4, total_with_vat.encode("utf-8")),
        (5, vat_amount.encode("utf-8")),
    ]
    if invoice_hash:
        tags.append((6, invoice_hash.encode("utf-8")))
    if crypto_stamp:
        tags.append((7, crypto_stamp.encode("utf-8")))
    if public_key:
        tags.append((8, public_key.encode("utf-8")))
    if stamp_signature:
        tags.append((9, stamp_signature.encode("utf-8")))

    tlv_bytes = bytearray()
    for tag_num, val_bytes in tags:
        tlv_bytes.append(tag_num)
        tlv_bytes.append(len(val_bytes))
        tlv_bytes.extend(val_bytes)

    return base64.b64encode(tlv_bytes).decode("ascii")


def decode_zatca_tlv(b64_qr: str) -> dict[int, str]:
    """Décode un QR Code TLV ZATCA depuis sa chaîne Base64."""
    try:
        raw = base64.b64decode(b64_qr.strip(), validate=True)
    except Exception as e:
        raise ValueError(f"Base64 invalide : {e}") from e

    idx = 0
    parsed = {}
    while idx < len(raw):
        if idx + 2 > len(raw):
            break
        tag = raw[idx]
        length = raw[idx + 1]
        val = raw[idx + 2 : idx + 2 + length]
        parsed[tag] = val.decode("utf-8", errors="replace")
        idx += 2 + length

    return parsed


def audit_zatca_batch(invoices: list[dict]) -> dict:
    """
    Vérifie la continuité d'une chaîne de factures ZATCA (ICV + PIH).
    Chaque facture doit comporter : id, icv, uuid, pih, invoice_hash
    """
    anomalies = []
    expected_icv = 1
    expected_pih = GENESIS_PIH

    for i, inv in enumerate(invoices):
        inv_id = inv.get("id", f"INV-{i + 1}")
        icv = inv.get("icv")
        u = inv.get("uuid", "")
        pih = inv.get("pih", "")
        curr_hash = inv.get("invoice_hash", "")

        # 1. Check UUID
        if not validate_uuid_v4(u):
            anomalies.append(f"Facture {inv_id}: UUID v4 non conforme ({u})")

        # 2. Check ICV monotonicity
        if icv != expected_icv:
            anomalies.append(
                f"Facture {inv_id}: Rupture de séquence ICV ({icv} attendu {expected_icv})"
            )

        # 3. Check PIH continuity
        if pih != expected_pih:
            anomalies.append(
                f"Facture {inv_id}: Rupture de chaîne PIH (PIH={pih[:10]}... attendu={expected_pih[:10]}...)"
            )

        # 4. Check Hash integrity
        if not is_valid_base64_sha256(curr_hash):
            anomalies.append(f"Facture {inv_id}: Hash SHA-256 invalide ({curr_hash})")

        expected_icv = (icv + 1) if isinstance(icv, int) else expected_icv + 1
        expected_pih = curr_hash if is_valid_base64_sha256(curr_hash) else expected_pih

    return {
        "total_factures": len(invoices),
        "est_valide": len(anomalies) == 0,
        "anomalies": anomalies,
    }


def repair_zatca_chain(invoices: list[dict]) -> tuple[list[dict], list[str]]:
    """Répare une séquence de factures ZATCA rompue (réaligne ICV et recalcule la chaîne PIH)."""
    repaired = []
    actions = []
    curr_pih = GENESIS_PIH

    for i, inv in enumerate(invoices, start=1):
        item = dict(inv)
        inv_id = item.get("id", f"INV-{i}")

        if item.get("icv") != i:
            actions.append(f"Facture {inv_id} : ICV corrigé de {item.get('icv')} à {i}")
            item["icv"] = i

        if item.get("pih") != curr_pih:
            actions.append(f"Facture {inv_id} : PIH réaligné sur le hash précédent")
            item["pih"] = curr_pih

        if not validate_uuid_v4(item.get("uuid", "")):
            new_u = str(uuid.uuid4())
            actions.append(f"Facture {inv_id} : UUID généré ({new_u})")
            item["uuid"] = new_u

        if not is_valid_base64_sha256(item.get("invoice_hash", "")):
            synth_content = f"{item['uuid']}|{item['icv']}|{item['pih']}|{item.get('total', '0')}"
            new_hash = canonical_invoice_hash(synth_content)
            actions.append(f"Facture {inv_id} : Hash SHA-256 calculé ({new_hash[:10]}...)")
            item["invoice_hash"] = new_hash

        curr_pih = item["invoice_hash"]
        repaired.append(item)

    return repaired, actions
