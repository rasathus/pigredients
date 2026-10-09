"""Byte-exact tests for the SPI drivers, run against a fake ``spidev``.

Expected values are derived by hand from the original (Python 2) driver
logic, not from the ported output, so they guard the port.
"""
import sys
import types

import pytest


class FakeSpiDev(object):
    instances = []
    response = [0, 0, 0]

    def __init__(self):
        self.calls = []          # (method, list-of-ints)
        self.opened = None
        FakeSpiDev.instances.append(self)

    def open(self, bus, device):
        self.opened = (bus, device)

    def xfer(self, data, *args):
        self.calls.append(("xfer", list(data)))
        return list(FakeSpiDev.response)

    def xfer2(self, data, *args):
        self.calls.append(("xfer2", list(data)))
        return list(FakeSpiDev.response)

    def writebytes(self, data):
        self.calls.append(("writebytes", list(data)))

    def close(self):
        pass


@pytest.fixture(autouse=True)
def fake_spidev(monkeypatch):
    module = types.ModuleType("spidev")
    module.SpiDev = FakeSpiDev
    monkeypatch.setitem(sys.modules, "spidev", module)
    FakeSpiDev.instances = []
    FakeSpiDev.response = [0, 0, 0]
    yield module


def _make(cls, **kwargs):
    chip = cls(**kwargs)
    spi = chip.spi
    spi.calls.clear()          # discard the zero'd frame sent by __init__
    return chip, spi


def _all_ints(calls):
    for _, data in calls:
        assert all(type(b) is int and 0 <= b <= 255 for b in data), data


FRAME = [[255, 0, 0], [0, 255, 0], [0, 0, 255]]


def _load(chain):
    for i, rgb in enumerate(FRAME):
        chain.set_ic(i, rgb)


def test_ws2801_frame():
    from pigredients.ics.ws2801 import WS2801_Chain
    chain, spi = _make(WS2801_Chain, ics_in_chain=3)
    _load(chain)
    assert spi.calls == []     # set_ic only stores state
    chain.set()
    assert spi.calls == [("xfer2", [255, 0, 0, 0, 255, 0, 0, 0, 255])]
    _all_ints(spi.calls)


def test_ws2801_init_writes_zero_frame():
    from pigredients.ics.ws2801 import WS2801_Chain
    chain = WS2801_Chain(ics_in_chain=3)
    assert chain.spi.calls == [("xfer2", [0] * 9)]
    assert chain.spi.opened == (0, 0)


def test_lpd6803_frame():
    from pigredients.ics.lpd6803 import LPD6803_Chain
    chain, spi = _make(LPD6803_Chain, ics_in_chain=3)
    _load(chain)
    chain.set()
    # 1<<15 | R5<<10 | G5<<5 | B5, big endian:
    #   red   0x8000|0x7C00 = 0xFC00
    #   green 0x8000|0x03E0 = 0x83E0
    #   blue  0x8000|0x001F = 0x801F
    assert spi.calls == [
        ("xfer2", [0, 0, 0, 0]),                                  # start frame
        ("xfer2", [0xFC, 0x00, 0x83, 0xE0, 0x80, 0x1F]),          # pixels
        ("xfer2", [0, 0, 0]),                                     # append pulses
    ]
    _all_ints(spi.calls)


def test_lpd6803_five_bit_truncation():
    from pigredients.ics.lpd6803 import LPD6803_Chain
    chain, spi = _make(LPD6803_Chain, ics_in_chain=1)
    chain.set_ic(0, [8, 16, 7])    # >>3 -> 1, 2, 0
    chain.set()
    assert spi.calls[1] == ("xfer2", [0x80 | (1 << 2), (2 << 5) | 0])
    assert spi.calls[1][1] == [0x84, 0x40]


def test_lpd8806_frame():
    from pigredients.ics.lpd8806 import LPD8806_Chain
    chain, spi = _make(LPD8806_Chain, ics_in_chain=3)
    _load(chain)
    chain.set()
    # GRB order, each byte 0x80 | (v >> 1): 255 -> 0xFF, 0 -> 0x80
    assert spi.calls == [
        ("xfer2", [0x80, 0xFF, 0x80,
                   0xFF, 0x80, 0x80,
                   0x80, 0x80, 0xFF]),
        ("xfer2", [0, 0, 0]),                                     # latch
    ]
    _all_ints(spi.calls)


def test_lpd8806_extra_zero_per_32_ics():
    from pigredients.ics.lpd8806 import LPD8806_Chain
    chain, spi = _make(LPD8806_Chain, ics_in_chain=64)
    chain.set()
    pixels = spi.calls[0][1]
    assert len(pixels) == 64 * 3 + 2       # 64 // 32 == 2 trailing zeros
    assert pixels[-2:] == [0, 0]
    assert pixels[:3] == [0x80, 0x80, 0x80]


@pytest.mark.parametrize("modname,clsname", [
    ("ws2801", "WS2801_Chain"),
    ("lpd6803", "LPD6803_Chain"),
    ("lpd8806", "LPD8806_Chain"),
])
def test_rgbledclock_usage(modname, clsname):
    mod = __import__("pigredients.ics." + modname, fromlist=[clsname])
    chain = getattr(mod, clsname)(ics_in_chain=12)
    for i in range(12):
        chain.set_ic(i, [i, 255 - i, 128])
    chain.set()
    with pytest.raises(Exception):
        chain.set_ic(0)                 # default (None) rgb_value still rejected
    with pytest.raises(Exception):
        chain.set_ic(12, [0, 0, 0])


def test_shift_register_bytes():
    from pigredients.ics.ic74hc595 import Shift_Register, HIGH
    reg, spi = _make(Shift_Register, registers_in_chain=2)
    reg.set_pin(0, HIGH)
    reg.set()
    reg.set_pin(9, HIGH)
    reg.write()
    # pin 0 is the LSB of the first register; chain is written deepest first
    assert spi.calls == [("xfer2", [0b00000000, 0b00000001]),
                         ("xfer2", [0b00000010, 0b00000001])]


def test_shift_register_named_pin_and_all_on():
    from pigredients.ics.ic74hc595 import Shift_Register, HIGH
    reg, spi = _make(Shift_Register, registers_in_chain=1)
    reg.name_pin(7, "Bob")
    reg.set_pin("Bob", HIGH)
    reg.write()
    reg.all_on()
    assert spi.calls == [("xfer2", [0x80]), ("xfer2", [255])]


def test_mcp3008_read_input():
    from pigredients.ics.mcp3008 import MCP3008
    adc, spi = _make(MCP3008)
    FakeSpiDev.response = [0, 0b10, 0xAB]
    assert adc.read_input(3) == (2 << 8) + 0xAB == 683
    assert spi.calls == [("xfer2", [1, (8 + 3) << 4, 0])]
    assert spi.calls[0][1][1] == 176
    # only the low two bits of the second byte are data
    FakeSpiDev.response = [0xFF, 0xFF, 0xFF]
    assert adc.get_input(0) == 1023
    FakeSpiDev.response = [0, 1, 0]
    assert adc.read_input(0) == 256


def test_mcp3008_named_pin():
    from pigredients.ics.mcp3008 import MCP3008
    adc, spi = _make(MCP3008)
    adc.name_pin(5, "pot")
    FakeSpiDev.response = [0, 3, 1]
    assert adc.read_input("pot") == 769
    assert spi.calls == [("xfer2", [1, (8 + 5) << 4, 0])]
    with pytest.raises(Exception):
        adc.read_input("nope")
