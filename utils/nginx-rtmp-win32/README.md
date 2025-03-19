nginx-rtmp-win32
================

* Nginx: 1.14.1  
* Nginx-Rtmp-Module: 1.2.1  
* openssl-1.0.2p
* pcre-8.42
* zlib-1.2.11

# dev分支说明
在1.2.1基础上做一些小修改，原版请用master分支

# configure arguments
```
nginx version: nginx/1.14.1
built by cl 18.00.40629 for x86
built with OpenSSL 1.0.2p  14 Aug 2018
TLS SNI support enabled
configure arguments: --with-cc=cl --builddir=objs --with-debug --prefix= --conf-
path=conf/nginx.conf --pid-path=logs/nginx.pid --http-log-path=logs/access.log -
-error-log-path=logs/error.log --sbin-path=nginx.exe --http-client-body-temp-pat
h=temp/client_body_temp --http-proxy-temp-path=temp/proxy_temp --http-fastcgi-te
mp-path=temp/fastcgi_temp --http-scgi-temp-path=temp/scgi_temp --http-uwsgi-temp
-path=temp/uwsgi_temp --with-cc-opt=-DFD_SETSIZE=1024 --with-pcre=objs/lib/pcre-
8.42 --with-zlib=objs/lib/zlib-1.2.11 --with-select_module --with-http_v2_module
 --with-http_realip_module --with-http_addition_module --with-http_sub_module --
with-http_dav_module --with-http_stub_status_module --with-http_flv_module --wit
h-http_mp4_module --with-http_gunzip_module --with-http_gzip_static_module --wit
h-http_auth_request_module --with-http_random_index_module --with-http_secure_li
nk_module --with-http_slice_module --with-mail --with-stream --with-openssl=objs
/lib/openssl-1.0.2p --with-openssl-opt=no-asm --with-http_ssl_module --with-mail
_ssl_module --with-stream_ssl_module --add-module=objs/lib/nginx-rtmp-module/
```

# 使用方法
双击nginx.exe
# 简要说明
conf/nginx.conf 为配置文件实例  
RTMP监听 1935 端口，启用live 和hls 两个application  
HTTP监听 8080 端口，
* :8080/stat 查看stream状态  
* :8080/index.html 为一个直播播放与直播发布测试器
* :8080/vod.html 为一个支持RTMP和HLS点播的测试器

# 注意
不支持exec

# 直播测试工具 
内置了一个方便测试的pc端推流于播放的工具
![img](https://github.com/NodeMedia/NodeMediaDevClient/raw/master/QQ20160310-0.png)
源码在此:https://github.com/NodeMedia/NodeMediaDevClient

# H265
支持ID=12的h265流,需要客户端支持.
