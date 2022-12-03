#!/usr/bin/env python3
# https://github.com/EONRaider/Packet-Sniffer

__author__ = "EONRaider @ keybase.io/eonraider"

import argparse


class CLIParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Network packet sniffer"
        )

    def parse(self) -> argparse.Namespace:
        self.parser.add_argument(
            "-i",
            "--interface",
            type=str,
            default=None,
            help="Interface from which Ethernet frames will be captured "
                 "(monitors all available interfaces by default).",
        )
        self.parser.add_argument(
            "-d",
            "--data",
            action="store_true",
            help="Output packet data during capture.",
        )
        return self.parser.parse_args()

