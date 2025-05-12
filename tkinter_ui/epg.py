import os
import os.path
import tkinter as tk
from tkinter import ttk

import utils.constants as constants
from utils.config import config
from utils.tools import resource_path


class EpgUI:
    def init_ui(self, root):
        """
        Init epg UI
        """
        frame_epg_open_epg = tk.Frame(root)
        frame_epg_open_epg.pack(fill=tk.X)

        self.open_epg_label = tk.Label(
            frame_epg_open_epg, text="开启EPG源:", width=9
        )
        self.open_epg_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_epg_var = tk.BooleanVar(value=config.open_epg)
        self.open_epg_checkbutton = ttk.Checkbutton(
            frame_epg_open_epg,
            variable=self.open_epg_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_epg,
        )
        self.open_epg_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_epg_epg_urls = tk.Frame(root)
        frame_epg_epg_urls.pack(fill=tk.X)
        frame_epg_urls_column1 = tk.Frame(frame_epg_epg_urls)
        frame_epg_urls_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_epg_urls_column2 = tk.Frame(frame_epg_epg_urls)
        frame_epg_urls_column2.pack(side=tk.LEFT, fill=tk.Y)

        self.epg_urls_label = tk.Label(
            frame_epg_urls_column1, text="EPG:", width=9
        )
        self.epg_urls_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.epg_file_button = tk.ttk.Button(
            frame_epg_urls_column2,
            text="编辑",
            command=self.edit_epg_file,
        )
        self.epg_file_button.pack(side=tk.LEFT, padx=4, pady=0)

    def update_open_epg(self):
        config.set("Settings", "open_epg", str(self.open_epg_var.get()))

    def edit_epg_file(self):
        path = resource_path(constants.epg_path)
        if os.path.exists(path):
            os.system(f'notepad.exe {path}')

    def change_entry_state(self, state):
        for entry in [
            "open_epg_checkbutton",
            "epg_file_button",
        ]:
            getattr(self, entry).config(state=state)
