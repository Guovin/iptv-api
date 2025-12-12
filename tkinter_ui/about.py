import tkinter as tk
import webbrowser

from PIL import Image, ImageTk

from utils.tools import resource_path


class AboutUI:
    def init_ui(self, root=None, version=None):
        about_window = tk.Toplevel(root)
        about_window.title("关于")
        about_window_width = 430
        about_window_height = 480

        version_frame = tk.Frame(about_window)
        version_frame.pack(side=tk.TOP, fill=tk.X)

        version_label = tk.Label(version_frame, text=f"版本: {version}")
        version_label.pack()

        author_row = tk.Frame(about_window)
        author_row.pack()
        author_row_column1 = tk.Frame(author_row)
        author_row_column1.pack(side=tk.LEFT, fill=tk.Y)
        author_row_column2 = tk.Frame(author_row)
        author_row_column2.pack(side=tk.RIGHT, fill=tk.Y)
        author_label = tk.Label(author_row_column1, text="作者:")
        author_label.pack()
        author_name = tk.Label(
            author_row_column2, text="Govin", fg="blue", cursor="hand2"
        )
        author_name.pack()
        author_name.bind(
            "<Button-1>",
            lambda e: webbrowser.open_new_tab("https://github.com/Guovin"),
        )

        project_row = tk.Frame(about_window)
        project_row.pack()
        project_row_column1 = tk.Frame(project_row)
        project_row_column1.pack(side=tk.LEFT, fill=tk.Y)
        project_row_column2 = tk.Frame(project_row)
        project_row_column2.pack(side=tk.RIGHT, fill=tk.Y)
        project_label = tk.Label(project_row_column1, text="项目地址:")
        project_label.pack()
        project_link = tk.Label(
            project_row_column2,
            text="https://github.com/Guovin/iptv-api",
            fg="blue",
            cursor="hand2",
        )
        project_link.pack()
        project_link.bind(
            "<Button-1>",
            lambda e: webbrowser.open_new_tab("https://github.com/Guovin/iptv-api"),
        )

        disclaimer_label = tk.Label(
            version_frame,
            text="本软件仅供学习交流用途，数据均来源于互联网，禁止商业行为，一切法律责任与作者无关。",
            wraplength=265,
        )
        disclaimer_label.pack()

        image = Image.open(resource_path("static/images/alipay.jpg"))
        resized_image = image.resize((250, 300))
        photo = ImageTk.PhotoImage(resized_image)
        image_label = tk.Label(about_window, image=photo)
        image_label.image = photo
        image_label.pack()

        appreciate_label = tk.Label(
            about_window, text="开发维护不易，请我喝杯咖啡☕️吧~"
        )
        appreciate_label.pack()

        confirm_button = tk.ttk.Button(
            about_window, text="确定", command=about_window.destroy
        )
        confirm_button.pack(side=tk.RIGHT, padx=5)

        main_width = root.winfo_width()
        main_height = root.winfo_height()
        main_x = root.winfo_x()
        main_y = root.winfo_y()
        pos_x = main_x + (main_width // 2) - (about_window_width // 2)
        pos_y = main_y + (main_height // 2) - (about_window_height // 2)
        about_window.geometry(
            f"{about_window_width}x{about_window_height}+{pos_x}+{pos_y}"
        )
        about_window.iconbitmap(resource_path("favicon.ico"))
