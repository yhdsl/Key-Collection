## Key社全收集计划/档案楼/资源站/合集

### 资源网站

*一个旨在记录和免费分享Key社作品资源和周边的地方。*

更为具体的内容，请前往[*资源站*](https://yhdsl.github.io/Key-Collection)查看资源详情或其他资料。

或者也可以快速前往：

- [作品条目目录](https://yhdsl.github.io/Key-Collection/key/index)
- [音乐条目目录](https://yhdsl.github.io/Key-Collection/music/index)
- [资源下载页面](https://yhdsl.github.io/Key-Collection/download)

> 注意，该全收集计划仍在施工中 (WIP)  
> 这表明收录的内容随时可能会进行增补修改  
> 如果你希望参与其中，请通过本仓库中的 [*Discussions*](https://github.com/yhdsl/Key-Collection/discussions) 联系我们

> 目前项目需要若干位热心的键っ子  
> 为项目提供稳定的资源分享平台  
> 如果你有余力帮助我们  
> 请查看下文已知问题部分

### 参与开发

该全收集计划分为*条目资料记录*和*条目资源收藏*两部分。

其中本仓库主要包含资料记录部分，而资源收藏则分流至若干个网盘中。

如果希望参与至资料记录的工作中，切记**不要直接修改 `docs` 内的文件**，
这些内容是从数据库中自动生成的，请改用如下的方法。

使用 git 克隆本仓库至本地
```shell
git clone https://github.com/yhdsl/Key-Collection.git
cd Key-Collection
```

设置运行环境 (建议单独创建一个虚拟环境)
```shell
pip install -r .\requirements.txt
```

接下来运行 web ui
```shell
cd db
python ui.py
```

并前往 http://localhost:8090 修改或增加条目

最后执行以下命令更新文档
```shell
python make.py
```

### 已知的问题

#### 有很多条目不完整

目前项目正处于起步阶段，请耐心等待。

#### 没有看到下载链接

目前项目需要若干稳定的平台进行资源分享，例如 Onedrive 等。

如果你能够有余力帮助我们，请通过 [*Discussions*](https://github.com/yhdsl/Key-Collection/discussions) 联系我们

#### 常见的游戏/动漫没有收藏

考虑到缩减整体资源的体积，我们目前针对以下内容不做收藏：

- 常见的游戏资源，尤其是已在 Steam 平台上发布的作品
- 非PC平台上的游戏资源，例如 PSP 或 Android 等
- 其他没有太大收藏意义的资源，例如海外版本

如果你迫切的想要收藏以上这些内容，请前往
[https://north-plus.net/read.php?tid-1881394.html](https://north-plus.net/read.php?tid-1881394.html) 获取。

- 动漫资源/原盘

该部分我们还在整理中，但目前优先级较后，请耐心等待。
