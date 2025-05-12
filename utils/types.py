from typing import TypedDict, Literal, Union, NotRequired

OriginType = Literal["live", "hls", "local", "whitelist", "subscribe", "hotel", "multicast", "online_search"]
IPvType = Literal["ipv4", "ipv6", None]


class ChannelData(TypedDict):
    """
    Channel data types, including url, date, resolution, origin and ipv_type
    """
    id: int
    url: str
    host: str
    date: NotRequired[str | None]
    resolution: NotRequired[str | None]
    origin: OriginType
    ipv_type: IPvType
    location: NotRequired[str | None]
    isp: NotRequired[str | None]
    headers: NotRequired[dict[str, str] | None]
    catchup: NotRequired[dict[str, str] | None]
    extra_info: NotRequired[str]


CategoryChannelData = dict[str, dict[str, list[ChannelData]]]


class TestResult(TypedDict):
    """
    Test result types, including speed, delay, resolution
    """
    speed: int | float | None
    delay: int | float | None
    resolution: int | str | None


TestResultCacheData = dict[str, list[TestResult]]

ChannelTestResult = Union[ChannelData, TestResult]
