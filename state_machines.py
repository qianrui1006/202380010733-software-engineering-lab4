"""软件工程实验四的状态机。"""

import argparse
from enum import Enum, auto
from pathlib import Path
from typing import Iterable, Iterator


class TankState(Enum):
    STANDBY = auto()
    HEATING = auto()
    SLEEPING = auto()
    REPAIRING = auto()


class Tank:
    def __init__(self):
        self.state = TankState.STANDBY

    @property
    def relay_on(self):
        return self.state is TankState.HEATING

    def sample(self, minute, temperature, has_water, *, fault=False, repaired=False):
        """输入当天分钟数、温度、水量和维修事件。"""
        if not 0 <= minute < 1440:
            raise ValueError("minute 必须在 0 到 1439 之间")
        if fault:
            self.state = TankState.REPAIRING
        elif self.state is TankState.REPAIRING and not repaired:
            return self.state
        elif not 420 <= minute < 1380:
            self.state = TankState.SLEEPING
        elif self.relay_on and has_water and temperature < 100:
            return self.state
        elif has_water and temperature < 20:
            self.state = TankState.HEATING
        else:
            self.state = TankState.STANDBY
        return self.state


class PanelState(Enum):
    READING = auto()
    LOCKED = auto()
    SELECTING = auto()


class ControlPanel:
    def __init__(self, password):
        if len(password) != 4:
            raise ValueError("密码必须恰好 4 个字符")
        self.state = PanelState.READING
        self.failures = 0
        self._password = password
        self._buffer = ""
        self._locked_at = None

    def tick(self, now):
        """now 来自同一单调时钟，单位为秒。"""
        if self._locked_at is not None and now - self._locked_at > 120:
            self._locked_at = None
            self.failures = 0
            self.state = PanelState.READING

    def press(self, character, now):
        if len(character) != 1:
            raise ValueError("每次只能输入一个字符")
        self.tick(now)
        if self.state is not PanelState.READING:
            return self.state
        self._buffer += character
        if len(self._buffer) < 4:
            return self.state

        entered = self._buffer
        self._buffer = ""
        if entered == self._password:
            self.failures = 0
            self.state = PanelState.SELECTING
        else:
            self.failures += 1
            if self.failures == 3:
                self._locked_at = now
                self.state = PanelState.LOCKED
        return self.state


class ScanState(Enum):
    OUTSIDE = auto()
    INSIDE = auto()
    ESCAPED = auto()


def extract_strings(characters: Iterable[str]) -> Iterator[str]:
    """顺序产出完整字符串。characters 逐项提供单个字符。"""
    state = ScanState.OUTSIDE
    buffer: list[str] = []
    opening = 0
    for offset, character in enumerate(characters, start=1):
        if state is ScanState.OUTSIDE:
            if character == '"':
                opening = offset
                state = ScanState.INSIDE
        elif state is ScanState.ESCAPED:
            buffer.append(character)
            state = ScanState.INSIDE
        elif character == "\\":
            state = ScanState.ESCAPED
        elif character == '"':
            yield "".join(buffer)
            buffer.clear()
            state = ScanState.OUTSIDE
        else:
            buffer.append(character)

    if state is not ScanState.OUTSIDE:
        reason = "转义缺少后继字符" if state is ScanState.ESCAPED else "双引号未闭合"
        raise ValueError(f"第 {opening} 个字符开始的字符串{reason}")


def main():
    parser = argparse.ArgumentParser(description="提取源文件中的双引号字符串")
    parser.add_argument("file", type=Path, help="输入源文件")
    parser.add_argument("--encoding", default="utf-8-sig", help="文件编码")
    args = parser.parse_args()
    try:
        with args.file.open(encoding=args.encoding, newline="") as source:
            for value in extract_strings(ch for line in source for ch in line):
                print(value)
    except (OSError, ValueError, LookupError) as error:
        parser.exit(1, f"错误：{error}\n")


if __name__ == "__main__":
    main()
