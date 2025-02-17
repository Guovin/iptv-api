<div align="center">
  <img src="./static/images/logo.png" alt="logo"/>
  <h1 align="center">IPTV-API</h1>
</div>

<div align="center">一个可高度自定义的IPTV接口更新项目📺，自定义频道菜单，自动获取直播源，测速验效后生成可用的结果，可实现『✨秒播级体验🚀』</div>
<br>
<p align="center">
  <a href="https://github.com/Guovin/iptv-api/releases/latest">
    <img src="https://img.shields.io/github/v/release/guovin/iptv-api" />
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-%20%3D%203.13-47c219" />
  </a>
  <a href="https://github.com/Guovin/iptv-api/releases/latest">
    <img src="https://img.shields.io/github/downloads/guovin/iptv-api/total" />
  </a>
  <a href="https://hub.docker.com/repository/docker/guovern/iptv-api">
    <img src="https://img.shields.io/docker/pulls/guovern/iptv-api" />
  </a>
  <a href="https://github.com/Guovin/iptv-api/fork">
    <img src="https://img.shields.io/github/forks/guovin/iptv-api" />
  </a>
</p>

[English](./README_en.md) | 中文

✨💻[IPTV-Web](https://github.com/Guovin/iptv-web)：IPTV电视直播源管理平台，支持在线播放等功能，开发中...

- [✅ 特点](#特点)
- [🔗 最新结果](#最新结果)
- [⚙️ 配置参数](#配置)
- [🚀 快速上手](#快速上手)
    - [工作流](#工作流)
    - [命令行](#命令行)
    - [GUI软件](#GUI-软件)
    - [Docker](#Docker)
- [📖 详细教程](./docs/tutorial.md)
- [🗓️ 更新日志](./CHANGELOG.md)
- [❤️ 赞赏](#赞赏)
- [👀 关注(更新订阅+答疑交流)](#关注)
- [📣 免责声明](#免责声明)
- [⚖️ 许可证](#许可证)

📍订阅源来自：

- [iptv-org/iptv](https://github.com/iptv-org/iptv)
- [suxuang/myIPTV](https://github.com/suxuang/myIPTV)
- [kimwang1978/collect-tv-txt](https://github.com/kimwang1978/collect-tv-txt)
- [xzw832/cmys](https://github.com/xzw832/cmys)
- [asdjkl6/tv](https://github.com/asdjkl6/tv)
- [yuanzl77/IPTV](https://github.com/yuanzl77/IPTV)
- [fanmingming/live](https://github.com/fanmingming/live)
- [vbskycn/iptv](https://github.com/vbskycn/iptv)
- [YueChan/Live](https://github.com/YueChan/Live)
- [YanG-1989/m3u](https://github.com/YanG-1989/m3u)

📍频道图标来自：

- [fanmingming/live](https://github.com/fanmingming/live)

## 特点

- ✅ 自定义模板，生成您想要的频道
- ✅ 支持多种获取源方式：本地源、组播源、酒店源、订阅源、关键字搜索
- ✅ 接口测速验效，获取延迟、速率、分辨率，过滤无效接口
- ✅ 偏好设置：IPv4、IPv6、接口来源排序优先级与数量配置、接口白名单
- ✅ 定时执行，北京时间每日 6:00 与 18:00 执行更新
- ✅ 支持多种运行方式：工作流、命令行、GUI 软件、Docker(amd64/arm64/arm v7)
- ✨ 更多功能请见[配置参数](#配置)

## 最新结果

- 接口源：

```bash
https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u
```

```bash
https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.txt
```

或

```bash
https://cdn.jsdelivr.net/gh/Guovin/iptv-api@gd/output/result.m3u
```

```bash
https://cdn.jsdelivr.net/gh/Guovin/iptv-api@gd/output/result.txt
```

- 数据源：

```bash
https://raw.githubusercontent.com/Guovin/iptv-api/gd/source.json
```

或

```bash
https://cdn.jsdelivr.net/gh/Guovin/iptv-api@gd/source.json
```

## 配置

| 配置项                    | 描述                                                                                                                                                                    | 默认值               |
|:-----------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------|
| open_driver            | 开启浏览器运行，若更新无数据可开启此模式，较消耗性能                                                                                                                                            | False             |
| open_empty_category    | 开启无结果频道分类，自动归类至底部                                                                                                                                                     | False             |
| open_filter_resolution | 开启分辨率过滤，低于最小分辨率（min_resolution）的接口将会被过滤，GUI用户需要手动安装FFmpeg，程序会自动调用FFmpeg获取接口分辨率，推荐开启，虽然会增加测速阶段耗时，但能更有效地区分是否可播放的接口                                                      | True              |
| open_filter_speed      | 开启速率过滤，低于最小速率（min_speed）的接口将会被过滤                                                                                                                                      | True              |
| open_hotel             | 开启酒店源功能，关闭后所有酒店源工作模式都将关闭                                                                                                                                              | True              |
| open_hotel_foodie      | 开启 Foodie 酒店源工作模式                                                                                                                                                     | True              |
| open_hotel_fofa        | 开启 FOFA、ZoomEye 酒店源工作模式                                                                                                                                               | True              |
| open_keep_all          | 开启保留所有检索结果，会保留非模板频道名称的结果，推荐手动维护时开启                                                                                                                                    | False             |
| open_local             | 开启本地源功能，将使用模板文件与本地源文件中的数据                                                                                                                                             | True              |
| open_m3u_result        | 开启转换生成 m3u 文件类型结果链接，支持显示频道图标                                                                                                                                          | True              |
| open_multicast         | 开启组播源功能，关闭后所有组播源工作模式都将关闭                                                                                                                                              | True              |
| open_multicast_foodie  | 开启 Foodie 组播源工作模式                                                                                                                                                     | True              |
| open_multicast_fofa    | 开启 FOFA 组播源工作模式                                                                                                                                                       | True              |
| open_online_search     | 开启关键字搜索源功能                                                                                                                                                            | False             |
| open_proxy             | 开启代理，自动获取免费可用代理，若更新无数据可开启此模式                                                                                                                                          | False             |
| open_request           | 开启查询请求，数据来源于网络（仅针对酒店源与组播源）                                                                                                                                            | False             |
| open_service           | 开启页面服务，用于控制是否启动结果页面服务；如果使用青龙等平台部署，有专门设定的定时任务，需要更新完成后停止运行，可以关闭该功能                                                                                                      | True              |
| open_sort              | 开启排序功能（响应速度、日期、分辨率）                                                                                                                                                   | True              |
| open_subscribe         | 开启订阅源功能                                                                                                                                                               | False             |
| open_supply            | 开启补偿机制模式，用于控制当频道接口数量不足时，自动将不满足条件（例如低于最小速率）但可能可用的接口添加至结果中，从而避免结果为空的情况                                                                                                  | True              |
| open_update            | 开启更新，用于控制是否更新接口，若关闭则所有工作模式（获取接口和测速）均停止                                                                                                                                | True              |
| open_update_time       | 开启显示更新时间                                                                                                                                                              | True              |
| open_url_info          | 开启显示接口说明信息，用于控制是否显示接口来源、分辨率、协议类型等信息，为$符号后的内容，播放软件使用该信息对接口进行描述，若部分播放器（如PotPlayer）不支持解析导致无法播放可关闭                                                                        | False             |
| open_use_cache         | 开启使用本地缓存数据，适用于查询请求失败场景（仅针对酒店源与组播源）                                                                                                                                    | True              |
| open_history           | 开启使用历史更新结果（包含模板与结果文件的接口），合并至本次更新中                                                                                                                                     | True              |
| app_port               | 页面服务端口，用于控制页面服务的端口号                                                                                                                                                   | 8000              |
| final_file             | 生成结果文件路径                                                                                                                                                              | output/result.txt |
| hotel_num              | 结果中偏好的酒店源接口数量                                                                                                                                                         | 10                |
| hotel_page_num         | 酒店地区获取分页数量                                                                                                                                                            | 1                 |
| hotel_region_list      | 酒店源地区列表，"全部"表示所有地区                                                                                                                                                    | 全部                |
| ipv4_num               | 结果中偏好的 IPv4 接口数量                                                                                                                                                      | 5                 |
| ipv6_num               | 结果中偏好的 IPv6 接口数量                                                                                                                                                      | 5                 |
| ipv6_support           | 强制认为当前网络支持IPv6，跳过检测                                                                                                                                                   | False             |
| ipv_type               | 生成结果中接口的协议类型，可选值：ipv4、ipv6、全部、all                                                                                                                                     | 全部                |
| ipv_type_prefer        | 接口协议类型偏好，优先将该类型的接口排在结果前面，可选值：ipv4、ipv6、自动、auto                                                                                                                        | ipv6,ipv4         |
| local_file             | 本地源文件路径                                                                                                                                                               | config/local.txt  |
| local_num              | 结果中偏好的本地源接口数量                                                                                                                                                         | 10                |
| min_resolution         | 接口最小分辨率，需要开启 open_filter_resolution 才能生效                                                                                                                              | 1920x1080         |
| min_speed              | 接口最小速率（单位M/s），需要开启 open_filter_speed 才能生效                                                                                                                             | 0.2               |
| multicast_num          | 结果中偏好的组播源接口数量                                                                                                                                                         | 10                |
| multicast_page_num     | 组播地区获取分页数量                                                                                                                                                            | 1                 |
| multicast_region_list  | 组播源地区列表，"全部"表示所有地区                                                                                                                                                    | 全部                |
| online_search_num      | 结果中偏好的关键字搜索接口数量                                                                                                                                                       | 0                 |
| online_search_page_num | 关键字搜索频道获取分页数量                                                                                                                                                         | 1                 |
| origin_type_prefer     | 结果偏好的接口来源，结果优先按该顺序进行排序，逗号分隔，例如：local,hotel,multicast,subscribe,online_search；local：本地源，hotel：酒店源，multicast：组播源，subscribe：订阅源，online_search：关键字搜索；不填写则表示不指定来源，按照接口速率排序 |                   |
| recent_days            | 获取最近时间范围内更新的接口（单位天），适当减小可避免出现匹配问题                                                                                                                                     | 30                |
| request_timeout        | 查询请求超时时长，单位秒(s)，用于控制查询接口文本链接的超时时长以及重试时长，调整此值能优化更新时间                                                                                                                   | 10                |
| sort_timeout           | 单个接口测速超时时长，单位秒(s)；数值越大测速所属时间越长，能提高获取接口数量，但质量会有所下降；数值越小测速所需时间越短，能获取低延时的接口，质量较好；调整此值能优化更新时间                                                                             | 10                |
| sort_duplicate_limit   | 相同域名接口允许重复执行次数，用于控制执行测速、获取分辨率时的重复次数，数值越大结果越准确，但耗时会增加                                                                                                                  | 3                 |
| source_file            | 模板文件路径                                                                                                                                                                | config/demo.txt   |
| subscribe_num          | 结果中偏好的订阅源接口数量                                                                                                                                                         | 10                |
| time_zone              | 时区，可用于控制更新时间显示的时区，可选值：Asia/Shanghai 或其它时区编码                                                                                                                           | Asia/Shanghai     |
| urls_limit             | 单个频道接口数量                                                                                                                                                              | 10                |
| update_time_position   | 更新时间显示位置，需要开启 open_update_time 才能生效，可选值：top、bottom，top: 显示于结果顶部，bottom: 显示于结果底部                                                                                       | top               |

## 快速上手

### 工作流

Fork 本项目并开启工作流更新，具体步骤请见[详细教程](./docs/tutorial.md)

### 命令行

```shell
pip install pipenv
```

```shell
pipenv install --dev
```

启动更新：

```shell
pipenv run dev
```

启动服务：

```shell
pipenv run service
```

### GUI 软件

1. 下载[IPTV-API 更新软件](https://github.com/Guovin/iptv-api/releases)，打开软件，点击更新，即可完成更新

2. 或者在项目目录下运行以下命令，即可打开 GUI 软件：

```shell
pipenv run ui
```

<img src="./docs/images/ui.png" alt="IPTV-API更新软件" title="IPTV-API更新软件" style="height:600px" />

### Docker

- iptv-api（完整版本）：性能要求较高，更新速度较慢，稳定性、成功率高；修改配置 open_driver = False 可切换到 Lite
  版本运行模式（推荐酒店源、组播源、关键字搜索使用此版本）
- iptv-api:lite（精简版本）：轻量级，性能要求低，更新速度快，稳定性不确定（推荐订阅源使用此版本）

#### 1. 拉取镜像

- iptv-api

```bash
docker pull guovern/iptv-api:latest
```

🚀 代理加速（推荐国内用户使用）：

```bash
docker pull docker.1ms.run/guovern/iptv-api:latest
```

- iptv-api:lite

```bash
docker pull guovern/iptv-api:lite
```

🚀 代理加速（推荐国内用户使用）：

```bash
docker pull docker.1ms.run/guovern/iptv-api:lite
```

#### 2. 运行容器

- iptv-api

```bash
docker run -d -p 8000:8000 guovern/iptv-api
```

- iptv-api:lite

```bash
docker run -d -p 8000:8000 guovern/iptv-api:lite
```

##### 挂载（推荐）：

实现宿主机文件与容器文件同步，修改模板、配置、获取更新结果文件可直接在宿主机文件夹下操作

以宿主机路径/etc/docker 为例：

- iptv-api

```bash
-v /etc/docker/config:/iptv-api/config
-v /etc/docker/output:/iptv-api/output
```

- iptv-api:lite

```bash
-v /etc/docker/config:/iptv-api-lite/config
-v /etc/docker/output:/iptv-api-lite/output
```

##### 环境变量：

- 端口

```bash
-e APP_PORT=8000
```

- 定时执行时间

```bash
-e UPDATE_CRON1="0 22 * * *"
-e UPDATE_CRON2="0 10 * * *"
```

#### 3. 更新结果

- 接口地址：`ip:8000`
- m3u 接口：`ip:8000/m3u`
- txt 接口：`ip:8000/txt`
- 接口内容：`ip:8000/content`
- 测速日志：`ip:8000/log`

## 更新日志

[更新日志](./CHANGELOG.md)

## 赞赏

<div>开发维护不易，请我喝杯咖啡☕️吧~</div>

| 支付宝                                  | 微信                                      |
|--------------------------------------|-----------------------------------------|
| ![支付宝扫码](./static/images/alipay.jpg) | ![微信扫码](./static/images/appreciate.jpg) |

## 关注

微信公众号搜索 Govin，或扫码，接收更新推送、学习更多使用技巧：

![微信公众号](./static/images/qrcode.jpg)

## 免责声明

本项目仅供学习交流用途，接口数据均来源于网络，如有侵权，请联系删除

## 许可证

[MIT](./LICENSE) License &copy; 2024-PRESENT [Govin](https://github.com/guovin)
