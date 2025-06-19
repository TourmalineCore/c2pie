# JPG Structure Information

JPEG is a lossy compressed image format that uses the Discrete Cosine Transform (DCT) and Huffman coding to reduce file size while maintaining acceptable visual quality.

## Basic Structure of a JPEG File

A JPEG file is composed of segments (markers), each starting with a 0xFF byte followed by a marker code. Some markers have additional data, while others are standalone.

**Main Parts of a JPEG File:**
- Start of Image (SOI) Marker – 0xFFD8
- Application-Specific (APPn) Markers (Optional) – 0xFFE0 to 0xFFEF   
    Contains metadata (e.g., APP0 for JFIF/Exif data).
- Quantization Tables (DQT) – 0xFFDB
- Start of Frame (SOF) – 0xFFC0
- Huffman Tables (DHT) – 0xFFC4
- Start of Scan (SOS) – 0xFFDA
- Compressed Image Data (Entropy-Coded Segment)
- End of Image (EOI) Marker – 0xFFD9

## Embedding of C2PA Manifest Store

Embedding a C2PA Manifest Store into a JPEG (JPG) file involves inserting the manifest as a custom metadata segment while preserving JPEG compatibility.

The C2PA standard recommends implementing C2PA Manifest Store as a part of the APP11 segment (0xFFEB). For further information please follow to [C2PA specification: A.3.1 Embedding manifests into JPEG](https://c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_embedding_manifests_into_jpeg).

**APP11 structure**:
- Marker (0xFFEB)
- Segment Length (2 bytes)
- CI: default value is 0x4A50 or 'JP' in hex view (2 bytes)
- EN: segment ID of JPEG APP11 segment. Starts from 1 (2 bytes)
- Z: sequence number of part of JPEG APP11 Segment (4 bytes)
- L_BOX: length of JPEG APP11 segment payload (4 bytes)
- T_BOX: type of JPEG APP11 segment (4 bytes).

***Please note that JPEG APP11 Segment may contain only 65537 bytes. If the payload is longer than the maximum segment length, then you need to create a new segment with the remaining part of payload and increase the segment sequence number (Z).***
