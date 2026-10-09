import importlib
import sys
import types


def test_core_imports_without_hardware_deps():
    # No spidev / smbus / serial / Adafruit_I2C injected here on purpose.
    import pigredients
    import pigredients.ics
    import pigredients.core.bitman
    import pigredients.displays
    assert pigredients.__version__


def test_bitman():
    from pigredients.core.bitman import BitSequence
    b = BitSequence(0b10101010)
    assert len(b) == 8
    assert str(b) == "0b10101010"
    assert b.twos_complement() == -86
    b[0] = 1
    assert int(b) == 0b10101011
    assert list(BitSequence(0b101)) == [1, 0, 1, 0, 0, 0, 0, 0]


def test_serial_display_writes_bytes(monkeypatch):
    class FakeSerial(object):
        def __init__(self, *a, **k):
            self.written = []

        def write(self, data):
            assert isinstance(data, bytes)
            self.written.append(data)

        def read(self, n):
            return b"b"

    mod = types.ModuleType("serial")
    mod.Serial = FakeSerial
    monkeypatch.setitem(sys.modules, "serial", mod)
    sys.modules.pop("pigredients.displays.textStarSerialLCD", None)
    lcd = importlib.import_module("pigredients.displays.textStarSerialLCD")
    d = lcd.Display()
    d.position_cursor(1, 2)
    d.capped_bar(16, 50)
    d.clear()
    d.window_home()
    assert d.ser.written == [b"\xfeP\x01\x02", b"\xfeb\x10\x32", b"\x0c", b"\xfeG\x01"]
