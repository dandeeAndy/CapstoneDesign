from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Vision_color(_message.Message):
    __slots__ = ["vision"]
    VISION_FIELD_NUMBER: _ClassVar[int]
    vision: str
    def __init__(self, vision: _Optional[str] = ...) -> None: ...

class Counts(_message.Message):
    __slots__ = ["red", "yellow", "green", "blue", "purple"]
    RED_FIELD_NUMBER: _ClassVar[int]
    YELLOW_FIELD_NUMBER: _ClassVar[int]
    GREEN_FIELD_NUMBER: _ClassVar[int]
    BLUE_FIELD_NUMBER: _ClassVar[int]
    PURPLE_FIELD_NUMBER: _ClassVar[int]
    red: int
    yellow: int
    green: int
    blue: int
    purple: int
    def __init__(self, red: _Optional[int] = ..., yellow: _Optional[int] = ..., green: _Optional[int] = ..., blue: _Optional[int] = ..., purple: _Optional[int] = ...) -> None: ...

class robot1_color(_message.Message):
    __slots__ = ["now"]
    NOW_FIELD_NUMBER: _ClassVar[int]
    now: str
    def __init__(self, now: _Optional[str] = ...) -> None: ...

class remain(_message.Message):
    __slots__ = ["remain_line1", "remain_line2", "remain_line3", "remain_line4", "remain_line5", "remain_line6"]
    REMAIN_LINE1_FIELD_NUMBER: _ClassVar[int]
    REMAIN_LINE2_FIELD_NUMBER: _ClassVar[int]
    REMAIN_LINE3_FIELD_NUMBER: _ClassVar[int]
    REMAIN_LINE4_FIELD_NUMBER: _ClassVar[int]
    REMAIN_LINE5_FIELD_NUMBER: _ClassVar[int]
    REMAIN_LINE6_FIELD_NUMBER: _ClassVar[int]
    remain_line1: int
    remain_line2: int
    remain_line3: int
    remain_line4: int
    remain_line5: int
    remain_line6: int
    def __init__(self, remain_line1: _Optional[int] = ..., remain_line2: _Optional[int] = ..., remain_line3: _Optional[int] = ..., remain_line4: _Optional[int] = ..., remain_line5: _Optional[int] = ..., remain_line6: _Optional[int] = ...) -> None: ...

class maximum(_message.Message):
    __slots__ = ["maximum_line1", "maximum_line2", "maximum_line3", "maximum_line4", "maximum_line5", "maximum_line6"]
    MAXIMUM_LINE1_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_LINE2_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_LINE3_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_LINE4_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_LINE5_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_LINE6_FIELD_NUMBER: _ClassVar[int]
    maximum_line1: int
    maximum_line2: int
    maximum_line3: int
    maximum_line4: int
    maximum_line5: int
    maximum_line6: int
    def __init__(self, maximum_line1: _Optional[int] = ..., maximum_line2: _Optional[int] = ..., maximum_line3: _Optional[int] = ..., maximum_line4: _Optional[int] = ..., maximum_line5: _Optional[int] = ..., maximum_line6: _Optional[int] = ...) -> None: ...

class robot2_weight(_message.Message):
    __slots__ = ["robot2_weight"]
    ROBOT2_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    robot2_weight: int
    def __init__(self, robot2_weight: _Optional[int] = ...) -> None: ...

class robot3_weight(_message.Message):
    __slots__ = ["robot3_weight"]
    ROBOT3_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    robot3_weight: int
    def __init__(self, robot3_weight: _Optional[int] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
