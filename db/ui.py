"""
通过简易的 WebUI 快速新增Key社的作品条目
"""

import datetime
import functools
import pathlib
import re
import sqlite3
import typing

import natsort
import nicegui


CON = sqlite3.connect("../database.db")

ClassType: tuple[str, ...] = tuple(
    name.stem
    for name in natsort.os_sorted(pathlib.Path("../docs/key").glob("*.md"))
    if name.stem != "index"
)


class Data:
    TypeType = tuple()  #: 可用的类别
    StatusType = tuple()  #: 可用的状态
    CollectType = tuple()  #: 可用的收集状态
    ClassType = ClassType  #: 可用的作品，根据已有的文档名称自动生成

    AllAttribute = (
        "name", "icon", "time", "the_type", "status",
        "collect", "tags", "bangumi_id", "steam_id", "vndb_id",
        "vgmdb_id", "introduction", "ps1", "ps2", "ps3",
        "the_class",
    )  #: 全部属性名称

    def __init__(self, keep_type="", keep_class=""):
        """
        原始条目父类
        """
        self._name = ""  #: 条目名称
        self._icon = ""  #: 条目状态图标，自动生成

        self._time = ""  #: 条目最早发布时间，精确到日
        self._type = ""  #: 条目类别
        self._status = ""  #: 条目状态

        self._collect = ""  #: 条目原始资源收集状态

        self._introduction = ""  #: 条目简介
        self._ps1 = ""  #: 条目备注1
        self._ps2 = ""  #: 条目备注2
        self._ps3 = ""  #: 条目备注3

        self._tags: list[str] = []  #: 条目标签
        self._class = ""  #: 条目所属的作品

        # 外部链接 ID
        self._bangumi_id = ""  #: Bangumi 番组计划
        self._steam_id = ""  #: Steam
        self._vndb_id = ""  #: VNDB
        self._vgmdb_id = ""  #: VGMdb

        if bool(keep_type):
            self.the_type = keep_type
        if bool(keep_class):
            self.the_class = keep_class
        return

    @property
    def name(self) -> str:
        """
        :return:
            条目名称
        """
        return self._name

    @name.setter
    def name(self, value: str):
        """
        :param value:
            条目名称
        """
        self._name = str(value).strip()
        return

    @property
    def icon(self) -> str:
        """
        :return:
            条目状态图标，
            自动生成
        """
        return self.collect[-1]

    @property
    def time(self) -> str:
        """
        需子类实现

        :return:
            条目最早发布时间，
            组合文本由子类实现
        """
        return self._time

    @time.setter
    def time(self, value: str):
        """
        :param value:
            条目最早发布时间
        """
        self._time = str(value).strip()
        return

    @property
    def time_source(self):
        """
        :return:
            条目最早发布时间，
            返回原始储存内容
        """
        return self._time

    @property
    def the_type(self) -> str:
        """
        :return:
            条目类别
        """
        return self._type

    @the_type.setter
    def the_type(self, value: str):
        """
        :param value:
            条目类别
        """
        if str(value) in self.TypeType:
            self._type = str(value).strip()
        else:
            raise ValueError(value)
        return

    @property
    def status(self) -> str:
        """
        :return:
            条目状态
        """
        return self._status

    @status.setter
    def status(self, value: str):
        """
        :param value:
            条目状态
        """
        if str(value) in self.StatusType:
            self._status = str(value).strip()
        else:
            raise ValueError(value)
        return

    @property
    def collect(self) -> str:
        """
        :return:
            条目原始资源收集状态
        """
        return self._collect

    @collect.setter
    def collect(self, value: str):
        """
        :param value:
            条目原始资源收集状态
        """
        if str(value) in self.CollectType:
            self._collect = str(value).strip()
        else:
            raise ValueError(value)
        return

    @property
    def introduction(self) -> str:
        """
        :return:
            条目简介
        """
        return self._introduction

    @introduction.setter
    def introduction(self, value: str):
        """
        :param value:
            条目简介
        """
        self._introduction = str(value).rstrip()
        return

    @property
    def ps1(self) -> str:
        """
        :return:
            条目备注1
        """
        return self._ps1

    @ps1.setter
    def ps1(self, value: str):
        """
        :param value:
            条目备注1
        """
        self._ps1 = str(value).rstrip()
        return

    @property
    def ps2(self) -> str:
        """
        :return:
            条目备注2
        """
        return self._ps2

    @ps2.setter
    def ps2(self, value: str):
        """
        :param value:
            条目备注2
        """
        self._ps2 = str(value).rstrip()
        return

    @property
    def ps3(self) -> str:
        """
        :return:
            条目备注3
        """
        return self._ps3

    @ps3.setter
    def ps3(self, value: str):
        """
        :param value:
            条目备注3
        """
        self._ps3 = str(value).rstrip()
        return

    @property
    def tags(self) -> str:
        """
        :return:
            条目标签，
            已转换为字符串
        """
        return ";".join(self._tags)

    @tags.setter
    def tags(self, value: list[str] | str):
        """
        :param value:
            条目标签，
            当传入列表时会进行覆盖设置
        """
        if isinstance(value, str) and bool(str(value)):
            self._tags.append(str(value).strip())
        elif isinstance(value, list):
            self._tags = list(str(tag).strip() for tag in value if bool(tag))
        else:
            raise ValueError(value)
        return

    @property
    def the_class(self) -> str:
        """
        :return:
            条目所属的作品
        """
        return self._class

    @the_class.setter
    def the_class(self, value: str):
        """
        :param value:
            条目所属的作品
        """
        if str(value) in self.ClassType:
            self._class = str(value).strip()
        else:
            raise ValueError(value)
        return

    @the_class.deleter
    def the_class(self):
        """
        清空条目所属的作品
        """
        self._class = ""
        return

    @property
    def bangumi_id(self) -> str:
        """
        :return:
            Bangumi 番组计划 外部链接 ID
        """
        return self._bangumi_id

    @bangumi_id.setter
    def bangumi_id(self, value: str):
        """
        :param value:
            Bangumi 番组计划 外部链接 ID
        """
        self._bangumi_id = str(value).strip()
        return

    @property
    def steam_id(self) -> str:
        """
        :return:
            Steam 外部链接 ID
        """
        return self._steam_id

    @steam_id.setter
    def steam_id(self, value: str):
        """
        :param value:
            Steam 外部链接 ID
        """
        self._steam_id = str(value).strip()
        return

    @property
    def vndb_id(self) -> str:
        """
        :return:
            VNDB 外部链接 ID
        """
        return self._vndb_id

    @vndb_id.setter
    def vndb_id(self, value: str):
        """
        :param value:
            VNDB 外部链接 ID
        """
        self._vndb_id = str(value).strip()
        return

    @property
    def vgmdb_id(self) -> str:
        """
        :return:
            VGMdb 外部链接 ID
        """
        return self._vgmdb_id

    @vgmdb_id.setter
    def vgmdb_id(self, value: str):
        """
        :param value:
            VGMdb 外部链接 ID
        """
        self._vgmdb_id = str(value).strip()
        return

    def submit(self):
        """
        需子类实现

        提交条目信息到数据库，
        不会额外检查数据类型，
        因此若类型错误，
        则由数据库表的约束抛出异常
        """
        raise NotImplementedError

    def new(self, keep=True) -> typing.Self:
        """
        需子类实现

        返回类的新实例，
        并根据需要保留部分信息

        :param keep:
            是否保留部分数据
        """
        raise NotImplementedError


class KeyData(Data):
    TypeType = ("游戏", "动漫", "小说", "书籍", "漫画", "画集", "设定集", "公式书", "杂志", "其它")  #: 可用的类别
    StatusType = ("未发售👀", "已发售🎉", "连载中🚋", "已完结🎉", "不适用⛔")  #: 可用的状态
    CollectType = ("已收藏✅", "无资源❌", "未收藏🔘", "有问题❓", "等待中👀", "更新中🚋", "不适用⛔")  #: 可用的收集状态

    AllAttribute = (
        "name", "name_zh", "icon", "time", "the_type",
        "status", "collect", "collect_zh", "tags", "bangumi_id",
        "steam_id", "vndb_id", "vgmdb_id", "introduction", "ps1",
        "ps2", "ps3", "the_class", "the_class_other",
    )  #: 全部属性名称

    def __init__(self, keep_type="", keep_class="", keep_class_other=""):
        """
        通用条目数据类

        :param keep_type:
            可选的条目类别

        :param keep_class:
            可选的条目所属作品

        :param keep_class_other:
            可选的条目辅助所属作品
        """
        super().__init__(keep_type, keep_class)

        self._name_zh = ""  #: 条目中文名称
        self._collect_zh = ""  #: 条目汉化资源收集状态
        self._class_other = ""  #: 为 杂货铺 提供额外信息的所属分类
        self._main = False  #: 主要条目标志

        if bool(keep_class_other):
            self.the_class_other = keep_class_other
        return

    @property
    def icon(self) -> str:
        collect_icon = self.collect[-1]
        collect_zh_icon = self.collect_zh[-1]
        if collect_icon not in ('❌', '🔘'):
            return collect_icon
        else:
            if collect_zh_icon not in ('❌', '🔘', '⛔'):
                return collect_zh_icon
            else:
                return collect_icon

    @property
    def time(self) -> str:
        """
        :return:
            条目最早发布时间，
            会根据条目状态更改内容
        """
        if self.status in ("未发售👀", ):
            return f"{self._time} (预计)"
        else:
            return self._time

    @time.setter
    def time(self, value: str):
        self._time = str(value).strip()
        return

    @property
    def name_zh(self) -> str:
        """
        :return:
            条目中文名称
        """
        return self._name_zh

    @name_zh.setter
    def name_zh(self, value: str):
        """
        :param value:
            条目中文名称
        """
        self._name_zh = str(value).strip()
        return

    @property
    def collect_zh(self) -> str:
        """
        :return:
            条目汉化资源收集状态
        """
        return self._collect_zh

    @collect_zh.setter
    def collect_zh(self, value: str):
        """
        :param value:
            条目汉化资源收集状态
        """
        if str(value) in self.CollectType:
            self._collect_zh = str(value).strip()
        else:
            raise ValueError(value)
        return

    @property
    def the_class_other(self) -> str:
        """
        :return:
            为 杂货铺 提供额外信息的所属分类
        """
        if self.the_class == self.ClassType[0]:
            return self._class_other
        else:
            return ""

    @the_class_other.setter
    def the_class_other(self, value: str):
        """
        :param value:
            为 杂货铺 提供额外信息的所属分类
        """
        if str(value) != self.ClassType[0]:
            self._class_other = str(value).strip()
        else:
            raise ValueError(value)
        return

    @property
    def main(self) -> bool:
        """
        :return:
            主要条目标志
        """
        return self._main

    @main.setter
    def main(self, value: bool):
        """
        :param value:
            主要条目标志
        """
        self._main = bool(value)
        return

    def submit(self):
        """
        提交数据至数据库

        数据验证将委托至数据库内的相关约束

        :raise sqlite3.DatabaseError:
            当未通过数据库验证时抛出
        """
        if self.main:
            table_name = "main"
        else:
            table_name = "key"

        global CON
        cur = CON.cursor()

        params = [getattr(self, item) for item in self.AllAttribute]
        cur.execute(
            f"INSERT INTO {table_name} VALUES ({('?, ' * len(params))[: -2]})",
            params
        )
        CON.commit()
        cur.close()
        return

    def new(self, keep=True) -> typing.Self:
        """
        返回类的新实例，
        并根据需要保留部分信息

        :param keep:
            是否保留部分数据
        """
        if keep:
            return KeyData(
                keep_type=self.the_type,
                keep_class=self.the_class,
                keep_class_other=self.the_class_other)
        else:
            return KeyData()


class MusicData(Data):
    TypeType = ("音乐", )  #: 可用的类别
    StatusType = ("未发售👀", "已发售🎉")  #: 可用的状态
    CollectType = ("已收藏✅", "无资源❌", "未收藏🔘", "有问题❓", "等待中👀", "不适用⛔")  #: 可用的收集状态
    ClassType = ("",) + ClassType
    ClassMusicType = ("KSLA", "KSLC", "KSLV", "KSL", "Key-Product", "Key-Other")  # 可用的Key社音乐类别
    FileType = ("未知", "WAV", "FLAC", "MP3")  #: 可用的音乐格式

    AllAttribute = (
        "name", "icon", "artist", "catalog_number", "time",
        "the_type", "status", "collect", "collect_booklet", "collect_dvd",
        "file_type", "tags", "bangumi_id", "steam_id", "vndb_id",
        "vgmdb_id", "introduction", "ps1", "ps2", "ps3",
        "the_class", "the_class_music",
    )  #: 全部属性名称

    def __init__(self, keep_type="", keep_class="", keep_class_music=""):
        """
        音乐条目数据类

        :param keep_type:
            可选的条目类别

        :param keep_class:
            可选的条目所属作品

        :param keep_class_music:
            可选的Key社音乐类别
        """
        super().__init__(keep_type, keep_class)
        self.the_type = self.TypeType[0]

        self._artist: list[str] = []  #: 艺术家
        self._catalog_number: list[str] = []  #: 专辑编号
        self._file_type = ""  #: 音乐格式
        self._collect_booklet = ""  #: 条目 Booklet 资源收集状态
        self._collect_dvd = ""  #: 条目 BD/DVD 资源收集状态
        self._class_music = ""  #: Key社音乐类别

        if bool(keep_class_music):
            self.keep_class_music = keep_class_music
        return

    @property
    def icon(self) -> str:
        icon_tuple = ('🔘', '❓', '👀')
        if self.collect_booklet[-1] in icon_tuple:
            return self.collect_booklet[-1]
        elif self.collect_dvd[-1] in icon_tuple:
            return self.collect_dvd[-1]
        else:
            return self.collect[-1]

    @property
    def time(self) -> str:
        """
        :return:
            条目最早发布时间，
            会根据条目状态更改内容
        """
        if self.status in ("未发售👀", ):
            return f"{self._time} (预计)"
        else:
            return self._time

    @time.setter
    def time(self, value: str):
        self._time = str(value).strip()
        return

    @property
    def artist(self) -> str:
        """
        :return:
            艺术家
        """
        return ';'.join(self._artist)

    @artist.setter
    def artist(self, value: str | list[str]):
        """
        :param value:
            艺术家
        """
        if isinstance(value, str) and bool(str(value)):
            self._artist.append(str(value).strip())
        elif isinstance(value, list):
            self._artist = list(str(artist).strip() for artist in value if bool(artist))
        else:
            raise TypeError(value)
        return

    @property
    def catalog_number(self) -> str:
        """
        :return:
            专辑编号
        """
        if bool(self._catalog_number):
            return '&'.join(self._catalog_number)
        else:
            return '&'.join(["N/A"])

    @catalog_number.setter
    def catalog_number(self, value: str | list[str]):
        """
        :param value:
            专辑编号
        """
        if isinstance(value, list):
            self._catalog_number = list(str(number).strip() for number in value if bool(number))
        elif isinstance(value, str) and bool(str(value)):
            self._catalog_number.append(str(value).strip())
        else:
            raise TypeError(value)
        return

    @property
    def file_type(self) -> str:
        """
        :return:
            音乐格式
        """
        return self._file_type

    @file_type.setter
    def file_type(self, value: str):
        """
        :param value:
            音乐格式
        """
        if value in self.FileType:
            self._file_type = str(value).strip()
        else:
            raise ValueError(value)
        return

    @property
    def collect_booklet(self) -> str:
        """
        :return:
            条目 Booklet 资源收集状态
        """
        return self._collect_booklet

    @collect_booklet.setter
    def collect_booklet(self, value: str):
        """
        :param value:
            条目 Booklet 资源收集状态
        """
        if value in self.CollectType:
            self._collect_booklet = str(value).strip()
        else:
            raise ValueError(value)
        return

    @property
    def collect_dvd(self) -> str:
        """
        :return:
            条目 BD/DVD 资源收集状态
        """
        return self._collect_dvd

    @collect_dvd.setter
    def collect_dvd(self, value: str):
        """
        :param value:
            条目 BD/DVD 资源收集状态
        """
        if value in self.CollectType:
            self._collect_dvd = str(value).strip()
        else:
            raise ValueError(value)
        return

    @property
    def the_class(self) -> str:
        return self._class

    @the_class.setter
    def the_class(self, value: str):
        if str(value) != self.ClassType[1]:
            self._class = str(value).strip()
        else:
            raise ValueError(value)
        return

    @the_class.deleter
    def the_class(self):
        self._class = ""
        return

    @property
    def the_class_music(self) -> str:
        """
        :return:
            Key社音乐类别
        """
        return self._class_music

    @the_class_music.setter
    def the_class_music(self, value: str):
        """
        :param value:
            Key社音乐类别
        """
        if value in self.ClassMusicType:
            self._class_music = str(value).strip()
        else:
            raise ValueError(value)
        return

    def submit(self):
        """
        提交数据至数据库

        数据验证将委托至数据库内的相关约束

        :raise sqlite3.DatabaseError:
            当未通过数据库验证时抛出
        """
        global CON
        cur = CON.cursor()

        params = [getattr(self, item) for item in self.AllAttribute]
        # noinspection SqlInsertValues
        cur.execute(
            f"INSERT INTO music VALUES ({('?, ' * len(params))[: -2]})",
            params
        )
        CON.commit()
        cur.close()
        return

    def new(self, keep=True) -> typing.Self:
        """
        返回类的新实例，
        并根据需要保留部分信息

        :param keep:
            是否保留部分数据
        """
        if keep:
            return MusicData(
                keep_type=self.the_type,
                keep_class=self.the_class,
                keep_class_music=self.the_class_music)
        else:
            return MusicData()


def get_date(value: str) -> datetime.date:
    """
    处理不同类型的日期输入

    :param value:
        原始的日期输入

    :return:
        正确映射后的 datetime.date

    :raise TypeError:
        当 日期格式错误 时抛出

    :raise ValueError:
        当 日期内容不合法 时抛出
    """
    m = re.fullmatch(
        r"(?P<year>\d{4})[/\-年](?P<month>\d{1,2})[/\-月](?P<day>\d{1,2})(日)?",
        str(value)
    )

    if m is None:
        raise TypeError("日期格式错误")
    else:
        year = m.groupdict()["year"]
        month = m.groupdict()["month"]
        day = m.groupdict()["day"]
        return datetime.date(int(year), int(month), int(day))


def verify_date(value: str) -> str | None:
    """
    日期输入的验证函数
    """
    if not bool(value):
        return "条目发行日期不能为空"
    try:
        get_date(value)
    except TypeError:
        return "日期格式错误"
    except ValueError:
        return "日期内容不合法"
    else:
        return None


def forward_date(value: str) -> str:
    """
    将日期输入规范化以便于传递
    """
    try:
        date = get_date(value)
    except (TypeError, ValueError):
        return ""
    else:
        return date.strftime("%Y/%m/%d")


def get_id(value: str, web: typing.Literal["bangumi", "steam", "vndb", "vgmdb"]) -> str:
    """
    提取外部网站链接中的 ID，
    对于纯数字输入将直接返回

    :param value:
        原始 ID 或外部链接输入

    :param web:
        外部链接的类型

    :return:
        条目对应的 id

    :raise TypeError:
        当外部链接不合法时抛出

    :raise ValueError:
        当外部链接类型错误时抛出，
        这是一个内部编码错误时才会抛出的异常
    """
    if bool(re.fullmatch(r"\d+", str(value))):
        return str(value)

    if web == "bangumi":
        m = re.fullmatch(
            r"http(s)?://(bangumi|bgm|chii)\.(tv|in)/subject/(?P<id>\d+)",
            str(value)
        )
    elif web == "steam":
        m = re.fullmatch(
            r"http(s)?://store.steampowered.com/app/(?P<id>\d+)/.*",
            str(value)
        )
    elif web == "vndb":
        m = re.fullmatch(
            r"http(s)?://vndb.org/v(?P<id>\d+)",
            str(value)
        )
    elif web == "vgmdb":
        m = re.fullmatch(
            r"http(s)?://vgmdb.net/album/(?P<id>\d+)",
            str(value)
        )
    else:
        raise ValueError(f"无效的外部链接类型 {web}")

    if m is None:
        raise TypeError("链接格式不合法")
    else:
        return m.groupdict()["id"]


def verify_id(value: str, web: typing.Literal["bangumi", "steam", "vndb", "vgmdb"]) -> str | None:
    """
    外部链接的验证函数
    """
    if not bool(value):
        return None
    try:
        get_id(value, web)
    except TypeError:
        return "链接格式不合法"
    else:
        return None


def forward_id(value: str, web: typing.Literal["bangumi", "steam", "vndb", "vgmdb"]) -> str:
    """
    正确处理 ID 获取时的异常以便于传递
    """
    if not bool(value):
        return ""
    try:
        return get_id(value, web)
    except TypeError:
        return ""


def forward_tags(value: list[str], sep: str) -> list[str]:
    """
    确保 tag 输入中不会包含分隔字符

    :param value:
        原始输入

    :param sep:
        分隔字符

    :return:
        安全处理后的输入
    """
    if bool(value):
        if sep in value[-1]:
            nicegui.ui.notify(f"输入中包含非法字符: '{sep}'", type="warning")
            return value[:-1]
        else:
            return value
    else:
        return value


def split_artist(value: str) -> list[str]:
    """
    自动分割艺术家输入

    :param value:
        原始的艺术家输入

    :return:
        分割后的输入列表
    """
    if not bool(value):
        return []

    guess_sep = (';', ',', '/', '、')
    artist_list = [value]
    for s in guess_sep:
        if value.count(s) > 1:
            artist_list = value.split(s)
            break
    return [a.strip() for a in artist_list]


def _get_full_catalog_number(number_f: str, number_e: str) -> list[str]:
    """
    生成专辑编号列表

    :param number_f:
        第一个专辑编号

    :param number_e:
        截止的数字

    :return:
        完整的专辑编号列表
    """
    prefix = number_f[:-len(number_e)]
    catalog_number_list = []
    for suffix in range(int(number_f[-len(number_e):]), int(number_e) + 1):
        suffix = '0' * abs(len(number_e) - len(str(suffix))) + str(suffix)
        catalog_number_list.append(f"{prefix}{suffix}")
    return catalog_number_list


def split_catalog_number(value: str) -> list[str]:
    """
    自动分割专辑编号输入

    :param value:
        原始的专辑编号输入

    :return:
        分割后的输入列表
    """
    if not bool(value):
        return []

    if '&' in value:
        catalog_number_list = value.split('&')
    elif value.count('-') == 2:
        number_check_list = value.rsplit('-', maxsplit=2)
        try:
            int(number_check_list[1])
            int(number_check_list[2])
        except ValueError:
            catalog_number_list = [value]
        else:
            catalog_number_list = _get_full_catalog_number(*value.rsplit('-', maxsplit=1))
    elif "~" in value:
        catalog_number_list = _get_full_catalog_number(*value.rsplit('~', maxsplit=1))
    else:
        catalog_number_list = [value]

    return list(c.strip() for c in catalog_number_list)


def get_table_data(mode: typing.Literal["主要作品", "通用作品", "音乐作品"]) -> dict[int, KeyData | MusicData]:
    """
    从数据库中读取数据并转换为 Data 的子类

    :param mode:
        数据表的类型

    :return:
        包含 Data 的子类和对应 ID 的字典
    """
    if mode == "主要作品":
        table_name = "main"
        data = KeyData()
    elif mode == "通用作品":
        table_name = "key"
        data = KeyData()
    elif mode == "音乐作品":
        table_name = "music"
        data = MusicData()
    else:
        raise TypeError(mode)

    cur = CON.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    sql_data = cur.fetchall()

    table_data = {}
    for i in range(len(sql_data)):
        for attribute, value in zip(data.AllAttribute, sql_data[i]):
            if attribute == "icon":
                continue
            elif attribute == "time" and value[-5:] == " (预计)":
                value = value[:-5]
            elif attribute == "tags":
                value = value.split(';')
            elif attribute == "artist":
                value = value.split(';')
            elif attribute == "catalog_number":
                value = value.split('&')
            elif attribute == "the_class_other" and not bool(value):
                continue

            setattr(data, attribute, value)

        if mode == "主要作品":
            setattr(data, "main", True)

        table_data[i] = data
        data = data.new(keep=False)
    return table_data


def get_table_columns(mode: typing.Literal["主要作品", "通用作品", "音乐作品"]) -> list[dict[str, str]]:
    """
    :param mode:
        数据表的类型

    :return:
        对应的数据表的行
    """
    if mode in ("主要作品", "通用作品"):
        columns = [
            {'name': 'name', 'label': '条目名称', 'field': 'name', 'align': 'left'},
            {'name': 'name_zh', 'label': '条目名称 (中文)', 'field': 'name_zh', 'align': 'left'},
            {'name': 'icon', 'label': '条目状态', 'field': 'icon', 'align': 'left'},
            {'name': 'the_class', 'label': '条目所属作品', 'field': 'the_class', 'align': 'left'},
            {'name': 'the_class_other', 'label': '条目所属作品 (辅助)', 'field': 'the_class_other', 'align': 'left'},
        ]
    elif mode == "音乐作品":
        columns = [
            {'name': 'name', 'label': '专辑名', 'field': 'name', 'align': 'left'},
            {'name': 'icon', 'label': '专辑状态', 'field': 'icon', 'align': 'left'},
            {'name': 'the_class', 'label': '专辑所属作品', 'field': 'the_class', 'align': 'left'},
            {'name': 'the_class_music', 'label': 'Key社音乐类型', 'field': 'the_class_music', 'align': 'left'},
        ]
    else:
        raise TypeError(mode)
    return columns


def get_table_rows(
        mode: typing.Literal["主要作品", "通用作品", "音乐作品"],
        table_data: dict[int, KeyData | MusicData]
) -> list[dict[str, int | str]]:
    """
    :param mode:
        数据表的类型

    :param table_data:
        包含 Data 子类和 ID 的字典

    :return:
        对应的数据表的列，
        逆序排序
    """
    rows = []
    if mode in ("主要作品", "通用作品"):
        for i in reversed(table_data.keys()):
            data = table_data[i]
            rows_dict = {
                'id': i,
                'name': data.name,
                'name_zh': data.name_zh,
                'icon': data.icon,
                'the_class': data.the_class,
                'the_class_other': data.the_class_other
            }
            rows.append(rows_dict)
    elif mode == "音乐作品":
        for j in reversed(table_data.keys()):
            data = table_data[j]
            rows_dict = {
                'id': j,
                'name': data.name,
                'icon': data.icon,
                'the_class': data.the_class,
                'the_class_music': data.the_class_music
            }
            rows.append(rows_dict)
    else:
        raise TypeError(mode)
    return rows


# noinspection DuplicatedCode
@nicegui.ui.refreshable
def web_ui(
        key_data: KeyData | None = None,
        music_data: MusicData | None = None,
        data_type_value: typing.Literal["通用", "音乐"] = "通用"
):
    """
    构建 WebUI

    并负责内容验证

    :param key_data:
        提前设定完成的 key_data

    :param music_data:
        提前设定完成的 music_data

    :param data_type_value:
        默认条目页面
    """
    if key_data is None:
        key_data = KeyData()
    if music_data is None:
        music_data = MusicData()

    key_check_list: list[nicegui.elements] = []
    music_check_list: list[nicegui.elements] = []

    nicegui.ui.add_css(
        """
        body {
            background-color: #eaeaea;
        }
        """
    )

    def submit(
            mode: typing.Literal["key", "music"],
            check_list: list[nicegui.elements],
            button: nicegui.ui.dropdown_button | nicegui.ui.button,
            keep=True
    ):
        """
        执行全部输入元素的校验函数并提交至数据库

        :param mode:
            待提交的类型

        :param check_list:
            包含全部输入元素的列表

        :param button:
            发送点击事件的按钮对象，
            用于实现幂等性

        :param keep:
            是否清空全部输入
        """
        button.disable()

        validate_list: list[bool] = []
        for element in check_list:
            try:
                validate_list.append(element.validate())
            except AttributeError:
                pass
        if all(validate_list):
            nonlocal key_data
            nonlocal music_data
            try:
                if mode == "key":
                    key_data.submit()
                    key_data = key_data.new(keep)
                elif mode == "music":
                    music_data.submit()
                    music_data = music_data.new(keep)
            except sqlite3.DatabaseError as error:
                nicegui.ui.notify("未能通过数据库校验!", type="negative")
                button.enable()
                raise error from error
            else:
                nicegui.ui.notify("已提交", type="positive")
                button.enable()
                web_ui.refresh(key_data=key_data, music_data=music_data, data_type_value=data_type.value)
        else:
            nicegui.ui.notify("存在未通过校验的输入", type="negative")
            button.enable()

        return

    def clear(
            mode: typing.Literal["key", "music"],
            button: nicegui.ui.dropdown_button | nicegui.ui.button
    ):
        """
        清除全部输入

        :param mode:
            待清空输入的类型

        :param button:
            发送点击事件的按钮对象，
            用于实现幂等性
        """
        button.disable()
        nonlocal key_data
        nonlocal music_data
        if mode == "key":
            key_data = key_data.new(keep=False)
        elif mode == "music":
            music_data = music_data.new(keep=False)
        else:
            raise TypeError(mode)
        button.enable()
        nicegui.ui.notify("已清空", type="positive")
        web_ui.refresh(key_data=key_data, music_data=music_data, data_type_value=data_type.value)
        return

    with nicegui.ui.column().classes('w-full items-center') as page_main:

        # 类型切换
        with nicegui.ui.card(align_items='center').classes('w-2/5'):
            with nicegui.ui.row(align_items="center"):
                nicegui.ui.label("请选择条目类型: ")
                data_type = nicegui.ui.toggle(["通用", "音乐"], value=data_type_value)

        nicegui.ui.separator().classes('w-2/5')

        # 作品部分
        with nicegui.ui.column().bind_visibility_from(data_type, 'value', value="通用").classes('w-2/5'):
            with nicegui.ui.card().classes('w-full'):
                nicegui.ui.label("⦿ 条目名称")

                key_name = nicegui.ui.input(
                    label="条目名称 (原文)",
                    placeholder="请输入...",
                    validation={'条目名称不能为空': lambda value: bool(value)}
                )
                key_name.classes('w-full')
                key_name.bind_value(
                    key_data,
                    "name",
                    forward=lambda value: value if isinstance(value, str) else "",
                )
                key_name.props('clearable')
                key_check_list.append(key_name)

                key_name_zh = nicegui.ui.input(
                    label="条目名称 (中文) | 没有则置空",
                    placeholder="请输入..."
                )
                key_name_zh.classes('w-full')
                key_name_zh.bind_value(
                    key_data,
                    "name_zh",
                    forward=lambda value: value if isinstance(value, str) else "",
                )
                key_name_zh.props('clearable')
                key_check_list.append(key_name_zh)

            with nicegui.ui.card().classes('w-full'):
                nicegui.ui.label("⦿ 条目元数据")

                with nicegui.ui.row(align_items="center").classes('w-full'):
                    key_class = nicegui.ui.select(
                        list(key_data.ClassType),
                        label="条目所属作品",
                        with_input=True,
                        validation={'条目所属作品不能为空': lambda value: bool(value)}
                    )
                    key_class.classes('w-4/5')
                    key_class.bind_value(
                        key_data,
                        "the_class",
                        forward=lambda value: value if isinstance(value, str) else ""
                    )
                    key_check_list.append(key_class)

                    key_main = nicegui.ui.checkbox(text="主要作品", value=False)
                    key_main.bind_value(key_data, "main")
                    key_main.bind_enabled_from(
                        key_class,
                        "value",
                        backward=lambda value: value != key_data.ClassType[0]
                    )
                    key_check_list.append(key_main)

                key_other_class = nicegui.ui.input(
                    label="条目所属作品 (辅助)",
                    placeholder="请输入...",
                    validation={
                        '条目所属作品 (辅助) 不能为空':
                            lambda value: (key_class.value != key_data.ClassType[0]) or bool(value)
                    }
                )
                key_other_class.classes('w-full')
                key_other_class.props('clearable')
                key_other_class.bind_value(
                    key_data,
                    "the_class_other",
                    forward=lambda value: value if isinstance(value, str) and (value != key_data.ClassType[0]) else ""
                )
                key_other_class.bind_enabled_from(
                    key_class,
                    "value",
                    backward=lambda value: value == key_data.ClassType[0]
                )
                key_other_class.tooltip("辅助 杂货铺 部分正确处理条目分类")
                key_check_list.append(key_other_class)

                key_tag = nicegui.ui.select(
                    key_data.tags.split(";") if bool(key_data.tags) else [],
                    label="条目标签",
                    new_value_mode="add-unique",
                    multiple=True,
                    clearable=True
                )
                key_tag.classes('w-full')
                key_tag.props('use-chips')
                key_tag.bind_value(
                    key_data,
                    "tags",
                    forward=lambda value: forward_tags(value, sep=";"),
                    backward=lambda value: value.split(";")
                )
                key_tag.tooltip("请勿输入包含 ; 的内容")
                key_check_list.append(key_tag)

            with nicegui.ui.card().classes('w-full'):
                nicegui.ui.label("⦿ 条目信息")

                with nicegui.ui.row(align_items="center").classes('w-full'):
                    key_time =  nicegui.ui.input(
                        label="条目发行日期",
                        placeholder="请输入...",
                        validation=verify_date
                    )
                    key_time.classes('w-2/5')
                    key_time.set_value(key_data.time_source)
                    key_time.bind_value_to(
                        key_data,
                        "time",
                        forward=forward_date
                    )
                    with nicegui.ui.menu().props('no-parent-event') as menu:
                        with nicegui.ui.date(mask="YYYY/MM/DD") as date:
                            date.set_value(key_data.time_source)
                            key_time.bind_value(
                                date,
                                "value",
                                forward=forward_date
                            )
                            with nicegui.ui.row().classes('justify-end'):
                                nicegui.ui.button('关闭', on_click=menu.close).props('flat')
                    with key_time.add_slot('append'):
                        nicegui.ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                    key_check_list.append(key_time)

                    with nicegui.ui.column(align_items="center").classes("w-1/2 items-center"):
                        nicegui.ui.label().bind_text_from(
                            key_data,
                            "time",
                            backward=lambda value: value if bool(value) else "请输入条目发行日期"
                        ).tooltip("进行规范化之后的条目发行日期")

                with nicegui.ui.row().classes('w-full'):
                    key_type = nicegui.ui.select(
                        list(key_data.TypeType),
                        label="条目类别",
                        validation={'条目类别不能为空': lambda value: bool(value)}
                    )
                    key_type.classes('w-2/5')
                    key_type.bind_value(
                        key_data,
                        "the_type",
                        forward=lambda value: value if isinstance(value, str) else ""
                    )
                    key_check_list.append(key_type)

                    key_status = nicegui.ui.select(
                        list(key_data.StatusType),
                        label="条目状态",
                        validation={'条目状态不能为空': lambda value: bool(value)}
                    )
                    key_status.classes('w-1/2')
                    key_status.bind_value(
                        key_data,
                        "status",
                        forward=lambda value: value if isinstance(value, str) else ""
                    )
                    key_check_list.append(key_status)

            with nicegui.ui.card().classes('w-full'):
                nicegui.ui.label("⦿ 条目收藏状态")

                with nicegui.ui.row().classes('w-full'):
                    key_collect = nicegui.ui.select(
                        list(key_data.CollectType),
                        label="原版资源收藏状态",
                        validation={'原版资源收藏状态不能为空': lambda value: bool(value)}
                    )
                    key_collect.classes('w-2/5')
                    key_collect.bind_value(
                        key_data,
                        "collect",
                        forward=lambda value: value if isinstance(value, str) else ""
                    )
                    key_check_list.append(key_collect)

                    key_collect_zh = nicegui.ui.select(
                        list(key_data.CollectType),
                        label="汉化资源收藏状态",
                        validation={'汉化资源收藏状态不能为空': lambda value: bool(value)}
                    )
                    key_collect_zh.classes('w-1/2')
                    key_collect_zh.bind_value(
                        key_data,
                        "collect_zh",
                        forward=lambda value: value if isinstance(value, str) else ""
                    )
                    key_check_list.append(key_collect_zh)

                    def key_status_sync(value: str):
                        """同步条目状态的改变"""
                        if value == "未发售👀":
                            key_collect.value = "等待中👀"
                            key_collect_zh.value = "不适用⛔"
                        elif value == "连载中🚋":
                            key_collect.value = "更新中🚋"
                        elif value == "不适用⛔":
                            key_collect.value = "不适用⛔"
                            key_collect_zh.value = "不适用⛔"
                        return

                    key_status.on_value_change(callback=lambda event: key_status_sync(event.value))

            with nicegui.ui.card().classes('w-full'):
                nicegui.ui.label("⦿ 条目外部链接")

                with nicegui.ui.row().classes('w-full'):
                    with nicegui.ui.input(label="Bangumi 链接", placeholder="请输入...") as key_bangumi:
                        key_bangumi.validation = functools.partial(verify_id, web="bangumi")
                        key_bangumi.classes('w-2/5')
                        key_bangumi.set_value(key_data.bangumi_id)
                        key_bangumi.bind_value_to(
                            key_data,
                            "bangumi_id",
                            forward=functools.partial(forward_id, web="bangumi")
                        )
                        key_bangumi.props('clearable')
                        tooltip = nicegui.ui.tooltip()
                        tooltip.bind_text_from(key_data,"bangumi_id")
                        tooltip.bind_visibility_from(
                            key_data,
                            "bangumi_id",
                            backward=lambda value: bool(value)
                        )
                        key_check_list.append(key_bangumi)

                    with nicegui.ui.input(label="Steam 链接", placeholder="请输入...") as key_steam:
                        key_steam.validation = functools.partial(verify_id, web="steam")
                        key_steam.classes('w-1/2')
                        key_steam.set_value(key_data.steam_id)
                        key_steam.bind_value_to(
                            key_data,
                            "steam_id",
                            forward=functools.partial(forward_id, web="steam")
                        )
                        key_steam.props('clearable')
                        tooltip = nicegui.ui.tooltip()
                        tooltip.bind_text_from(key_data,"steam_id")
                        tooltip.bind_visibility_from(
                            key_data,
                            "steam_id",
                            backward=lambda value: bool(value)
                        )
                        key_check_list.append(key_steam)

                with nicegui.ui.row().classes('w-full'):
                    with nicegui.ui.input(label="VNDB 链接", placeholder="请输入...") as key_vndb:
                        key_vndb.validation = functools.partial(verify_id, web="vndb")
                        key_vndb.classes('w-2/5')
                        key_vndb.set_value(key_data.vndb_id)
                        key_vndb.bind_value_to(
                            key_data,
                            "vndb_id",
                            forward=functools.partial(forward_id, web="vndb")
                        )
                        key_vndb.props('clearable')
                        tooltip = nicegui.ui.tooltip()
                        tooltip.bind_text_from(key_data,"vndb_id")
                        tooltip.bind_visibility_from(
                            key_data,
                            "vndb_id",
                            backward=lambda value: bool(value)
                        )
                        key_check_list.append(key_vndb)

                    with nicegui.ui.input(label="VGMdb 链接", placeholder="请输入...") as key_vgmdb:
                        key_vgmdb.validation = functools.partial(verify_id, web="vgmdb")
                        key_vgmdb.classes('w-1/2')
                        key_vgmdb.set_value(key_data.vgmdb_id)
                        key_vgmdb.bind_value_to(
                            key_data,
                            "vgmdb_id",
                            forward=functools.partial(forward_id, web="vgmdb")
                        )
                        key_vgmdb.props('clearable')
                        tooltip = nicegui.ui.tooltip()
                        tooltip.bind_text_from(key_data,"vgmdb_id")
                        tooltip.bind_visibility_from(
                            key_data,
                            "vgmdb_id",
                            backward=lambda value: bool(value)
                        )
                        key_check_list.append(key_vgmdb)

            with nicegui.ui.card().classes('w-full'):
                nicegui.ui.label("⦿ 条目简介和备注")

                key_introduction = nicegui.ui.textarea(
                    label="条目简介",
                    placeholder="请输入..."
                )
                key_introduction.classes('w-full')
                key_introduction.bind_value(
                    key_data,
                    "introduction",
                    forward=lambda value: value if isinstance(value, str) else ""
                )
                key_introduction.props('clearable')
                key_check_list.append(key_introduction)

                nicegui.ui.separator().classes('w-full')

                key_ps1 = nicegui.ui.textarea(
                    label="条目备注1",
                    placeholder="请输入..."
                )
                key_ps1.classes('w-full')
                key_ps1.bind_value(
                    key_data,
                    "ps1",
                    forward=lambda value: value if isinstance(value, str) else ""
                )
                key_ps1.props('clearable')
                key_check_list.append(key_ps1)

                key_ps2 = nicegui.ui.textarea(
                    label="条目备注2",
                    placeholder="请输入...",
                    validation={'请填写在 备注1 中': lambda value: bool(key_ps1.value) or (not bool(value))}
                )
                key_ps2.classes('w-full')
                key_ps2.bind_value(
                    key_data,
                    "ps2",
                    forward=lambda value: value if isinstance(value, str) else ""
                )
                key_ps2.props('clearable')
                key_check_list.append(key_ps2)

                key_ps3 = nicegui.ui.textarea(
                    label="条目备注3",
                    placeholder="请输入...",
                    validation={
                        '请填写在 备注1 中': lambda value: bool(key_ps1.value) or (not bool(value)),
                        '请填写在 备注2 中': lambda value: bool(key_ps2.value) or (not bool(value))
                    }
                )
                key_ps3.classes('w-full')
                key_ps3.bind_value(
                    key_data,
                    "ps3",
                    forward=lambda value: value if isinstance(value, str) else ""
                )
                key_ps3.props('clearable')
                key_check_list.append(key_ps3)

            nicegui.ui.separator().classes('w-full')

            with nicegui.ui.row().classes('w-full justify-end'):
                with nicegui.ui.dropdown_button(
                        "提交",
                        value=False,
                        on_click=lambda event: submit(
                            mode="key",
                            check_list=key_check_list,
                            button=event.sender,
                            keep=True
                        ),
                        color="primary",
                        auto_close=False,
                        split=True
                ) as key_submit:
                    key_submit.classes('w-1/6')
                    key_submit_with_clear = nicegui.ui.button(
                        "提交并清空",
                        on_click=lambda event: submit(
                            mode="key",
                            check_list=key_check_list,
                            button=event.sender,
                            keep=False
                        ),
                        color="red"
                    )
                    key_submit_with_clear.classes("w-full")

                key_clear = nicegui.ui.button(
                    "重置全部内容",
                    on_click=lambda event: clear(mode="key", button=event.sender),
                    color="red"
                )
                key_clear.classes('w-1/5')

        # 音乐部分
        with nicegui.ui.column().bind_visibility_from(data_type, 'value', value="音乐").classes('w-2/5'):
            # with nicegui.ui.card().classes('w-full'):
            #     with nicegui.ui.row(align_items="center").classes('w-full justify-between'):
            #         nicegui.ui.label("⦿ 自动提取数据")
            #
            #         nicegui.ui.button(
            #             "提取",
            #             on_click=lambda event: auto_music_date(music_data, button=event.sender),
            #             color="primary"
            #         )
            #
            #     with nicegui.ui.row().classes('w-full'):
            #         music_auto_vgmdb = nicegui.ui.input(
            #             label="VGMdb 链接 | 用于自动提取",
            #             placeholder="请输入..."
            #         )
            #         music_auto_vgmdb.validation = functools.partial(verify_id, web="vgmdb")
            #         music_auto_vgmdb.classes('w-2/5')
            #         music_auto_vgmdb.bind_value_to(
            #             music_data,
            #             "vgmdb_id",
            #             forward=functools.partial(forward_id, web="vgmdb")
            #         )
            #         music_auto_vgmdb.props('clearable')
            #
            #         music_auto_bangumi = nicegui.ui.input(
            #             label="Bangumi 链接 | 用于自动提取",
            #             placeholder="请输入..."
            #         )
            #         music_auto_bangumi.validation = functools.partial(verify_id, web="bangumi")
            #         music_auto_bangumi.classes('w-1/2')
            #         music_auto_bangumi.bind_value_to(
            #             music_data,
            #             "bangumi_id",
            #             forward=functools.partial(forward_id, web="bangumi")
            #         )
            #         music_auto_bangumi.props('clearable')

            with nicegui.ui.card().classes('w-full'):
                nicegui.ui.label("⦿ 专辑元数据")

                other_class_type = list(key_data.ClassType)
                other_class_type.pop(0)
                music_class = nicegui.ui.select(
                    [""] + other_class_type,
                    label="专辑所属作品 | 没有则置空",
                    with_input=True,
                    new_value_mode="add-unique",
                    clearable=True
                )
                music_class.classes('w-full')
                music_class.bind_value(
                    music_data,
                    "the_class",
                    forward=lambda value: value if isinstance(value, str) else ""
                )
                music_check_list.append(music_class)

                with nicegui.ui.row(align_items="center").classes('w-full'):
                    music_type_class = nicegui.ui.select(
                        list(music_data.ClassMusicType),
                        label="Key社音乐类型",
                        with_input=True,
                        validation={
                            'Key社音乐类型不能为空': lambda value: bool(value)
                        }
                    )
                    music_type_class.classes('w-2/5')
                    music_type_class.bind_value(
                        music_data,
                        "the_class_music",
                        forward=lambda value: value if isinstance(value, str) else ""
                    )
                    music_check_list.append(music_type_class)

                    music_type_text = {
                        "": "请选择音乐类型来获取对应的解释",
                        "KSLA": "KSL中带有KSLA/KSLM专辑编号的条目",
                        "KSLC": "KSL中带有KSLC专辑编号的条目",
                        "KSLV": "KSL中带有KSLV专辑编号的条目，一般会带有BD/DVD",
                        "KSL": "Key Sounds Label 中带有其它专辑编号的条目",
                        "Key-Product": "属于Key社作品，但不属于KSL的条目",
                        "Key-Other": "其它与Key社有关的音乐条目"
                    }
                    nicegui.ui.label().bind_text_from(
                        music_type_class,
                        "value",
                        backward=lambda value: music_type_text[value] if bool(value) else music_type_text[""]
                    )

                music_tag = nicegui.ui.select(
                    music_data.tags.split(";") if bool(music_data.tags) else ['OST', 'Drama'],
                    label="音乐标签",
                    new_value_mode="add-unique",
                    multiple=True,
                    clearable=True
                )
                music_tag.classes('w-full')
                music_tag.props('use-chips')
                music_tag.bind_value(
                    music_data,
                    "tags",
                    forward=lambda value: forward_tags(value, sep=";"),
                    backward=lambda value: value.split(";")
                )
                music_tag.tooltip("请勿输入包含 ; 的内容, 以及请勿重复添加 专辑编号 做为标签")
                music_check_list.append(music_tag)

            with nicegui.ui.card().classes('w-full'):
                nicegui.ui.label("⦿ 专辑信息")

                music_name = nicegui.ui.input(
                    label="专辑名",
                    placeholder="请输入...",
                    validation={'专辑名不能为空': lambda value: bool(value)}
                )
                music_name.classes('w-full')
                music_name.bind_value(
                    music_data,
                    "name",
                    forward=lambda value: value if isinstance(value, str) else "",
                )
                music_name.props('clearable')
                music_check_list.append(music_name)

                with nicegui.ui.row(align_items="center").classes('w-full'):
                    music_artist = nicegui.ui.select(
                        music_data.artist.split(";") if bool(music_data.artist) else [],
                        label="艺术家",
                        new_value_mode="add-unique",
                        multiple=True,
                        clearable=True,
                        validation={'艺术家不能为空': lambda value: bool(''.join(value))}
                    )
                    music_artist.classes('w-4/5')
                    music_artist.props('use-chips')
                    music_artist.bind_value(
                        music_data,
                        "artist",
                        forward=lambda value: forward_tags(value, sep=";"),
                        backward=lambda value: value.split(";")
                    )
                    music_artist.tooltip("请勿输入包含 ; 的内容")
                    music_check_list.append(music_artist)

                    with nicegui.ui.input(
                        label="艺术家 (自动分割)",
                        placeholder="请输入...",
                        validation={'艺术家不能为空': lambda value: bool(value) or bool(''.join(music_artist.value))}
                    ) as music_artist_split:
                        music_artist_split.classes('w-4/5')
                        music_artist_split.set_value(music_data.artist)
                        music_artist_split.bind_value_to(
                            music_data,
                            "artist",
                            forward=split_artist,
                        )
                        music_artist_split.props('clearable')
                        music_check_list.append(music_artist_split)
                        nicegui.ui.tooltip().bind_text_from(
                            music_data,
                            "artist",
                            backward=lambda value: str(value.split(";")),
                        )

                    music_artist_split_check = nicegui.ui.checkbox(text="自动分割", value=False)
                    music_artist_split_check.tooltip("自动将输入分割为多个艺术家输入")
                    music_artist.bind_visibility_from(music_artist_split_check, "value", value=False)
                    music_artist_split.bind_visibility_from(music_artist_split_check, "value", value=True)

                with nicegui.ui.row(align_items="center").classes('w-full'):
                    music_catalog_number = nicegui.ui.select(
                        music_data.catalog_number.split("&") if music_data.catalog_number != "N/A" else [],
                        label="专辑编号 | 没有则置空",
                        new_value_mode="add-unique",
                        multiple=True,
                        clearable=True
                    )
                    music_catalog_number.classes('w-4/5')
                    music_catalog_number.props('use-chips')
                    music_catalog_number.bind_value(
                        music_data,
                        "catalog_number",
                        forward=lambda value: forward_tags(value, sep="&"),
                        backward=lambda value: value.split("&")
                    )
                    music_catalog_number.tooltip("请勿输入包含 & 的内容，以及尽可能拆分为多个专辑编号输入")
                    music_check_list.append(music_catalog_number)

                    with nicegui.ui.input(
                        label="专辑编号 (自动分割) | 没有则置空",
                        placeholder="请输入..."
                    ) as music_catalog_number_split:
                        music_catalog_number_split.classes('w-4/5')
                        music_catalog_number_split.set_value(music_data.catalog_number)
                        music_catalog_number_split.bind_value_to(
                            music_data,
                            "catalog_number",
                            forward=split_catalog_number,
                        )
                        music_catalog_number_split.props('clearable')
                        music_check_list.append(music_catalog_number_split)
                        nicegui.ui.tooltip().bind_text_from(
                            music_data,
                            "catalog_number",
                            backward=lambda value: str(value.split("&")),
                        )

                    music_catalog_number_split_check = nicegui.ui.checkbox(text="自动分割", value=False)
                    music_catalog_number_split_check.tooltip("自动将输入分割为多个专辑编号输入")
                    music_catalog_number.bind_visibility_from(
                        music_catalog_number_split_check,
                        "value",
                        value=False
                    )
                    music_catalog_number_split.bind_visibility_from(
                        music_catalog_number_split_check,
                        "value",
                        value=True
                    )

                with nicegui.ui.row(align_items="center").classes('w-full'):
                    music_time = nicegui.ui.input(
                        label="专辑发行日期",
                        placeholder="请输入...",
                        validation=verify_date
                    )
                    music_time.classes('w-2/5')
                    music_time.value = music_data.time_source
                    music_time.bind_value_to(
                        music_data,
                        "time",
                        forward=forward_date
                    )
                    with nicegui.ui.menu().props('no-parent-event') as menu:
                        with nicegui.ui.date(mask="YYYY/MM/DD") as date:
                            date.set_value(music_data.time_source)
                            music_time.bind_value(
                                date,
                                "value",
                                forward=forward_date
                            )
                            with nicegui.ui.row().classes('justify-end'):
                                nicegui.ui.button('关闭', on_click=menu.close).props('flat')
                    with music_time.add_slot('append'):
                        nicegui.ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                    music_check_list.append(music_time)

                    with nicegui.ui.column(align_items="center").classes("w-1/2 items-center"):
                        nicegui.ui.label().bind_text_from(
                            music_data,
                            "time",
                            backward=lambda value: value if bool(value) else "请输入专辑发行日期"
                        ).tooltip("进行规范化之后的专辑发行日期")

                music_status = nicegui.ui.select(
                    list(music_data.StatusType),
                    label="专辑状态",
                    validation={'专辑状态不能为空': lambda value: bool(value)}
                )
                music_status.classes('w-full')
                music_status.bind_value(
                    music_data,
                    "status",
                    forward=lambda value: value if isinstance(value, str) else ""
                )
                music_check_list.append(music_status)

            with nicegui.ui.card().classes('w-full'):
                nicegui.ui.label("⦿ 专辑收藏状态")

                with nicegui.ui.row().classes('w-full'):
                    collect_type = list(music_data.CollectType)
                    collect_type.pop(-1)
                    music_collect = nicegui.ui.select(
                        collect_type,
                        label="资源收藏状态",
                        validation={'资源收藏状态不能为空': lambda value: bool(value)}
                    )
                    music_collect.classes('w-2/5')
                    music_collect.bind_value(
                        music_data,
                        "collect",
                        forward=lambda value: value if isinstance(value, str) else ""
                    )
                    music_check_list.append(music_collect)

                    music_file_type = nicegui.ui.select(
                        list(music_data.FileType),
                        label="音乐格式",
                        validation={'音乐格式不能为空': lambda value: bool(value)}
                    )
                    music_file_type.classes('w-1/2')
                    music_file_type.bind_value(
                        music_data,
                        "file_type",
                        forward=lambda value: value if isinstance(value, str) else ""
                    )
                    music_check_list.append(music_file_type)

                with nicegui.ui.row().classes('w-full'):
                    music_collect_booklet = nicegui.ui.select(
                        list(music_data.CollectType),
                        label="Booklet收藏状态",
                        validation={'Booklet收藏状态不能为空': lambda value: bool(value)}
                    )
                    music_collect_booklet.classes('w-2/5')
                    music_collect_booklet.bind_value(
                        music_data,
                        "collect_booklet",
                        forward=lambda value: value if isinstance(value, str) else ""
                    )
                    music_check_list.append(music_collect_booklet)

                    music_collect_dvd = nicegui.ui.select(
                        list(music_data.CollectType),
                        label="BD/DVD收藏状态",
                        validation={'BD/DVD收藏状态不能为空': lambda value: bool(value)}
                    )
                    music_collect_dvd.classes('w-1/2')
                    music_collect_dvd.bind_value(
                        music_data,
                        "collect_dvd",
                        forward=lambda value: value if isinstance(value, str) else ""
                    )
                    music_check_list.append(music_collect_dvd)

                def music_status_sync(value: str):
                    """同步专辑状态的改变"""
                    if value == "未发售👀":
                        music_collect.value = "等待中👀"
                    return

                music_status.on_value_change(callback=lambda event: music_status_sync(event.value))

                def music_collect_sync(value: str):
                    """同步专辑收藏状态的改变"""
                    if value in ("无资源❌", "未收藏🔘", "等待中👀"):
                        music_file_type.value = "未知"
                        music_collect_booklet.value = "不适用⛔"
                        music_collect_dvd.value = "不适用⛔"
                    return

                music_collect.on_value_change(callback=lambda event: music_collect_sync(event.value))

            with nicegui.ui.card().classes('w-full'):
                nicegui.ui.label("⦿ 专辑外部链接")

                with nicegui.ui.row().classes('w-full'):
                    with nicegui.ui.input(label="Bangumi 链接", placeholder="请输入...") as music_bangumi:
                        music_bangumi.validation = functools.partial(verify_id, web="bangumi")
                        music_bangumi.classes('w-2/5')
                        music_bangumi.set_value(music_data.bangumi_id)
                        music_bangumi.bind_value_to(
                            music_data,
                            "bangumi_id",
                            forward=functools.partial(forward_id, web="bangumi")
                        )
                        music_bangumi.props('clearable')
                        tooltip = nicegui.ui.tooltip()
                        tooltip.bind_text_from(music_data,"bangumi_id")
                        tooltip.bind_visibility_from(
                            music_data,
                            "bangumi_id",
                            backward=lambda value: bool(value)
                        )
                        music_check_list.append(music_bangumi)

                    with nicegui.ui.input(label="Steam 链接", placeholder="请输入...") as music_steam:
                        music_steam.validation = functools.partial(verify_id, web="steam")
                        music_steam.classes('w-1/2')
                        music_steam.set_value(music_data.steam_id)
                        music_steam.bind_value_to(
                            music_data,
                            "steam_id",
                            forward=functools.partial(forward_id, web="steam")
                        )
                        music_steam.props('clearable')
                        tooltip = nicegui.ui.tooltip()
                        tooltip.bind_text_from(music_data,"steam_id")
                        tooltip.bind_visibility_from(
                            music_data,
                            "steam_id",
                            backward=lambda value: bool(value)
                        )
                        music_check_list.append(music_steam)

                with nicegui.ui.row().classes('w-full'):
                    with nicegui.ui.input(label="VNDB 链接", placeholder="请输入...") as music_vndb:
                        music_vndb.validation = functools.partial(verify_id, web="vndb")
                        music_vndb.classes('w-2/5')
                        music_vndb.set_value(music_data.vndb_id)
                        music_vndb.bind_value_to(
                            music_data,
                            "vndb_id",
                            forward=functools.partial(forward_id, web="vndb")
                        )
                        music_vndb.props('clearable')
                        tooltip = nicegui.ui.tooltip()
                        tooltip.bind_text_from(music_data,"vndb_id")
                        tooltip.bind_visibility_from(
                            music_data,
                            "vndb_id",
                            backward=lambda value: bool(value)
                        )
                        music_check_list.append(music_vndb)
                        music_vndb.disable()

                    with nicegui.ui.input(label="VGMdb 链接", placeholder="请输入...") as music_vgmdb:
                        music_vgmdb.validation = functools.partial(verify_id, web="vgmdb")
                        music_vgmdb.classes('w-1/2')
                        music_vgmdb.set_value(music_data.vgmdb_id)
                        music_vgmdb.bind_value_to(
                            music_data,
                            "vgmdb_id",
                            forward=functools.partial(forward_id, web="vgmdb")
                        )
                        music_vgmdb.props('clearable')
                        tooltip = nicegui.ui.tooltip()
                        tooltip.bind_text_from(music_data,"vgmdb_id")
                        tooltip.bind_visibility_from(
                            music_data,
                            "vgmdb_id",
                            backward=lambda value: bool(value)
                        )
                        music_check_list.append(music_vgmdb)

            with nicegui.ui.card().classes('w-full'):
                nicegui.ui.label("⦿ 专辑简介和备注")

                music_introduction = nicegui.ui.textarea(
                    label="专辑简介",
                    placeholder="请输入..."
                )
                music_introduction.classes('w-full')
                music_introduction.bind_value(
                    music_data,
                    "introduction",
                    forward=lambda value: value if isinstance(value, str) else ""
                )
                music_introduction.props('clearable')
                music_check_list.append(music_introduction)

                nicegui.ui.separator().classes('w-full')

                music_ps1 = nicegui.ui.textarea(
                    label="专辑备注1",
                    placeholder="请输入..."
                )
                music_ps1.classes('w-full')
                music_ps1.bind_value(
                    music_data,
                    "ps1",
                    forward=lambda value: value if isinstance(value, str) else ""
                )
                music_ps1.props('clearable')
                music_check_list.append(music_ps1)

                music_ps2 = nicegui.ui.textarea(
                    label="专辑备注2",
                    placeholder="请输入...",
                    validation={'请填写在 备注1 中': lambda value: bool(music_ps1.value) or (not bool(value))}
                )
                music_ps2.classes('w-full')
                music_ps2.bind_value(
                    music_data,
                    "ps2",
                    forward=lambda value: value if isinstance(value, str) else ""
                )
                music_ps2.props('clearable')
                music_check_list.append(music_ps2)

                music_ps3 = nicegui.ui.textarea(
                    label="专辑备注3",
                    placeholder="请输入...",
                    validation={
                        '请填写在 备注1 中': lambda value: bool(music_ps1.value) or (not bool(value)),
                        '请填写在 备注2 中': lambda value: bool(music_ps2.value) or (not bool(value))
                    }
                )
                music_ps3.classes('w-full')
                music_ps3.bind_value(
                    music_data,
                    "ps3",
                    forward=lambda value: value if isinstance(value, str) else ""
                )
                music_ps3.props('clearable')
                music_check_list.append(music_ps3)

            nicegui.ui.separator().classes('w-full')

            with nicegui.ui.row().classes('w-full justify-end'):
                with nicegui.ui.dropdown_button(
                        "提交",
                        value=False,
                        on_click=lambda event: submit(
                            mode="music",
                            check_list=music_check_list,
                            button=event.sender,
                            keep=True
                        ),
                        color="primary",
                        auto_close=False,
                        split=True
                ) as music_submit:
                    music_submit.classes('w-1/6')
                    music_submit_with_clear = nicegui.ui.button(
                        "提交并清空",
                        on_click=lambda event: submit(
                            mode="music",
                            check_list=music_check_list,
                            button=event.sender,
                            keep=False
                        ),
                        color="red"
                    )
                    music_submit_with_clear.classes("w-full")

                music_clear = nicegui.ui.button(
                    "重置全部内容",
                    on_click=lambda event: clear(mode="music", button=event.sender),
                    color="red"
                )
                music_clear.classes('w-1/5')

    with nicegui.ui.column().classes('w-full items-center') as page_database:
        page_database.visible = False

        # 数据库类型切换
        with nicegui.ui.card(align_items='center').classes('w-3/5'):
            with nicegui.ui.row(align_items="center"):
                nicegui.ui.label("请选择数据库类型: ")
                db_type = nicegui.ui.toggle(["主要作品", "通用作品", "音乐作品"], value="主要作品")

        nicegui.ui.separator().classes('w-3/5')

        # 控制区
        with nicegui.ui.card().classes('w-3/5'):
            with nicegui.ui.column().classes('w-full'):
                with nicegui.ui.row(align_items="center").classes('w-full justify-between'):
                    table_select = nicegui.ui.label()
                    table_select.classes("w-3/5")

                    with nicegui.ui.row():
                        table_data_edit = nicegui.ui.button("修改此条目")
                        table_data_edit.tooltip("未提交将丢失该条目数据")
                        table_data_add = nicegui.ui.button("关联新作品")

                nicegui.ui.separator().classes('w-full')

                with nicegui.ui.row(align_items="center").classes('w-full justify-between'):
                    table_filter = nicegui.ui.input(
                        label="搜索数据表",
                        placeholder="请输入..."
                    )
                    table_filter.classes('w-3/5')
                    table_filter.props('clearable')

                    table_data_update = nicegui.ui.button("刷新", icon='refresh')

        # 数据表
        with nicegui.ui.column().classes('w-3/5'):
            table_data = get_table_data(mode=db_type.value)
            table_columns = get_table_columns(mode=db_type.value)
            table_rows = get_table_rows(mode=db_type.value, table_data=table_data)
            db_table = nicegui.ui.table(
                columns=table_columns,
                rows=table_rows,
                row_key="id",
                selection="single",
                pagination=20
            )
            db_table.classes('w-full')

        def table_update():
            """
            更新数据表，
            并清空选择项和分页
            """
            nonlocal table_data
            table_data = get_table_data(mode=db_type.value)
            db_table.columns = get_table_columns(mode=db_type.value)
            db_table.rows = get_table_rows(mode=db_type.value, table_data=table_data)
            db_table.pagination['page'] = 1
            db_table.selected = []
            return

        def table_edit(add=False):
            """
            修改数据表中的条目，
            如果非添加新作品，
            则从数据库中移除该条目

            :param add:
                视为添加新的作品
            """
            table_data_edit.disable()
            table_data_add.disable()

            if not bool(db_table.selected):
                nicegui.ui.notify("未选择任何条目", type="warning")
                table_data_edit.enable()
                table_data_add.enable()
            else:
                data = table_data[db_table.selected[0]['id']]
                if add:
                    del data.the_class
                else:
                    cur = CON.cursor()
                    if db_type.value in ("主要作品", "通用作品"):
                        if db_type.value == "主要作品":
                            table_name = "main"
                        else:
                            table_name = "key"
                        cur.execute(
                            f"DELETE FROM {table_name} WHERE name=? AND the_class=? AND the_class_other=?",
                            (data.name, data.the_class, data.the_class_other)
                        )
                    else:
                        cur.execute(
                            f"DELETE FROM music WHERE name=? AND the_class=? AND the_class_music=?",
                            (data.name, data.the_class, data.the_class_music)
                        )
                    CON.commit()
                    cur.close()

                if isinstance(data, KeyData):
                    web_ui.refresh(key_data=data, music_data=music_data, data_type_value="通用")
                else:
                    web_ui.refresh(key_data=key_data, music_data=data, data_type_value="音乐")

            return

        db_type.on_value_change(table_update)

        table_select.bind_text_from(
            db_table,
            "selected",
            backward=lambda value: f"已选择: {value[0]["name"]} "if bool(value) else "未选择任何条目"
        )
        table_data_edit.on_click(functools.partial(table_edit, add=False))
        table_data_add.on_click(functools.partial(table_edit, add=True))
        table_filter.bind_value(db_table, "filter")
        table_data_update.on_click(table_update)

    def page_toggle():
        """
        切换页面显示
        """
        page_main.visible = not page_main.visible
        page_database.visible = not page_database.visible
        table_update()
        return

    nicegui.ui.colors(accent='#9CC6E0')
    with nicegui.ui.page_sticky(x_offset=18, y_offset=18):
        page_main_button = nicegui.ui.button(icon='table_chart', on_click=page_toggle)
        page_main_button.props('fab color=accent')

    return


if __name__ in {"__main__", "__mp_main__"}:
    try:
        web_ui()
    except Exception as e:
        nicegui.ui.notify(f"未处理的异常: {str(e)}", type="negative")
        CON.commit()
        CON.close()
        raise e from e
    nicegui.ui.run(
        host="localhost",
        port=8090,
        title="Key社条目资料",
        favicon="../docs/assets/img/favicon.svg",
        dark=None,
        language="zh-CN",
        fastapi_docs=False,
        show=False,
        reload=False,
        uvicorn_logging_level="info",
        use_colors=True
    )
    CON.commit()
    CON.close()
