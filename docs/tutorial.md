# 使用教程

[English](./tutorial_en.md) | 中文

IPTV-API是一个可高度自定义的IPTV接口更新项目📺，自定义频道菜单，自动获取直播源，测速验效后生成可用的结果，可实现『✨秒播级体验🚀』

## 步骤一：Fork 本项目

将本仓库的源代码复制至个人账号仓库中

### 1. 首页点击 Fork：

![Fork入口](./images/fork-btn.png 'Fork入口')

### 2. Fork 创建个人仓库：

1. 个人仓库命名，可按您喜欢的名字随意命名（最终直播源结果链接取决于该名称），这里以默认 TV 为例
2. 确认信息无误后，点击确认创建

![Fork详情](./images/fork-detail.png 'Fork详情')

## 步骤二：更新源代码

由于本项目将持续迭代优化，如果您想获取最新的更新内容，可进行如下操作

### 1. Star

打开 https://github.com/Guovin/iptv-api ，点击 Star 收藏该项目（您的 Star 是我持续更新的动力）
![Star](./images/star.png 'Star')

### 2. Watch

关注该项目，后续更新日志将以 releases 发布，届时您将收到邮件通知
![Watch-activity](./images/watch-activity.png 'Watch All Activity')

### 3. Sync fork

#### 正常更新：

回到您 Fork 后的仓库首页，如果项目有更新内容，点击 Sync fork，Update branch 确认即可更新最新代码
![Sync-fork](./images/sync-fork.png 'Sync fork')

#### 没有 Update branch 按钮，更新冲突：

这是因为某些文件与主仓库的默认文件冲突了，点击 Discard commits 即可更新最新代码
![冲突解决](./images/conflict.png '冲突解决')

## 步骤三：修改模板

当您在步骤一中点击确认创建，成功后会自动跳转到您的个人仓库。这个时候您的个人仓库就创建完成了，可以定制个人的直播源频道菜单了！

### 1. 点击 config 文件夹内 demo.txt 模板文件：

![config文件夹入口](./images/config-folder.png 'config文件夹入口')

![demo.txt入口](./images/demo-btn.png 'demo.txt入口')
您可以复制并参考默认模板的格式进行后续操作。

### 2. config 文件夹内创建个人模板 user_demo.txt：

1. 创建文件
2. 模板文件命名为 user_demo.txt
3.

模板文件需要按照（频道分类,#genre#），（频道名称,频道接口）进行编写，注意是英文逗号。如果需要将该接口设为白名单（不测速、保留在结果最前），可在地址后添加$!即可，例如http://xxx$!
。后面也可以添加额外说明信息，如：http://xxx$!白名单接口

4. 点击 Commit changes...进行保存

![创建user_demo.txt](./images/edit-user-demo.png '创建user_demo.txt')

## 步骤四：修改配置

跟编辑模板一样，修改运行配置

### 1. 点击 config 文件夹内的 config.ini 配置文件：

![config.ini入口](./images/config-btn.png 'config.ini入口')

### 2. 复制默认配置文件内容：

![copy config.ini](./images/copy-config.png '复制默认配置')

### 3. config 文件夹内新建个人配置文件 user_config.ini：

1. 创建文件
2. 配置文件命名为 user_config.ini
3. 粘贴默认配置
4. 修改模板和结果文件配置：
    - source_file = config/user_demo.txt
    - final_file = output/user_result.txt
5. 点击 Commit changes...进行保存

![创建user_config.ini](./images/edit-user-config.png '创建user_config.ini')

按照您的需要适当调整配置，以下是默认配置说明：
[配置参数](./config.md)

## 步骤五：运行更新

### 方式一：工作流

#### 注意： 请谨慎使用工作流更新，如果您有大量的频道需要更新，请使用本地更新，勿使用自动更新，配置不当可能导致账户或工作流封禁！

如果您的模板和配置修改没有问题的话，这时就可以配置 Actions 来实现自动更新啦

### 1. 进入 Actions：

![Actions入口](./images/actions-btn.png 'Actions入口')

### 2. 开启 Actions 工作流：

![开启Actions工作流](./images/actions-enable.png '开启Actions工作流')
由于 Fork 的仓库 Actions 工作流是默认关闭的，需要您手动确认开启，点击红框中的按钮确认开启

![Actions工作流开启成功](./images/actions-home.png 'Actions工作流开启成功')
开启成功后，可以看到目前是没有任何工作流在运行的，别急，下面开始运行您第一个更新工作流

### 3. 运行更新工作流：

#### （1）启用 update schedule：

1. 点击 Workflows 分类下的 update schedule
2. 由于 Fork 的仓库工作流是默认关闭的，点击 Enable workflow 按钮确认开启

![开启Workflows更新](./images/workflows-btn.png '开启Workflows更新')

#### （2）根据分支运行 Workflow：

这个时候就可以运行更新工作流了

1. 点击 Run workflow
2. 这里可以切换您要运行的仓库分支，由于 Fork 默认拉取的是 master 分支，如果您修改的模板和配置也在 master 分支，这里选择
   master 就好了，点击 Run workflow 确认运行

![运行Workflow](./images/workflows-run.png '运行Workflow')

#### （3）Workflow 运行中：

稍等片刻，就可以看到您的第一条更新工作流已经在运行了！
![Workflow运行中](./images/workflow-running.png 'Workflow运行中')
（注意：由于运行时间取决于您的模板频道数量以及页数等配置，也很大程度取决于当前网络状况，请耐心等待，默认模板与配置一般需要 25
分钟左右。）

#### （4）Workflow 取消运行：

如果您觉得这次的更新不太合适，需要修改模板或配置再运行，可以点击 Cancel run 取消本次运行
![取消运行Workflow](./images/workflow-cancel.png '取消运行Workflow')

#### （5）Workflow 运行成功：

如果一切正常，稍等片刻后就可以看到该条工作流已经执行成功（绿色勾图标）
![Workflow执行成功](./images/workflow-success.png 'Workflow执行成功')
此时您可以访问代理文件链接，查看最新结果有没有同步即可：
https://cdn.jsdelivr.net/gh/您的github用户名/仓库名称（对应上述Fork创建时的TV）@master/output/user_result.txt
![用户名与仓库名称](./images/rep-info.png '用户名与仓库名称')

如果访问该链接能正常返回更新后的接口内容，说明您的直播源接口链接已经大功告成了！将该链接复制粘贴到 TVBox
等软件配置栏中即可使用~

- 注意：除了首次执行工作流需要您手动触发，后续执行（默认北京时间每日 6:00 与 18:00）将自动触发。如果您修改了模板或配置文件想立刻执行更新，可手动触发（2）中的
  Run workflow 即可。

### 4.修改工作流更新频率（可选）

如果您想修改更新频率（默认北京时间每日 6:00 与 18:00），可修改 on:schedule:- cron 字段：
![.github/workflows/main.yml](./images/schedule-cron.png '.github/workflows/main.yml')
如果您想 每 2 天执行更新可以这样修改：

```bash
- cron: '0 22 */2 * *'
- cron: '0 10 */2 * *'
```

#### 1. 强烈不建议修改更新频率过高，因为短时间内的接口内容并无差异，过高的更新频率与高耗时运行的工作流都有可能被判定为资源滥用，导致仓库与账户被封禁的风险。

#### 2. 请留意您的工作流运行时长，若发现执行时间过长，需要适当删减模板中频道数量、修改配置中的分页数量和接口数量，以达到合规的运行要求。

### 方式二：命令行

1. 安装 Python
   请至官方下载并安装 Python，安装时请选择将 Python 添加到系统环境变量 Path 中

2. 运行更新
   项目目录下打开终端 CMD 依次运行以下命令：

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

### 方式三：GUI 软件

1. 下载[IPTV-API 更新软件](https://github.com/Guovin/iptv-api/releases)，打开软件，点击更新，即可完成更新

2. 或者在项目目录下运行以下命令，即可打开 GUI 软件：

```shell
pipenv run ui
```

![IPTV-API 更新软件](./images/ui.png 'IPTV-API 更新软件')

### 方式四：Docker

- iptv-api（完整版本）：性能要求较高，更新速度较慢，稳定性、成功率高；修改配置 open_driver = False 可切换到 Lite
  版本运行模式（推荐酒店源、组播源、关键字搜索使用此版本）
- iptv-api:lite（精简版本）：轻量级，性能要求低，更新速度快，稳定性不确定（推荐订阅源使用此版本）

1. 拉取镜像：

- iptv-api：

```bash
docker pull guovern/iptv-api:latest
```

- iptv-api:lite：

```bash
docker pull guovern/iptv-api:lite
```

2. 运行容器：

- iptv-api：

```bash
docker run -d -p 8000:8000 guovern/iptv-api
```

- iptv-api:lite：

```bash
docker run -d -p 8000:8000 guovern/iptv-api:lite
```

卷挂载参数（可选）：
实现宿主机文件与容器文件同步，修改模板、配置、获取更新结果文件可直接在宿主机文件夹下操作

以宿主机路径/etc/docker 为例：

- iptv-api：

```bash
docker run -v /etc/docker/config:/iptv-api/config -v /etc/docker/output:/iptv-api/output -d -p 8000:8000 guovern/iptv-api
```

- iptv-api:lite：

```bash
docker run -v /etc/docker/config:/iptv-api-lite/config -v /etc/docker/output:/iptv-api-lite/output -d -p 8000:8000 guovern/iptv-api:lite
```

端口环境变量：

```bash
-e APP_PORT=8000
```

3. 更新结果：

- 接口地址：ip:8000
- M3u 接口：ip:8000/m3u
- Txt 接口：ip:8000/txt
- 接口内容：ip:8000/content
- 测速日志：ip:8000/log

### 上传更新文件至仓库（可选）

如果您没有自己的域名地址，接口更新完成后，将 user_result.txt 上传至个人仓库，即可使用
https://cdn.jsdelivr.net/gh/您的github用户名/仓库名称（对应上述Fork创建时的TV）@master/output/user_result.txt
![用户名与仓库名称](./images/rep-info.png '用户名与仓库名称')
