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

| Feature                               | Status | Description                                                                                                |
|:--------------------------------------|:------:|:-----------------------------------------------------------------------------------------------------------|
| **Custom Templates**                  |   ✅    | Generate personalized channels as you wish                                                                 |
| **Channel Alias**                     |   ✅    | Improves channel result coverage and accuracy, supports regular expressions                                |
| **Multiple Source Types**             |   ✅    | Supports local sources, multicast, hotel sources, subscriptions, and keyword search                        |
| **RTMP Streaming**                    |   ✅    | Supports Live and HLS modes to enhance live playback experience                                            |
| **Playback Interfaces**               |   ✅    | Supports acquisition and generation of playback interfaces                                                 |
| **EPG (Electronic Program Guide)**    |   ✅    | Displays channel preview content                                                                           |
| **Channel Logo**                      |   ✅    | Supports custom channel logo library sources                                                               |
| **Interface Speed Test & Validation** |   ✅    | Measures latency, speed, resolution, and filters invalid interfaces                                        |
| **Advanced Preferences**              |   ✅    | IPv4/IPv6, interface sorting priority, quantity configuration, blacklist/whitelist, region & ISP filtering |
| **Scheduled Tasks**                   |   ✅    | Automatically updates at 6:00 and 18:00 Beijing time daily by default; customizable schedule               |
| **Multiple Run Modes**                |   ✅    | Supports workflow, CLI, GUI software, Docker (amd64/arm64/arm v7)                                          |
| **More Features**                     |   ✨    | See [Configuration Parameters](#Config) section for details                                                |

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

| Configuration Item     | Description                                                                                                                                                                                                                                                                                                                                                                                                                      | Default Value     |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------|
| open_driver            | Enable browser execution, If there are no updates, this mode can be enabled, which consumes more performance                                                                                                                                                                                                                                                                                                                     | False             |
| open_epg               | Enable EPG function, support channel display preview content                                                                                                                                                                                                                                                                                                                                                                     | True              |
| open_empty_category    | Enable the No Results Channel Category, which will automatically categorize channels without results to the bottom                                                                                                                                                                                                                                                                                                               | False             |
| open_filter_resolution | Enable resolution filtering, interfaces below the minimum resolution (min_resolution) will be filtered, GUI users need to manually install FFmpeg, the program will automatically call FFmpeg to obtain the interface resolution, it is recommended to enable, although it will increase the time-consuming of the speed measurement stage, but it can more effectively distinguish whether the interface can be played          | True              |
| open_filter_speed      | Enable speed filtering, interfaces with speed lower than the minimum speed (min_speed) will be filtered                                                                                                                                                                                                                                                                                                                          | True              |
| open_hotel             | Enable the hotel source function, after closing it all hotel source working modes will be disabled                                                                                                                                                                                                                                                                                                                               | False             |
| open_hotel_foodie      | Enable Foodie hotel source work mode                                                                                                                                                                                                                                                                                                                                                                                             | True              |
| open_hotel_fofa        | Enable FOFA、ZoomEye hotel source work mode                                                                                                                                                                                                                                                                                                                                                                                       | False             |
| open_local             | Enable local source function, will use the data in the template file and the local source file                                                                                                                                                                                                                                                                                                                                   | True              |
| open_m3u_result        | Enable the conversion to generate m3u file type result links, supporting the display of channel icons                                                                                                                                                                                                                                                                                                                            | True              |
| open_multicast         | Enable the multicast source function, after disabling it all multicast sources will stop working                                                                                                                                                                                                                                                                                                                                 | False             |
| open_multicast_foodie  | Enable Foodie multicast source work mode                                                                                                                                                                                                                                                                                                                                                                                         | True              |
| open_multicast_fofa    | Enable FOFA multicast source work mode                                                                                                                                                                                                                                                                                                                                                                                           | False             |
| open_online_search     | Enable keyword search source feature                                                                                                                                                                                                                                                                                                                                                                                             | False             |
| open_request           | Enable query request, the data is obtained from the network (only for hotel sources and multicast sources)                                                                                                                                                                                                                                                                                                                       | False             |
| open_rtmp              | Enable RTMP push function, need to install FFmpeg, use local bandwidth to improve the interface playback experience                                                                                                                                                                                                                                                                                                              | False             |
| open_service           | Enable page service, used to control whether to start the result page service; if deployed on platforms like Qinglong with dedicated scheduled tasks, the function can be turned off after updates are completed and the task is stopped                                                                                                                                                                                         | True              |
| open_speed_test        | Enable speed test functionality to obtain response time, rate, and resolution                                                                                                                                                                                                                                                                                                                                                    | True              |
| open_subscribe         | Enable subscription source feature                                                                                                                                                                                                                                                                                                                                                                                               | True              |
| open_supply            | Enable compensation mechanism mode, used to control when the number of channel interfaces is insufficient, automatically add interfaces that do not meet the conditions (such as lower than the minimum rate) but may be available to the result, thereby avoiding the result being empty                                                                                                                                        | True              |
| open_update            | Enable updates, if disabled then only the result page service is run                                                                                                                                                                                                                                                                                                                                                             | True              |
| open_update_time       | Enable show update time                                                                                                                                                                                                                                                                                                                                                                                                          | True              |
| open_url_info          | Enable to display interface description information, used to control whether to display interface source, resolution, protocol type and other information, the content after the $ symbol, the playback software uses this information to describe the interface, if some players (such as PotPlayer) do not support parsing and cannot play, you can turn it off                                                                | False             |
| open_use_cache         | Enable the use of local cache data, applicable to the query request failure scenario (only for hotel sources and multicast sources)                                                                                                                                                                                                                                                                                              | True              |
| open_history           | Enable the use of historical update results (including the interface for template and result files) and merge them into the current update                                                                                                                                                                                                                                                                                       | True              |
| open_headers           | Enable to use the request header verification information contained in M3U, used for speed measurement and other operations. Note: Only a few players support playing this type of interface with verification information, which is turned off by default                                                                                                                                                                       | False             |
| app_host               | Page service Host address, default is to use the local machine IP                                                                                                                                                                                                                                                                                                                                                                |                   |
| app_port               | Page service port, used to control the port number of the page service                                                                                                                                                                                                                                                                                                                                                           | 8000              |
| cdn_url                | CDN proxy acceleration address, used for accelerated access to subscription sources, channel icons and other resources                                                                                                                                                                                                                                                                                                           |                   |
| final_file             | Generated result file path                                                                                                                                                                                                                                                                                                                                                                                                       | output/result.txt |
| hotel_num              | The number of preferred hotel source interfaces in the results                                                                                                                                                                                                                                                                                                                                                                   | 10                |
| hotel_page_num         | Number of pages to retrieve for hotel regions                                                                                                                                                                                                                                                                                                                                                                                    | 1                 |
| hotel_region_list      | List of hotel source regions, 'all' indicates all regions                                                                                                                                                                                                                                                                                                                                                                        | all               |
| isp                    | Interface operator, used to control the result to only include the filled operator type, supports keyword filtering, separated by English commas, not filled in means no operator specified                                                                                                                                                                                                                                      |                   |
| ipv4_num               | The preferred number of IPv4 interfaces in the result                                                                                                                                                                                                                                                                                                                                                                            | 5                 |
| ipv6_num               | The preferred number of IPv6 interfaces in the result                                                                                                                                                                                                                                                                                                                                                                            | 5                 |
| ipv6_support           | It is forced to consider that the current network supports IPv6 and skip the check                                                                                                                                                                                                                                                                                                                                               | False             |
| ipv_type               | The protocol type of interface in the generated result, optional values: ipv4, ipv6, all                                                                                                                                                                                                                                                                                                                                         | all               |
| ipv_type_prefer        | Interface protocol type preference, prioritize interfaces of this type in the results, optional values: ipv4, ipv6, auto                                                                                                                                                                                                                                                                                                         | ipv6,ipv4         |
| location               | Interface location, used to control the result to only include the filled location type, supports keyword filtering, separated by English commas, not filled in means no location specified, it is recommended to use the location close to the user, which can improve the playback experience                                                                                                                                  |                   |
| local_file             | Local source file path                                                                                                                                                                                                                                                                                                                                                                                                           | config/local.txt  |
| local_num              | Preferred number of local source interfaces in the result                                                                                                                                                                                                                                                                                                                                                                        | 10                |
| logo_url               | Channel logo library URL address                                                                                                                                                                                                                                                                                                                                                                                                 |                   |
| logo_type              | Channel logo file type                                                                                                                                                                                                                                                                                                                                                                                                           | png               |
| min_resolution         | Minimum interface resolution, requires enabling open_filter_resolution to take effect                                                                                                                                                                                                                                                                                                                                            | 1920x1080         |
| max_resolution         | Maximum interface resolution, requires enabling open_filter_resolution to take effect                                                                                                                                                                                                                                                                                                                                            | 1920x1080         |
| min_speed              | Minimum interface speed (M/s), requires enabling open_filter_speed to take effect                                                                                                                                                                                                                                                                                                                                                | 0.5               |
| multicast_num          | The number of preferred multicast source interfaces in the results                                                                                                                                                                                                                                                                                                                                                               | 10                |
| multicast_page_num     | Number of pages to retrieve for multicast regions                                                                                                                                                                                                                                                                                                                                                                                | 1                 |
| multicast_region_list  | Multicast source region list, 'all' indicates all regions                                                                                                                                                                                                                                                                                                                                                                        | all               |
| online_search_num      | The number of preferred keyword search interfaces in the results                                                                                                                                                                                                                                                                                                                                                                 | 0                 |
| online_search_page_num | Page retrieval quantity for keyword search channels                                                                                                                                                                                                                                                                                                                                                                              | 1                 |
| origin_type_prefer     | Preferred interface source of the result, the result is sorted according to this order, separated by commas, for example: local, hotel, multicast, subscribe, online_search; local: local source, hotel: hotel source, multicast: multicast source, subscribe: subscription source, online_search: keyword search; If not filled in, it means that the source is not specified, and it is sorted according to the interface rate |                   |
| recent_days            | Retrieve interfaces updated within a recent time range (in days), reducing appropriately can avoid matching issues                                                                                                                                                                                                                                                                                                               | 30                |
| request_timeout        | Query request timeout duration, in seconds (s), used to control the timeout and retry duration for querying interface text links. Adjusting this value can optimize update time.                                                                                                                                                                                                                                                 | 10                |
| speed_test_limit       | Number of interfaces to be tested at the same time, used to control the concurrency during the speed measurement stage, the larger the value, the shorter the speed measurement time, higher load, and the result may be inaccurate; The smaller the value, the longer the speed measurement time, lower load, and more accurate results; Adjusting this value can optimize the update time                                      | 10                |
| speed_test_timeout     | Single interface speed measurement timeout duration, unit seconds (s); The larger the value, the longer the speed measurement time, which can improve the number of interfaces obtained, but the quality will decline; The smaller the value, the shorter the speed measurement time, which can obtain low-latency interfaces with better quality; Adjusting this value can optimize the update time                             | 10                |
| speed_test_filter_host | Use Host address for filtering during speed measurement, channels with the same Host address will share speed measurement data, enabling this can significantly reduce the time required for speed measurement, but may lead to inaccurate speed measurement results                                                                                                                                                             | False             |
| source_file            | Template file path                                                                                                                                                                                                                                                                                                                                                                                                               | config/demo.txt   |
| subscribe_num          | The number of preferred subscribe source interfaces in the results                                                                                                                                                                                                                                                                                                                                                               | 10                |
| time_zone              | Time zone, can be used to control the time zone displayed by the update time, optional values: Asia/Shanghai or other time zone codes                                                                                                                                                                                                                                                                                            | Asia/Shanghai     |
| urls_limit             | Number of interfaces per channel                                                                                                                                                                                                                                                                                                                                                                                                 | 10                |
| update_interval        | Scheduled execution update interval, unit hours, set 0 or empty means run only once, does not apply to workflow                                                                                                                                                                                                                                                                                                                  | 12                |
| update_time_position   | Update time display position, need to enable open_update_time to take effect, optional values: top, bottom, top: display at the top of the result, bottom: display at the bottom of the result                                                                                                                                                                                                                                   | top               |

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
│   └── live.m3u/txt       # RTMP live stream result
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

#### 1. Pull the image

```bash
docker pull guovern/iptv-api:latest
```

🚀 Proxy acceleration (recommended for users in China):

```bash
docker pull docker.1ms.run/guovern/iptv-api:latest
```

#### 2. Run the container

```bash
docker run -d -p 8000:8000 guovern/iptv-api
```

##### Mount(Recommended):

This allows synchronization of files between the host machine and the container. Modifying templates, configurations,
and retrieving updated result files can be directly operated in the host machine's folder.

Taking the host path /etc/docker as an example:

```bash
-v /etc/docker/config:/iptv-api/config
-v /etc/docker/output:/iptv-api/output
```

##### Environment Variables:

| Variable | Description          | Default Value    |
|:---------|:---------------------|:-----------------|
| APP_HOST | Service host address | Local machine IP |
| APP_PORT | Service port         | 8000             |

In addition to the environment variables listed above, you can also override the [configuration items](#Config) in the
configuration file via environment variables.

#### 3. Update Results

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

- RTMP Streaming:

> [!NOTE]
> 1. To stream local video sources, create a `live` or `hls` (recommended) folder in the `config` directory.
> 2. The `live` folder is used for live streaming interfaces, and the `hls` folder is used for HLS streaming interfaces.
> 3. Place video files named after the `channel name` into these folders, and the program will automatically stream them
     to the corresponding channels.
> 4. Visit http://localhost:8080/stat to view real-time streaming status statistics.

| Streaming Endpoint | Description                      |
|:-------------------|:---------------------------------|
| /live              | live streaming endpoint          |
| /hls               | hls streaming endpoint           |
| /live/txt          | live txt streaming endpoint      |
| /hls/txt           | hls txt streaming endpoint       |
| /live/m3u          | live m3u streaming endpoint      |
| /hls/m3u           | hls m3u streaming endpoint       |
| /live/ipv4/txt     | live ipv4 txt streaming endpoint |
| /hls/ipv4/txt      | hls ipv4 txt streaming endpoint  |
| /live/ipv4/m3u     | live ipv4 m3u streaming endpoint |
| /hls/ipv4/m3u      | hls ipv4 m3u streaming endpoint  |
| /live/ipv6/txt     | live ipv6 txt streaming endpoint |
| /hls/ipv6/txt      | hls ipv6 txt streaming endpoint  |
| /live/ipv6/m3u     | live ipv6 m3u streaming endpoint |
| /hls/ipv6/m3u      | hls ipv6 m3u streaming endpoint  |

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
