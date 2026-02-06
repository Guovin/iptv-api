import os
import os.path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import utils.constants as constants
from utils.config import config
from utils.tools import resource_path


class LocalUI:
    def init_ui(self, root):
        """
        Init local UI
        """
        frame_local_open_local = tk.Frame(root)
        frame_local_open_local.pack(fill=tk.X)

        self.open_local_label = tk.Label(
            frame_local_open_local, text="开启本地源:", width=8
        )
        self.open_local_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_local_var = tk.BooleanVar(value=config.open_local)
        self.open_local_checkbutton = ttk.Checkbutton(
            frame_local_open_local,
            variable=self.open_local_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_local,
        )
        self.open_local_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_local_file = tk.Frame(root)
        frame_local_file.pack(fill=tk.X)

        self.local_file_edit_button = tk.ttk.Button(
            frame_local_file,
            text="编辑",
            command=lambda: self.edit_file(constants.local_path),
        )
        self.local_file_edit_button.pack(side=tk.LEFT, padx=4, pady=0)

    def update_open_local(self):
        config.set("Settings", "open_local", str(self.open_local_var.get()))

    def select_local_file(self):
        filepath = filedialog.askopenfilename(
            initialdir=os.getcwd(), title="选择本地源文件", filetypes=[("txt", "*.txt")]
        )
        if filepath:
            self.local_file_entry.delete(0, tk.END)
            self.local_file_entry.insert(0, filepath)
            config.set("Settings", "local_file", filepath)

    def edit_file(self, path):
        if os.path.exists(resource_path(path)):
            os.system(f'notepad.exe {path}')
        else:
            print(f"File {path} not found!")
            messagebox.showerror("Error", f"File {path} not found!")

    def change_entry_state(self, state):
        for entry in [
            "open_local_checkbutton",
            "local_file_edit_button",
        ]:
            getattr(self, entry).config(state=state)
