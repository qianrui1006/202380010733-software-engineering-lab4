import unittest

from state_machines import ControlPanel, PanelState, Tank, TankState, extract_strings


class TankTests(unittest.TestCase):
    def setUp(self):
        self.tank = Tank()

    def check(self, expected, minute, temp, water, **events):
        self.assertIs(self.tank.sample(minute, temp, water, **events), expected)
        self.assertEqual(self.tank.relay_on, expected is TankState.HEATING)

    def test_temperature_boundaries(self):
        self.check(TankState.STANDBY, 600, 20, True)
        self.check(TankState.HEATING, 600, 19.9, True)
        self.check(TankState.HEATING, 601, 99.9, True)
        self.check(TankState.STANDBY, 602, 100, True)
        self.check(TankState.STANDBY, 603, 21, True)

    def test_water_absence(self):
        self.check(TankState.STANDBY, 600, 10, False)
        self.check(TankState.HEATING, 601, 10, True)
        self.check(TankState.STANDBY, 602, 50, False)

    def test_day_night_boundaries(self):
        self.check(TankState.HEATING, 1379, 10, True)
        self.check(TankState.SLEEPING, 1380, 10, True)
        self.check(TankState.SLEEPING, 419, 10, True)
        self.check(TankState.HEATING, 420, 10, True)

    def test_fault_priority_and_repair(self):
        self.check(TankState.HEATING, 1379, 10, True)
        self.check(TankState.REPAIRING, 1380, 10, True, fault=True, repaired=True)
        self.check(TankState.REPAIRING, 1381, 10, True)
        self.check(TankState.SLEEPING, 1382, 10, True, repaired=True)
        self.check(TankState.HEATING, 420, 10, True)


class PanelTests(unittest.TestCase):
    def setUp(self):
        self.panel = ControlPanel("2468")

    def enter(self, text, now):
        for character in text:
            self.panel.press(character, now)
        return self.panel.state

    def test_partial_then_success(self):
        self.assertIs(self.enter("246", 0), PanelState.READING)
        self.assertIs(self.enter("8", 1), PanelState.SELECTING)

    def test_third_failure_and_timeout(self):
        for attempt in (1, 2):
            self.assertIs(self.enter("0000", attempt), PanelState.READING)
            self.assertEqual(self.panel.failures, attempt)
        self.assertIs(self.enter("0000", 3), PanelState.LOCKED)
        self.assertIs(self.enter("2468", 123), PanelState.LOCKED)
        self.panel.tick(123.001)
        self.assertIs(self.panel.state, PanelState.READING)
        self.assertEqual(self.panel.failures, 0)
        self.assertIs(self.enter("2468", 124), PanelState.SELECTING)

    def test_success_resets_failures(self):
        self.enter("0000", 0)
        self.assertIs(self.enter("2468", 1), PanelState.SELECTING)
        self.assertEqual(self.panel.failures, 0)


class ExtractionTests(unittest.TestCase):
    def test_chinese_and_escaped_quotes(self):
        source = r'"一般学习一门编程语言的时候，基本上第一个程序是输出\"Hello World!\""'
        expected = '一般学习一门编程语言的时候，基本上第一个程序是输出"Hello World!"'
        self.assertEqual(list(extract_strings(source)), [expected])

    def test_empty_adjacent_and_escaped_backslash(self):
        self.assertEqual(list(extract_strings(r'"" "a""b" "C:\\tmp"')), ["", "a", "b", r"C:\tmp"])

    def test_arbitrary_escape_and_multiline(self):
        self.assertEqual(list(extract_strings('"x\\q\nz"')), ["xq\nz"])

    def test_no_literals(self):
        self.assertEqual(list(extract_strings("x = 42")), [])

    def test_unclosed_quote(self):
        with self.assertRaisesRegex(ValueError, "未闭合"):
            list(extract_strings('"abc'))

    def test_trailing_escape(self):
        with self.assertRaisesRegex(ValueError, "缺少后继"):
            list(extract_strings('"abc\\'))


if __name__ == "__main__":
    unittest.main()
