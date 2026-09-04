#!/usr/bin/env python3
"""Install a local CLI link without replacing any other command."""
import argparse
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bin-dir',type=Path,default=Path.home()/'.local/bin')
    args=parser.parse_args()
    source=Path(__file__).resolve().with_name('agent-science')
    target=args.bin_dir.expanduser().resolve()/'agent-science'
    if target.exists() or target.is_symlink():
        if not target.is_symlink() or target.resolve()!=source:
            parser.error(f'{target} already exists; no command was replaced')
    else:
        target.parent.mkdir(parents=True,exist_ok=True)
        target.symlink_to(source)
    print(f'Installed {target}')
    print('Run: agent-science case review --root .')
    return 0


if __name__=='__main__':raise SystemExit(main())
