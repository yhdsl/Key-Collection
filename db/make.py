"""
使用数据库构建文档
"""

import datetime
import pathlib
import re
import sqlite3
import typing

import natsort

import ui


RECENTLY_UPDATED_LIMIT_MAIN = 3  #: 最近更新的主条目限制
RECENTLY_UPDATED_LIMIT_OTHER = 10  #: 最近更新的其他条目限制，其中音乐部分分开统计


CON = sqlite3.connect("../database.db")


MetadataEnd = "[//]: # (Metadata End)\n"
TXTEnd = "[//]: # (TXT End)\n"


KeyFileDict: dict[str, pathlib.Path] = {
    name.stem: name
    for name in natsort.os_sorted(pathlib.Path("../docs/key").glob("*.md"))
    if name.stem != "index"
}

MusicFileDict: dict[str, pathlib.Path] = {
    name.stem: name
    for name in natsort.os_sorted(pathlib.Path("../docs/music").glob("*.md"))
    if name.stem != "index"
}


def split_file(path: pathlib.Path) -> tuple[list[str], list[str], list[str]]:
    """
    拆分条目 Markdown 文件为三部分，
    元数据部分、非自动化生成部分和自动化部分

    :param path:
        Markdown 文件的 Path 实例

    :return:
        拆分后的文件内容

    :raise ValueError:
        当 Markdown 文件无法被拆分时抛出
    """
    with path.open(mode="r", encoding="utf-8") as fp:
        file_read = fp.readlines()

    try:
        metadata_end_index = file_read.index(MetadataEnd)
        txt_end_index = file_read.index(TXTEnd)
    except ValueError as e:
        raise ValueError(str(path)) from e

    return (
        file_read[:metadata_end_index],
        file_read[metadata_end_index + 2: txt_end_index],
        file_read[txt_end_index + 2:]
    )


def write_file(path: pathlib.Path, metadata_list: list[str], markdown_list: list[str]):
    """
    写入文件，
    包含自定义的元数据部分和自动化生成部分，
    以及原有的保留文本

    :param path:
        代写入的 Markdown 文件的 Path 实例

    :param metadata_list:
        元数据部分

    :param markdown_list:
        自动化生成部分
    """
    txt_list = split_file(path)[1]

    with path.open(mode="w", encoding="utf-8") as fp:
        fp.writelines(metadata_list + [MetadataEnd, '\n'] + txt_list + [TXTEnd, '\n'] + markdown_list)

    return


def clear(path: pathlib.Path):
    """
    清空条目 Markdown 文件，
    会保留非自动化生成部分

    :param path:
        Markdown 文件的 Path 实例
    """
    file_split = split_file(path)

    file_write = [MetadataEnd, '\n'] + file_split[1] + [TXTEnd, '\n']
    with path.open(mode="w", encoding="utf-8") as fp:
        fp.writelines(file_write)
    return


def clear_all():
    """
    清空全部等待自动化生成的 Markdown 文档
    """
    for path in KeyFileDict.values():
        clear(path)
    for path in MusicFileDict.values():
        clear(path)

    open("../docs/changelog.md", mode="w", encoding="utf-8").close()

    with open("../docs/help.md", mode="r", encoding="utf-8") as fp1:
        file_read = fp1.readlines()
    try:
        txt_end_index = file_read.index(TXTEnd)
    except ValueError as e:
        raise ValueError("../docs/help.md") from e
    with open("../docs/help.md", mode="w", encoding="utf-8") as fp2:
        fp2.writelines(file_read[:txt_end_index] + [TXTEnd, '\n'])

    return


def get_key_data(sql_data: list[str]) -> dict[str, str | list[str]]:
    """
    将数据库中 Key社条目 处理后映射至一个字典中

    :param sql_data:
        数据库原始数据

    :return:
        处理后映射的字典
    """
    data_dict = {
        "_data_type": "key"
    }

    for attribute, value in zip(ui.KeyData.AllAttribute, sql_data):
        if attribute == "tags":
            value = value.split(";")

        data_dict[attribute] = value
    return data_dict


def get_music_data(sql_data: list[str]) -> dict[str, str | list[str]]:
    """
    将数据库中 Key社音乐条目 处理后映射至一个字典中

    :param sql_data:
        数据库原始数据

    :return:
        处理后映射的字典
    """
    data_dict = {
        "_data_type": "music"
    }

    for attribute, value in zip(ui.MusicData.AllAttribute, sql_data):
        if attribute == "artist":
            value = value.split(";")
        elif attribute == "catalog_number":
            value = value.split("&")

            if len(value) == 1:
                catalog_number_title_value = value[0]
            else:
                catalog_number_f = value[0].rsplit("-", maxsplit=1)[1]
                catalog_number_e = value[-1].rsplit("-", maxsplit=1)[1]
                diff = int(catalog_number_e) - int(catalog_number_f)
                if diff == 0:
                    catalog_number_title_value = value[0]
                else:
                    catalog_number_title_value = f"{value[0]}~{value[-1][-len(str(diff)):]}"
            data_dict["catalog_number_title"] = catalog_number_title_value

        elif attribute == "tags":
            value = value.split(";")

        data_dict[attribute] = value
    return data_dict


def _get_link_markdown(
        mode: typing.Literal["bangumi", "steam", "vndb", "vgmdb"],
        link_id: str
) -> list[str]:
    """
    获取外部链接对应的 Markdown 文本列表，
    根据 ID 的有无选择合适的 HTML 表示

    :param mode:
        外部链接类型

    :param link_id:
        链接 ID

    :return:
        对应的 Markdown 文本列表
    """
    if mode == "bangumi":
        link_text = "Bangumi 番组计划"
        link_url = "https://bgm.tv/subject/"
    elif mode == "steam":
        link_text = "Steam"
        link_url = "https://store.steampowered.com/app/"
    elif mode == "vndb":
        link_text = "VNDB"
        link_url = "https://vndb.org/v"
    elif mode == "vgmdb":
        link_text = "VGMdb"
        link_url = "https://vgmdb.net/album/"
    else:
        raise TypeError(mode)

    if bool(link_id):
        link_list = [
            f'        <a href="{link_url}{link_id}" class="card" target=”_blank”>\n',
            f'            前往 <i class="{mode}">{link_text}</i> 对应的页面\n',
            f'        </a>\n',
        ]
    else:
        link_list = [
            f'        <div class="card disable">\n',
            f'            前往 {link_text} 对应的页面\n',
            f'        </div>\n',
        ]
    return link_list


def get_key_markdown(
        data_dict: dict[str, str | list[str]],
        level=2,
        recently_updated=False
) -> list[str]:
    """
    将映射的条目字典处理为合适的 Markdown 表达

    :param data_dict:
        映射后的字典

    :param level:
        标题等级

    :param recently_updated:
        是否为最近更新的条目

    :return:
        处理后的 Markdown 文本列表
    """
    if recently_updated:
        title_ex = ' :material-alert-decagram:{ .mdx-pulse title="最近更新" }'
    else:
        title_ex = ''

    markdown_list = [
        fr'{'#' * int(level)} \[{data_dict["the_type"]}] {data_dict["name"]} ({data_dict["icon"]})' + \
        f'{title_ex}\n',
        f'\n',
    ]

    tag_list = []
    if ''.join(data_dict["tags"]):
        for tag in data_dict["tags"]:
            tag_list.append(f'<small>:material-tag-text: {tag}</small>\n')
        tag_list.append(f'\n')
    markdown_list += tag_list

    markdown_list += [
        f'```\n',
        f'条目名称: {data_dict["name"]}\n',
        f'中文名称: {data_dict["name_zh"]}\n',
        f'发售时间: {data_dict["time"]}\n',
        f'类别: {data_dict["the_type"]}\n',
        f'状态: {data_dict["status"]}\n',
        f'\n',
        f'原版资源: {data_dict["collect"]}\n',
        f'汉化资源: {data_dict["collect_zh"]}\n',
        f'\n',
        f'简介: {data_dict["introduction"]}\n',
        f'\n',
        f'备注1: {data_dict["ps1"]}\n',
        f'备注2: {data_dict["ps2"]}\n',
        f'备注3: {data_dict["ps3"]}\n',
        f'```\n',
        f'\n',
    ]

    link_list = [
        f'<div class="result">\n',
        f'    <div class="grid">\n',
    ]
    link_list += _get_link_markdown(mode="bangumi", link_id=data_dict["bangumi_id"])
    link_list += _get_link_markdown(mode="steam", link_id=data_dict["steam_id"])
    link_list += _get_link_markdown(mode="vndb", link_id=data_dict["vndb_id"])
    link_list += _get_link_markdown(mode="vgmdb", link_id=data_dict["vgmdb_id"])
    link_list += [
        f'    </div>\n',
        f'</div>\n',
        f'\n',
    ]
    markdown_list += link_list
    return markdown_list


def get_music_markdown(
        data_dict: dict[str, str | list[str]],
        level=2,
        recently_updated=False,
        product_list: list[str] | None = None
) -> list[str]:
    """
    将映射的音乐字典处理为合适的 Markdown 表达

    :param data_dict:
        映射后的字典

    :param level:
        标题等级

    :param recently_updated:
        是否为最近更新的条目

    :param product_list:
        可选的包含链接作品的条目列表，
        注意去除排序前缀

    :return:
        处理后的 Markdown 文本列表
    """
    if recently_updated:
        title_ex = ' :material-alert-decagram:{ .mdx-pulse title="最近更新" }'
    else:
        title_ex = ''

    markdown_list = [
        fr'{'#' * int(level)} \[{data_dict["catalog_number_title"]}] {data_dict["name"]} ({data_dict["icon"]})' + \
        f'{title_ex}\n',
        f'\n',
    ]

    tag_list = []

    if product_list:
        for name in product_list:
            if bool(name):
                tag_list.append(
                    f'<small>:octicons-link-16: {name}</small>\n',
                )
        tag_list.append(f'\n')

    for catalog_number in data_dict["catalog_number"]:
        tag_list.append(f'<small>:material-music-box-multiple: {catalog_number}</small>\n')
    tag_list.append(f'\n')

    if ''.join(data_dict["tags"]):
        for tag in data_dict["tags"]:
            tag_list.append(f'<small>:material-tag-text: {tag}</small>\n')
        tag_list.append(f'\n')

    markdown_list += tag_list

    markdown_list += [
        f'```\n',
        f'专辑名: {data_dict["name"]}\n',
        f'艺术家: {'; '.join(data_dict["artist"])}\n',
        f'专辑编号: {data_dict["catalog_number_title"]}\n',
        f'发售时间: {data_dict["time"]}\n',
        f'状态: {data_dict["status"]}\n',
        f'\n',
        f'资源: {data_dict["collect"]}\n',
        f'音乐格式: {data_dict["file_type"]}\n',
        f'Booklet: {data_dict["collect_booklet"]}\n',
        f'BD/DVD: {data_dict["collect_dvd"]}\n',
        f'\n',
        f'简介: {data_dict["introduction"]}\n',
        f'\n',
        f'备注1: {data_dict["ps1"]}\n',
        f'备注2: {data_dict["ps2"]}\n',
        f'备注3: {data_dict["ps3"]}\n',
        f'```\n',
        f'\n',
    ]

    link_list = [
        f'<div class="result">\n',
        f'    <div class="grid">\n',
    ]
    link_list += _get_link_markdown(mode="bangumi", link_id=data_dict["bangumi_id"])
    link_list += _get_link_markdown(mode="steam", link_id=data_dict["steam_id"])
    link_list += _get_link_markdown(mode="vndb", link_id="")
    link_list += _get_link_markdown(mode="vgmdb", link_id=data_dict["vgmdb_id"])
    link_list += [
        f'    </div>\n',
        f'</div>\n',
        f'\n',
    ]
    markdown_list += link_list
    return markdown_list


def get_recently_updated() -> tuple[
    tuple[str, ...], tuple[dict[str, str | list[str]], ...], tuple[dict[str, str | list[str]], ...]
]:
    """
    :return:
        包含最近更新条目的文件名，
        以及包含最近更新的条目和音乐的处理后的字典的列表，
        最近更新的数目由 RECENTLY_UPDATED_LIMIT 变量控制
    """
    cur = CON.cursor()

    recently_updated_key = []
    recently_updated_music = []
    recently_updated_file = []

    cur.execute(f"SELECT * FROM main")
    for sql_data in cur.fetchall()[-RECENTLY_UPDATED_LIMIT_MAIN:]:
        key_data = get_key_data(sql_data)
        recently_updated_key.append(key_data)
        recently_updated_file.append(key_data["the_class"])

    cur.execute(f"SELECT * FROM key")
    for sql_data in cur.fetchall()[-RECENTLY_UPDATED_LIMIT_OTHER:]:
        key_data = get_key_data(sql_data)
        recently_updated_key.append(key_data)
        recently_updated_file.append(key_data["the_class"])

    cur.execute(f"SELECT * FROM music")
    for sql_data in cur.fetchall()[-RECENTLY_UPDATED_LIMIT_OTHER:]:
        recently_updated_music.append(get_music_data(sql_data))

    try:
        recently_updated_file.remove("A00 杂货铺")
    except ValueError:
        pass

    return tuple(recently_updated_file), tuple(recently_updated_key), tuple(recently_updated_music)


def _sorted_func(data: dict[str, str | list[str]]) -> datetime.date:
    """
    排序函数，
    按照发行时间进行排序

    :param data:
        待排序的映射后的字典

    :return:
        发行时间，处理为 date 实例
    """
    time = data["time"]
    if time[-5:] == " (预计)":
        time = time[:-5]

    data_list = time.split("/", maxsplit=2)
    return datetime.date(int(data_list[0]), int(data_list[1]), int(data_list[2]))


def _get_unique_list(sql_data: list[list[str]]):
    """
    从 SQL 结果中生成用于排序的唯一列表

    :param sql_data:
        SQL 数据，
        只考虑第一个查询列

    :return:
        用于排序的唯一列表
    """
    unique_list = []
    for i in sql_data:
        data = i[0]
        if data not in unique_list:
            unique_list.append(data)
    return unique_list


def _get_product_source_name(product_name: str) -> str:
    """
    返回去掉排序前缀的作品名称

    :param product_name:
        原始的作品名称

    :return:
        处理后的作品名称
    """
    m = re.fullmatch(fr"[ABCD]\d\d(\.\d+)? (?P<source_name>.+)", product_name)
    if m:
        source_name = m.groupdict()["source_name"]
    else:
        source_name = product_name
    return source_name


def get_music_markdown_with_product(
        sql_data_list: list[list[str]],
        level: int,
        recently_updated_music: tuple[dict[str, str | list[str]], ...] | None = None
) -> list[str]:
    """
    处理音乐条目中关联至多个作品的数据

    由于在数据库中多个作品的关联是分为多个数据行进行记录的，
    因此需要将其特别处理为作品列表，
    以防止出现重复条目文本

    音乐条目的文本顺序是按照发行时间进行排序的

    :param sql_data_list:
        从数据库中获取的原始数据

    :param level:
        标题等级

    :param recently_updated_music:
        包含最近更新音乐条目的列表，
        如果为 None 则不会进行处理

    :return:
        正确处理后的包含全部条目 Markdown 文本的列表
    """
    music_data_list = [get_music_data(sql_data) for sql_data in sql_data_list]
    music_data_list.sort(key=_sorted_func)

    markdown_list = []

    latest_data = {}
    product_list = []
    latest_recently_updated = False
    for music_data in music_data_list:
        product_name = music_data["the_class"]
        product_name = _get_product_source_name(product_name)
        try:
            recently_updated = music_data in recently_updated_music
        except TypeError:
            recently_updated = False
        music_data.pop("the_class")

        if not bool(latest_data):  # 首次进入循环
            latest_data = music_data
            product_list.append(product_name)
            latest_recently_updated |= recently_updated
        else:
            if music_data == latest_data:  # 条目匹配
                product_list.append(product_name)
                latest_recently_updated |= recently_updated
            else:  # 条目不匹配
                markdown_list += get_music_markdown(
                    data_dict=latest_data,
                    level=level,
                    recently_updated=latest_recently_updated,
                    product_list=sorted(product_list)
                )

                latest_data = music_data
                product_list = [product_name]
                latest_recently_updated = recently_updated

    if bool(latest_data):
        markdown_list += get_music_markdown(
            data_dict=latest_data,
            level=level,
            recently_updated=latest_recently_updated,
            product_list=sorted(product_list)
        )

    return markdown_list


def gen_help_page(help_key_list: list[str]):
    """
    自动化生成帮助页，
    与其它页面不同的是，
    不包含元数据部分

    其中作品部分直接传入，
    以保证排序一致

    :param help_key_list:
        作品部分，
        注意标题等级为3，
        不使用最近更新功能
    """
    with open("../docs/help.md", mode="r", encoding="utf-8") as fp1:
        file_read = fp1.readlines()

    txt_end_index = file_read.index(TXTEnd)

    markdown_list = file_read[:txt_end_index]
    markdown_list += [TXTEnd, '\n']

    markdown_list += [
        f'## 需要帮助的条目\n'
        f'\n'
    ]
    markdown_list += help_key_list

    markdown_list += [
        f'## 需要帮助的音乐\n'
        f'\n'
    ]
    cur = CON.cursor()
    cur.execute(f"SELECT * FROM music WHERE icon = '❌' OR icon = '❓'")
    sql_data = cur.fetchall()
    cur.close()
    markdown_list += get_music_markdown_with_product(
        sql_data,
        level=3,
        recently_updated_music=None
    )

    with open("../docs/help.md", mode="w", encoding="utf-8") as fp2:
        fp2.writelines(markdown_list)
    return


def build():
    clear_all()

    with open("../CHANGELOG.md", mode="r", encoding="utf-8") as fp1:
        changelog_read = fp1.readlines()
    with open("../docs/changelog.md", mode="w", encoding="utf-8") as fp2:
        fp2.writelines(changelog_read)

    help_key_list = []

    recently_updated_file, recently_updated_key, recently_updated_music = get_recently_updated()

    for key_name in KeyFileDict.keys():
        cur = CON.cursor()

        if key_name == "A00 杂货铺":
            metadata_list = []
            markdown_list = []

            cur.execute(f"SELECT the_class_other FROM key WHERE the_class = 'A00 杂货铺'")
            the_class_other_list = _get_unique_list(sql_data=cur.fetchall())

            for the_class_other in the_class_other_list:
                markdown_list += [
                    f'## {the_class_other}\n',
                    f'\n',
                ]

                cur.execute(
                    f"SELECT * FROM key WHERE the_class = 'A00 杂货铺' AND the_class_other = ?",
                    (the_class_other,)
                )
                key_data_list = [get_key_data(sql_data) for sql_data in cur.fetchall()]
                key_data_list.sort(key=_sorted_func)
                for key_data in key_data_list:
                    markdown_list += get_key_markdown(
                        key_data,
                        level=3,
                        recently_updated=(key_data in recently_updated_key)
                    )

                    if key_data["icon"] in ('❌', '❓'):
                        help_key_list += get_key_markdown(
                            key_data,
                            level=3,
                            recently_updated=False
                    )

                markdown_list += [
                    f'---\n'
                    f'\n'
                ]
            markdown_list = markdown_list[: -2]

        else:
            if key_name in recently_updated_file:
                metadata_list = [
                    f'---\n'
                    f'status: new\n'
                    f'---\n'
                    f'\n'
                ]
            else:
                metadata_list = []
            markdown_list = []

            cur.execute(
                f"SELECT * FROM main WHERE the_class = ?",
                (key_name,)
            )
            try:
                sql_data = cur.fetchall()[0]
            except IndexError:
                continue
            else:
                key_main_data = get_key_data(sql_data)
                markdown_list += get_key_markdown(
                    key_main_data,
                    level=2,
                    recently_updated=(key_main_data in recently_updated_key)
                    )

                if key_main_data["icon"] in ('❌', '❓'):
                    help_key_list += get_key_markdown(
                        key_main_data,
                        level=3,
                        recently_updated=False
                    )

            cur.execute(
                f"SELECT * FROM key WHERE the_class = ?",
                (key_name,)
            )
            key_data_list = [get_key_data(sql_data) for sql_data in cur.fetchall()]
            if bool(key_data_list):
                markdown_list += [
                    f'---\n'
                    f'\n'
                    f'## 附属作品\n'
                    f'\n'
                ]
                key_data_list.sort(key=_sorted_func)
                for key_data in key_data_list:
                    markdown_list += get_key_markdown(
                        key_data,
                        level=3,
                        recently_updated=(key_data in recently_updated_key)
                    )

                    if key_data["icon"] in ('❌', '❓'):
                        help_key_list += get_key_markdown(
                            key_data,
                            level=3,
                            recently_updated=False
                        )

            cur.execute(
                f"SELECT * FROM music WHERE the_class = ?",
                (key_name,)
            )
            music_data_list = [get_music_data(sql_data) for sql_data in cur.fetchall()]
            if bool(music_data_list):
                markdown_list += [
                    f'---\n'
                    f'\n'
                    f'## 附属音乐\n'
                    f'\n'
                ]
                music_data_list.sort(key=_sorted_func)
                for music_data in music_data_list:
                    markdown_list += get_music_markdown(
                        music_data,
                        level=3,
                        recently_updated=(music_data in recently_updated_key),
                        product_list=None
                    )

        cur.close()
        write_file(
            KeyFileDict[key_name],
            metadata_list,
            markdown_list
        )

    for music_name in MusicFileDict.keys():
        cur = CON.cursor()
        metadata_list = []

        if music_name == "Key-Product":
            markdown_list = []

            cur.execute(f"SELECT the_class FROM music WHERE the_class_music = 'Key-Product'")
            the_class_list = _get_unique_list(sql_data=cur.fetchall())

            for the_class in the_class_list:
                if not bool(the_class):
                    raise ValueError("Key-Product 内包含错误作品名")
                else:
                    markdown_list += [
                        f'## {_get_product_source_name(the_class)}\n',
                        f'\n',
                    ]

                    cur.execute(
                        f"SELECT * FROM music WHERE the_class = ? AND the_class_music = ?",
                        (the_class, music_name)
                    )
                    music_sql_data = cur.fetchall()
                    markdown_list += get_music_markdown_with_product(
                        music_sql_data,
                        level=3,
                        recently_updated_music=recently_updated_music
                    )
                markdown_list += [
                    f"---\n"
                ]

        else:
            cur.execute(
                f"SELECT * FROM music WHERE the_class_music = ?",
                (music_name,)
            )
            music_sql_data = cur.fetchall()
            markdown_list = get_music_markdown_with_product(
                music_sql_data,
                level=2,
                recently_updated_music=recently_updated_music
            )

        cur.close()
        write_file(
            MusicFileDict[music_name],
            metadata_list,
            markdown_list
        )

    gen_help_page(help_key_list)

    return


if __name__ == '__main__':
    build()
