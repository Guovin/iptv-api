<div align="center">
  <img src="./static/images/logo.png" alt="logo"/>
  <h1 align="center">IPTV-API</h1>
</div>

📺 IPTV live-source auto-update platform — 🤖 fully automated collection, filtering, speed-testing, and generation
pipeline 🚀. Supports extensive customization; paste the resulting URL into your player to watch

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

[中文](./README.md) | English

</div>

🎉💻 [IPTV-Web](https://github.com/Guovin/iptv-web): IPTV live stream management platform, supports online playback and
other features, under development...

💖 [Channel Alias Collection Plan](https://github.com/Guovin/iptv-api/discussions/1082)

- [✅ Core Features](#core-features)
- [🔗 Latest results](#latest-results)
- [⚙️ Config parameter](#Config)
- [🚀 Quick Start](#quick-start)
    - [Configuration and Results Directory](#configuration-and-results-directory)
    - [Workflow](#workflow)
    - [Command Line](#command-line)
    - [GUI Software](#gui-software)
    - [Docker](#docker)
- [📖 Detailed Tutorial](./docs/tutorial_en.md)
- [🗓️ Changelog](./CHANGELOG.md)
- [❤️ Donations](#donations)
- [👀 Follow](#follow)
- [⭐️ Star History](#star-history)
- [📣 Disclaimer](#disclaimer)
- [⚖️ License](#license)

> [!IMPORTANT]
> 1. The default data sources, such as subscription sources, come from open-source projects on GitHub and are for
     demonstration purposes only. They may have stability issues.
> 2. This project does not guarantee or explain the stability of the interface results.
> 3. To achieve optimal stability, it is recommended to maintain the data sources yourself.

<details>
  <summary>Default Data Sources</summary>

📍Subscription sources are from:

- [Guovin/iptv-database](https://github.com/Guovin/iptv-database)
- [iptv-org/iptv](https://github.com/iptv-org/iptv)
- [suxuang/myIPTV](https://github.com/suxuang/myIPTV)
- [kimwang1978/collect-tv-txt](https://github.com/kimwang1978/collect-tv-txt)
- [vbskycn/iptv](https://github.com/vbskycn/iptv)

📍Channel icons are from:

- [fanmingming/live](https://github.com/fanmingming/live)

</details>

## Core Features

| Feature                               | Status | Description                                                                                                                         |
|:--------------------------------------|:------:|:------------------------------------------------------------------------------------------------------------------------------------|
| **Custom Templates**                  |   ✅    | Generate personalized channels as you wish                                                                                          |
| **Channel Alias**                     |   ✅    | Improves channel result coverage and accuracy, supports regular expressions                                                         |
| **Multiple Source Types**             |   ✅    | Supports local sources, multicast, hotel sources, subscriptions, and keyword search                                                 |
| **RTMP streaming**                    |   ✅    | Supports HLS mode (segmented / adaptive bitrate), improves compatibility and reduces buffering, enhancing playback on weak networks |
| **Playback Interfaces**               |   ✅    | Supports acquisition and generation of playback interfaces                                                                          |
| **EPG (Electronic Program Guide)**    |   ✅    | Displays channel preview content                                                                                                    |
| **Channel Logo**                      |   ✅    | Supports custom channel logo library sources                                                                                        |
| **Interface Speed Test & Validation** |   ✅    | Measures latency, speed, resolution, and filters invalid interfaces                                                                 |
| **Advanced Preferences**              |   ✅    | IPv4/IPv6, interface sorting priority, quantity configuration, blacklist/whitelist, region & ISP filtering                          |
| **Scheduled Tasks**                   |   ✅    | Automatically updates at 6:00 and 18:00 Beijing time daily by default; customizable schedule                                        |
| **Multiple Run Modes**                |   ✅    | Supports workflow, CLI, GUI software, Docker (amd64/arm64/arm v7)                                                                   |
| **More Features**                     |   ✨    | See [Configuration Parameters](#Config) section for details                                                                         |

## Latest results

> [!IMPORTANT]\
> The following addresses may not be stable for access within China. It is recommended to prepend a proxy address for
> use. You can reply with `cdn` in the public account to obtain it.

### Live Sources

- Default

```bash
https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u
```

- IPv6

```bash
https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/ipv6/result.m3u
```

- IPv4

```bash
https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/ipv4/result.m3u
```

### VOD source

```bash
https://raw.githubusercontent.com/Guovin/iptv-api/gd/source.json
```

## Config

> [!NOTE]\
> The following configuration items are located in `config/config.ini` and can be modified via the configuration file or
> environment variables. Save changes and restart to apply.

| Configuration Item     | Description                                                                                                                                                                                                                                                                                                                                                          | Default Value     |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------|
| open_update            | Enable updates, used to control whether to update interfaces. If disabled, all working modes (getting interfaces and speed tests) stop.                                                                                                                                                                                                                              | True              |
| open_empty_category    | Enable empty category, channels without results will automatically be classified to the bottom.                                                                                                                                                                                                                                                                      | False             |
| open_update_time       | Enable display of update time.                                                                                                                                                                                                                                                                                                                                       | True              |
| open_url_info          | Enable to display interface description information, used to control whether to display interface source, resolution, protocol type and other information (content after `$`). The player uses this information to describe the interface. If some players (such as PotPlayer) do not support parsing and cannot play, you can turn it off.                          | False             |
| open_epg               | Enable EPG function, support channel display preview content.                                                                                                                                                                                                                                                                                                        | True              |
| open_m3u_result        | Enable converting and generating m3u file type result links, supporting the display of channel icons.                                                                                                                                                                                                                                                                | True              |
| urls_limit             | Number of interfaces per channel.                                                                                                                                                                                                                                                                                                                                    | 10                |
| update_time_position   | Update time display position, takes effect only when `open_update_time` is enabled. Optional values: `top`, `bottom`. `top`: display at the top of the result, `bottom`: display at the bottom.                                                                                                                                                                      | top               |
| language               | Application language setting; Optional values: zh_CN, en                                                                                                                                                                                                                                                                                                             | zh_CN             |
| update_mode            | Scheduled execution update mode, does not apply to workflow; Optional values: interval, time; interval: execute by interval time, time: execute at specified time point                                                                                                                                                                                              | interval          |
| update_interval        | Scheduled execution update interval, only takes effect when update_mode = interval, unit hours, set to 0 or empty to run only once                                                                                                                                                                                                                                   | 12                |
| update_times           | Scheduled execution update time point, only takes effect when update_mode = time, format HH:MM, supports multiple time points separated by commas                                                                                                                                                                                                                    |                   |
| update_startup         | Execute update at startup, used to control whether to execute an update immediately after the program starts                                                                                                                                                                                                                                                         | True              |
| time_zone              | Time zone, can be used to control the time zone for scheduled execution or display update time; Optional values: Asia/Shanghai or other time zone codes                                                                                                                                                                                                              | Asia/Shanghai     |
| source_file            | Template file path.                                                                                                                                                                                                                                                                                                                                                  | config/demo.txt   |
| final_file             | Generated result file path.                                                                                                                                                                                                                                                                                                                                          | output/result.txt |
| open_service           | Enable page service, used to control whether to start the result page service. If using platforms such as Qinglong with scheduled tasks, and you need the program to exit after update is finished, you can disable this.                                                                                                                                            | True              |
| app_port               | Page service port, used to control the port number of the page service.                                                                                                                                                                                                                                                                                              | 5180              |
| public_scheme          | Public network protocol. Optional values: `http`, `https`.                                                                                                                                                                                                                                                                                                           | http              |
| public_domain          | Public network Host address, used to generate access URLs in the result; uses local machine IP by default.                                                                                                                                                                                                                                                           | 127.0.0.1         |
| cdn_url                | CDN proxy acceleration address, used for accelerated access to subscription sources, channel icons and other resources.                                                                                                                                                                                                                                              |                   |
| open_driver            | Enable browser execution. If there are no updates, this mode can be enabled to try fetching data via a browser, but it consumes more resources.                                                                                                                                                                                                                      | False             |
| open_hotel             | Enable hotel source function; after disabling, all hotel source working modes will be turned off.                                                                                                                                                                                                                                                                    | False             |
| open_multicast         | Enable multicast source function; after disabling, all multicast source working modes will be turned off.                                                                                                                                                                                                                                                            | False             |
| open_local             | Enable local source function, will use the data in the template file and the local source file (`local.txt`).                                                                                                                                                                                                                                                        | True              |
| open_subscribe         | Enable subscription source function.                                                                                                                                                                                                                                                                                                                                 | True              |
| open_online_search     | Enable keyword search source function.                                                                                                                                                                                                                                                                                                                               | False             |
| open_hotel_foodie      | Enable Foodie hotel source working mode.                                                                                                                                                                                                                                                                                                                             | True              |
| open_hotel_fofa        | Enable FOFA / ZoomEye hotel source working mode.                                                                                                                                                                                                                                                                                                                     | False             |
| open_multicast_foodie  | Enable Foodie multicast source working mode.                                                                                                                                                                                                                                                                                                                         | True              |
| open_multicast_fofa    | Enable FOFA multicast source working mode.                                                                                                                                                                                                                                                                                                                           | False             |
| open_request           | Enable query requests, data is obtained from the network (only for hotel sources and multicast sources).                                                                                                                                                                                                                                                             | False             |
| open_use_cache         | Enable using local cached data, suitable for scenarios where query requests fail (only for hotel sources and multicast sources).                                                                                                                                                                                                                                     | True              |
| open_history           | Enable using historical update results (including interfaces from template and result files), merged into this update.                                                                                                                                                                                                                                               | True              |
| open_headers           | Enable using request header authentication information contained in M3U, used for speed test and other operations. Note: only a few players support playing such interfaces with authentication info, so it is disabled by default.                                                                                                                                  | False             |
| open_speed_test        | Enable speed test functionality to obtain response time, rate, and resolution.                                                                                                                                                                                                                                                                                       | True              |
| open_filter_resolution | Enable resolution filtering. Interfaces below the minimum resolution (`min_resolution`) will be filtered. GUI users need to manually install FFmpeg; the program will call FFmpeg to obtain interface resolution. Recommended to enable: although it increases speed test time, it more effectively distinguishes playable interfaces.                               | True              |
| open_filter_speed      | Enable speed filtering. Interfaces below the minimum speed (`min_speed`) will be filtered.                                                                                                                                                                                                                                                                           | True              |
| open_supply            | Enable compensation mechanism mode. When the number of channel interfaces is insufficient, interfaces that do not meet the conditions (such as lower than minimum speed) but may still be available will be added to the result to avoid empty results.                                                                                                              | True              |
| min_resolution         | Minimum interface resolution, takes effect only when `open_filter_resolution` is enabled.                                                                                                                                                                                                                                                                            | 1920x1080         |
| max_resolution         | Maximum interface resolution, takes effect only when `open_filter_resolution` is enabled.                                                                                                                                                                                                                                                                            | 1920x1080         |
| min_speed              | Minimum interface speed (unit: M/s), takes effect only when `open_filter_speed` is enabled.                                                                                                                                                                                                                                                                          | 0.5               |
| speed_test_limit       | Number of interfaces to test at the same time. Controls concurrency in the speed test stage. Larger values shorten speed test time but increase load and may reduce accuracy; smaller values increase time but reduce load and improve accuracy.                                                                                                                     | 10                |
| speed_test_timeout     | Single interface speed test timeout duration in seconds. Larger values increase speed test time and number of interfaces obtained (but with lower average quality); smaller values reduce time and favor low-latency, higher-quality interfaces.                                                                                                                     | 10                |
| speed_test_filter_host | Use Host address to de-duplicate speed tests. Channels with the same Host share speed test data. Enabling this can greatly reduce speed test time but may cause inaccurate results.                                                                                                                                                                                  | False             |
| request_timeout        | Query request timeout duration in seconds, used to control timeout and retry duration when querying interface text links. Adjusting this value can optimize update time.                                                                                                                                                                                             | 10                |
| recent_days            | Retrieve interfaces updated within the recent time range (in days). Reducing this appropriately can avoid matching issues.                                                                                                                                                                                                                                           | 30                |
| ipv4_num               | Preferred number of IPv4 interfaces in the result.                                                                                                                                                                                                                                                                                                                   |                   |
| ipv6_num               | Preferred number of IPv6 interfaces in the result.                                                                                                                                                                                                                                                                                                                   |                   |
| ipv6_support           | Force treating the current network as IPv6-supported and skip detection.                                                                                                                                                                                                                                                                                             | False             |
| ipv_type               | Protocol type of interfaces in the generated result. Optional values: `ipv4`, `ipv6`, `全部`, `all`.                                                                                                                                                                                                                                                                   | 全部                |
| ipv_type_prefer        | Interface protocol type preference. Preferred type will be ordered earlier in the result. Optional values: `ipv4`, `ipv6`, `自动`, `auto`.                                                                                                                                                                                                                             | auto              |
| location               | Interface location filter. Result will only contain interfaces whose location matches the given keywords (comma-separated). Leave empty to not restrict by location. Recommended to set near the end user to improve playback experience.                                                                                                                            |                   |
| isp                    | Interface operator filter. Result will only contain interfaces whose operator matches the given keywords (comma-separated). Leave empty to not restrict by operator.                                                                                                                                                                                                 |                   |
| origin_type_prefer     | Preferred interface source ordering. The result is sorted in this order (comma-separated). Example: `local,hotel,multicast,subscribe,online_search`. `local`: local source; `hotel`: hotel source; `multicast`: multicast source; `subscribe`: subscription source; `online_search`: keyword search. Leave empty to not specify and sort by interface speed instead. |                   |
| local_file             | Local source file path.                                                                                                                                                                                                                                                                                                                                              | config/local.txt  |
| local_num              | Preferred number of local source interfaces in the result.                                                                                                                                                                                                                                                                                                           | 10                |
| subscribe_num          | Preferred number of subscription source interfaces in the result.                                                                                                                                                                                                                                                                                                    | 10                |
| hotel_num              | Preferred number of hotel source interfaces in the result.                                                                                                                                                                                                                                                                                                           | 10                |
| hotel_page_num         | Number of pages to retrieve for hotel regions.                                                                                                                                                                                                                                                                                                                       | 1                 |
| hotel_region_list      | Hotel source region list; `"全部"` / `all` means all regions.                                                                                                                                                                                                                                                                                                          | 全部                |
| multicast_num          | Preferred number of multicast source interfaces in the result.                                                                                                                                                                                                                                                                                                       | 10                |
| multicast_page_num     | Number of pages to retrieve for multicast regions.                                                                                                                                                                                                                                                                                                                   | 1                 |
| multicast_region_list  | Multicast source region list; `"全部"` / `all` means all regions.                                                                                                                                                                                                                                                                                                      | 全部                |
| online_search_num      | Preferred number of keyword search interfaces in the result.                                                                                                                                                                                                                                                                                                         | 0                 |
| online_search_page_num | Number of pages to retrieve for keyword search channels.                                                                                                                                                                                                                                                                                                             | 1                 |
| logo_url               | Channel logo library URL.                                                                                                                                                                                                                                                                                                                                            |                   |
| logo_type              | Channel logo file type.                                                                                                                                                                                                                                                                                                                                              | png               |
| open_rtmp              | Enable RTMP push function. Requires FFmpeg installed, uses local bandwidth to improve playback experience.                                                                                                                                                                                                                                                           | True              |
| nginx_http_port        | Nginx HTTP service port, used for the HTTP service of RTMP push forwarding.                                                                                                                                                                                                                                                                                          | 8080              |
| nginx_rtmp_port        | Nginx RTMP service port, used for the RTMP service of RTMP push forwarding.                                                                                                                                                                                                                                                                                          | 1935              |
| rtmp_idle_timeout      | RTMP channel idle stop-streaming timeout in seconds. When no one watches for longer than this duration, streaming is stopped, helping reduce server resource usage.                                                                                                                                                                                                  | 60                |
| rtmp_max_streams       | Maximum number of concurrent RTMP push streams. Controls how many channels can be pushed at the same time. Larger values increase server load; tune to optimize resource usage.                                                                                                                                                                                      | 10                |

## Quick Start

### Configuration and Results Directory

```
iptv-api/                  # Project root directory
├── config                 # Configuration files directory, includes config files, templates, etc.
│   └── config.ini         # Configuration parameters file
│   └── rtp                # Multicast IPs for each region/operator
│   └── demo.txt           # Channel template
│   └── alias.txt          # Channel aliases
│   └── blacklist.txt      # Interface blacklist
│   └── whitelist.txt      # Interface whitelist
│   └── subscribe.txt      # Channel subscription sources list
│   └── local.txt          # Local source file
│   └── epg.txt            # EPG subscription sources list
├── output                 # Output files directory, includes generated result files, etc.
│   └── data               # Result data cache directory
│   └── epg                # EPG result directory
│   └── ipv4               # IPv4 result directory
│   └── ipv6               # IPv6 result directory
│   └── result.m3u/txt     # m3u/txt result
│   └── hls.m3u/txt        # RTMP hls stream result
│   └── log                # Log files directory
│       └── result.log     # Valid result log
│       └── speed_test.log # Speed test log
│       └── statistic.log  # Statistics result log
│       └── nomatch.log    # Unmatched channel records
└── source.json            # VOD source configuration file
```

### Workflow

Fork this project and initiate workflow updates, detailed steps are available
at [Detailed Tutorial](./docs/tutorial_en.md)

### Command Line

```shell
pip install pipenv
```

```shell
pipenv install --dev
```

Start update:

```shell
pipenv run dev
```

Start service:

```shell
pipenv run service
```

### GUI Software

1. Download the [IPTV-API Update Software](https://github.com/Guovin/iptv-api/releases), open the software, and click
   Start to perform the update

2. Or run the following command in the project directory to open the GUI software:

```shell
pipenv run ui
```

<img src="./docs/images/ui.png" alt="IPTV-API update software" title="IPTV-API update software" style="height:600px" />

### Docker

#### One‑click deployment with Compose

[docker-compose.yml](./docker-compose.yml)

```bash
docker compose up -d
```

#### Manual deployment with commands

##### 1. Pull the image

```bash
docker pull guovern/iptv-api:latest
```

🚀 Proxy acceleration (recommended for users in Mainland China, may be cached):

```bash
docker pull docker.1ms.run/guovern/iptv-api:latest
```

##### 2. Run the container

```bash
docker run -d -p 5180:5180 guovern/iptv-api
```

**Environment Variables:**

| Variable        | Description             | Default Value |
|:----------------|:------------------------|:--------------|
| APP_PORT        | Service port            | 5180          |
| NGINX_HTTP_PORT | Nginx HTTP service port | 8080          |
| NGINX_RTMP_PORT | Nginx RTMP service port | 1935          |

In addition to the environment variables listed above, you can also override the [configuration items](#Config) in the
configuration file via environment variables.

**Mounts:** used to synchronize files between the host and the container. You can edit templates, configs, and access
generated result files directly on the host. Append the following options to the run command above:

Mount config directory:

```bash
-v /iptv-api/config:/iptv-api/config
```

Mount output directory:

```bash
-v /iptv-api/output:/iptv-api/output
```

##### 3. Update Results

| Endpoint        | Description                                     |
|:----------------|:------------------------------------------------|
| /               | Default endpoint                                |
| /m3u            | m3u format endpoint                             |
| /txt            | txt format endpoint                             |
| /ipv4           | ipv4 default endpoint                           |
| /ipv6           | ipv6 default endpoint                           |
| /ipv4/txt       | ipv4 txt endpoint                               |
| /ipv6/txt       | ipv6 txt endpoint                               |
| /ipv4/m3u       | ipv4 m3u endpoint                               |
| /ipv6/m3u       | ipv6 m3u endpoint                               |
| /content        | Endpoint content                                |
| /log/result     | Log of valid results                            |
| /log/speed-test | Log of all interfaces involved in speed testing |
| /log/statistic  | Log of statistics results                       |
| /log/nomatch    | Log of unmatched channels                       |

**RTMP Streaming:**

> [!NOTE]
> 1. After enabling streaming, obtained sources (for example subscription sources) will be streamed by default.
> 2. To stream local video sources, create an `hls` folder inside the `config` directory.
> 3. Place video files named with the `channel name` into that folder; the program will automatically stream them to the
     corresponding channels.
> 4. Visit `http://127.0.0.1:8080/stat` to view real-time streaming status and statistics.

| Streaming Endpoint | Description                         |
|:-------------------|:------------------------------------|
| /hls               | hls streaming endpoint              |
| /hls/txt           | hls txt streaming endpoint          |
| /hls/m3u           | hls m3u streaming endpoint          |
| /hls/ipv4          | hls ipv4 default streaming endpoint |
| /hls/ipv6          | hls ipv6 default streaming endpoint |
| /hls/ipv4/txt      | hls ipv4 txt streaming endpoint     |
| /hls/ipv4/m3u      | hls ipv4 m3u streaming endpoint     |
| /hls/ipv6/txt      | hls ipv6 txt streaming endpoint     |
| /hls/ipv6/m3u      | hls ipv6 m3u streaming endpoint     |

## Changelog

[Changelog](./CHANGELOG.md)

## Follow

### GitHub

Follow my GitHub account [Guovin](https://github.com/Guovin) to find more useful projects

### WeChat public account

WeChat public account search for Govin, or scan the code to receive updates and learn more tips:

![Wechat public account](./static/images/qrcode.jpg)

## Star History

[![Star History Chart](https://starchart.cc/Guovin/iptv-api.svg?variant=adaptive)](https://starchart.cc/Guovin/iptv-api)

## Donations

<div>Development and maintenance are not easy, please buy me a coffee ~</div>

| Alipay                                | Wechat                                    |
|---------------------------------------|-------------------------------------------|
| ![Alipay](./static/images/alipay.jpg) | ![Wechat](./static/images/appreciate.jpg) |

## Disclaimer

This project is for learning and communication purposes only. All interface data comes from the internet. If there is
any infringement, please contact us for removal.

## License

[MIT](./LICENSE) License &copy; 2024-PRESENT [Govin](https://github.com/guovin)
