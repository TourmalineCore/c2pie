# JUMBF Box Header
LBOX_SIZE = 4  # Length of the LBox field in bytes
TBOX_SIZE = 4  # Length of the TBox field in bytes
HEADER_SIZE = LBOX_SIZE + TBOX_SIZE  # Total box header size in bytes

# JUMBF Description Box (jumd)
CONTENT_TYPE_SIZE = 16  # UUID content type size
TOGGLE_SIZE = 1  # Description box flags size
JUMD_MIN_PAYLOAD_SIZE = CONTENT_TYPE_SIZE + TOGGLE_SIZE + 1  # +1 for minimum null-terminator
LABEL_OFFSET = CONTENT_TYPE_SIZE + TOGGLE_SIZE  # Label offset within the jumd payload

# Box Type Hex Values
JUMB_TYPE = b"jumb".hex()
JUMD_TYPE = b"jumd".hex()
JSON_TYPE = b"json".hex()

# Endianness
BYTE_ORDER = "big"
