# 使用教程

[English](./tutorial_en.md) | 中文

<div align="center">
  <img src="../static/images/logo.png" alt="logo"/>
  <h1 align="center">IPTV-API</h1>
</div>

📺IPTV直播源自动更新平台，『🤖全自动采集、筛选、测速、生成流程🚀』，支持丰富的个性化配置，将结果地址输入播放器即可观看

以下一共4种安装运行方式，选择一种适合您的即可

## 工作流部署

使用Github工作流部署，自动更新接口

### 进入IPTV-API项目

打开 https://github.com/Guovin/iptv-api 点击`Star`收藏该项目（您的Star是我持续更新的动力）
![Star](./images/star.png 'Star')

### Fork

将本仓库的源代码复制至个人账号仓库中
![Fork入口](./images/fork-btn.png 'Fork入口')

1. 个人仓库命名，可按您喜欢的名字随意命名（最终直播源结果链接取决于该名称），这里以默认`iptv-api`为例
2. 确认信息无误后，点击确认创建

![Fork详情](./images/fork-detail.png 'Fork详情')

### 更新源代码

由于本项目将持续迭代优化，如果您想获取最新的更新内容，可进行如下操作

#### 1. Watch

关注该项目，后续更新日志将以`releases`发布，届时您将收到邮件通知
![Watch-activity](./images/watch-activity.png 'Watch All Activity')

#### 2. Sync fork

- 正常更新：

回到您 Fork 后的仓库首页，如果项目有更新内容，点击`Sync fork`，`Update branch`确认即可更新最新代码
![Sync-fork](./images/sync-fork.png 'Sync fork')

- 没有`Update branch`按钮，更新冲突：

这是因为某些文件与主仓库的默认文件冲突了，点击`Discard commits`即可更新最新代码
![冲突解决](./images/conflict.png '冲突解决')

> [!IMPORTANT]
> 为了避免后续更新代码发生冲突，以下修改`config`目录下的文件时建议复制文件后重命名添加`user_`前缀

### 修改模板

当您在步骤一中点击确认创建，成功后会自动跳转到您的个人仓库。这个时候您的个人仓库就创建完成了，可以定制个人的直播源频道菜单了！

#### 1. 点击 config 文件夹内 demo.txt 模板文件：

![config文件夹入口](./images/config-folder.png 'config文件夹入口')

![demo.txt入口](./images/demo-btn.png 'demo.txt入口')

您可以复制并参考默认模板的格式进行后续操作。

#### 2. config 文件夹内创建个人模板 user_demo.txt：

1. 点击`config`目录
2. 创建文件
3. 模板文件命名为`user_demo.txt`
4. 模板文件需要按照（频道分类,#genre#），（频道名称,频道接口）进行编写，注意是英文逗号。如果需要将该接口设为白名单（不测速、保留在结果最前），可在地址后添加
   `$!`即可，例如http://xxx$!。后面也可以添加额外说明信息，如：http://xxx$!白名单
5. 点击`Commit changes...`进行保存

![创建user_demo.txt](./images/edit-user-demo.png '创建user_demo.txt')

### 修改配置

跟编辑模板一样，修改运行配置

#### 1. 点击 config 文件夹内的 config.ini 配置文件：

![config.ini入口](./images/config-btn.png 'config.ini入口')

#### 2. 复制默认配置文件内容：

![copy config.ini](./images/copy-config.png '复制默认配置')

#### 3. config 文件夹内新建个人配置文件 user_config.ini：

1. 创建文件
2. 配置文件命名为`user_config.ini`
3. 粘贴默认配置 （创建`user_config.ini`可以只输入想要修改的配置项即可，无需全部复制 config.ini，注意配置文件上方的
   `[Settings]`必须保留，否则下方的自定义配置不生效）
4. 修改模板和结果文件配置以及CDN代理加速（推荐）：
    - source_file = config/user_demo.txt
    - final_file = output/user_result.txt
    - cdn_url = （前往`Govin`公众号回复`cdn`获取）
5. 点击`Commit changes...`进行保存

![创建user_config.ini](./images/edit-user-config.png '创建user_config.ini')
![编辑final_file配置](./images/edit-user-final-file.png '编辑source_file配置')
![编辑source_file配置](./images/edit-user-source-file.png '编辑source_file配置')

按照您的需要适当调整配置，以下是默认配置说明：
[配置参数](./config.md)

> [!NOTE]
> 1. 对于开启显示接口信息，由于部分播放器（如`PotPlayer`）不支持解析接口补充信息，导致无法正常播放，可修改配置:`open_url_info
=False`（GUI：取消勾选显示接口信息）关闭该功能
> 2. 如果你的网络确定支持IPv6，可修改配置:`ipv6_support = True`(GUI：勾选`强制认为当前网络支持IPv6`）跳过支持性检查

#### 同理你可以自定义订阅源、黑名单、白名单

- 订阅源（`config/subscribe.txt`）

  由于没有提供默认订阅地址，所以您需要自行添加，否则更新结果可能为空。支持txt和m3u地址作为订阅，程序将依次读取其中的频道接口数据。
  ![订阅源](./images/subscribe.png '订阅源')


- 本地源（`config/local.txt`）

  频道接口数据来源于本地文件，程序将依次读取其中的频道接口数据


- EPG源（`config/epg.txt`）

  频道预告信息数据来源，程序将依次获取文件中订阅地址的频道预告数据，进行汇总输出


- 频道别名（`config/alias.txt`）

  频道名称的别名名单，用于获取接口时将多种名称映射为一个名称的结果，可以提升获取量与准确率，格式：模板频道名称,别名1,别名2,别名3


- 黑名单（`config/blacklist.txt`）

  符合黑名单关键字的接口将会被过滤，不会被收集，比如含广告等低质量接口


- 白名单（`config/whitelist.txt`）

  白名单内的接口或订阅源获取的接口将不会参与测速，优先排序至结果最前。填写频道名称会直接保留该记录至最终结果，如：CCTV-1,接口地址，只填写接口地址则对所有频道生效，多条记录换行输入。

### 运行更新

如果您的模板和配置修改没有问题的话，这时就可以配置`Actions`来实现自动更新

#### 1. 进入 Actions：

![Actions入口](./images/actions-btn.png 'Actions入口')

#### 2. 开启 Actions 工作流：

![开启Actions工作流](./images/actions-enable.png '开启Actions工作流')
由于 Fork 的仓库 Actions 工作流是默认关闭的，需要您手动确认开启，点击红框中的按钮确认开启

![Actions工作流开启成功](./images/actions-home.png 'Actions工作流开启成功')
开启成功后，可以看到目前是没有任何工作流在运行的，别急，下面开始运行您第一个更新工作流

#### 3. 运行更新工作流：

##### （1）启用update schedule：

1. 点击`Workflows`分类下的`update schedule`
2. 由于 Fork 的仓库工作流是默认关闭的，点击`Enable workflow`按钮确认开启

![开启Workflows更新](./images/workflows-btn.png '开启Workflows更新')

##### （2）根据分支运行 Workflow：

这个时候就可以运行更新工作流了

1. 点击`Run workflow`
2. 这里可以切换您要运行的仓库分支，由于 Fork 默认拉取的是`master`分支，如果您修改的模板和配置也在该分支，这里选择`master`
   就好了，点击`Run workflow`确认运行

![运行Workflow](./images/workflows-run.png '运行Workflow')

##### （3）Workflow 运行中：

稍等片刻，就可以看到您的第一条更新工作流已经在运行了！

![Workflow运行中](./images/workflow-running.png 'Workflow运行中')

> [!NOTE]\
> 由于运行时间取决于您的模板频道数量以及页数等配置，也很大程度取决于当前网络状况，请耐心等待，默认模板与配置一般需要15
> 分钟左右。

##### （4）Workflow 取消运行：

如果您觉得这次的更新不太合适，需要修改模板或配置再运行，可以点击`Cancel run`取消本次运行
![取消运行Workflow](./images/workflow-cancel.png '取消运行Workflow')

##### （5）Workflow 运行成功：

如果一切正常，稍等片刻后就可以看到该条工作流已经执行成功（绿色勾图标）

![Workflow执行成功](./images/workflow-success.png 'Workflow执行成功')

此时您可以访问文件链接，查看最新结果有没有同步即可：
https://raw.githubusercontent.com/您的github用户名/仓库名称（对应上述Fork创建时的iptv-api）/master/output/user_result.txt

代理加速地址（推荐）：
{cdn_url}/https://raw.githubusercontent.com/您的github用户名/仓库名称（对应上述Fork创建时的iptv-api）/master/output/user_result.txt

![用户名与仓库名称](./images/rep-info.png '用户名与仓库名称')

如果访问该链接能正常返回更新后的接口内容，说明您的直播源接口链接已经大功告成了！将该链接复制粘贴到`TVBox`
等播放器配置栏中即可使用~

> [!NOTE]\
> 除了首次执行工作流需要您手动触发，后续执行（默认北京时间`每日6:00与18:00`）将自动触发。如果您修改了模板或配置文件想立刻执行更新，可手动触发（2）中的
`Run workflow`即可。

#### 4.修改工作流更新频率（可选）

如果您想修改更新频率（默认北京时间每日`6:00与18:00`），可修改`on:schedule:- cron`字段：
![.github/workflows/main.yml](./images/schedule-cron.png '.github/workflows/main.yml')

如果您想 每 2 天执行更新可以这样修改：

```bash
- cron: '0 22 */2 * *'
- cron: '0 10 */2 * *'
```

> [!WARNING]
> 1. 强烈不建议修改更新频率过高，因为短时间内的接口内容并无差异，过高的更新频率与高耗时运行的工作流都有可能被判定为资源滥用，导致仓库与账户被封禁的风险。
> 2. 请留意您的工作流运行时长，若发现执行时间过长，需要适当删减模板中频道数量、修改配置中的分页数量和接口数量，以达到合规的运行要求。

## 命令行

1. 安装 Python
   请至官方下载并安装 Python，安装时请选择将 Python 添加到系统环境变量 Path 中

2. 运行更新
   项目目录下打开终端 CMD 依次运行以下命令：

安装依赖：

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

## GUI 软件

1. 下载[IPTV-API 更新软件](https://github.com/Guovin/iptv-api/releases)，打开软件，点击启动，即可进行更新

2. 或者在项目目录下运行以下命令，即可打开 GUI 软件：

```shell
pipenv run ui
```

![IPTV-API 更新软件](./images/ui.png 'IPTV-API 更新软件')

## Docker

### 1. Compose部署（推荐）

下载[docker-compose.yml](../docker-compose.yml)或复制内容创建（内部参数可按需更改），在文件所在路径下运行以下命令即可部署：

```bash
docker compose up -d
```

### 2. 手动命令部署

#### （1）拉取镜像

```bash
docker pull guovern/iptv-api:latest
```

🚀 代理加速（若拉取失败可以使用该命令，但有可能拉取的是旧版本）：

```bash
docker pull docker.1ms.run/guovern/iptv-api:latest
```

#### （2）运行容器

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

除了以上环境变量，还支持通过环境变量覆盖配置文件中的[配置项](../docs/config.md)

**挂载：** 实现宿主机文件与容器文件同步，修改模板、配置、获取更新结果文件可直接在宿主机文件夹下操作，在上述运行命令后添加以下参数

```bash
# 挂载配置目录
-v /iptv-api/config:/iptv-api/config
# 挂载结果目录
-v /iptv-api/output:/iptv-api/output
```

#### 3. 更新结果

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
