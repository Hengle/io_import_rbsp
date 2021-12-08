"""Index of all known .bsp format variants"""
__all__ = ["arkane", "gearbox", "id_software", "infinity_ward", "nexon",
           "raven", "respawn", "ritual", "scripts_from_file_magic", "game_path_table"]

from . import arkane
from . import gearbox
from . import id_software
from . import infinity_ward
from . import ion_storm
from . import nexon
from . import raven
from . import respawn
from . import ritual
from . import troika
from . import valve
# TODO: xatrix.kingpin
# ^ https://github.com/QuakeTools/Kingpin-SDK-v1.21
# (Kingpin allegedly has it's own KRadiant "on the CD")


# NOTE: this dict can be generated from branch_scripts, but listing it here is more convenient
scripts_from_file_magic = {None: [id_software.quake,
                                  *gearbox.scripts,
                                  raven.hexen2,
                                  valve.goldsrc],
                           b"2015": [ritual.moh_allied_assault],
                           b"EF2!": [ritual.star_trek_elite_force2],
                           b"FAKK": [ritual.fakk2],
                           b"IBSP": [id_software.quake2,
                                     id_software.quake3,
                                     *infinity_ward.scripts,
                                     # NOTE: most of infinity_ward.scripts will be *.d3dbsp
                                     ion_storm.daikatana,
                                     raven.soldier_of_fortune,
                                     ritual.sin],
                           b"rBSP": [*respawn.scripts],
                           b"RBSP": [raven.soldier_of_fortune2,
                                     ritual.sin],
                           b"VBSP": [*arkane.scripts,
                                     *nexon.scripts,
                                     *troika.scripts,
                                     *[s for s in valve.scripts if (s is not valve.goldsrc)]]}


script_from_file_magic_and_version = dict()
# ^ {(file_magic, version): branch_script}
for file_magic, branch_scripts in scripts_from_file_magic.items():
    for branch_script in branch_scripts:
        for version in branch_script.GAME_VERSIONS.values():
            script_from_file_magic_and_version[(file_magic, version)] = branch_script

# FORCED DEFAULTS:
script_from_file_magic_and_version[(b"IBSP", 46)] = id_software.quake3
# ^ NOT raven.soldier_of_fortune
script_from_file_magic_and_version[(b"VBSP", 20)] = valve.orange_box
# ^ NOT nexon.vindictus OR valve.left4dead
script_from_file_magic_and_version[(b"VBSP", 21)] = valve.sdk_2013
# ^ NOT valve.alien_swarm OR valve.left4dead2
script_from_file_magic_and_version[(b"VBSP", 100)] = nexon.cso2
# ^ NOT nexon.cso2_2018
script_from_file_magic_and_version[(b"RBSP", 1)] = raven.soldier_of_fortune2
# ^ NOT ritual.sin


game_path_table = dict()
# ^ {"game": (script, version)}
for developer in (arkane, gearbox, id_software, infinity_ward, nexon, raven, respawn, ritual, valve):
    for script in developer.scripts:
        for game_path in script.GAME_PATHS:
            game_path_table[game_path] = (script, script.GAME_VERSIONS[game_path])
