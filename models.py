from typing import TypedDict, Union


class WinMap(TypedDict):
    L: str
    O1: str
    O2: str
    S: Union[str, float]
    win1: str
    win2: str
