import tkinter as tk
from tkinter import ttk

from utils.config import config


class SpeedUI:
    def init_ui(self, root=None):
        """
        Init speed UI
        """
        frame_default_sort = tk.Frame(root)
        frame_default_sort.pack(fill=tk.X)
        frame_default_sort_column1 = tk.Frame(frame_default_sort)
        frame_default_sort_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_sort_column2 = tk.Frame(frame_default_sort)
        frame_default_sort_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_speed_test_label = tk.Label(
            frame_default_sort_column1, text="开启测速:", width=12
        )
        self.open_speed_test_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_speed_test_var = tk.BooleanVar(value=config.open_speed_test)
        self.open_speed_test_checkbutton = ttk.Checkbutton(
            frame_default_sort_column1,
            variable=self.open_speed_test_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_speed_test,
        )
        self.open_speed_test_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.speed_test_limit_label = tk.Label(
            frame_default_sort_column2, text="测速并发:", width=12
        )
        self.speed_test_limit_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.speed_test_limit_entry = tk.Entry(frame_default_sort_column2, width=10)
        self.speed_test_limit_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.speed_test_limit_entry.insert(0, config.speed_test_limit)
        self.speed_test_limit_entry.bind("<KeyRelease>", self.update_speed_test_limit)

        self.speed_test_timeout_label = tk.Label(
            frame_default_sort_column2, text="响应超时(s):", width=12
        )
        self.speed_test_timeout_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.speed_test_timeout_entry = tk.Entry(frame_default_sort_column2, width=10)
        self.speed_test_timeout_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.speed_test_timeout_entry.insert(0, config.speed_test_timeout)
        self.speed_test_timeout_entry.bind("<KeyRelease>", self.update_speed_test_timeout)

        frame_default_sort_mode = tk.Frame(root)
        frame_default_sort_mode.pack(fill=tk.X)
        frame_default_sort_mode_column1 = tk.Frame(frame_default_sort_mode)
        frame_default_sort_mode_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_sort_mode_column2 = tk.Frame(frame_default_sort_mode)
        frame_default_sort_mode_column2.pack(side=tk.RIGHT, fill=tk.Y)

        frame_default_speed_params = tk.Frame(root)
        frame_default_speed_params.pack(fill=tk.X)
        frame_default_speed_params_column1 = tk.Frame(
            frame_default_speed_params
        )
        frame_default_speed_params_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_speed_params_column2 = tk.Frame(
            frame_default_speed_params
        )
        frame_default_speed_params_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_filter_speed_label = tk.Label(
            frame_default_speed_params_column1, text="速率过滤:", width=12
        )
        self.open_filter_speed_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_filter_speed_var = tk.BooleanVar(
            value=config.open_filter_speed
        )
        self.open_filter_speed_checkbutton = ttk.Checkbutton(
            frame_default_speed_params_column1,
            variable=self.open_filter_speed_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_filter_speed
        )
        self.open_filter_speed_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.min_speed_label = tk.Label(
            frame_default_speed_params_column2, text="最小速率(M/s):", width=12
        )
        self.min_speed_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.min_speed_entry = tk.Entry(
            frame_default_speed_params_column2, width=10
        )
        self.min_speed_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.min_speed_entry.insert(0, config.min_speed)
        self.min_speed_entry.bind("<KeyRelease>", self.update_min_speed)

        frame_default_resolution_params = tk.Frame(root)
        frame_default_resolution_params.pack(fill=tk.X)
        frame_default_resolution_params_column1 = tk.Frame(
            frame_default_resolution_params
        )
        frame_default_resolution_params_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_resolution_params_column2 = tk.Frame(
            frame_default_resolution_params
        )
        frame_default_resolution_params_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_filter_resolution_label = tk.Label(
            frame_default_resolution_params_column1, text="分辨率过滤:", width=12
        )
        self.open_filter_resolution_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_filter_resolution_var = tk.BooleanVar(
            value=config.open_filter_resolution
        )
        self.open_filter_resolution_checkbutton = ttk.Checkbutton(
            frame_default_resolution_params_column1,
            variable=self.open_filter_resolution_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_filter_resolution
        )
        self.open_filter_resolution_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.min_resolution_label = tk.Label(
            frame_default_resolution_params_column2, text="最小分辨率:", width=12
        )
        self.min_resolution_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.min_resolution_entry = tk.Entry(
            frame_default_resolution_params_column2, width=10
        )
        self.min_resolution_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.min_resolution_entry.insert(0, config.min_resolution)
        self.min_resolution_entry.bind("<KeyRelease>", self.update_min_resolution)

        self.max_resolution_label = tk.Label(
            frame_default_resolution_params_column2, text="最大分辨率:", width=12
        )
        self.max_resolution_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.max_resolution_entry = tk.Entry(
            frame_default_resolution_params_column2, width=10
        )
        self.max_resolution_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.max_resolution_entry.insert(0, config.max_resolution)
        self.max_resolution_entry.bind("<KeyRelease>", self.update_max_resolution)

        frame_default_sort_params = tk.Frame(root)
        frame_default_sort_params.pack(fill=tk.X)

        self.speed_test_filter_host_label = tk.Label(
            frame_default_sort_params, text="共享Host结果:", width=12
        )
        self.speed_test_filter_host_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.speed_test_filter_host_var = tk.BooleanVar(
            value=config.speed_test_filter_host
        )
        self.speed_test_filter_host_checkbutton = ttk.Checkbutton(
            frame_default_sort_params,
            variable=self.speed_test_filter_host_var,
            onvalue=True,
            offvalue=False,
            command=self.update_speed_test_filter_host
        )
        self.speed_test_filter_host_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

    def update_open_speed_test(self):
        config.set("Settings", "open_speed_test", str(self.open_speed_test_var.get()))

    def update_speed_test_limit(self, event):
        config.set("Settings", "speed_test_limit", self.speed_test_limit_entry.get())

    def update_speed_test_timeout(self, event):
        config.set("Settings", "speed_test_timeout", self.speed_test_timeout_entry.get())

    def update_open_filter_speed(self):
        config.set(
            "Settings",
            "open_filter_speed",
            str(self.open_filter_speed_var.get()),
        )

    def update_min_speed(self, event):
        config.set("Settings", "min_speed", self.min_speed_entry.get())

    def update_open_filter_resolution(self):
        config.set(
            "Settings",
            "open_filter_resolution",
            str(self.open_filter_resolution_var.get()),
        )

    def update_min_resolution(self, event):
        config.set("Settings", "min_resolution", self.min_resolution_entry.get())

    def update_max_resolution(self, event):
        config.set("Settings", "max_resolution", self.max_resolution_entry.get())

    def update_speed_test_filter_host(self, event):
        config.set("Settings", "speed_test_filter_host", self.speed_test_filter_host_var.get())

    def change_entry_state(self, state):
        for entry in [
            "open_speed_test_checkbutton",
            "speed_test_limit_entry",
            "speed_test_timeout_entry",
            "open_filter_speed_checkbutton",
            "min_speed_entry",
            "open_filter_resolution_checkbutton",
            "min_resolution_entry",
            "max_resolution_entry",
            "speed_test_filter_host_checkbutton"
        ]:
            getattr(self, entry).config(state=state)
