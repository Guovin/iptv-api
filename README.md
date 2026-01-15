<div align="center">
  <img src="./static/images/logo.png" alt="logo"/>
  <h1 align="center">IPTV-API</h1>
</div>

📺IPTV直播源自动更新平台，『🤖全自动采集、筛选、测速、生成流程🚀』，支持丰富的个性化配置，将结果地址输入播放器即可观看

<p align="center">
  <br>
  <a href="https://trendshift.io/repositories/12327" target="_blank"><img src="https://trendshift.io/api/badge/repositories/12327" alt="Guovin%2Fiptv-api | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>

<p align="center">
  <a href="https://github.com/Guovin/iptv-api/releases/latest">
    <img src="https://img.shields.io/github/v/release/guovin/iptv-api?label=Version" />
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.13-47c219?label=Python" />
  </a>
  <a href="https://github.com/Guovin/iptv-api/releases/latest">
    <img src="https://img.shields.io/github/downloads/guovin/iptv-api/total?label=GUI%20Downloads" />
  </a>
  <a href="https://hub.docker.com/repository/docker/guovern/iptv-api">
    <img src="https://img.shields.io/docker/pulls/guovern/iptv-api?label=Docker%20Pulls" />
  </a>
  <a href="https://github.com/Guovin/iptv-api/fork">
    <img src="https://img.shields.io/github/forks/guovin/iptv-api?label=Forks" />
  </a>
</p>

<div align="center">

[English](./README_en.md) | 中文

</div>

- [✅ 核心特性](#核心特性)
- [⚙️ 配置参数](#配置)
- [🚀 快速上手](#快速上手)
    - [配置与结果目录](#配置与结果目录)
    - [工作流](#工作流)
    - [命令行](#命令行)
    - [GUI软件](#GUI-软件)
    - [Docker](#Docker)
- [📖 详细教程](./docs/tutorial.md)
- [🗓️ 更新日志](./CHANGELOG.md)
- [👀 关注](#关注)
- [⭐️ Star统计](#Star统计)
- [❤️ 捐赠](#捐赠)
- [⚠️ 免责声明](#免责声明)
- [⚖️ 许可证](#许可证)

> [!IMPORTANT]
> 1. 前往`Govin`公众号回复`cdn`获取加速地址，提升订阅源与频道图标等资源的访问速度
> 2. 本项目不提供数据源，请自行添加后生成结果
> 3. 生成结果质量取决于数据源与网络环境等因素，请合理调整[配置参数](#配置)以获取更符合需求的结果

## 核心特性

| 功能         | 支持状态 | 说明                                         |
|:-----------|:----:|:-------------------------------------------|
| **自定义模板**  |  ✅   | 生成自己想要的频道菜单                                |
| **频道别名**   |  ✅   | 提升频道结果获取量与准确率，支持正则表达式                      |
| **多源聚合**   |  ✅   | 本地源、订阅源                                    |
| **推流**     |  ✅   | 改善弱网播放体验，支持浏览器直接播放                         |
| **回放类接口**  |  ✅   | 回放类接口的获取与生成                                |
| **EPG**    |  ✅   | 获取并显示频道预告内容                                |
| **频道台标**   |  ✅   | 自定义频道台标库来源                                 |
| **测速验效**   |  ✅   | 获取延迟、速率、分辨率，过滤无效接口，支持实时输出结果                |
| **高级偏好设置** |  ✅   | 速率、分辨率、黑/白名单、归属地与运营商自定义过滤                  |
| **结果管理**   |  ✅   | 结果分类存储与访问、日志记录、未匹配频道记录、统计分析、冻结过滤/解冻回归、数据缓存 |
| **定时任务**   |  ✅   | 定时或间隔执行更新                                  |
| **多平台部署**  |  ✅   | 工作流、命令行、GUI 软件、Docker (amd64/arm64/arm v7) |
| **更多功能**   |  ✨   | 详见[配置参数](#配置)章节                            |

## 配置

> [!NOTE]\
> 以下配置项位于`config/config.ini`文件中，支持通过配置文件或环境变量进行修改，修改保存后重启即可生效

| 配置项                    | 描述                                                                                                                   | 默认值               |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------|:------------------|
| open_update            | 开启更新，用于控制是否更新接口，若关闭则所有工作模式（获取接口和测速）均停止                                                                               | True              |
| open_empty_category    | 开启无结果频道分类，自动归类至底部                                                                                                    | False             |
| open_update_time       | 开启显示更新时间                                                                                                             | True              |
| open_url_info          | 开启显示接口说明信息，用于控制是否显示接口来源、分辨率、协议类型等信息，为 $ 符号后的内容，播放软件使用该信息对接口进行描述，若部分播放器（如 PotPlayer）不支持解析导致无法播放可关闭                    | False             |
| open_epg               | 开启 EPG 功能，支持频道显示预告内容                                                                                                 | True              |
| open_m3u_result        | 开启转换生成 m3u 文件类型结果链接，支持显示频道图标                                                                                         | True              |
| urls_limit             | 单个频道接口数量                                                                                                             | 10                |
| update_time_position   | 更新时间显示位置，需要开启 open_update_time 才能生效，可选值: top、bottom；top: 显示于结果顶部，bottom: 显示于结果底部                                     | top               |
| language               | 系统语言设置；可选值: zh_CN、en                                                                                                 | zh_CN             |
| update_mode            | 定时执行更新时间模式，不作用于工作流；可选值: interval、time； interval: 按间隔时间执行，time: 按指定时间点执行                                              | interval          |
| update_interval        | 定时执行更新时间间隔，仅在update_mode = interval时生效，单位小时，设置 0 或空则只运行一次                                                            | 12                |
| update_times           | 定时执行更新时间点，仅在update_mode = time时生效，格式 HH:MM，支持多个时间点逗号分隔                                                               |                   |
| update_startup         | 启动时执行更新，用于控制程序启动后是否立即执行一次更新                                                                                          | True              |
| time_zone              | 时区，可用于控制定时执行时区或显示更新时间的时区；可选值: Asia/Shanghai 或其它时区编码                                                                  | Asia/Shanghai     |
| source_file            | 模板文件路径                                                                                                               | config/demo.txt   |
| final_file             | 生成结果文件路径                                                                                                             | output/result.txt |
| open_service           | 开启页面服务，用于控制是否启动结果页面服务；如果使用青龙等平台部署，有专门设定的定时任务，需要更新完成后停止运行，可以关闭该功能                                                     | True              |
| app_port               | 页面服务端口，用于控制页面服务的端口号                                                                                                  | 5180              |
| public_scheme          | 公网协议；可选值: http、https                                                                                                 | http              |
| public_domain          | 公网 Host 地址，用于生成结果中的访问地址，默认使用本机 IP                                                                                    | 127.0.0.1         |
| cdn_url                | CDN 代理加速地址，用于订阅源、频道图标等资源的加速访问                                                                                        |                   |
| open_local             | 开启本地源功能，将使用模板文件与本地源文件（local.txt）中的数据                                                                                 | True              |
| open_subscribe         | 开启订阅源功能                                                                                                              | True              |
| open_history           | 开启使用历史更新结果（包含模板与结果文件的接口），合并至本次更新中                                                                                    | True              |
| open_headers           | 开启使用 M3U 内含的请求头验证信息，用于测速等操作，注意：只有个别播放器支持播放这类含验证信息的接口，默认为关闭                                                           | False             |
| open_speed_test        | 开启测速功能，获取响应时间、速率、分辨率                                                                                                 | True              |
| open_filter_resolution | 开启分辨率过滤，低于最小分辨率（min_resolution）的接口将会被过滤，GUI 用户需要手动安装 FFmpeg，程序会自动调用 FFmpeg 获取接口分辨率，推荐开启，虽然会增加测速阶段耗时，但能更有效地区分是否可播放的接口 | True              |
| open_filter_speed      | 开启速率过滤，低于最小速率（min_speed）的接口将会被过滤                                                                                     | True              |
| open_supply            | 开启补偿机制模式，用于控制当频道接口数量不足时，自动将不满足条件（例如低于最小速率）但可能可用的接口添加至结果中，从而避免结果为空的情况                                                 | True              |
| min_resolution         | 接口最小分辨率，需要开启 open_filter_resolution 才能生效                                                                             | 1920x1080         |
| max_resolution         | 接口最大分辨率，需要开启 open_filter_resolution 才能生效                                                                             | 1920x1080         |
| min_speed              | 接口最小速率（单位 M/s），需要开启 open_filter_speed 才能生效                                                                           | 0.5               |
| speed_test_limit       | 同时执行测速的接口数量，用于控制测速阶段的并发数量，数值越大测速所需时间越短，负载较高，结果可能不准确；数值越小测速所需时间越长，低负载，结果较准确；调整此值能优化更新时间                               | 10                |
| speed_test_timeout     | 单个接口测速超时时长，单位秒(s)；数值越大测速所需时间越长，能提高获取接口数量，但质量会有所下降；数值越小测速所需时间越短，能获取低延时的接口，质量较好；调整此值能优化更新时间                            | 10                |
| speed_test_filter_host | 测速阶段使用 Host 地址进行过滤，相同 Host 地址的频道将共用测速数据，开启后可大幅减少测速所需时间，但可能会导致测速结果不准确                                                 | False             |
| request_timeout        | 查询请求超时时长，单位秒(s)，用于控制查询接口文本链接的超时时长以及重试时长，调整此值能优化更新时间                                                                  | 10                |
| ipv6_support           | 强制认为当前网络支持 IPv6，跳过检测                                                                                                 | False             |
| ipv_type               | 生成结果中接口的协议类型；可选值: ipv4、ipv6、all                                                                                      | all               |
| ipv_type_prefer        | 接口协议类型偏好，优先将该类型的接口排在结果前面；可选值: ipv4、ipv6、auto                                                                         | auto              |
| location               | 接口归属地，用于控制结果只包含填写的归属地类型，支持关键字过滤，英文逗号分隔，不填写表示不指定归属地，建议使用靠近使用者的归属地，能提升播放体验                                             |                   |
| isp                    | 接口运营商，用于控制结果中只包含填写的运营商类型，支持关键字过滤，英文逗号分隔，不填写表示不指定运营商                                                                  |                   |
| origin_type_prefer     | 结果偏好的接口来源，结果优先按该顺序进行排序，逗号分隔，例如: local,subscribe；不填写则表示不指定来源，按照接口速率排序                                                 |                   |
| local_file             | 本地源文件路径                                                                                                              | config/local.txt  |
| local_num              | 结果中偏好的本地源接口数量                                                                                                        | 10                |
| subscribe_num          | 结果中偏好的订阅源接口数量                                                                                                        | 10                |
| logo_url               | 频道台标库地址                                                                                                              |                   |
| logo_type              | 频道台标文件类型                                                                                                             | png               |
| open_rtmp              | 开启 RTMP 推流功能，需要安装 FFmpeg，利用本地带宽提升接口播放体验                                                                              | True              |
| nginx_http_port        | Nginx HTTP 服务端口，用于 RTMP 推流转发的 HTTP 服务端口                                                                              | 8080              |
| nginx_rtmp_port        | Nginx RTMP 服务端口，用于 RTMP 推流转发的 RTMP 服务端口                                                                              | 1935              |
| rtmp_idle_timeout      | RTMP 频道接口空闲停止推流超时时长，单位秒(s)，用于控制接口无人观看时超过该时长后停止推流，调整此值能优化服务器资源占用                                                      | 300               |
| rtmp_max_streams       | RTMP 推流最大并发数量，用于控制同时推流的频道数量，数值越大服务器压力越大，调整此值能优化服务器资源占用                                                               | 10                |

## 快速上手

### 配置与结果目录

```
iptv-api/                  # 项目根目录
├── config                 # 配置文件目录，包含配置文件、模板文件等
│   └── config.ini         # 配置参数文件
│   └── demo.txt           # 频道模板
│   └── alias.txt          # 频道别名
│   └── blacklist.txt      # 接口黑名单
│   └── whitelist.txt      # 接口白名单
│   └── subscribe.txt      # 频道订阅源列表
│   └── local.txt          # 本地源文件
│   └── epg.txt            # EPG订阅源列表
└── output                 # 结果文件目录，包含生成的结果文件等
    └── data               # 结果数据缓存目录
    └── epg                # EPG结果目录
    └── ipv4               # IPv4结果目录
    └── ipv6               # IPv6结果目录
    └── result.m3u/txt     # m3u/txt结果
    └── hls.m3u/txt        # RTMP hls推流结果
    └── log                # 日志文件目录
        └── result.log     # 有效结果日志
        └── speed_test.log # 测速日志
        └── statistic.log  # 统计结果日志
        └── nomatch.log    # 未匹配频道记录
```

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

1. 下载[IPTV-API 更新软件](https://github.com/Guovin/iptv-api/releases)，打开软件，点击启动，即可进行更新

2. 或者在项目目录下运行以下命令，即可打开 GUI 软件：

```shell
pipenv run ui
```

<img src="./docs/images/ui.png" alt="IPTV-API更新软件" title="IPTV-API更新软件" style="height:600px" />

### Docker

#### 1. Compose部署（推荐）

下载[docker-compose.yml](./docker-compose.yml)或复制内容创建（内部参数可按需更改），在文件所在路径下运行以下命令即可部署：

```bash
docker compose up -d
```

#### 2. 手动命令部署

##### （1）拉取镜像

```bash
docker pull guovern/iptv-api:latest
```

🚀 代理加速（若拉取失败可以使用该命令，但有可能拉取的是旧版本）：

```bash
docker pull docker.1ms.run/guovern/iptv-api:latest
```

##### （2）运行容器

```bash
docker run -d -p 80:8080 guovern/iptv-api
```

**环境变量：**

| 变量              | 描述                                | 默认值       |
|:----------------|:----------------------------------|:----------|
| PUBLIC_DOMAIN   | 公网域名或IP地址，决定外部访问或推流结果的Host地址      | 127.0.0.1 |
| PUBLIC_PORT     | 公网端口，设置为映射后的端口，决定外部访问地址和推流结果地址的端口 | 80        |
| NGINX_HTTP_PORT | HTTP服务端口，外部访问需要映射该端口              | 8080      |

如果需要修改环境变量，在上述运行命令后添加以下参数：

```bash
# 修改公网域名
-e PUBLIC_DOMAIN=your.domain.com
# 修改公网端口
-e PUBLIC_PORT=80
```

除了以上环境变量，还支持通过环境变量覆盖配置文件中的[配置项](#配置)

**挂载：** 实现宿主机文件与容器文件同步，修改模板、配置、获取更新结果文件可直接在宿主机文件夹下操作，在上述运行命令后添加以下参数

```bash
# 挂载配置目录
-v /iptv-api/config:/iptv-api/config
# 挂载结果目录
-v /iptv-api/output:/iptv-api/output
```

##### 3. 更新结果

| 接口              | 描述          |
|:----------------|:------------|
| /               | 默认接口        |
| /m3u            | m3u 格式接口    |
| /txt            | txt 格式接口    |
| /ipv4           | ipv4 默认接口   |
| /ipv6           | ipv6 默认接口   |
| /ipv4/txt       | ipv4 txt接口  |
| /ipv6/txt       | ipv6 txt接口  |
| /ipv4/m3u       | ipv4 m3u接口  |
| /ipv6/m3u       | ipv6 m3u接口  |
| /content        | 接口文本内容      |
| /log/result     | 有效结果的日志     |
| /log/speed-test | 所有参与测速接口的日志 |
| /log/statistic  | 统计结果的日志     |
| /log/nomatch    | 未匹配频道的日志    |

**RTMP 推流：**

> [!NOTE]
> 1. 如果是服务器部署，请务必配置`PUBLIC_DOMAIN`环境变量为服务器域名或IP地址，`PUBLIC_PORT`环境变量为公网端口，否则推流地址无法访问
> 2. 开启推流后，默认会将获取到的接口（如订阅源）进行推流
> 3. 如果需要对本地视频源进行推流，可在`config`目录下新建`hls`文件夹，将以`频道名称命名`的视频文件放入其中，程序会自动推流到对应的频道中

| 推流接口          | 描述           |
|:--------------|:-------------|
| /hls          | 推流接口         |
| /hls/txt      | 推流txt接口      |
| /hls/m3u      | 推流m3u接口      |
| /hls/ipv4     | 推流ipv4 默认接口  |
| /hls/ipv6     | 推流ipv6 默认接口  |
| /hls/ipv4/txt | 推流ipv4 txt接口 |
| /hls/ipv4/m3u | 推流ipv4 m3u接口 |
| /hls/ipv6/txt | 推流ipv6 txt接口 |
| /hls/ipv6/m3u | 推流ipv6 m3u接口 |
| /stat         | 推流状态统计接口     |

## 更新日志

[更新日志](./CHANGELOG.md)

## 关注

### Github

关注我的Github账号[Guovin](https://github.com/Guovin)，获取更多实用项目

### 微信公众号

微信公众号搜索 Govin，或扫码，接收更新推送、学习更多使用技巧：

![微信公众号](./static/images/qrcode.jpg)

### 需要更多帮助？

联系邮箱：`360996299@qq.com`

## Star统计

[![Star统计](https://starchart.cc/Guovin/iptv-api.svg?variant=adaptive)](https://starchart.cc/Guovin/iptv-api)

## 捐赠

<div>开发维护不易，请我喝杯咖啡☕️吧~</div>

| 支付宝                                  | 微信                                      |
|--------------------------------------|-----------------------------------------|
| ![支付宝扫码](./static/images/alipay.jpg) | ![微信扫码](./static/images/appreciate.jpg) |

## 免责声明

- 本项目仅为工具/框架，不包含或提供任何直播源、受版权保护的节目或其他第三方内容。用户需自行添加数据源并确保所使用的数据源及使用行为符合所在地区法律法规。
- 使用者对通过本项目获取、分发或播放的内容独立负责。请勿用于传播、分发或观看未经授权的受版权保护内容。
- 在使用本项目时，应遵守当地相关法律法规与监管要求。作者不对因用户使用本项目而产生的任何法律责任承担责任。
- 商业、企业或生产环境使用前建议咨询法律顾问并做好合规审查。

## 许可证

[MIT](./LICENSE) License &copy; 2024-PRESENT [Govin](https://github.com/guovin)
