#!/usr/bin/env python3
# https://github.com/EONRaider/Packet-Sniffer

__author__ = "EONRaider @ keybase.io/eonraider"

import itertools
from socket import PF_PACKET, SOCK_RAW, ntohs, socket
from typing import Iterator

from src.output import OutputToScreen

import netprotocols


class Decoder:
    def __init__(self, interface: str):
        """Decodes packets incoming from a given interface.

        :param interface: Interface from which packets will be captured
            and decoded.
        """
        self.interface = interface
        self.data = None
        self.protocol_queue = ["Ethernet"]
        self.packet_num: int = 0

    def listen(self) -> Iterator:
        """Yields a decoded packet as an instance of Protocol."""
        with socket(PF_PACKET, SOCK_RAW, ntohs(0x0003)) as sock:
            if self.interface is not None:
                sock.bind((self.interface, 0))
            for self.packet_num in itertools.count(1):
                raw_packet = sock.recv(9000)
                start = 0
                for proto in self.protocol_queue:
                    proto_class = getattr(netprotocols, proto)
                    end = start + proto_class.header_len
                    protocol = proto_class.decode(raw_packet[start:end])
                    setattr(self, proto.lower(), protocol)
                    if protocol.encapsulated_proto in (None, "undefined"):
                        break
                    self.protocol_queue.append(protocol.encapsulated_proto)
                    start = end
                self.data = raw_packet[end:]
                yield self
                del self.protocol_queue[1:]


class PacketSniffer:
    def __init__(self):
        """Monitor a network interface for incoming data, decode it and
        send to pre-defined output methods."""
        self._observers = list()

    def register(self, observer) -> None:
        """Register an observer for processing/output of decoded
        frames.

        :param observer: Any object that implements the interface
        defined by the output.OutputMethod abstract base-class."""
        self._observers.append(observer)

    def _notify_all(self, *args, **kwargs) -> None:
        """Send a decoded frame to all registered observers for further
        processing/output."""
        [observer.update(*args, **kwargs) for observer in self._observers]

    def listen(self, interface: str) -> Iterator:
        """Directly output a captured Ethernet frame while
        simultaneously notifying all registered observers, if any.

        :param interface: Interface from which a given frame will be
            captured and decoded.
        """
        try:
            for frame in Decoder(interface).execute():
                self._notify_all(frame)
                yield frame
        except KeyboardInterrupt:
            raise SystemExit("Aborting packet capture...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Network packet sniffer")
    parser.add_argument(
        "-i", "--interface",
        type=str,
        default=None,
        help="Interface from which packets will be captured (monitors all "
             "available interfaces by default)."
    )
    parser.add_argument(
        "-d", "--display-data",
        action="store_true",
        help="Output packet data during capture."
    )
    _args = parser.parse_args()

    PacketSniffer().execute(_args.display_data, interface=_args.interface)
