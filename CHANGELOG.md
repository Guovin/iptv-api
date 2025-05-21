# 更新日志（Changelog）

## v1.7.1

### 2025/5/9

### 🚀 新功能 ###

---

- 新增支持获取接口`归属地`与`运营商`（利用`纯真IP数据库`实现），支持关键字过滤，可通过配置`location`与`isp`
  生成想要的结果，建议优先使用靠近使用环境的归属地与本机网络运营商，以提升播放效果（#1058）
- 新增支持无需开启测速的情况下，可对接口进行`排序`，输出结果日志

### 🌟 优化 ###

---

- 优化`IPv6`结果进入缓存
- 调整`冻结结果的阈值`，加入`最大延迟`与`最小速率`限制
- 调整默认配置`ipv_type_prefer = auto`，即根据网络环境自动选择排序IPv4与IPv6结果的优先级
- 频道结果日志文件更名为`result.log`
- 更新部分配置参数描述

### 🐛 修复 ###

---

- 修复`IPv6含参数结果`匹配问题（#1048）
- 修复白名单生成结果失败（#1055）

### 🗑️ 移除 ###

---

- 移除无效的`IPv6订阅源`

> [!NOTE]
> 有小伙伴对部署后首次更新时间变长有疑问，其实这是正常的。
> 因为从`v1.7.0`开始，为了提升频道测速准确性，默认对接口进行全量测速。
> 目前首次运行一般`30分钟`左右，如果是新增的频道比较多首次运行时间会比较长。
> 但这并不会影响使用，由于默认模板已经内置了部分更新结果（`output/cache.pkl.gz`），部署后可立即访问使用。
> 同时测速阶段可根据历史数据跳过无效接口，无需担心，后续更新所需时间会明显减少。
> 如果你介意，可开启Host共享模式（`speed_test_filter_host = True`），相同Host的接口会共享测速结果，可以大幅降低测速所需时间，但结果准确性也会下降。

<details>
  <summary>English</summary>

### 🚀 New Features ###

---

- Added support for obtaining interface `location` and `ISP` (implemented using the `IPIP database`), supports keyword
  filtering. You can configure `location` and `isp` to generate desired results. It is recommended to prioritize the
  location and ISP close to the usage environment to improve playback performance (#1058).
- Added support for sorting interfaces and outputting result logs without enabling speed testing.

### 🌟 Optimizations ###

---

- Optimized caching of `IPv6` results.
- Adjusted the `frozen result threshold` by adding `maximum latency` and `minimum speed` limits.
- Adjusted the default configuration `ipv_type_prefer = auto`, which automatically prioritizes sorting of IPv4 and IPv6
  results based on the network environment.
- Renamed the channel result log file to `result.log`.
- Updated descriptions of some configuration parameters.

### 🐛 Bug Fixes ###

---

- Fixed the issue with matching `IPv6 results with parameters` (#1048).
- Fixed the failure to generate whitelist results (#1055).

### 🗑️ Removals ###

---

- Removed invalid `IPv6 subscription sources`.

> [!NOTE]
> Some users have raised concerns about the longer initial update time after deployment. This is actually normal.
> Starting from `v1.7.0`, to improve the accuracy of channel speed tests,
> full speed testing of interfaces is enabled by default.
> The first run usually takes about `30 minutes`. If there are many new channels, the initial run time may be longer.
> However, this does not affect usage, as the default template already includes some pre-updated results
> (`output/cache.pkl.gz`), allowing immediate access after deployment.
> During the speed test phase, invalid interfaces can be skipped based on historical data, so there is no need to worry.
> Subsequent updates will take significantly less time.
> If you are concerned, you can enable Host sharing mode (`speed_test_filter_host = True`), where interfaces with the
> same Host share speed test results. This can greatly reduce the time required for speed testing,
> but the accuracy of the results may decrease.

</details>

## v1.7.0

### 2025/5/1

### 🚀 新功能 ###

---

- 新增`频道别名`功能（`config/alias.txt`），提升频道名称匹配能力
- 新增`EPG`功能（订阅文件配置`config/epg.txt`），显示频道预告信息
- 支持`回放类接口`获取与生成
- 新增`历史结果`的冻结与解冻，`冻结`：无效结果不参与测速，`解冻`：无结果时自动解冻重新测速
- 新增`最大分辨率`限制`max_resolution`
- 支持含`请求头`信息接口测速与生成，需播放器支持才可播放，可通过`open_headers`控制是否开启
- 新增测速并发数量配置`speed_test_limit`，实现控制测速负载压力
- 新增`Host数据共享`配置`speed_test_filter_host`，实现相同Host地址接口可共享测速结果
- 新增`推流统计`GUI按钮

### 🌟 优化 ###

---

- 重构`测速与排序`逻辑，适配更多类型接口的测速（#1009）
- 提供`内置结果`，解决首次运行等待期间无结果问题（可能不稳定，建议使用更新后结果）
- 优化接口测速默认为`全接口测速`，解决Host共享结果部分接口测速不准确问题
- 调整测速结果以`速率`排序，`分辨率`不再参与，解决部分低速率接口在前的问题
- 默认开启`推流`，调整`HLS`分片配置，推荐使用`HLS`接口，缓解卡顿情况
- 重构接口`额外信息`处理逻辑
- 测速相关配置项更名为`speed_test_*`，修改输出日志文案
- 调整默认最低接口速率为`0.5M/s`
- 更新黑名单，增加无效接口与`音频`接口

### 🐛 修复 ###

---

- 修复工作流运行问题，更换使用最新`ubuntu`版本（#1032）
- 修复`M3U`订阅源白名单失效问题（#1019）
- 修复部分`组播源`测速问题（#1026）
- 修复接口协议分类结果生成失败问题

### 🗑️ 移除 ###

---

- 移除部分失效订阅源
- 移除代理更新功能`open_proxy`
- 移除保留模式`open_keep_all`
- 移除重复执行`sort_duplicate_limit`

<details>
  <summary>English</summary>

### 🚀 New Features ###

---

- Added `Channel Alias` feature (`config/alias.txt`) to improve channel name matching.
- Added `EPG` feature (subscription file configuration `config/epg.txt`) to display channel program information.
- Support for `Playback Interface` retrieval and generation.
- Added `historical results` freezing and unfreezing. `Freezing`: Invalid results are excluded from speed testing.
  `Unfreezing`: Automatically unfreezes and retests when no results are available.
- Added `Maximum Resolution` limit `max_resolution`.
- Support for speed testing and generation of interfaces with `Request Headers`. Requires player support for playback
  and can be controlled via `open_headers`.
- Added configuration for speed test concurrency `speed_test_limit` to control speed test load pressure.
- Added `Host Data Sharing` configuration `speed_test_filter_host` to allow interfaces with the same Host address to
  share speed test results.
- Added Stream Statistics GUI button.

### 🌟 Optimizations ###

---

- Refactored `Speed Test and Sorting` logic to adapt to more types of interfaces (#1009).
- Provided `Built-in Results` to address the issue of no results during the first run (may be unstable, recommended to
  use updated results).
- Optimized interface speed testing to default to `Full Interface Speed Test`, resolving inaccuracies in speed tests for
  some interfaces with shared Host results.
- Adjusted speed test results to sort by `Rate`, with `Resolution` no longer included, resolving the issue of low-rate
  interfaces appearing at the top.
- Defaulted to enabling `Streaming`, adjusted `HLS` fragment configuration, and recommended using `HLS` interfaces to
  alleviate stuttering.
- Refactored the handling logic for interface `Additional Information`.
- Renamed speed test-related configuration items to `speed_test_*` and updated output log text.
- Adjusted the default minimum interface rate to `0.5M/s`.
- Updated the blacklist to include invalid interfaces and `audio` interfaces.

### 🐛 Bug Fixes ###

---

- Fixed workflow execution issues by switching to the latest `Ubuntu` version (#1032).
- Fixed the issue where the `M3U` subscription source whitelist was not working (#1019).
- Fixed speed test issues for some `Multicast Sources` (#1026).
- Fixed the failure to generate results for interface protocol classification.

### 🗑️ Removals ###

---

- Removed some invalid subscription sources.
- Removed proxy update feature `open_proxy`.
- Removed retention mode `open_keep_all`.
- Removed duplicate execution `sort_duplicate_limit`.

</details>

## v1.6.3

### 2025/4/3

- ✨ 新增支持RTMP推流（工作流不支持），支持`Live/HLS`推流，订阅结果可转换为对应模式推流输出，也可通过`config`目录内创建`live`或
  `hls`目录定义读取本地视频源
- ✨ Docker镜像合并为`guovern/iptv-api`，大小与精简版一致，不再区分完整版与精简版，`latest`为最新版，支持获取历史版本，如
  `1.6.2`
- ✨ 新增支持GUI最小化至系统托盘区运行
- ✨ 新增支持`IPv4/IPv6`双栈访问，支持`txt`与`m3u`区分IPv协议类型访问
- ✨ 增加构建版本号，支持保留历史版本
- 🐛 优化黑名单非url关键字匹配问题
- 🐛 修复Docker容器启动提示`no crontab for root`
- 🐛 修复IPv6结果过滤问题

<details>
  <summary>English</summary>

- ✨ Added support for RTMP streaming (not supported by workflows), supporting `Live/HLS` streaming. Subscription results
  can be converted to the corresponding mode for streaming output, and local video sources can be defined by creating
  `live` or `hls` directories in the `config` directory.
- ✨ Merged Docker images into `guovern/iptv-api`, with the same size as the slim version. No longer distinguish between
  full and slim versions. `latest` is the latest version, and historical versions can be obtained, such as `1.6.2`.
- ✨ Added support for minimizing the GUI to the system tray.
- ✨ Added support for dual-stack `IPv4/IPv6` access, supporting `txt` and `m3u` to distinguish between IPv protocol
  types.
- ✨ Added build version number, supporting the retention of historical versions.
- 🐛 Optimized the issue of non-URL keyword matching in the blacklist.
- 🐛 Fixed the `no crontab for root` prompt when starting the Docker container.
- 🐛 Fixed the issue of filtering IPv6 results.

</details>

## v1.6.2

### 2025/3/4

- ✨ 新增支持CDN代理加速，配置项：`cdn_url`，用于订阅源与频道图标资源加速访问，可关注公众号私信`获取代理地址`
- ✨ 新增支持`rtsp`协议接口
- ✨ 新增支持本地源频道名称模糊匹配
- ✨ 新增订阅源`Guovin/iptv-database`，来源于新仓库[IPTV-Database](https://github.com/Guovin/iptv-database)
- 🐛 修复支持含验证信息的接口匹配（#946）
- 🐛 修复输出结果文件问题，接口url不完整，丢失部分信息（#925）
- 🪄 优化运行流程，调整默认配置：关闭组播源、酒店源获取

<details>
  <summary>English</summary>

- ✨ Added support for CDN proxy acceleration, configuration item: `cdn_url`, for accelerating access to subscription
  sources and channel icon resources. You can follow the public account and send a private message to
  `get the proxy address`
- ✨ Added support for `rtsp` protocol interface
- ✨ Added support for fuzzy matching of local source channel names
- ✨ Added subscription source `Guovin/iptv-database`, from the new
  repository [IPTV-Database](https://github.com/Guovin/iptv-database)
- 🐛 Fixed support for matching interfaces with verification information (#946)
- 🐛 Fixed the issue with the output result file where the interface URL was incomplete and some information was
  missing (#925)
- 🪄 Optimized the running process and adjusted the default configuration: disabled multicast source and hotel source
  retrieval

</details>

## v1.6.1

### 2025/2/21

- 🎉 预告：💻[IPTV-Web](https://github.com/Guovin/iptv-web)：IPTV电视直播源管理平台，支持在线播放等功能，开发中...
- ⚠️ 注意：若属于旧版本升级，更新该版本需要手动删除旧版本结果缓存文件`output/cache.pkl`
- ✨ 新增支持`IPv6域名解析`，提升IPv6接口识别能力（#910）
- ✨ Docker更新时间环境变量精简为`UPDATE_CRON`，支持多个时间设置（#920）
- ✨ 更新组播源与酒店源离线数据
- 🪄 移除默认代理，由于集中访问压力过大，出现失效情况，建议自行定义订阅源和结果的代理地址，或关注公众号回复获取代理地址
- 🪄 重构频道数据格式`tuple`为`dict`，增加类型定义，优化数据处理，调整目录结构
- 🪄 正则匹配预编译，提升效率
- 🐛 调整Docker `FFmpeg`构建版本，解决部分域名无法获取分辨率问题（#864）
- 🐛 修复Docker重启时创建重复定时任务问题（#916）
- 🐛 合并默认与用户配置，用户配置只需填写变更项即可（#892，@wongsyrone）
- 🐛 修复结果生成失败问题（#863，#870，#875）

<details>
  <summary>English</summary>

- 🎉 Preview: 💻[IPTV-Web](https://github.com/Guovin/iptv-web): IPTV live stream management platform, supports online
  playback and other features, under development...
- ⚠️ Note: If upgrading from an older version, you need to manually delete the old version's result cache file
  `output/cache.pkl`
- ✨ Added support for `IPv6 domain name resolution`, improving IPv6 interface recognition capability (#910)
- ✨ Simplified Docker update time environment variable to `UPDATE_CRON`, supporting multiple time settings (#920)
- ✨ Updated offline data for multicast sources and hotel sources
- 🪄 Removed default proxy due to high access pressure causing failures, it is recommended to define your own proxy
  address for subscription sources and results, or follow the public account to get the proxy address
- 🪄 Refactored channel data format from `tuple` to `dict`, added type definitions, optimized data processing, and
  adjusted directory structure
- 🪄 Precompiled regex matching to improve efficiency
- 🐛 Adjusted Docker `FFmpeg` build version to resolve issues with some domain names not being able to get resolution (
  #864)
- 🐛 Fixed issue of creating duplicate scheduled tasks when Docker restarts (#916)
- 🐛 Merged default and user configurations, users only need to fill in the changes (#892, @wongsyrone)
- 🐛 Fixed issue of result generation failure (#863, #870, #875)

</details>

## v1.6.0

### 2025/1/22

- ✨ 新增支持`本地源`
- ✨ 使用新的代理地址`https://ghproxy.cc`
- ✨ 新增支持Docker修改定时任务时间，环境变量：`UPDATE_CRON1`, `UPDATE_CRON2`（#440）
- ✨ 新增同域名重复执行测速次数配置`sort_duplicate_limit`
- ✨ 新增`广东联通`RTP
- 🐛 修复补偿模式结果输出问题（#813）
- 🐛 修复无域名后缀、空格接口匹配问题（#832，#837）
- 🐛 修复无结果状态文件写入报错（#841）
- 🐛 修复GUI无法保存测速延迟设置
- 🐛 修复Docker版本文件丢失（#800）
- 🪄 `open_use_old_result`更名为`open_history`
- 🪄 优化对接口中`%`符号的转义处理（#853）
- 🪄 优化以接口Host去重（#846）
- 🪄 支持协议类型偏好`ipv_type_prefer`可设置为空，可实现全部类型按速率排序输出结果

<details>
  <summary>English</summary>

- ✨ Added support for `local sources`
- ✨ Using new proxy address `https://ghproxy.cc`
- ✨ Added support for modifying Docker scheduled task time, environment variables: `UPDATE_CRON1`, `UPDATE_CRON2` (#440)
- ✨ Added configuration for the number of speed tests for the same domain `sort_duplicate_limit`
- ✨ Added `Guangdong Unicom` RTP
- 🐛 Fixed compensation mode result output issue (#813)
- 🐛 Fixed issue with interface matching without domain suffix and spaces (#832, #837)
- 🐛 Fixed error writing to file in no result state (#841)
- 🐛 Fixed GUI unable to save speed test delay settings
- 🐛 Fixed Docker version file loss issue (#800)
- 🪄 `open_use_old_result` renamed to `open_history`
- 🪄 Optimized escaping of `%` symbol in interfaces (#853)
- 🪄 Optimized deduplication by interface host (#846)
- 🪄 Supported setting `ipv_type_prefer` to empty, allowing all types to be sorted by speed for output results

</details>

## v1.5.9

### 2025/1/8

- ❤️ 2025年第一次更新，祝大家新年快乐，万事如意
- ✨ 公众号详细教程文章已发布，欢迎关注`Govin`公众号获取
- ✨ 新增支持`rtmp`协议接口（#780）
- ✨ 新增支持修改更新时间位置（`update_time_position`）（#755）
- ✨ 新增支持修改时区（`time_zone`）（#759）
- ✨ 更新组播源与酒店源离线数据，增加`广东移动组播RTP`（#773）
- ✨ 更新Github CDN代理地址（#796）
- ✨ GUI使用Github工作流基于源码自动构建并发布，唯一下载途径是[Release](https://github.com/Guovin/iptv-api/releases)
  ，若安全软件有误报，请添加信任
- ✨ 增加版本信息打印输出
- ✨ 更新部分教程文档图片
- 🐛 修复m3u更新时间logo显示问题（#794）
- 🐛 修复测速阶段出现`cookie illegal key`问题（#728,#787）
- 🐛 修复白名单接口排序与接口信息命名问题（#765）
- 🐛 修复组播源更新结果异常问题
- 🐛 修复写入结果目录为空问题
- 🪄 调整接口状态码判断，只处理`200`状态码（#779）
- 🪄 调整默认不显示接口信息，兼容更多播放器

<details>
  <summary>English</summary>

- ❤️ First update of 2025, wishing everyone a Happy New Year and all the best
- ✨ Detailed tutorial articles have been published on the `Govin` public account, welcome to follow for more information
- ✨ Added support for `rtmp` protocol interface (#780)
- ✨ Added support for modifying update time position (`update_time_position`) (#755)
- ✨ Added support for modifying time zone (`time_zone`) (#759)
- ✨ Updated offline data for multicast sources and hotel sources, added `Guangdong Mobile Multicast RTP` (#773)
- ✨ Updated GitHub CDN proxy address (#796)
- ✨ GUI is automatically built and released based on the source code using GitHub workflows, the only download method
  is [Release](https://github.com/Guovin/iptv-api/releases). If there are false positives from security software, please
  add it to the trust list
- ✨ Added version information print output
- ✨ Updated some tutorial document images
- 🐛 Fixed m3u update time logo display issue (#794)
- 🐛 Fixed `cookie illegal key` issue during speed test phase (#728, #787)
- 🐛 Fixed whitelist interface sorting and interface information naming issue (#765)
- 🐛 Fixed abnormal results issue for multicast source updates
- 🐛 Fixed empty result directory issue
- 🪄 Adjusted interface status code judgment to only process `200` status code (#779)
- 🪄 Adjusted to hide interface information by default, compatible with more players

</details>

## v1.5.8

### 2024/12/30

- ✨ 推荐本次更新，实测可实现秒播级的观看体验，不可播放的情况明显减少
- ✨ 支持获取分辨率，GUI用户需要手动安装`FFmpeg`（#608）
- ✨ 支持`text/plain`结果输出，解决部分播放器显示问题（#736）
- ✨ 增加默认订阅源
- 🐛 修复IPv6接口测速输出的速率结果异常（#739）
- 🐛 修复GUI出现的错误输出（#743）
- 🐛 修复分辨率数值比较异常（#744）
- 🐛 修复台标无法显示（#762）
- 🪄 优化接口测速方法，兼容多种`m3u8`接口类型
- 🪄 调整Github工作流执行结果IPv类型为自动，即根据网络环境自动选择IPv4或IPv6，若有需要可手动设置`ipv_type_prefer`调整输出偏好
- 🪄 更新部分配置参数说明

<details>
  <summary>English</summary>

- ✨ Recommended update, tested to achieve instant playback experience, significantly reducing playback failures
- ✨ Support for obtaining resolution, GUI users need to manually install `FFmpeg` (#608)
- ✨ Support for `text/plain` result output, solving display issues in some players (#736)
- ✨ Added default subscription sources
- 🐛 Fixed abnormal speed results for IPv6 interface speed tests (#739)
- 🐛 Fixed error output in GUI (#743)
- 🐛 Fixed abnormal resolution value comparison (#744)
- 🐛 Fixed logo display issue (#762)
- 🪄 Optimized interface speed test method, compatible with various `m3u8` interface types
- 🪄 Adjusted GitHub workflow execution result IPv type to automatic, selecting IPv4 or IPv6 based on network
  environment, with manual setting option for `ipv_type_prefer`
- 🪄 Updated some configuration parameter descriptions

</details>

## v1.5.7

### 2024/12/23

- ❤️ 推荐关注微信公众号（Govin），订阅更新通知与使用技巧等文章推送，还可进行答疑和交流讨论
- ⚠️ 本次更新涉及配置变更，以最新 `config/config.ini` 为准，工作流用户需复制最新配置至`user_config.ini`
  ，Docker用户需清除主机挂载的旧配置
- ✨ 新增补偿机制模式（`open_supply`），用于控制是否开启补偿机制，当满足条件的结果数量不足时，将可能可用的接口补充到结果中
- ✨ 新增支持通过配置修改服务端口（`app_port`）
- ✨ 新增ghgo.xyz CDN代理加速
- ✨ config.ini配置文件新增注释说明（#704）
- ✨ 更新酒店源与组播源离线数据
- 🐛 修复IPv6接口测速异常低速率问题（#697、#713）
- 🐛 修复Sort接口可能出现的超时等待问题（#705、#719）
- 🐛 修复历史白名单结果导致移除白名单无效问题（#713）
- 🐛 修复订阅源白名单无效问题（#724）
- 🪄 优化更新时间url使用首个频道接口地址
- 🪄 优化接口来源偏好可设置为空，可实现全部来源按速率排序输出结果

<details>
  <summary>English</summary>

- ❤️ Recommended to follow the WeChat public account (Govin) to subscribe to update notifications and articles on usage
  tips, as well as for Q&A and discussion.
- ⚠️ This update involves configuration changes. Refer to the latest `config/config.ini`. Workflow users need to copy
  the latest configuration to `user_config.ini`, and Docker users need to clear the old configuration mounted on the
  host.
- ✨ Added compensation mechanism mode (`open_supply`) to control whether to enable the compensation mechanism. When the
  number of results meeting the conditions is insufficient, potentially available interfaces will be supplemented into
  the results.
- ✨ Added support for modifying the server port through configuration (`app_port`).
- ✨ Added ghgo.xyz CDN proxy acceleration.
- ✨ Added comments to the config.ini configuration file (#704).
- ✨ Updated offline data for hotel sources and multicast sources.
- 🐛 Fixed the issue of abnormally low speed rates for IPv6 interface speed tests (#697, #713).
- 🐛 Fixed the issue of possible timeout waiting in the Sort interface (#705, #719).
- 🐛 Fixed the issue where historical whitelist results caused the removal of the whitelist to be ineffective (#713).
- 🐛 Fixed the issue where the subscription source whitelist was ineffective (#724).
- 🪄 Optimized the update time URL to use the first channel interface address.
- 🪄 Optimized the interface source preference to be set to empty, allowing all sources to be sorted by speed for output
  results.

</details>

## v1.5.6

### 2024/12/17

- ❤️ 推荐关注微信公众号（Govin），订阅更新通知与使用技巧等文章推送，还可进行答疑和交流讨论
- ⚠️ 本次更新涉及配置变更，以最新 `config/config.ini` 为准，工作流用户需复制最新配置至`user_config.ini`
- ✨ 新增白名单列表功能，支持自定义接口和订阅源关键字白名单，文件位于`config/whitelist.txt`，工作流用户为了避免冲突覆盖，建议文件重命名添加
  `user_`前缀（#584,#599）
- ✨ 新增黑名单列表功能，支持接口关键字黑名单，文件位于`config/blacklist.txt`，工作流用户为了避免冲突覆盖，建议文件重命名添加
  `user_`前缀
- ✨ 新增订阅源列表功能，文件位于`config/subscribe.txt`，工作流用户为了避免冲突覆盖，建议文件重命名添加`user_`前缀
- ✨ 新增支持获取接口速率、最低速率过滤（`open_filter_speed`、`min_speed`）
- ✨ 新增支持修改Docker服务端口环境变量（`APP_PORT`）（#619）
- ✨ 新增jsdelivr代理地址，支持TLSv1.1 和 TLSv1.2 协议（#639）
- ✨ 新增离线数据和网络数据查询开关（`open_use_cache`, `open_request`）
- ✨ 新增控制是否使用离线数据和网络数据查询（`open_use_cache`、`open_request`）
- ✨ 新增支持跳过检查是否支持ipv6（`ipv6_support`）
- ✨ 调整GUI界面布局，新增测速设置页面，跳转编辑白/黑名单、订阅源列表文本
- 🐛 修复部分m3u8接口测速导致任务超时（#621）
- 🐛 修复GUI日志线程占用问题（#655）
- 🐛 补充显示更新时间配置文档（#622）
- 🪄 优化接口测速方法，移除`yt-dlp`（#621）
- 🗑️ 移除配置：`open_ffmpeg`、`subscribe_urls`、`resolution_weight`、`response_time_weight`、`url_keywords_blacklist`

<details>
  <summary>English</summary>

- ❤️ Recommend following the WeChat public account (Govin) to subscribe to update notifications and articles on usage
  tips, as well as for Q&A and discussion.
- ⚠️ This update involves configuration changes. Refer to the latest `config/config.ini`. Workflow users need to copy
  the latest configuration to `user_config.ini`.
- ✨ Added whitelist feature, supporting custom interface and subscription source keyword whitelists. The file is located
  at `config/whitelist.txt`. To avoid conflict, workflow users are advised to rename the file with a `user_` prefix (
  #584, #599).
- ✨ Added blacklist feature, supporting interface keyword blacklists. The file is located at `config/blacklist.txt`. To
  avoid conflict, workflow users are advised to rename the file with a `user_` prefix.
- ✨ Added subscription source list feature. The file is located at `config/subscribe.txt`. To avoid conflict, workflow
  users are advised to rename the file with a `user_` prefix.
- ✨ Added support for fetching interface speed and minimum speed filtering (`open_filter_speed`, `min_speed`).
- ✨ Added support for modifying Docker server port environment variable (`APP_PORT`) (#619).
- ✨ Added jsdelivr proxy address, supporting TLSv1.1 and TLSv1.2 protocols (#639).
- ✨ Added switches for offline data and network data queries (`open_use_cache`, `open_request`).
- ✨ Added control for whether to use offline data and network data queries (`open_use_cache`, `open_request`).
- ✨ Added support for skipping the check for IPv6 support (`ipv6_support`).
- ✨ Adjusted GUI layout, added speed test settings page, and links to edit whitelist/blacklist and subscription source
  list text files.
- 🐛 Fixed issue where some m3u8 interface speed tests caused task timeouts (#621).
- 🐛 Fixed GUI log thread occupation issue (#655).
- 🐛 Added display of update time in configuration documentation (#622).
- 🪄 Optimized interface speed test method, removed `yt-dlp` (#621).
- 🗑️ Removed configurations: `open_ffmpeg`, `subscribe_urls`, `resolution_weight`, `response_time_weight`,
  `url_keywords_blacklist`.

</details>

## v1.5.5

### 2024/12/2

- ✨ 增加部分订阅源，移除失效源
- 🐛 调整github代理地址，解决访问失效（#603）
- 🐛 修复GUI测速阶段重复弹出窗口问题（#600）
- 🐛 修正宁夏/青海模板频道（#594）
- 🐛 修复IPv6结果为空问题
- 🪄 优化Docker测速CPU占用问题（#606）
- 🛠 调整部分默认配置

<details>
  <summary>English</summary>

- ✨ Added some subscription sources, removed invalid sources
- 🐛 Adjusted GitHub proxy address to fix access failure (#603)
- 🐛 Fixed repeated pop-up window issue during GUI speed test phase (#600)
- 🐛 Corrected Ningxia/Qinghai template channels (#594)
- 🐛 Fixed issue with empty IPv6 results
- 🪄 Optimized Docker speed test CPU usage (#606)
- 🛠 Adjusted some default configurations

</details>

## v1.5.4

### 2024/11/29

- ⚠️ Python 升级至 3.13，该版本已不支持 Win7，若有需要请使用 v1.5.3
- ⚠️ Github 仓库改名：iptv-api，使用旧接口地址请及时更换新地址
- ⚠️ Docker 新镜像仓库启用：guovern/iptv-api（旧版的 tv-driver 改为：guovern/iptv-api:latest，tv-requests 改为
  guovern/iptv-api:lite），iptv-api:latest 为完整版、iptv-api:lite 为精简版，请使用新的名称命令进行拉取，旧仓库将不再维护
- ❤️ 新增微信公众号关注途径（公众号搜索：Govin），推荐关注公众号，可订阅更新通知与使用技巧等文章推送，还可进行交流讨论
- ✨ 更换测速方法（yt-dlp），重构测速逻辑，提升准确性、稳定性与效率，减小接口切换延迟（#563）
- ✨ 新增支持 ARM v7（#562）
- ✨ 新增双结果 API 访问（ip/m3u, ip/txt）（#581）
- ✨ 新增启动 API 服务命令（pipenv run service）
- 🪄 优化 Docker 镜像大小（完整版：-25%，精简版：-66%）
- 🐛 修复部分播放器不支持的信息间隔符（#581）

<details>
  <summary>English</summary>

- ⚠️ Python has been upgraded to version 3.13, which no longer supports Win7. If needed, please use version v1.5.3.
- ⚠️ The GitHub repository has been renamed to iptv-api. If you are using the old API address, please update it to the
  new one promptly.
- ⚠️ New Docker image repository is now active: guovern/iptv-api (the old tv-driver is now guovern/iptv-api:latest, and
  tv-requests is now guovern/iptv-api:lite). iptv-api:latest is the full version, and iptv-api:lite is the lightweight
  version. Please use the new names to pull the images, as the old repository will no longer be maintained.
- ❤️ A new way to follow the WeChat official account (search for: Govin) has been added. It is recommended to follow the
  official account to subscribe to update notifications, usage tips, and engage in discussions.
- ✨ The speed measurement method has been changed to yt-dlp, and the speed measurement logic has been refactored to
  improve accuracy, stability, and efficiency, reducing interface switching delay (#563).
- ✨ Support for ARM v7 has been added (#562).
- ✨ Dual result API access (ip/m3u, ip/txt) has been added (#581).
- ✨ A command to start the API service (pipenv run service) has been added.
- 🪄 The size of the Docker image has been optimized (Full version: -25%, Lite version: -66%).
- 🐛 Fixed the information delimiter issue for some players that do not support it (#581).

</details>

## v1.5.3

### 2024/11/19

⚠️ 这将是支持 Win7 的最后一个版本

- 🐛 修复 GUI “显示无结果分类”设置后保存失败（#564）
- 🐛 修复命令行启动报错 (#567）

<details>
  <summary>English</summary>

⚠️ This will be the last version supporting Win7

- 🐛 Fixed the issue where the GUI setting for "Display No Results Category" failed to save (#564).
- 🐛 Fixed the error when starting from the command line (#567).

</details>

## v1.5.2

### 2024/11/15

- ✨ 新增各省份地方台
- ✨ 新增控制显示无结果频道分类配置（open_empty_category）（#551）
- ✨ 调整接口源（#526）
- 🪄 优化频道数据插入速度
- 🪄 优化 IPv6 测速逻辑，解决无结果问题
- 🪄 优化页面服务启动与 docker 定时任务日志输出
- 🪄 调整默认配置：接口数量 urls_limit=10 等数量配置，增加订阅源
- 🐛 修复运行停止问题（#527）
- 🐛 修复 Win7 GUI 启动问题（#536）
- 🗑️ 移除部分无效订阅源
- 🗑️ 移除域名黑名单配置（domain_blacklist），请使用接口关键字黑名单（url_keywords_blacklist）替代

<details>
  <summary>English</summary>

- ✨ Added local channels for each province.
- ✨ Added configuration to control the display of the No Results Channel Category (open_empty_category) (#551).
- ✨ Adjusted interface sources (#526).
- 🪄 Optimized the speed of channel data insertion.
- 🪄 Optimized IPv6 speed test logic to resolve no results issues.
- 🪄 Optimized page service startup and Docker scheduled task log output.
- 🪄 Adjusted default configurations: number of interfaces urls_limit=10, etc., and added subscription sources.
- 🐛 Fixed the issue of the program stopping (#527).
- 🐛 Fixed the issue of Win7 GUI startup (#536).
- 🗑️ Removed some invalid subscription sources.
- 🗑️ Removed the domain blacklist configuration (domain_blacklist). Please use the interface keyword blacklist (
  url_keywords_blacklist) instead.

</details>

## v1.5.1

### 2024/11/5

- ✨ 新增频道接口白名单：不参与测速，永远保留在结果最前面（#470）
  使用方法：
    1. 模板频道接口地址后添加$!即可实现（如：广东珠江,http://xxx.m3u$! ）
    2. 额外信息补充（如：广东珠江,http://xxx.m3u$!额外信息 ），更多接口白名单请至https:
       //github.com/Guovin/iptv-api/issues/514 讨论
- ✨ 新增 🈳 无结果频道分类：无结果频道默认归类至该底部分类下（#473）
- ✨ 接口地址增加来源类型说明
- ✨ 默认模板增加广东民生（#481）、广州综合（#504）
- 🪄 优化偏好结果输出
- 🪄 重构配置读取与增加全局常量
- 🐛 修复部分接口匹配失败问题
- 🐛 修复更新结果为空等问题（#464，#467）
- 🐛 修复接口地址复制空格问题（#472 by:@haohaitao）
- 🐛 修复结果日志 unpack error
- 🐛 修复结果接口信息为空问题（#505）
- 🗑️ 移除仓库根目录 txt 结果文件，请至 output 目录下查看结果文件

<details>
  <summary>English</summary>

- ✨ Added channel interface whitelist: Not participating in speed testing, always kept at the very front of the
  results. (#470)
  Usage:
    1. Add $! after the template channel interface address (e.g., Guangdong Pearl River, http://xxx.m3u$!).
    2. Additional information can be appended (e.g., Guangdong Pearl River, http://xxx.m3u$! Additional Information) (
       #470). For more interface whitelists, please discuss at https://github.com/Guovin/iptv-api/issues/514.
- ✨ Added 🈳 No Results Channel Category: Channels without results are categorized under this bottom category by
  default (#473).
- ✨ Interface addresses now include source type descriptions.
- ✨ Default templates now include Guangdong People's Livelihood (#481) and Guangzhou Comprehensive (#504).
- 🪄 Optimized preferred result output.
- 🪄 Refactored configuration reading and added global constants.
- 🐛 Fixed issues with partial interface matching failures.
- 🐛 Fixed problems with empty update results, etc. (#464, #467).
- 🐛 Fixed the issue of spaces being copied with the interface address (#472 by:@haohaitao).
- 🐛 Fixed the unpack error in result logs.
- 🐛 Fixed the issue of empty interface information in results (#505).
- 🗑️ Removed txt result files from the repository root directory. Please check the result files in the output directory.

</details>

## v1.5.0

### 2024/10/25

- ✨🛠 新增结果偏好设置：

    1. 接口来源优先级（origin_type_prefer）与数量设置（hotel_num, multicast_num, subscribe_num, online_search_num）
    2. IPv 类型优先级（ipv_type_prefer）与数量设置（ipv4_num, ipv6_num）

- ✨🛠 新增控制接口测速超时时间（sort_timeout）（#388）
- ✨🛠 新增控制是否开启页面服务（open_service）（青龙等平台可使用该配置实现任务执行完成后停止运行）
- ✨🛠 新增控制是否显示接口相关信息（open_url_info）（#431）
- ✨ 新增支持 m3u 地址订阅源（#389）
- ✨ 新增 🏛 经典剧场
- 🪄 优化 Docker ARM64 FFmpeg 支持（部分 ARM 设备无法运行 driver 镜像建议使用 requests 镜像）
- 🪄 优化组播获取非数值域名 ip 地址（#410）
- 🪄 优化使用旧配置文件时可能出现的新参数不存在报错问题，使用默认值
- 🐛 修复对于非规范 txt 文本转换 m3u 报错问题（#422）
- 🐛 修复 IPv6 接口获取失败问题（#452）

<details>
  <summary>English</summary>

- ✨🛠 Added result preference settings:
    1. Source priority (origin_type_prefer) and quantity settings (hotel_num, multicast_num, subscribe_num,
       online_search_num)
    2. IPv type priority (ipv_type_prefer) and quantity settings (ipv4_num, ipv6_num)
- ✨🛠 Added control for API speed test timeout (sort_timeout) (#388)
- ✨🛠 Added control to enable or disable page service (open_service) (this configuration can be used on platforms like
  QingLong to stop running after task completion)
- ✨🛠 Added control to show or hide API related information (open_url_info) (#431)
- ✨ Added support for m3u address subscription sources (#389)
- ✨ Added 🏛 Classic Theater
- 🪄 Optimized Docker ARM64 FFmpeg support (it is recommended to use the requests image for some ARM devices that cannot
  run the driver image)
- 🪄 Optimized obtaining non-numeric domain IP addresses for multicast (#410)
- 🪄 Optimize the issue of non-existent new parameters when using old configuration files, use default values
- 🐛 Fixed issues with converting non-standard txt files to m3u format (#422)
- 🐛 Fixed issues with failing to obtain IPv6 interface information (#452)

</details>

## v1.4.9

### 2024/10/11

- 注意：本次更新涉及配置变更，请以最新 config/config.ini 为准，工作流使用 user_config.ini 或 docker 挂载的用户请及时更新配置文件
- 新增支持 docker arm64 镜像（#369）
- 新增分辨率过滤功能（相关配置：open_filter_resolution，min_resolution）
- 新增显示更新时间（相关配置：open_update_time）
- 优化测速效率（#359）
- 优化权重值选择交互
- 调整默认模板，增加默认订阅源
- 移除央视台球部分错误组播地址
- 更新使用教程

- Warning: This update involves configuration changes. Please refer to the latest config.ini. Users of workflow using
  user_config.ini or Docker mounted configurations should update their configuration files promptly
- Add support for Docker ARM64 images (#369)
- Add resolution filtering feature (related configurations: open_filter_resolution, min_resolution)
- Add display of update time (related configuration: open_update_time)
- Optimize speed testing efficiency (#359)
- Optimize weight value selection interaction
- Adjust the default template and add default subscription sources
- Remove the incorrect multicast addresses for the CCTV Snooker section
- Update usage guide

## v1.4.8

### 2024/09/27

- 默认模板增加部分频道：咪咕直播、央视付费频道、电影频道、港澳台、地方频道等
- 订阅源增加默认订阅地址
- 优化订阅源、在线搜索测速效率
- 增加汕头频道组播
- 调整默认接口数量为 30

- Add some channels to the default template: Migu Live, CCTV Pay Channels, Movie Channel, Hong Kong and Macau Channels,
  Local Channels, etc
- Add default subscription addresses to the subscription source
- Optimize the efficiency of subscription source and online search speed tests
- Add Shantou channel multicast
- Adjust the default number of interfaces to 30

## v1.4.7

### 2024/09/26

- 修复部分设备本地运行软件 driver 问题(#335)
- 修复 driver 模式下新版谷歌浏览器白屏问题
- 增加历史结果缓存(result_cache.pkl)，用于测速优化
- 重构测速方法，提升测速效率
- 优化测速进度条显示

- Fix some issues with local software driver operation on certain devices (#335)
- Fix the white screen issue with the new version of Google Chrome in driver mode
- Add historical result cache (result_cache.pkl) for performance optimization
- Refactor speed test methods to improve efficiency
- Optimize speed test progress bar display

## v1.4.6

### 2024/9/20

- 优化 IPv6 测试是否支持(#328)
- 优化 404 类接口测速(#329)

- Optimize IPv6 test support (#328)
- Optimize 404 class interface speed test (#329)

## v1.4.5

### 2024/9/19

- 修复 IPv6 接口测速(#325)

- Fix IPv6 Interface Speed Test (#325)

## v1.4.4

### 2024/9/14

- 修复组播接口测速可能出现结果频道分类空的问题
- 修复使用历史更新结果时可能出现模板不存在的频道问题
- 更新 FOFA 组播、酒店缓存
- 更新默认模板(demo.txt)内容
- 更新使用教程

- Fix the issue where multicast interface speed test may result in an empty channel category
- Fix the issue where channels may appear missing when updating results with history
- Update FOFA multicast and hotel cache
- Update default template (demo.txt) content
- Update user guide

## v1.4.3

### 2024/9/11

- 修正 RTP 文件：贵州电信文件错误，第一财经、东方财经等频道命名，地址错误

- Fixed RTP files: Corrected errors in Guizhou Telecom files, including naming and address errors for channels such as
  First Financial and Oriental Financial

## v1.4.2

### 2024/9/10

- 新增内蒙古、甘肃、海南、云南地区
- 更新 FOFA 酒店、组播缓存
- 更新组播 RTP 文件
- 优化测速过滤无效接口
- 增加接口域名黑名单，避免频道花屏情况
- 修复 FOFA requests 模式请求失败导致程序中止问题

- Added Inner Mongolia, Gansu, Hainan, and Yunnan regions
- Updated FOFA hotels and multicast cache
- Updated multicast RTP files
- Optimize speed test to filter out invalid interfaces
- Add interface domain name blacklist to avoid channel screen distortion
- Fix issue where FOFA requests mode failure leads to program termination

## v1.4.1

### 2024/9/9

- 新增 FOFA 缓存，解决访问限制问题
- 修复 CCTV-5+等频道 M3U 转换问题（#301）
- 优化频道匹配问题
- 优化地区选择空格情况

- Added FOFA cache to address access restrictions
- Fixed M3U conversion issues for channels like CCTV-5+ (#301)
- Optimized channel matching issues
- Improved handling of spaces in region selection

## v1.4.0

### 2024/9/5

- 注意：本次更新涉及配置变更，请以最新 config/config.ini 为准，工作流使用 user_config.ini 或 docker 挂载的用户请及时更新配置文件
- 新增组播源运行模式：FOFA、Tonkiang
- 新增支持组播源自定义维护频道 IP，目录位于 config/rtp，文件按“地区\_运营商”命名
- 优化测速方法，大幅提升组播源、酒店源的测速速度
- 优化频道名称匹配方法，支持模糊匹配，提高命中率
- 优化地区输入选择框
- 修复 driver 模式请求问题
- 修复组播地区选择全部时无法运行问题
- 修复工作流使用 user_config 时无法生成 m3u 结果问题

- Warning: This update involves configuration changes. Please refer to the latest config/config.ini. Users using
  user_config.ini or Docker-mounted configurations should update their configuration files promptly.
- Added multicast source operation modes: FOFA, Tonkiang.
- Added support for custom-maintained multicast source channel IPs, located in config/rtp, with files named by "
  region_operator".
- Optimized speed test method, significantly improving the speed test of multicast sources and hotel sources.
- Optimized channel name matching method to support fuzzy matching, increasing hit rate.
- Optimized region input selection box.
- Fixed an issue with driver mode requests.
- Fixed an issue where multicast would not run when all regions were selected.
- Fixed an issue where workflows using user_config could not generate m3u results.

## v1.3.9

### 2024/8/30

- 酒店源新增 ZoomEye 数据源，开启 FOFA 配置即可使用（Added ZoomEye data source to hotel sources, can be used by enabling
  FOFA configuration）
- 酒店源、组播源地区选项增加“全部”选项（Added "all" option to the region selection for hotel sources and multicast
  sources）
- 调整默认运行配置：关闭订阅源更新、Tonkiang 酒店源更新（Adjusted default runtime configuration: disabled subscription
  source updates and Tonkiang hotel source updates）

## v1.3.8

### 2024/8/29

- 更新组播地区 IP 缓存数据（Update multicast area IP cache data）
- 移除 source_channels 配置项（Remove source_channels configuration item）
- 优化模板频道名称匹配（Optimize template channel name matching）
- 优化进度条，显示接口处理进度（Optimize the progress bar to display the interface processing progress）
- UI 软件增加部分图标（Add some icons to the UI software）

## v1.3.7

### 2024/8/27

- 新增支持 M3U 结果格式转换，支持显示频道图标(open_m3u_result)（Added support for M3U result format conversion, including
  channel icon display (open_m3u_result)）
- 新增对于无结果的频道进行额外补充查询（Added additional queries for channels with no results）
- 增加控制使用 FFmpeg 开关(open_ffmpeg)（Added a switch to control the use of FFmpeg (open_ffmpeg)）
- 调整默认配置以酒店源模式运行（Adjusted default configuration to run in hotel source mode）
- 优化测速方法（Optimize Speed Test Method）
- 修复酒店源 CCTV 类等频道结果匹配异常（Fixed abnormal matching of results for hotel source CCTV channels）
- 修复组播源、酒店源 driver 运行问题（Fixed issues with multicast source and hotel source driver operation）
- 修复订阅源更新异常（Fixed subscription source update anomalies）

## v1.3.6

### 2024/8/22

- 新增酒店源更新，支持 Tonkiang、FOFA 两种工作模式（Added hotel source updates, supporting Tonkiang and FOFA working modes）
- 重构 UI 界面软件，新增帮助-关于、获取频道名称编辑、酒店源相关配置、软件图标（Refactored UI interface software, added
  Help-About, channel name editing, hotel source related configuration, and software icon）
- 新增测速日志页面服务，结果链接后添加/log 即可查看（Added a new speed test log page service. To view the results, simply
  add /log to the link）
- 移除关注频道相关配置（Removed configuration related to followed channels）
- 修复 Docker 定时任务未执行问题（Fixed issue with Docker scheduled tasks not executing）
- 修复使用历史结果时频道数据异常问题（Fixed issue with channel data anomalies when using historical results）
- 优化 UI 界面软件运行生成配置目录，方便查看与修改（Optimized UI interface software to generate configuration directory
  for easier viewing and modification）

## v1.3.5

### 2024/8/14

- 新增支持地区组播 ip 更新，调整默认以此模式运行，基本实现高清流畅播放（#225）（Added support for updating multicast IP for
  new regions and adjusted the default to run in this mode, basically achieving high-definition smooth playback (#225)）
- 新增支持使用 FFmpeg 进行测速排序、获取分辨率信息，本地运行请手动安装 FFmpeg（Added support for speed sorting and
  resolution information using FFmpeg. Manually install FFmpeg when running locally）
- 接口源增加分辨率信息，用于源切换时显示（Added resolution information to the interface source for display during source
  switching）
- 调整配置文件与结果文件路径（config、output 目录），方便 docker 卷挂载（#226）（Adjusted the paths for configuration and
  result files (config, output directories) to facilitate Docker volume mounting (#226)）
- 修改配置文件类型（config.ini）（Modified the configuration file type (config.ini)）

## v1.3.4

### 2024/7/31

- 新增配置 open_use_old_result：保留使用历史更新结果，合并至本次更新中（Add configuration open_use_old_result: Keep using
  the previous update results and merge them into the current update）
- 新增配置 open_keep_all：保留所有检索结果，推荐手动维护时开启（#121）（Add configuration open_keep_all: Keep all search
  results, recommend enabling it for manual maintenance (#121)）

## v1.3.3

### 2024/7/19

- 支持 Docker 卷挂载目录映射（Support for Docker volume mount directory mapping）
- 新增 requests 随机 User-Agent（Added random User-Agent for requests）
- 修复读取用户配置问题（#208）（Fixed issue with reading user configuration (#208)）
- 支持单日更新两次：6 点与 18 点（Supports updating twice a day: at 6 AM and 6 PM）

## v1.3.2

### 2024/7/10

- 新增支持频道名称简体繁体匹配（Added support for channel name Simplified and Traditional Chinese match）
- 新增 Docker 修改模板与配置教程（Added Docker modification template and configuration tutorial）
- 修复频道更新结果为空问题（Fixed the issue where channel update result is empty）

## v1.3.1

### 2024/7/9

- 重构代码，模块拆分，优化 CPU/内存占用（Refactor code, modular decomposition, optimize CPU/memory usage）
- 新增两种工作模式：driver 模式、requests 模式，具体差异见文档说明（Add two new working modes: driver mode and requests
  mode, see documentation for specific differences）
- 调整软件界面，功能分类摆放，增加配置：开启更新、开启浏览器模式、开启代理（Adjust the software interface, arrange features by
  category, add configurations: enable updates, enable browser mode, enable proxy）
- 调整工作流更新时间为北京时间每日 6:00（Adjust workflow update time to 6:00 AM Beijing time daily）
- Docker 镜像增加两种工作模式版本（Docker image adds two new working mode versions）

## v1.3.0

### 2024/7/1

- 新增更新结果页面服务（ip:8000）（Add new update results page service (ip:8000)）
- 新增支持 Docker 运行，并支持定时自动更新（Added support for Docker running and automatic updates）
- 修复在线查询更新，增加随机代理、失败重试，提高获取结果成功率（Fixed online query update, added random proxy, increased
  failure retry, and improved the success rate of getting results）
- 更换使用阿里云镜像源（Switched to use Alibaba Cloud mirror source）
- 增加更新开关配置：open_update（Add update switch configuration: open_update）
- 更新说明文档（Update documentation）

## v1.2.4

### 2024/6/21

- 优化排序执行逻辑（Optimize the sorting execution logic）
- 优化超时重试方法（Optimize the timeout retry method）
- 调整默认配置 open_sort：关闭工作流测速排序，建议本地运行更准确（Adjust the default configuration open_sort: turn off the
  workflow speed test sorting, local execution is recommended for more accurate results）

## v1.2.3

### 2024/6/17

- 新增请求重连重试功能（Added request reconnection retry function）
- 修复个别系统环境文件路径报错问题（Fixed some system environment file path errors）

## v1.2.2

### 2024/6/16

- 优化在线查询更新速度与修复无更新结果情况（Optimize online query update speed and fix no update result situation）
- 解决个别环境运行更新报错（Solved the problem of running updates in some environments）

## v1.2.1

### 2024/6/15

- 兼容 Win7 系统，请使用 Python 版本>=3.8（Compatible with Windows 7 system, please use Python version >= 3.8）
- 修复部分设备运行更新报错（Fixed an error that occurred when some devices ran updates）
- 修复工作流更新错误（Fixed an error in the workflow update）
- 新增捐赠途径（主页底部），本项目完全免费，维护不易，若对您有帮助，可选择捐赠（Add new donation channels (bottom of the
  homepage), this project is completely free, maintenance is not easy, if it helps you, you can choose to donate）

## v1.2.0

### 2024/6/9

- 异步并发、多线程支持，大幅提升更新速度（近 10 倍）（Asynchronous concurrency and multi-threading support, significantly
  increasing update speeds (nearly 10 times faster)）
- 新增更新工具软件（release 附件:update-tool.exe），首个版本可能会有不可预见的问题，请见谅（Added new update tool software (
  release attachment: update-tool.exe); the first version may have unforeseen issues, please be understanding）

## v1.1.6

### 2024/5/17

- 增加组播源可全地区运行更新（Added multicast sources to run region-wide updates）
- 修改默认值：关闭在线检索功能，组播源全地区更新（Change the default value: Disable the online search function and update
  the multicast source in all regions）

## v1.1.5

### 2024/5/17

- 增加模糊匹配规则，适配在线检索、订阅源、组播源（Add fuzzy matching rules for online search, subscription sources, and
  multicast sources）
- 增加订阅源、组播源更新进度条（Added the update progress bar for subscription sources and multicast sources）
- 优化组播源更新可能出现的无匹配结果情况（Optimize the possible situation of no match results in multicast source
  updates）
- 移除部分错误日志打印（Removes some error log prints）
- 移除严格匹配配置（Removes strict matching configurations）

## v1.1.4

### 2024/5/15

- 新增组播源功能（Added multicast source feature）
- 新增控制开关，控制多种获取模式的启用状态（Added control switch to manage the activation status of various acquisition
  modes）
- 新增严格匹配（Added strict matching）
- 优化文件读取，提升模板初始化速度（Optimized file reading to improve initialization speed based on templates）

## v1.1.3

### 2024/5/8

- 优化频道接口不对应问题（#99）（Optimize the mismatch problem of the channel interface (#99)）
- 处理 tqdm 安全问题（Handle the security issue of tqdm）
- 修改即将被废弃的命令（Modify the commands that are about to be deprecated）

## v1.1.2

### 2024/5/7

- 重构接口获取方法，增强通用性，适应结构变更（Refactored the method for obtaining the interface, enhanced its universality,
  and adapted to structural changes）
- 修复 gd 分支自动更新问题（#105）（Fixed the automatic update issue of the gd branch (#105)）
- 优化自定义接口源获取，接口去重（Optimized the acquisition of custom interface sources and removed duplicate interfaces）

## v1.1.1

### 2024/4/29

- 为避免代码合并冲突，移除 master 分支作为运行更新工作流，master 仅作为新功能发布分支，有使用我的链接的小伙伴请修改使用 gd
  分支（void code merge conflicts, the master branch has been removed as the branch for running update workflows. The
  master branch is now only used for releasing new features. If you are using my link, please modify it to use the gd
  branch）

## v1.1.0

### 2024/4/26

- 新增自定义接口获取源，配置项为 extend_base_urls（#56）（Added custom interface for source acquisition, the configuration
  item is extend_base_urls (#56)）

## v1.0.9

### 2024/4/25

- 改进接口获取方法，增强处理多种失效场景（Improve the method of obtaining the interface, enhance the handling of various
  failure scenarios）

## v1.0.8

### 2024/4/24

- 跟进某个节点检索频道名称参数变更（#91）（Follow up on the parameter change of channel name retrieval for a certain node (
  #91)）
- 调整默认运行配置（Adjust the default running configuration）

## v1.0.7

### 2024/4/19

- 增加双节点接口来源，按最佳节点更新（Added dual-node interface source, update according to the best node）
- 优化频道更新结果为空的情况（#81）（Optimized the situation where the channel update result is empty (#81)）
- 调整工作流资源使用限制逻辑，在允许的范围内提升更新速度（Adjusted the logic of workflow resource usage limit, increase
  the update speed within the allowable range）

## v1.0.6

### 2024/4/12

- 恢复工作流更新，请谨慎合理使用，勿尝试更改默认运行参数，可能导致封禁的风险！首推使用本地更新（Workflow updates have been
  restored. Please use them carefully and do not attempt to change the default runtime parameters, as this may risk
  being banned! It is recommended to use local updates first.）
- 调整默认配置参数，降低单次更新运行时长（Adjusted the default configuration parameters to reduce the runtime of a single
  update.）
- 依赖版本锁定，解决可能出现的环境错误（#72）（Dependency versions have been locked to solve potential environmental
  errors (#72).）
- 优化逻辑与增加检测，避免网络异常占用工作流运行（Optimized logic and added checks to prevent network anomalies from
  occupying workflow operations.）

## v1.0.5

### 2024/4/10

- 移除工作流更新，鉴于有少数人反馈工作流甚至账号被封禁的情况，安全起见，只能暂时移除工作流更新机制，后续将增加其它平台部署方案（Removed
  workflow updates, in view of the feedback from a few people that their workflows and even accounts have been banned,
  for safety reasons, the workflow update mechanism can only be temporarily removed, and other platform deployment plans
  will be added in the future）
- 新增本地更新，同时移除更新频道个数限制，具体使用方法请见快速上手（Added local updates and removed the limit on the number
  of channel updates. For specific usage, please see the quick start guide）
- 适配提供方接口位置变更（Adapted to the change of the provider's interface location）

## v1.0.4

### 2024/4/8

- 更新 Github 使用条款，请务必仔细阅读并遵守（Updated GitHub Terms of Service, please read and comply carefully）
- 更新使用说明，关于可能导致工作流资源滥用的情况说明（Updated usage instructions, explanation about situations that may
  lead to workflow resource abuse）
- 增加.gitignore 文件，忽略用户配置、接口更新结果、日志文件等上传，非代码逻辑修改请不要发起 Pull requests，避免影响他人使用（Added
  .gitignore file to ignore uploads of user configurations, interface update results, log files, etc. Please do not
  initiate pull requests for non-code logic modifications to avoid affecting others' use）
- 调整更新频率，北京时间每日 8:00 执行一次（Adjusted update frequency, executes once daily at 8:00 am Beijing time）
- 调整更新频道数量上限（200 个）（Adjusted the maximum limit for updating channel numbers (200)）

## v1.0.3

### 2024/4/7

- 新增接口域名黑名单（Add interface domain blacklist）
- 新增接口关键字黑名单（Add interface keyword blacklist）
- 调整过滤逻辑执行顺序，提升工作流更新效率（Adjust the execution order of the filtering logic to improve workflow update
  efficiency）

## v1.0.2

### 2024/4/5

- 修复用户配置后接口更新结果与日志文件命名问题（Fix the issue of interface update results and log file naming after user
  configuration）

## v1.0.1

### 2024/4/1

- 适配接口提供方变更，调整接口链接与信息提取方法（Adapt to changes from the interface provider, adjust the interface link
  and information extraction method）

---

## v1.0.0

### 2024/3/30

- 修复工作流读取配置与更新文件对比问题（Fix the issue of workflow reading configuration and comparing updated files）

---

### 2024/3/29

- 修复用户专属配置更新结果失败（Fix user specific configuration update failure）

---

### 2024/3/26

- 新增快速上手-详细教程（Add a Quick Start - detailed tutorial）
- 新增以 releases 发布版本更新信息（Add release notes for version updates using releases）

---

### 2024/3/25

- 增加代码防覆盖，用户可使用 user\_作为文件前缀以区分独有配置，可避免在合并更新时本地代码被上游仓库代码覆盖，如
  user_config.py、user_demo.txt、user_result.txt（Add code anti-overwriting. Users can use user\_ as the file prefix to
  distinguish unique configurations. This prevents local codes from being overwritten by upstream repository codes, such
  as user_config.py, user_demo.txt, and user_result.txt, when merging updates）

---

### 2024/3/21

- 修复潜在的更新文件追踪失效，导致更新失败（Fixed potential tracking failure of updated files, leading to update failure）
- 调整最近更新获取时间默认为 30 天（Adjusted the default recent update retrieval time to 30 days）
- 优化最近更新接口筛选，当筛选后不足指定接口个数时，将使用其它时间范围的可用接口补充（Optimized the recent update interface
  filter, when the number of interfaces is insufficient after filtering, other time range available interfaces will be
  used for supplementation）
- 优化珠江、CCTV 频道匹配问题（Optimized the matching problem of Zhujiang and CCTV channels）
- 移除推送实时触发更新（Removed push real-time trigger update）

---

### 2024/3/18

- 新增配置项：ipv_type，用于过滤 ipv4、ipv6 接口类型（Added configuration item: ipv_type, used to filter ipv4, ipv6
  interface types）
- 优化文件更新逻辑，避免更新失效引起文件丢失（Optimized file update logic to prevent file loss caused by update failure）
- 调整分页获取默认值：关注频道获取 6 页，常规频道获取 4 页，以提升更新速度（Adjusted the default value for pagination: fetch
  6 pages for followed channels, 4 pages for regular channels, to improve update speed）
- 增加接口日志文件 result.log 输出（Added output of interface log file result.log）
- 修复权重排序异常（Fixed weight sorting anomaly）

---

### 2024/3/15

- 优化代码结构（Optimize code structure）
- 新增接口日志，记录详细质量指标（Added interface logs to record detailed quality indicators）
- 新增可手动运行工作流触发更新（Added manual workflows to trigger updates）

---

### 2024/3/13

- 增加配置项：recent_days，筛选获取最近时间范围内更新的接口，默认最近 60 天（Added configuration item: recent_days, a filter
  to get the most recently updated interfaces, default to the last 60 days）
- 调整默认值：关注频道获取 8 页，常规频道获取 5 页（Adjusted default values: fetch 8 pages for followed channels, 5 pages
  for regular channels）

---

### 2024/3/6

- 更新文件代理说明（Update file proxy description）

---

### 2024/3/4

- 增加配置项：响应时间与分辨率权重值（Added configuration items: response time and resolution weight values）
- 移除配置项：是否过滤无效接口，始终执行过滤（Removed configuration items: whether to filter invalid interfaces, always
  perform filtering）
- 移除按日期排序，采用响应时间与分辨率作为排序规则（Removed sorting by date, using response time and resolution as sorting
  rules）
- 更新 README：增加修改更新频率、文件代理说明、更新日志（Updated README: added modification update frequency, file proxy
  description, update log）
