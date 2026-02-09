#!/usr/bin/env python
from __future__ import annotations

import argparse
from tofu_byte.main import GameMenu
from tofu_byte.config import DEBUG


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", type=str)
    args = parser.parse_args()
    # Add debug flags
    if args.debug:
        for x in args.debug.split(","):
            k, _, v = x.partition(":")
            DEBUG[k] = v or True
    GameMenu().run()


if __name__ == "__main__":
    run()
