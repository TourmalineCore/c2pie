from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from pathlib import Path

import requests as http
from pyasn1.codec.der import decoder, encoder
from pyasn1.type import univ
from pyasn1_modules import rfc2459, rfc3161

from c2pie.tsa.exceptions import TSAConnectionError, TSAResponseError

# SHA-256 OID: 2.16.840.1.101.3.4.2.1
_SHA256_OID = univ.ObjectIdentifier((2, 16, 840, 1, 101, 3, 4, 2, 1))


def _build_request(signature_bytes: bytes) -> tuple[bytes, int]:
    """
    TimeStampReq = {
      version,        ; INTEGER
      messageImprint, ; messageImprint
      nonce,          ; INTEGER OPTIONAL
      certReq,        ; BOOLEAN
    }

    messageImprint = {
        hashAlgorithm, ; AlgorithmIdentifier
        hashedMessage, ; OCTET STRING (octet ~ 8 bit)
    }
    """
    nonce = secrets.randbits(64)

    alg = rfc2459.AlgorithmIdentifier()
    alg["algorithm"] = _SHA256_OID

    imprint = rfc3161.MessageImprint()
    imprint["hashAlgorithm"] = alg
    imprint["hashedMessage"] = univ.OctetString(hashlib.sha256(signature_bytes).digest())

    req = rfc3161.TimeStampReq()
    req["version"] = 1
    req["messageImprint"] = imprint
    req["nonce"] = nonce
    req["certReq"] = True

    # Converting an ASN.1 object to bytes in DER format
    return encoder.encode(req), nonce


def _save_file(directory: Path, name: str, data: bytes) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_bytes(data)


def fetch_timestamp(
    signature_bytes: bytes,
    tsa_url: str,
    tsa_log_dir: str | None,
) -> bytes:
    time_stamp_req_der, nonce = _build_request(signature_bytes)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")

    nonce_hex = f"{nonce & 0xFFFFFFFF:08x}"
    prefix = f"{timestamp}_{nonce_hex}"

    if tsa_log_dir is not None:
        _save_file(Path(tsa_log_dir), f"{prefix}_request.der", time_stamp_req_der)

    try:
        """
        TimeStampResp = {
            status,          ; PKIStatusInfo,
            timeStampToken,  ; TimeStampToken OPTIONAL
        }
        """
        response = http.post(
            url=tsa_url,
            data=time_stamp_req_der,
            headers={"Content-Type": "application/timestamp-query"},
            timeout=30,
        )

        response.raise_for_status()
    except http.exceptions.RequestException as exc:
        raise TSAConnectionError(f"TSA request to {tsa_url!r} failed: {exc}") from exc

    resp_bytes = response.content

    if tsa_log_dir is not None:
        _save_file(Path(tsa_log_dir), f"{prefix}_response.der", resp_bytes)

    try:
        resp, _ = decoder.decode(resp_bytes, asn1Spec=rfc3161.TimeStampResp())
    except Exception as exc:
        raise TSAResponseError(f"Failed to parse TSA response: {exc}") from exc

    status = int(resp["status"]["status"])
    if status != 0:
        raise TSAResponseError(f"TSA returned non-granted status: {status}")

    time_stamp_token = resp["timeStampToken"]
    if not time_stamp_token.hasValue():
        raise TSAResponseError("TSA granted status but TimeStampToken is absent")

    return encoder.encode(time_stamp_token)
