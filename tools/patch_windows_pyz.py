#!/usr/bin/env python3
"""Patcher Windows du Terminagotchi recent distribue en .pyz.

Usage: python tools/patch_windows_pyz.py terminagotchi-essai.pyz
"""
import argparse
from pathlib import Path
from zipfile import ZipFile

POWERSHELL_COMMANDS = set("""pwd dir ls gci get-childitem get-location gl cd chdir sl set-location
pushd popd cat type gc get-content echo write-output cp copy cpi copy-item
mv move mi move-item rm del erase ri remove-item mkdir md ni new-item
rmdir rd clear cls clear-host history h get-history get-date get-process
ps gps stop-process start-process get-command gcm get-help help
select-string sls get-alias gal set-alias sal get-psdrive get-acl
add-content ac set-content sc out-file where-object where ?
foreach-object % sort-object sort select-object select measure-object
group-object test-path join-path split-path resolve-path test-connection
invoke-webrequest iwr invoke-restmethod irm write-host read-host
start-sleep sleep get-service set-variable get-variable remove-variable
get-item gi set-item si remove-item get-itemproperty get-member gm
get-executionpolicy get-computerinfo get-ciminstance get-netipaddress
get-netadapter get-nettcpconnection""".split())


def replace_once(text, old, new, filename):
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{filename}: expected one occurrence, found {count}: {old[:70]!r}")
    return text.replace(old, new, 1)


def patch(name, source):
    s = source.decode("utf-8")
    if name == "tg/scenes.py":
        s = replace_once(s,
            '    import re\n    import select\n    import termios\n    import time as _t\n    rep = {"kitty": False, "sixel": False, "cellule": None, "sextant": None, "da1": False}',
            '    # Windows does not provide termios or /dev/tty.\n'
            '    rep = {"kitty": False, "sixel": False, "cellule": None, "sextant": None, "da1": False}\n'
            '    if os.name == "nt":\n        return rep\n'
            '    import re\n    import select\n    import termios\n    import time as _t', name)
    elif name == "tg/plateforme.py":
        s = replace_once(s, 'IS_WIN = OSK == "windows"\n',
            'IS_WIN = OSK == "windows"\n'
            '# PowerShell aliases and cmdlets are not executables.\n'
            'POWERSHELL_COMMANDS = ' + repr(POWERSHELL_COMMANDS) + '\n', name)
    elif name == "tg/core.py":
        s = replace_once(s, 'from .plateforme import GEST, IS_WIN, est_colle, piege',
                         'from .plateforme import GEST, IS_WIN, POWERSHELL_COMMANDS, est_colle, piege', name)
        s = replace_once(s, 'return cmd in BUILTINS or shutil.which(cmd) is not None',
                         'return cmd in BUILTINS or (IS_WIN and cmd.lower() in POWERSHELL_COMMANDS) or shutil.which(cmd) is not None', name)
    elif name == "tg/verif.py":
        s = replace_once(s, 'from .plateforme import IS_WIN',
                         'from .plateforme import IS_WIN, POWERSHELL_COMMANDS', name)
        s = replace_once(s, 'if mot in core.BUILTINS or mot in BUILTINS_EN_PLUS:',
                         'if mot in core.BUILTINS or mot in BUILTINS_EN_PLUS or (IS_WIN and mot.lower() in POWERSHELL_COMMANDS):', name)
    return s.encode("utf-8")


def build(src, dst):
    if src.resolve() == dst.resolve():
        raise ValueError("Output cannot overwrite the input archive")
    targets = {"tg/scenes.py", "tg/plateforme.py", "tg/core.py", "tg/verif.py"}
    with ZipFile(src) as archive:
        missing = targets - set(archive.namelist())
        if missing:
            raise ValueError("Incompatible archive; missing: " + ", ".join(sorted(missing)))
        files = [(info, patch(info.filename, archive.read(info.filename))
                  if info.filename in targets else archive.read(info.filename))
                 for info in archive.infolist()]
    with ZipFile(dst, "w") as out:
        for info, data in files:
            out.writestr(info, data)
    with ZipFile(dst) as checked:
        assert checked.testzip() is None
    return dst


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    dst = args.output or args.source.with_name(args.source.stem + "-windows.pyz")
    print("Patched archive:", build(args.source, dst))


if __name__ == "__main__":
    main()
