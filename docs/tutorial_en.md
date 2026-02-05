# Tutorial

[中文](./tutorial.md) | English

<div align="center">
  <img src="../static/images/logo.svg" alt="IPTV-API logo"  width="120" height="120"/>
</div>

<p>
    <br>
    ⚡️ IPTV live-source automatic update platform — 🤖 fully automated collection, filtering, speed-testing, and generation 🚀. Supports extensive personalized configuration; paste the resulting address into a player to watch.
</p>

There are four installation and running methods in total (Workflows, Command Line, GUI, Docker). Choose the one that
suits you.

## Workflow deployment

Use GitHub Actions workflows to deploy and manually trigger the update endpoint.

> [!IMPORTANT]
> Because GitHub resources are limited, workflow updates can only be triggered manually.
> If you need frequent updates or scheduled runs, please deploy using another method.

### Enter the IPTV-API Project

Open https://github.com/Guovin/iptv-api and click `Star` to favorite this project (Your Star is my motivation for
continuous updates).
![Star](./images/star.png 'Star')

### Fork

Copy the source code of this repository to your personal account repository.
![Fork button](./images/fork-btn.png 'Fork button')

1. Name your personal repository as you like (the final live source result link depends on this name), here we use the
   default `iptv-api` as an example.
2. Confirm the information is correct and click to create.

![Fork details](./images/fork-detail.png 'Fork details')

### Update Source Code

Since this project will continue to iterate and optimize, if you want to get the latest updates, you can do the
following:

#### 1. Watch

Follow this project, and subsequent update logs will be released as `releases`, and you will receive email
notifications.
![Watch All Activity](./images/watch-activity.png 'Watch All Activity')

#### 2. Sync fork

- Normal update:

Go back to the homepage of your forked repository, if there are updates, click `Sync fork`, `Update branch` to confirm
and update the latest code.
![Sync fork](./images/sync-fork.png 'Sync fork')

- No `Update branch` button, update conflict:

This is because some files conflict with the default files of the main repository, click `Discard commits` to update the
latest code.
![Conflict resolution](./images/conflict.png 'Conflict resolution')

> [!IMPORTANT]
> To avoid conflicts when updating the code later, it is recommended to copy files in the `config` directory and rename
> them by adding the `user_` prefix before modifying.

### Modify Template

When you click to confirm creation in step one, you will automatically jump to your personal repository after success.
At this time, your personal repository has been created, and you can customize your live source channel menu!

#### 1. Click the demo.txt template file in the config folder:

![config folder entry](./images/config-folder.png 'config folder entry')

![demo.txt entry](./images/demo-btn.png 'demo.txt entry')

You can copy and refer to the format of the default template for subsequent operations.

#### 2. Create a personal template user_demo.txt in the config folder:

1. Click the `config` directory.
2. Create a file.
3. Name the template file `user_demo.txt`.
4. The template file needs to be written in the format of (channel category, #genre#), (channel name, channel interface)
   with a comma. If you want to whitelist the interface (no speed test, keep it at the top of the result), you can add
   `$!` after the address, such as http://xxx$!. You can also add additional information, such as: http://xxx$!
   whitelist.
5. Click `Commit changes...` to save.

![Create user_demo.txt](./images/edit-user-demo.png 'Create user_demo.txt')

### Modify Configuration

Like editing templates, modify the runtime configuration.

#### 1. Click the config.ini configuration file in the config folder:

![config.ini entry](./images/config-btn.png 'config.ini entry')

#### 2. Copy the default configuration file content:

![copy config.ini](./images/copy-config.png 'Copy default configuration')

#### 3. Create a personal configuration file user_config.ini in the config folder:

1. Create a file.
2. Name the configuration file `user_config.ini`.
3. Paste the default configuration. (when creating `user_config.ini`, you can only enter the configuration items you
   want to modify, no need to copy the entire `config.ini`. Note that the `[Settings]` at the top of the configuration
   file must be retained, otherwise the custom configuration below will not take effect)
4. Modify the template and result file configuration and CDN proxy acceleration (recommended):
    - source_file = config/user_demo.txt
    - final_file = output/user_result.txt
    - cdn_url = (go to the `Govin` public account and reply `cdn` to get it)
5. Click `Commit changes...` to save.

![Create user_config.ini](./images/edit-user-config.png 'Create user_config.ini')
![Edit final_file configuration](./images/edit-user-final-file.png 'Edit final_file configuration')
![Edit source_file configuration](./images/edit-user-source-file.png 'Edit source_file configuration')

Adjust the configuration as needed, here is the default configuration description:
[Configuration parameters](./config_en.md)

> [!NOTE]
> 1. For enabling interface information display, since some players (such as `PotPlayer`) do not support parsing
     interface
     supplementary information, causing playback failure, you can modify the configuration: `open_url_info = False` (
     GUI:
     uncheck display interface information) to disable this feature.
> 2. If your network supports IPv6, you can modify the configuration: `ipv6_support = True` (GUI: Check
     `Force assume the current network supports IPv6`) to skip the support check.

#### Add data sources and more

- Subscription sources (`config/subscribe.txt`)

  Since no default subscription addresses are provided, you need to add them yourself; otherwise the update results may
  be empty. Both `.txt` and `.m3u` URLs are supported as subscriptions, and the program will read channel interface
  entries from them sequentially.
  ![Subscription sources](./images/subscribe.png 'Subscription sources')


- Local sources（`config/local.txt`）

  Channel interface data comes from local files. If there are multiple local source files, you can create a `local`
  directory under `config` to store them; the program will read the channel interface data from them in order. Supports
  `txt` and `m3u` files.


- Logo source (`config/logo`)

  Directory for channel logo images. The program will match corresponding logo images in this directory based on the
  channel names in the template. If a remote library `logo_url` is used, the remote source will be preferred.


- EPG Source (`config/epg.txt`)

  The source of program guide information. The program will sequentially fetch the program guide data from the
  subscription addresses in the file and aggregate the output.


- Channel Aliases (`config/alias.txt`)

  A list of aliases for channel names, used to map multiple names to a single name when fetching from the interface,
  improving the fetch volume and accuracy. Format: TemplateChannelName,Alias1,Alias2,Alias3


- Blacklist (`config/blacklist.txt`)

  Interfaces that match the blacklist keywords will be filtered and not collected, such as low-quality interfaces with
  ads.


- Whitelist (`config/whitelist.txt`)

  Interfaces or subscription sources in the whitelist will not participate in speed testing and will be prioritized at
  the top of the results. Fill in the channel name to directly retain the record in the final result, such as: CCTV-1,
  interface address, only filling in the interface address will apply to all channels, multiple records are entered on
  separate lines.

### Run Update

If your template and configuration modifications are correct, you can configure `Actions` to achieve automatic updates.

#### 1. Enter Actions:

![Actions entry](./images/actions-btn.png 'Actions entry')

#### 2. Enable Actions workflow:

![Enable Actions workflow](./images/actions-enable.png 'Enable Actions workflow')
Since the Actions workflow of the forked repository is disabled by default, you need to manually confirm to enable it,
click the button in the red box to confirm enabling.
![Actions workflow enabled successfully](./images/actions-home.png 'Actions workflow enabled successfully')
After enabling successfully, you can see that there are no workflows running currently, don't worry, let's start running
your first update workflow below.

#### 3. Run the update workflow:

##### (1) Enable update schedule:

1. Click `update schedule` under the `Workflows` category.
2. Since the workflow of the forked repository is disabled by default, click the `Enable workflow` button to confirm the
   activation.

![Enable Workflows update](./images/workflows-btn.png 'Enable Workflows update')

##### (2) Run the Workflow based on branches:

Now you can run the update workflow.

1. Click `Run workflow`.
2. Here you can switch to the branch you want to run. Since the fork defaults to the `master` branch, if the template
   and configuration you modified are also in the `master` branch, just choose `master` here, and click `Run workflow`
   to confirm the run.

![Run Workflow](./images/workflows-run.png 'Run Workflow')

##### (3) Workflow in progress:

Wait a moment, and you will see that your first update workflow is running!
> [!NOTE]\
> The running time depends on the number of channels and pages in your template and other configurations, and also
> largely depends on the current network conditions. Please be patient. The default template and configuration usually
> take about 15 minutes.
![Workflow in progress](./images/workflow-running.png 'Workflow in progress')

##### (4) Cancel the running Workflow:

If you feel that this update is not quite right and you need to modify the template or configuration before running
again, you can click `Cancel run` to cancel this run.
![Cancel running Workflow](./images/workflow-cancel.png 'Cancel running Workflow')

##### (5) Workflow executed successfully:

If everything is normal, after a short wait, you will see that the workflow has been executed successfully (green check
mark).
![Workflow executed successfully](./images/workflow-success.png 'Workflow executed successfully')

At this point, you can visit the file link to see if the latest results have been synchronized:
https://raw.githubusercontent.com/your-github-username/repository-name/master/output/user_result.txt

Recommended CDN-accelerated URL:
{cdn_url}/https://raw.githubusercontent.com/your-github-username/repository-name/master/output/user_result.txt

![Username and Repository Name](./images/rep-info.png 'Username and Repository Name')

If you can access this link and it returns the updated interface content, then your live source interface link has been
successfully created! Simply copy and paste this link into software like `TVBox` in the configuration field to use~

> [!NOTE]\
> If you have modified the template or configuration files and want to execute the update immediately, you can manually
> trigger (2)`Run workflow`.

## Command Line

1. Install Python
   Please download and install Python from the official website, and select the option to add Python to the system
   environment variable Path during installation.

2. Run the update
   Open the terminal CMD in the project directory and run the following commands in sequence:

Install dependencies:

```shell
pip install pipenv
```

```shell
pipenv install --dev
```

Start the update:

```shell
pipenv run dev
```

Start the service:

```shell
pipenv run service
```

## GUI Software

1. Download the [IPTV-API Update Software](https://github.com/Guovin/iptv-api/releases), open the software, and click
   Start to perform the update.

2. Or run the following command in the project directory to open the GUI software:

```shell
pipenv run ui
```

![IPTV-API Update Software](./images/ui.png 'IPTV-API Update Software')

## Docker

### 1. Deployment with Compose

Download the [docker-compose.yml](../docker-compose.yml) or create one by copying the content (internal parameters can
be changed as needed), then run the following command in the path where the file is located:

```bash
docker compose up -d
```

### 2. Manual deployment with commands

#### (1) Pull the image

```bash
docker pull guovern/iptv-api:latest
```

🚀 Proxy acceleration (use this command if pulling fails, but it may download an older version):

```bash
docker pull docker.1ms.run/guovern/iptv-api:latest
```

#### (2) Run the container

```bash
docker run -d -p 80:8080 guovern/iptv-api
```

**Environment variables:**

| Variable        | Description                                                                                                      | Default   |
|:----------------|:-----------------------------------------------------------------------------------------------------------------|:----------|
| PUBLIC_DOMAIN   | Public domain or IP address, determines external access and the Host used in push stream results                 | 127.0.0.1 |
| PUBLIC_PORT     | Public port, set to the mapped port, determines external access address and the port used in push stream results | 80        |
| NGINX_HTTP_PORT | Nginx HTTP service port, needs to be mapped for external access                                                  | 8080      |

If you need to modify environment variables, add the following parameters after the above run command:

```bash
# Modify public domain
-e PUBLIC_DOMAIN=your.domain.com
# Modify public port
-e PUBLIC_PORT=80
```

In addition to the environment variables listed above, you can also override
the [configuration items](../docs/config_en.md) in the configuration file via environment variables.

**Mounts:** used to synchronize files between the host and the container. You can edit templates, configs, and access
generated result files directly on the host. Append the following options to the run command above:

```bash
# Mount config directory
-v /iptv-api/config:/iptv-api/config
# Mount output directory
-v /iptv-api/output:/iptv-api/output
```

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

**RTMP Streaming:**

> [!NOTE]
> 1. If deploying on a server, be sure to set the `PUBLIC_DOMAIN` environment variable to the server's domain name or IP
     address and the `PUBLIC_PORT` environment variable to the public port; otherwise the streaming addresses will not
     be accessible.
> 2. When streaming is enabled, obtained interfaces (e.g., subscription sources) will be streamed by default.
> 3. To stream local video sources, create an `hls` folder under the `config` directory and place video files named
     after the channel; the program will automatically stream them to the corresponding channels.

| Streaming Endpoint | Description                          |
|:-------------------|:-------------------------------------|
| /hls               | hls streaming endpoint               |
| /hls/txt           | hls txt streaming endpoint           |
| /hls/m3u           | hls m3u streaming endpoint           |
| /hls/ipv4          | hls ipv4 default streaming endpoint  |
| /hls/ipv6          | hls ipv6 default streaming endpoint  |
| /hls/ipv4/txt      | hls ipv4 txt streaming endpoint      |
| /hls/ipv4/m3u      | hls ipv4 m3u streaming endpoint      |
| /hls/ipv6/txt      | hls ipv6 txt streaming endpoint      |
| /hls/ipv6/m3u      | hls ipv6 m3u streaming endpoint      |
| /stat              | Streaming status statistics endpoint |
