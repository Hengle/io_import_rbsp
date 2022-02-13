from __future__ import annotations
import io
import itertools
import struct
from typing import List

from .. import shared
from .. import x360
from . import orange_box
from . import source


FILE_MAGIC = b"PSBV"

BSP_VERSION = 20

GAME_PATHS = {"Half-Life 2": "OrangeBox/hl2",
              "Half-Life 2: Episode 1": "OrangeBox/episodic",
              "Half-Life 2: Episode 2": "OrangeBox/ep2",
              "Portal": "OrangeBox/portal",
              "Team Fortress 2": "OrangeBox/tf"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = orange_box.LUMP


LumpHeader = x360.make_big_endian(source.LumpHeader)


# classes for each lump, in alphabetical order:
# NOTE: Leaf_x360 bitfields are flipped
# TODO: DisplacementInfo_x360, Primitive_x360
# -- see https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bspfile.h
# "#if !defined( BSP_USE_LESS_MEMORY )" & "#if defined( _X360 )" defines specifically


# special lump classes, in alphabetical order:
class GameLump_SPRP_x360:
    """use `lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropvXX)` to implement"""
    StaticPropClass: object
    model_names: List[str]
    leaves: List[int]
    props: List[object] | List[bytes]  # List[StaticPropClass]

    def __init__(self, raw_sprp_lump: bytes, StaticPropClass: object):
        self.StaticPropClass = StaticPropClass
        sprp_lump = io.BytesIO(raw_sprp_lump)
        model_name_count = int.from_bytes(sprp_lump.read(4), "big")
        model_names = struct.iter_unpack("128s", sprp_lump.read(128 * model_name_count))
        setattr(self, "model_names", [t[0].replace(b"\0", b"").decode() for t in model_names])
        leaf_count = int.from_bytes(sprp_lump.read(4), "big")
        leaves = itertools.chain(*struct.iter_unpack("H", sprp_lump.read(2 * leaf_count)))
        setattr(self, "leaves", list(leaves))
        prop_count = int.from_bytes(sprp_lump.read(4), "big")
        if StaticPropClass is None:
            raw_props = sprp_lump.read()
            prop_size = len(raw_props) // prop_count
            props = list()
            for i in range(prop_count):
                props.append(raw_props[i * prop_size:(i + 1) * prop_size])
            setattr(self, "props", props)
        else:
            read_size = struct.calcsize(StaticPropClass._format) * prop_count
            props = struct.iter_unpack(StaticPropClass._format, sprp_lump.read(read_size))
            setattr(self, "props", list(map(StaticPropClass.from_tuple, props)))
        here = sprp_lump.tell()
        end = sprp_lump.seek(0, 2)
        assert here == end, "Had some leftover bytes; StaticPropClass._format is incorrect!"

    def as_bytes(self) -> bytes:
        if len(self.props) > 0:
            prop_bytes = [struct.pack(self.StaticPropClass._format, *p.flat()) for p in self.props]
        else:
            prop_bytes = []
        return b"".join([int.to_bytes(len(self.model_names), 4, "big"),
                         *[struct.pack("128s", n) for n in self.model_names],
                         int.to_bytes(len(self.leaves), 4, "big"),
                         *[struct.pack("H", L) for L in self.leaves],
                         int.to_bytes(len(self.props), 4, "big"),
                         *prop_bytes])


StaticPropv4_x360 = x360.make_big_endian(source.StaticPropv4)
StaticPropv5_x360 = x360.make_big_endian(source.StaticPropv5)
StaticPropv6_x360 = x360.make_big_endian(source.StaticPropv6)
StaticPropv10_x360 = x360.make_big_endian(orange_box.StaticPropv10)


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES, LumpClasses = x360.convert_versioned(orange_box.BASIC_LUMP_CLASSES)
# copy used LumpClasses to globals
for LumpClass_name, LumpClass in LumpClasses.items():
    globals()[LumpClass_name] = LumpClass


LUMP_CLASSES, LumpClasses = x360.convert_versioned(orange_box.LUMP_CLASSES)
LUMP_CLASSES.pop("DISPLACEMENT_INFO")
LUMP_CLASSES.pop("PRIMITIVES")
# copy used LumpClasses to globals
for LumpClass_name, LumpClass in LumpClasses.items():
    globals()[LumpClass_name] = LumpClass
del LumpClass_name, LumpClass


SPECIAL_LUMP_CLASSES = {"ENTITIES":                 {0: shared.Entities},
                        # "PAKFILE":                  {0: PakFile_x360},
                        "TEXTURE_DATA_STRING_DATA": {0: shared.TextureDataStringData}}
# TODO: converted PhysicsCollide

GAME_LUMP_HEADER = x360.make_big_endian(orange_box.GAME_LUMP_HEADER)

GAME_LUMP_CLASSES = {"sprp": {4: lambda raw_lump: GameLump_SPRP_x360(raw_lump, StaticPropv4_x360),
                              5: lambda raw_lump: GameLump_SPRP_x360(raw_lump, StaticPropv5_x360),
                              6: lambda raw_lump: GameLump_SPRP_x360(raw_lump, StaticPropv6_x360),
                              7: lambda raw_lump: GameLump_SPRP_x360(raw_lump, StaticPropv10_x360),  # 7*
                              10: lambda raw_lump: GameLump_SPRP_x360(raw_lump, StaticPropv10_x360)}}
# ^ {"lump": {version: SpecialLumpClass}}


methods = [*orange_box.methods]
