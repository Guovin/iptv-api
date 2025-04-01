import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import utils.constants as constants
from utils.config import config
from utils.tools import resource_path


class DefaultUI:

    def init_ui(self, root):
        """
        Init default UI
        """
        frame_default_source_file = tk.Frame(root)
        frame_default_source_file.pack(fill=tk.X)
        frame_default_source_file_column1 = tk.Frame(frame_default_source_file)
        frame_default_source_file_column1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frame_default_source_file_column2 = tk.Frame(frame_default_source_file)
        frame_default_source_file_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.source_file_label = tk.Label(
            frame_default_source_file_column1, text="模板文件:", width=8
        )
        self.source_file_entry = tk.Entry(frame_default_source_file_column1)
        self.source_file_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.source_file_entry.pack(fill=tk.X, padx=4, expand=True)
        self.source_file_entry.insert(0, config.source_file)

        self.source_file_button = tk.ttk.Button(
            frame_default_source_file_column2,
            text="选择文件",
            command=self.select_source_file,
        )
        self.source_file_button.pack(side=tk.LEFT, padx=4, pady=0)

        self.source_file_edit_button = tk.ttk.Button(
            frame_default_source_file_column2,
            text="编辑",
            command=lambda: self.edit_file(config.source_file),
        )
        self.source_file_edit_button.pack(side=tk.LEFT, padx=4, pady=0)

        frame_default_final_file = tk.Frame(root)
        frame_default_final_file.pack(fill=tk.X)
        frame_default_final_file_column1 = tk.Frame(frame_default_final_file)
        frame_default_final_file_column1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frame_default_final_file_column2 = tk.Frame(frame_default_final_file)
        frame_default_final_file_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.final_file_label = tk.Label(
            frame_default_final_file_column1, text="结果文件:", width=8
        )
        self.final_file_entry = tk.Entry(frame_default_final_file_column1)
        self.final_file_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.final_file_entry.pack(fill=tk.X, padx=4, expand=True)
        self.final_file_entry.insert(0, config.final_file)

        self.final_file_button = tk.ttk.Button(
            frame_default_final_file_column2,
            text="选择文件",
            command=self.select_final_file,
        )
        self.final_file_button.pack(side=tk.LEFT, padx=4, pady=0)

        self.final_file_edit_button = tk.ttk.Button(
            frame_default_final_file_column2,
            text="编辑",
            command=lambda: self.edit_file(config.final_file),
        )
        self.final_file_edit_button.pack(side=tk.LEFT, padx=4, pady=0)

        frame_default_open_update = tk.Frame(root)
        frame_default_open_update.pack(fill=tk.X)
        frame_default_open_update_column1 = tk.Frame(frame_default_open_update)
        frame_default_open_update_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_open_update_column2 = tk.Frame(frame_default_open_update)
        frame_default_open_update_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_update_label = tk.Label(
            frame_default_open_update_column1, text="开启更新:", width=12
        )
        self.open_update_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_update_var = tk.BooleanVar(value=config.open_update)
        self.open_update_checkbutton = ttk.Checkbutton(
            frame_default_open_update_column1,
            variable=self.open_update_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_update
        )
        self.open_update_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.open_service_label = tk.Label(
            frame_default_open_update_column2, text="开启服务:", width=8
        )
        self.open_service_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_service_var = tk.BooleanVar(value=config.open_service)
        self.open_service_checkbutton = ttk.Checkbutton(
            frame_default_open_update_column2,
            variable=self.open_service_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_service
        )
        self.open_service_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.app_port_label = tk.Label(
            frame_default_open_update_column2, text="端口:", width=3
        )
        self.app_port_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.app_port_entry = tk.Entry(frame_default_open_update_column2, width=8)
        self.app_port_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.app_port_entry.insert(0, config.app_port)
        self.app_port_entry.bind("<KeyRelease>", self.update_app_port)

        frame_default_open_cache = tk.Frame(root)
        frame_default_open_cache.pack(fill=tk.X)
        frame_default_open_cache_column1 = tk.Frame(frame_default_open_cache)
        frame_default_open_cache_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_open_cache_column2 = tk.Frame(frame_default_open_cache)
        frame_default_open_cache_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_rtmp_label = tk.Label(
            frame_default_open_cache_column1, text="开启推流:", width=12
        )
        self.open_rtmp_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_rtmp_var = tk.BooleanVar(value=config.open_rtmp)
        self.open_rtmp_checkbutton = ttk.Checkbutton(
            frame_default_open_cache_column1,
            variable=self.open_rtmp_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_rtmp
        )
        self.open_rtmp_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.open_history_label = tk.Label(
            frame_default_open_cache_column2, text="使用历史结果:", width=12
        )
        self.open_history_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_history_var = tk.BooleanVar(value=config.open_history)
        self.open_history_checkbutton = ttk.Checkbutton(
            frame_default_open_cache_column2,
            variable=self.open_history_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_history,
        )
        self.open_history_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.open_use_cache_label = tk.Label(
            frame_default_open_cache_column2, text="使用离线数据:", width=12
        )
        self.open_use_cache_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_use_cache_var = tk.BooleanVar(value=config.open_use_cache)
        self.open_use_cache_checkbutton = ttk.Checkbutton(
            frame_default_open_cache_column2,
            variable=self.open_use_cache_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_use_cache,
        )
        self.open_use_cache_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_default_mode = tk.Frame(root)
        frame_default_mode.pack(fill=tk.X)
        frame_default_mode_params_column1 = tk.Frame(frame_default_mode)
        frame_default_mode_params_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_mode_params_column2 = tk.Frame(frame_default_mode)
        frame_default_mode_params_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_request_label = tk.Label(
            frame_default_mode_params_column1, text="开启网络请求:", width=12
        )
        self.open_request_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_request_var = tk.BooleanVar(value=config.open_request)
        self.open_request_checkbutton = ttk.Checkbutton(
            frame_default_mode_params_column1,
            variable=self.open_request_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_request
        )
        self.open_request_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.request_timeout_label = tk.Label(
            frame_default_mode_params_column2, text="请求超时(s):", width=12
        )
        self.request_timeout_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.request_timeout_entry = tk.Entry(frame_default_mode_params_column2, width=8)
        self.request_timeout_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.request_timeout_entry.insert(0, config.request_timeout)
        self.request_timeout_entry.bind("<KeyRelease>", self.update_request_timeout)

        frame_default_channel = tk.Frame(root)
        frame_default_channel.pack(fill=tk.X)
        frame_default_channel_column1 = tk.Frame(frame_default_channel)
        frame_default_channel_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_channel_column2 = tk.Frame(frame_default_channel)
        frame_default_channel_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.urls_limit_label = tk.Label(
            frame_default_channel_column1, text="频道接口数量:", width=12
        )
        self.urls_limit_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.urls_limit_entry = tk.Entry(frame_default_channel_column1, width=8)
        self.urls_limit_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.urls_limit_entry.insert(0, config.urls_limit)
        self.urls_limit_entry.bind("<KeyRelease>", self.update_urls_limit)

        self.ipv_type_label = tk.Label(
            frame_default_channel_column2, text="接口协议类型:", width=12
        )
        self.ipv_type_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.ipv_type_combo = ttk.Combobox(frame_default_channel_column2, width=5)
        self.ipv_type_combo.pack(side=tk.LEFT, padx=4, pady=8)
        self.ipv_type_combo["values"] = ("IPv4", "IPv6", "全部")
        if config.ipv_type == "ipv4":
            self.ipv_type_combo.current(0)
        elif config.ipv_type == "ipv6":
            self.ipv_type_combo.current(1)
        else:
            self.ipv_type_combo.current(2)
        self.ipv_type_combo.bind("<<ComboboxSelected>>", self.update_ipv_type)

        frame_proxy_mode = tk.Frame(root)
        frame_proxy_mode.pack(fill=tk.X)
        frame_proxy_mode_params_column1 = tk.Frame(frame_proxy_mode)
        frame_proxy_mode_params_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_proxy_mode_params_column2 = tk.Frame(frame_proxy_mode)
        frame_proxy_mode_params_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_proxy_label = tk.Label(
            frame_proxy_mode_params_column1, text="开启代理查询:", width=12
        )
        self.open_proxy_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_proxy_var = tk.BooleanVar(value=config.open_proxy)
        self.open_proxy_checkbutton = ttk.Checkbutton(
            frame_proxy_mode_params_column1,
            variable=self.open_proxy_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_proxy
        )
        self.open_proxy_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.open_keep_all_label = tk.Label(
            frame_proxy_mode_params_column2, text="完整记录:", width=12
        )
        self.open_keep_all_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_keep_all_var = tk.BooleanVar(value=config.open_keep_all)
        self.open_keep_all_checkbutton = ttk.Checkbutton(
            frame_proxy_mode_params_column2,
            variable=self.open_keep_all_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_keep_all
        )
        self.open_keep_all_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_m3u = tk.Frame(root)
        frame_m3u.pack(fill=tk.X)
        frame_proxy_m3u_column1 = tk.Frame(frame_m3u)
        frame_proxy_m3u_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_proxy_m3u_column2 = tk.Frame(frame_m3u)
        frame_proxy_m3u_column2.pack(side=tk.RIGHT, fill=tk.Y)
        self.open_m3u_result_label = tk.Label(
            frame_proxy_m3u_column1, text="M3U转换:", width=12
        )
        self.open_m3u_result_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_m3u_result_var = tk.BooleanVar(value=config.open_m3u_result)
        self.open_m3u_result_checkbutton = ttk.Checkbutton(
            frame_proxy_m3u_column1,
            variable=self.open_m3u_result_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_m3u_result
        )
        self.open_m3u_result_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.open_driver_label = tk.Label(
            frame_proxy_m3u_column2, text="浏览器模式:", width=12
        )
        self.open_driver_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_driver_var = tk.BooleanVar(value=config.open_driver)
        self.open_driver_checkbutton = ttk.Checkbutton(
            frame_proxy_m3u_column2,
            variable=self.open_driver_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_driver
        )
        self.open_driver_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_default_open_update_info = tk.Frame(root)
        frame_default_open_update_info.pack(fill=tk.X)
        frame_default_open_update_info_column1 = tk.Frame(
            frame_default_open_update_info
        )
        frame_default_open_update_info_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_open_update_info_column2 = tk.Frame(
            frame_default_open_update_info
        )
        frame_default_open_update_info_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_update_time_label = tk.Label(
            frame_default_open_update_info_column1, text="显示更新时间:", width=12
        )
        self.open_update_time_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_update_time_var = tk.BooleanVar(value=config.open_update_time)
        self.open_update_time_checkbutton = ttk.Checkbutton(
            frame_default_open_update_info_column1,
            variable=self.open_update_time_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_update_time,
        )
        self.open_update_time_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.update_time_position_label = tk.Label(
            frame_default_open_update_info_column1, text="位置:", width=3
        )
        self.update_time_position_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.update_time_position_combo = ttk.Combobox(frame_default_open_update_info_column1, width=5)
        self.update_time_position_combo.pack(side=tk.LEFT, padx=4, pady=8)
        self.update_time_position_combo["values"] = ("顶部", "底部")
        if config.update_time_position == "bottom":
            self.update_time_position_combo.current(1)
        else:
            self.update_time_position_combo.current(0)
        self.update_time_position_combo.bind("<<ComboboxSelected>>", self.update_update_time_position)

        self.open_url_info_label = tk.Label(
            frame_default_open_update_info_column2, text="显示接口信息:", width=12
        )
        self.open_url_info_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_url_info_var = tk.BooleanVar(value=config.open_url_info)
        self.open_url_info_checkbutton = ttk.Checkbutton(
            frame_default_open_update_info_column2,
            variable=self.open_url_info_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_url_info,
        )
        self.open_url_info_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_default_open_empty_category = tk.Frame(root)
        frame_default_open_empty_category.pack(fill=tk.X)
        frame_default_open_empty_category_column1 = tk.Frame(
            frame_default_open_empty_category
        )
        frame_default_open_empty_category_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_open_empty_category_column2 = tk.Frame(
            frame_default_open_empty_category
        )
        frame_default_open_empty_category_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_empty_category_label = tk.Label(
            frame_default_open_empty_category_column1, text="显示无结果分类:", width=12
        )
        self.open_empty_category_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_empty_category_var = tk.BooleanVar(value=config.open_empty_category)
        self.open_empty_category_checkbutton = ttk.Checkbutton(
            frame_default_open_empty_category_column1,
            variable=self.open_empty_category_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_empty_category,
        )
        self.open_empty_category_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.ipv6_support_label = tk.Label(
            frame_default_open_empty_category_column2, text="强制支持IPv6:", width=12
        )
        self.ipv6_support_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.ipv6_support_var = tk.BooleanVar(value=config.ipv6_support)
        self.ipv6_support_checkbutton = ttk.Checkbutton(
            frame_default_open_empty_category_column2,
            variable=self.ipv6_support_var,
            onvalue=True,
            offvalue=False,
            command=self.update_ipv6_support,
        )
        self.ipv6_support_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_time_zone = tk.Frame(root)
        frame_time_zone.pack(fill=tk.X)
        frame_time_zone_column1 = tk.Frame(
            frame_time_zone
        )
        frame_time_zone_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_time_zone_column2 = tk.Frame(
            frame_time_zone
        )
        frame_time_zone_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.time_zone_label = tk.Label(
            frame_time_zone_column1, text="时区:", width=12
        )
        self.time_zone_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.time_zone_entry = tk.Entry(frame_time_zone_column1, width=16)
        self.time_zone_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.time_zone_entry.insert(0, config.time_zone)
        self.time_zone_entry.bind("<KeyRelease>", self.update_time_zone)

        self.cdn_url_label = tk.Label(
            frame_time_zone_column2, text="CDN加速地址:", width=12
        )
        self.cdn_url_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.cdn_url_entry = tk.Entry(frame_time_zone_column2, width=20)
        self.cdn_url_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.cdn_url_entry.insert(0, config.cdn_url)
        self.cdn_url_entry.bind("<KeyRelease>", self.update_cdn_url)

        frame_default_url_keywords = tk.Frame(root)
        frame_default_url_keywords.pack(fill=tk.X)
        frame_default_url_keywords_column1 = tk.Frame(frame_default_url_keywords)
        frame_default_url_keywords_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_url_keywords_column2 = tk.Frame(frame_default_url_keywords)
        frame_default_url_keywords_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.url_keywords_whitelist_label = tk.Label(
            frame_default_url_keywords_column1, text="白名单:", width=12
        )
        self.url_keywords_whitelist_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.whitelist_file_button = tk.ttk.Button(
            frame_default_url_keywords_column1,
            text="编辑",
            command=self.edit_whitelist_file,
        )
        self.whitelist_file_button.pack(side=tk.LEFT, padx=4, pady=0)
        self.url_keywords_blacklist_label = tk.Label(
            frame_default_url_keywords_column2, text="黑名单:", width=12
        )
        self.url_keywords_blacklist_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.blacklist_file_button = tk.ttk.Button(
            frame_default_url_keywords_column2,
            text="编辑",
            command=self.edit_blacklist_file,
        )
        self.blacklist_file_button.pack(side=tk.LEFT, padx=4, pady=0)

    def update_open_update(self):
        config.set("Settings", "open_update", str(self.open_update_var.get()))

    def update_open_service(self):
        config.set("Settings", "open_service", str(self.open_update_var.get()))

    def update_app_port(self, event):
        config.set("Settings", "app_port", self.app_port_entry.get())

    def update_open_rtmp(self):
        config.set("Settings", "open_rtmp", str(self.open_rtmp_var.get()))

    def update_open_history(self):
        config.set(
            "Settings", "open_history", str(self.open_history_var.get())
        )

    def update_open_use_cache(self):
        config.set(
            "Settings", "open_use_cache", str(self.open_use_cache_var.get())
        )

    def select_source_file(self):
        filepath = filedialog.askopenfilename(
            initialdir=os.getcwd(), title="选择模板文件", filetypes=[("txt", "*.txt")]
        )
        if filepath:
            self.source_file_entry.delete(0, tk.END)
            self.source_file_entry.insert(0, filepath)
            config.set("Settings", "source_file", filepath)

    def select_final_file(self):
        filepath = filedialog.askopenfilename(
            initialdir=os.getcwd(), title="选择结果文件", filetypes=[("txt", "*.txt")]
        )
        if filepath:
            self.final_file_entry.delete(0, tk.END)
            self.final_file_entry.insert(0, filepath)
            config.set("Settings", "final_file", filepath)

    def update_open_request(self):
        config.set("Settings", "open_requests", str(self.open_request_var.get()))

    def update_open_driver(self):
        config.set("Settings", "open_driver", str(self.open_driver_var.get()))

    def update_open_proxy(self):
        config.set("Settings", "open_proxy", str(self.open_proxy_var.get()))

    def update_open_keep_all(self):
        config.set("Settings", "open_keep_all", str(self.open_keep_all_var.get()))

    def update_open_m3u_result(self):
        config.set("Settings", "open_m3u_result", str(self.open_m3u_result_var.get()))

    def update_request_timeout(self, event):
        config.set("Settings", "request_timeout", self.request_timeout_entry.get())

    def update_urls_limit(self, event):
        config.set("Settings", "urls_limit", self.urls_limit_entry.get())

    def update_time_zone(self, event):
        config.set("Settings", "time_zone", self.time_zone_entry.get())

    def update_cdn_url(self, event):
        config.set("Settings", "cdn_url", self.cdn_url_entry.get())

    def update_open_update_time(self):
        config.set("Settings", "open_update_time", str(self.open_update_time_var.get()))

    def update_open_url_info(self):
        config.set("Settings", "open_url_info", str(self.open_url_info_var.get()))

    def update_open_empty_category(self):
        config.set(
            "Settings", "open_empty_category", str(self.open_empty_category_var.get())
        )

    def update_ipv6_support(self):
        config.set(
            "Settings", "ipv6_support", str(self.ipv6_support_var.get())
        )

    def update_ipv_type(self, event):
        config.set("Settings", "ipv_type", self.ipv_type_combo.get())

    def update_update_time_position(self, event):
        config.set("Settings", "update_time_position",
                   'bottom' if self.update_time_position_combo.get() == '底部' else 'top')

    def edit_file(self, path):
        if os.path.exists(resource_path(path)):
            os.system(f'notepad.exe {path}')
        else:
            print(f"File {path} not found!")
            messagebox.showerror("Error", f"File {path} not found!")

    def edit_whitelist_file(self):
        self.edit_file(constants.whitelist_path)

    def edit_blacklist_file(self):
        self.edit_file(constants.blacklist_path)

    def change_entry_state(self, state):
        for entry in [
            "open_update_checkbutton",
            "open_service_checkbutton",
            "app_port_entry",
            "open_rtmp_checkbutton",
            "open_history_checkbutton",
            "open_use_cache_checkbutton",
            "open_request_checkbutton",
            "open_driver_checkbutton",
            "open_proxy_checkbutton",
            "request_timeout_entry",
            "source_file_entry",
            "source_file_button",
            "source_file_edit_button",
            "time_zone_entry",
            "cdn_url_entry",
            "final_file_entry",
            "final_file_button",
            "final_file_edit_button",
            "open_keep_all_checkbutton",
            "open_m3u_result_checkbutton",
            "urls_limit_entry",
            "update_time_position_combo",
            "open_update_time_checkbutton",
            "open_url_info_checkbutton",
            "open_empty_category_checkbutton",
            "ipv_type_combo",
            "ipv6_support_checkbutton",
            "whitelist_file_button",
            "blacklist_file_button",
        ]:
            getattr(self, entry).config(state=state)
