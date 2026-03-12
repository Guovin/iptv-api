import datetime
import os
import sys

from utils.ffmpeg import check_ffmpeg_installed_status

sys.path.append(os.path.dirname(sys.path[0]))
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from utils.config import config
from utils.tools import resource_path, get_version_info
from main import UpdateSource
import asyncio
import threading
import webbrowser
from about import AboutUI
from default import DefaultUI
from speed import SpeedUI
from prefer import PreferUI
from local import LocalUI
from subscribe import SubscribeUI
from epg import EpgUI
import pystray
from service.app import run_service


class TkinterUI:
    def __init__(self, root):
        info = get_version_info()
        self.root = root
        self.name = info.get("name", "")
        self.tray_icon = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_tray_icon()
        self.root.title(self.name)
        self.version = info.get("version", "")
        self.about_ui = AboutUI()
        self.default_ui = DefaultUI()
        self.speed_ui = SpeedUI()
        self.prefer_ui = PreferUI()
        self.local_ui = LocalUI()
        self.subscribe_ui = SubscribeUI()
        self.epg_ui = EpgUI()
        self.update_source = UpdateSource()
        self.update_running = False
        self.result_url = None
        self.now = None

    def on_closing(self):
        if messagebox.askyesno("提示",
                               "最小化至后台运行?",
                               icon="question",
                               default="yes",
                               detail="选择“是”将最小化至后台运行，选择“否”将退出程序"
                               ):
            self.root.withdraw()
            if not self.tray_icon:
                self.create_tray_icon()
        else:
            self.root.destroy()

    def create_tray_icon(self):
        image = Image.open(resource_path("favicon.ico"))
        menu = (pystray.MenuItem("显示", self.restore_window, default=True), pystray.MenuItem("退出", self.exit_app))
        self.tray_icon = pystray.Icon("name", image, self.name, menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_window(self):
        self.root.deiconify()

    def exit_app(self):
        self.tray_icon.stop()
        self.root.destroy()

    def view_result_link_callback(self, event):
        webbrowser.open_new_tab(self.result_url)

    def save_config(self):
        config.save()
        messagebox.showinfo("提示", "保存成功")

    def change_state(self, state):
        self.default_ui.change_entry_state(state=state)
        self.speed_ui.change_entry_state(state=state)
        self.prefer_ui.change_entry_state(state=state)
        self.local_ui.change_entry_state(state=state)
        self.subscribe_ui.change_entry_state(state=state)
        self.epg_ui.change_entry_state(state=state)

    async def run_update(self):
        self.update_running = not self.update_running
        if self.update_running:
            self.run_button.config(text="取消更新", state="normal")
            self.change_state("disabled")
            self.progress_bar["value"] = 0
            self.progress_label.pack()
            self.view_result_link.pack()
            self.progress_bar.pack()
            await self.update_source.start(self.update_progress)
        else:
            self.stop()
            self.update_source.stop()
            self.run_button.config(text="启动", state="normal")
            self.change_state("normal")
            self.progress_bar.pack_forget()
            self.view_result_link.pack_forget()
            self.progress_label.pack_forget()

    def on_run_update(self):
        if not self.update_running and (
                config.open_filter_resolution or config.open_rtmp) and not check_ffmpeg_installed_status():
            if messagebox.askyesno("提示",
                                   "使用分辨率、推流相关功能需要安装FFmpeg，为了实现更佳的观看体验，\n是否前往官网下载？"):
                return webbrowser.open("https://ffmpeg.org")

        if self.now:
            self.update_source.stop()

        loop = asyncio.new_event_loop()

        def run_loop():
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run_update())

        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        asyncio.get_event_loop().stop()

    def update_progress(self, title, progress, finished=False, url=None, now=None):
        self.progress_bar["value"] = progress
        self.now = now
        if finished and now:
            next_time = now + datetime.timedelta(hours=config.update_interval)
            title += f", 🕒下次更新时间: {next_time:%Y-%m-%d %H:%M:%S}"
        progress_text = f"{title}, 进度: {progress}%" if not finished else f"{title}"
        self.progress_label["text"] = progress_text
        self.root.update()
        if finished:
            self.run_button.config(text="定时更新中(重启)" if now else "启动", state="normal")
            self.update_running = False
            self.change_state("normal")
            if url:
                self.view_result_link.config(text=url)
                self.result_url = url

    def init_UI(self):

        menu_bar = tk.Menu(self.root)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(
            label="关于",
            command=lambda: self.about_ui.init_ui(root=self.root, version=self.version),
        )
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        self.root.config(menu=menu_bar)

        notebook = tk.ttk.Notebook(self.root)
        notebook.pack(fill="both", padx=10, pady=5)

        frame_default = tk.ttk.Frame(notebook)
        frame_speed = tk.ttk.Frame(notebook)
        frame_prefer = tk.ttk.Frame(notebook)
        frame_local = tk.ttk.Frame(notebook)
        frame_subscribe = tk.ttk.Frame(notebook)
        frame_epg = tk.ttk.Frame(notebook)

        settings_icon_source = Image.open(
            resource_path("static/images/settings_icon.png")
        ).resize((16, 16))
        settings_icon = ImageTk.PhotoImage(settings_icon_source)
        speed_icon_source = Image.open(
            resource_path("static/images/speed_icon.png")
        ).resize((16, 16))
        speed_icon = ImageTk.PhotoImage(speed_icon_source)
        prefer_icon_source = Image.open(
            resource_path("static/images/prefer_icon.png")
        ).resize((16, 16))
        prefer_icon = ImageTk.PhotoImage(prefer_icon_source)
        local_icon_source = Image.open(
            resource_path("static/images/local_icon.png")
        ).resize((16, 16))
        local_icon = ImageTk.PhotoImage(local_icon_source)
        subscribe_icon_source = Image.open(
            resource_path("static/images/subscribe_icon.png")
        ).resize((16, 16))
        subscribe_icon = ImageTk.PhotoImage(subscribe_icon_source)
        epg_icon_source = Image.open(
            resource_path("static/images/epg_icon.png")
        ).resize((16, 16))
        epg_icon = ImageTk.PhotoImage(epg_icon_source)

        notebook.add(
            frame_default, text="通用设置", image=settings_icon, compound=tk.LEFT
        )
        notebook.add(frame_speed, text="测速设置", image=speed_icon, compound=tk.LEFT)
        notebook.add(frame_prefer, text="偏好设置", image=prefer_icon, compound=tk.LEFT)
        notebook.add(
            frame_local, text="本地源", image=local_icon, compound=tk.LEFT
        )
        notebook.add(
            frame_subscribe, text="订阅源", image=subscribe_icon, compound=tk.LEFT
        )
        notebook.add(
            frame_epg,
            text="EPG",
            image=epg_icon,
            compound=tk.LEFT,
        )

        notebook.settings_icon = settings_icon
        notebook.speed_icon = speed_icon
        notebook.prefer_icon = prefer_icon
        notebook.local_icon = local_icon
        notebook.subscribe_icon = subscribe_icon
        notebook.epg_icon = epg_icon

        self.default_ui.init_ui(frame_default)
        self.speed_ui.init_ui(frame_speed)
        self.prefer_ui.init_ui(frame_prefer)
        self.local_ui.init_ui(frame_local)
        self.subscribe_ui.init_ui(frame_subscribe)
        self.epg_ui.init_ui(frame_epg)

        root_operate = tk.Frame(self.root)
        root_operate.pack(fill=tk.X, pady=8, padx=120)
        root_operate_column1 = tk.Frame(root_operate)
        root_operate_column1.pack(side=tk.LEFT, fill=tk.Y)
        root_operate_column2 = tk.Frame(root_operate)
        root_operate_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.save_button = tk.ttk.Button(
            root_operate_column1, text="保存设置", command=self.save_config
        )
        self.save_button.pack(side=tk.LEFT, padx=4, pady=8)

        self.run_button = tk.ttk.Button(
            root_operate_column2, text="启动", command=self.on_run_update
        )
        self.run_button.pack(side=tk.LEFT, padx=4, pady=8)

        root_progress = tk.Frame(self.root)
        root_progress.pack(fill=tk.X)

        self.progress_bar = tk.ttk.Progressbar(
            root_progress, length=300, mode="determinate"
        )
        self.progress_bar.pack_forget()
        self.progress_label = tk.Label(root_progress, text="进度: 0%")
        self.progress_label.pack_forget()
        self.view_result_link = tk.Label(
            root_progress, text="", fg="blue", cursor="hand2"
        )
        self.view_result_link.bind(
            "<Button-1>",
            self.view_result_link_callback,
        )
        self.view_result_link.pack_forget()


def get_root_location(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width = 620
    height = 670
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    return (width, height, x, y)


if __name__ == "__main__":
    root = tk.Tk()
    tkinter_ui = TkinterUI(root)
    tkinter_ui.init_UI()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry("%dx%d+%d+%d" % get_root_location(root))
    root.iconbitmap(resource_path("favicon.ico"))
    root.after(0, config.copy("config"))
    root.after(0, config.copy("utils/nginx-rtmp-win32"))
    root.after(0, config.copy("output"))
    if config.open_service:
        root.after(0, threading.Thread(target=run_service, daemon=True).start())
    root.mainloop()
