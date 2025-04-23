# Tutorial

[中文](./tutorial.md) | English

IPTV-API is a highly customizable IPTV interface update project 📺, allowing you to customize channel menus,
automatically obtain live sources, and generate available results after speed testing and validation, achieving a 『✨
instant playback experience 🚀』.

There are four installation and operation methods in total, choose the one that suits you.

## Workflow Deployment

Use GitHub workflow deployment to automatically update the interface.

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
4. Modify the template and result file configuration:
    - source_file = config/user_demo.txt
    - final_file = output/user_result.txt
5. Click `Commit changes...` to save.

![Create user_config.ini](./images/edit-user-config.png 'Create user_config.ini')
![Edit final_file configuration](./images/edit-user-final-file.png 'Edit final_file configuration')
![Edit source_file configuration](./images/edit-user-source-file.png 'Edit source_file configuration')

Adjust the configuration as needed, here is the default configuration description:
[Configuration parameters](./config.md)

> [!NOTE]
> 1. For enabling interface information display, since some players (such as `PotPlayer`) do not support parsing
     interface
     supplementary information, causing playback failure, you can modify the configuration: `open_url_info = False` (
     GUI:
     uncheck display interface information) to disable this feature.
> 2. If your network supports IPv6, you can modify the configuration: `ipv6_support = True` (GUI: Check
     `Force assume the current network supports IPv6`) to skip the support check.
> 3. Enabling keyword search (disabled by default) will significantly increase the update time, not recommended to
     enable.

#### Similarly, you can customize subscription sources, blacklists, and whitelists (it is recommended to copy files and rename them with the

`user_` prefix).

- Subscription sources (`config/subscribe.txt`)

  Supports txt and m3u addresses as subscriptions, the program will read the channel interface data in sequence.
  ![Subscription sources](./images/subscribe.png 'Subscription sources')


- Local sources（`config/local.txt`）

  The channel interface data comes from local files, and the program will read the channel interface data in sequence.
  ![Local sources](./images/local.png 'Local sources')


- Blacklist (`config/blacklist.txt`)

  Interfaces that match the blacklist keywords will be filtered and not collected, such as low-quality interfaces with
  ads.
  ![Blacklist](./images/blacklist.png 'Blacklist')


- Whitelist (`config/whitelist.txt`)

  Interfaces or subscription sources in the whitelist will not participate in speed testing and will be prioritized at
  the top of the results. Fill in the channel name to directly retain the record in the final result, such as: CCTV-1,
  interface address, only filling in the interface address will apply to all channels, multiple records are entered on
  separate lines.
  ![Whitelist](./images/whitelist.png 'Whitelist')


- Multicast data (`config/rtp`)

  In addition, you can also maintain multicast source data yourself, the files are located in the config/rtp directory,
  and the file naming format is: `region_operator.txt`.
  ![Multicast data](./images/rtp.png 'Multicast data')

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
https://raw.githubusercontent.com/your\_github\_username/repository\_name (corresponding to the TV
created when forking)
/master/output/user\_result.txt

Or proxy address:
https://cdn.jsdelivr.net/gh/your\_github\_username/repository\_name (corresponding to the TV created when forking)
@master/output/user\_result.txt

![Username and Repository Name](./images/rep-info.png 'Username and Repository Name')

If you can access this link and it returns the updated interface content, then your live source interface link has been
successfully created! Simply copy and paste this link into software like `TVBox` in the configuration field to use~

> [!NOTE]\
> Except for the first execution of the workflow, which requires you to manually trigger it, subsequent
> executions (default: 6:00 AM and 18:00 PM Beijing time daily) will be automatically triggered. If you have modified
> the template or configuration files and want to execute the update immediately, you can manually trigger (2)
`Run workflow`.

#### 4. Modify Workflow Update Frequency (optional)

If you want to modify the update frequency (default: 6:00 AM and 18:00 PM Beijing time daily), you can modify the
`on: schedule: - cron` field:
![.github/workflows/main.yml](./images/schedule-cron.png '.github/workflows/main.yml')

If you want to perform updates every 2 days, you can modify it like this:

```bash
- cron: '0 22 */2 * *'
- cron: '0 10 */2 * *'
```

> [!WARNING]
> 1. It is strongly recommended not to set the update frequency too high, as there is no significant difference in
     interface content over a short period. High update frequency and long-running workflows may be considered resource
     abuse, leading to the risk of repository and account suspension.
> 2. Please monitor the runtime of your workflows. If you find the execution time too long, reduce the number of
     channels in the template, adjust the pagination and interface count in the configuration to comply with runtime
     requirements.

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

1. Download the [IPTV-API update software](https://github.com/Guovin/iptv-api/releases), open the software, and click
   update to complete the update.

2. Or run the following command in the project directory to open the GUI software:

```shell
pipenv run ui
```

![IPTV-API Update Software](./images/ui.png 'IPTV-API Update Software')

If you do not understand the software configuration options, do not change anything, just click start.

## Docker

### 1. Pull the image

```bash
docker pull guovern/iptv-api:latest
```

🚀 Proxy acceleration (recommended for users in China):

```bash
docker pull docker.1ms.run/guovern/iptv-api:latest
```

### 2. Run the container

```bash
docker run -d -p 8000:8000 guovern/iptv-api
```

#### Mount (recommended):

This allows synchronization of files between the host machine and the container. Modifying templates, configurations,
and retrieving updated result files can be directly operated in the host machine's folder.

Taking the host path /etc/docker as an example:

```bash
-v /etc/docker/config:/iptv-api/config
-v /etc/docker/output:/iptv-api/output
```

> [!WARNING]\
> If you pull the image again to update the version, and there are changes or additions to the configuration files, be
> sure to overwrite the old configuration files in the host (config directory), as the host configuration files cannot
> be
> updated automatically. Otherwise, the container will still run with the old configuration.

#### Environment Variables:

| Variable    | Description          | Default Value      |
|:------------|:---------------------|:-------------------|
| APP_HOST    | Service host address | "http://localhost" |
| APP_PORT    | Service port         | 8000               |
| UPDATE_CRON | Scheduled task time  | "0 22,10 * * *"    |

### 3. Update Results

| Endpoint  | Description           |
|:----------|:----------------------|
| /         | Default endpoint      |
| /m3u      | m3u format endpoint   |
| /txt      | txt format endpoint   |
| /ipv4     | ipv4 default endpoint |
| /ipv6     | ipv6 default endpoint |
| /ipv4/txt | ipv4 txt endpoint     |
| /ipv6/txt | ipv6 txt endpoint     |
| /ipv4/m3u | ipv4 m3u endpoint     |
| /ipv6/m3u | ipv6 m3u endpoint     |
| /content  | Endpoint content      |
| /log      | Speed test log        |

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
