"""2018-onwards format"""
# https://git.sr.ht/~leite/cso2-bsp-converter/tree/master/item/src/bsptypes.hpp
from .. import base
from . import cso2


FILE_MAGIC = b"VBSP"

BSP_VERSION = 100  # 1.00?

GAME_PATHS = ["Counter-Strike: Online 2"]

GAME_VERSIONS = {GAME_PATH: BSP_VERSION for GAME_PATH in GAME_PATHS}


LUMP = cso2.LUMP


# struct CSO2BspHeader { char file_magic[4]; int version; CSO2LumpHeader headers[64]; int revision; };
lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}

read_lump_header = cso2.read_lump_header


# classes for each lump, in alphabetical order:
class DisplacementInfo(base.Struct):  # LUMP 26
    # NOTE: 10 bytes more than Vindictus
    __slots__ = ["unknown"]  # not yet used
    _format = "242B"
    _arrays = {"unknown": 242}

# TODO: dcubemap_t: 164 bytes
# TODO: Facev1


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = cso2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = cso2.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"DISPLACEMENT_INFO": {0: DisplacementInfo}})

SPECIAL_LUMP_CLASSES = cso2.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_CLASSES = cso2.GAME_LUMP_CLASSES.copy()
# ^ {"lump": {version: SpecialLumpClass}}


methods = [*cso2.methods]
