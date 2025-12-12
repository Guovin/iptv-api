# -*- mode: python ; coding: utf-8 -*-
import json

with open('version.json') as f:
    version_data = json.load(f)
    version = version_data['version']
    name = version_data['name']

a = Analysis(
    ['tkinter_ui.py', 'about.py', 'default.py', 'speed.py', 'prefer.py', 'local.py', 'multicast.py', 'hotel.py', 'subscribe.py', 'online_search.py', 'epg.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../config/config.ini', 'config'),
        ('../config/demo.txt', 'config'),
        ('../config/local.txt', 'config'),
        ('../config/whitelist.txt', 'config'),
        ('../config/blacklist.txt', 'config'),
        ('../config/subscribe.txt', 'config'),
        ('../config/epg.txt', 'config'),
        ('../config/alias.txt', 'config'),
        ('../config/rtp', 'config/rtp'),
        ('../output', 'output'),
        ('../updates/hotel/cache.pkl', 'updates/hotel'),
        ('../updates/multicast/multicast_map.json', 'updates/multicast'),
        ('../updates/multicast/cache.pkl', 'updates/multicast'),
        ('../utils/ip_checker/data/qqwry.ipdb', 'utils/ip_checker/data'),
        ('../utils/nginx-rtmp-win32', 'utils/nginx-rtmp-win32'),
        ('../static/images/alipay.jpg', 'static/images'),
        ('../static/images/settings_icon.png', 'static/images'),
        ('../static/images/speed_icon.png', 'static/images'),
        ('../static/images/prefer_icon.png', 'static/images'),
        ('../static/images/local_icon.png', 'static/images'),
        ('../static/images/hotel_icon.png', 'static/images'),
        ('../static/images/multicast_icon.png', 'static/images'),
        ('../static/images/subscribe_icon.png', 'static/images'),
        ('../static/images/online_search_icon.png', 'static/images'),
        ('../static/images/epg_icon.png', 'static/images'),
        ('favicon.ico', '.'),
        ('about.py', '.'),
        ('default.py', '.'),
        ('speed.py', '.'),
        ('prefer.py', '.'),
        ('local.py', '.'),
        ('multicast.py', '.'),
        ('hotel.py', '.'),
        ('subscribe.py', '.'),
        ('online_search.py', '.'),
        ('epg.py', '.'),
        ('select_combobox.py', '.'),
        ('../version.json', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=f'{name}-v{version}',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico'
)
