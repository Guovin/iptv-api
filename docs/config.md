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
| http_proxy             | HTTP 代理地址，用于获取订阅源等网络请求                                                                                               |                   |
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
| local_num              | 结果中偏好的本地源接口数量                                                                                                        | 10                |
| subscribe_num          | 结果中偏好的订阅源接口数量                                                                                                        | 10                |
| logo_url               | 频道台标库地址                                                                                                              |                   |
| logo_type              | 频道台标文件类型                                                                                                             | png               |
| open_rtmp              | 开启 RTMP 推流功能，需要安装 FFmpeg，利用本地带宽提升接口播放体验                                                                              | True              |
| nginx_http_port        | Nginx HTTP 服务端口，用于 RTMP 推流转发的 HTTP 服务端口                                                                              | 8080              |
| nginx_rtmp_port        | Nginx RTMP 服务端口，用于 RTMP 推流转发的 RTMP 服务端口                                                                              | 1935              |
| rtmp_idle_timeout      | RTMP 频道接口空闲停止推流超时时长，单位秒(s)，用于控制接口无人观看时超过该时长后停止推流，调整此值能优化服务器资源占用                                                      | 300               |
| rtmp_max_streams       | RTMP 推流最大并发数量，用于控制同时推流的频道数量，数值越大服务器压力越大，调整此值能优化服务器资源占用                                                               | 10                |