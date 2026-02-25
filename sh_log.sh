# 环境安装
# mamba create -p iptv pipenv python=3.13 requests
# conda activate iptv/
# 安装依赖
# pipenv install pytz --pypi-mirror https://pypi.tuna.tsinghua.edu.cn/simple
# 更新
export PATH=/Users/wangmaolin/project/iptv-api/backend/ffmpeg/macos/:$PATH
/Users/wangmaolin/envs/iptv/bin/python script/playlist.py 
pipenv run dev
git add output/result.m3u
git commit -m "Add latest user_result.m3u"
git push gitee master



# gitee
# git remote add gitee https://gitee.com/wml_1994/iptv.git


# # 使用方法
# cd /Users/wangmaolin/project/iptv
# # 1. 更新demo
# /Users/wangmaolin/miniforge3/bin/python script/playlist.py 
# # 2. 更新源
# docker run --rm -v /Users/wangmaolin/project/iptv/config:/iptv-api/config -v /Users/wangmaolin/project/iptv/output:/iptv-api/output docker.1ms.run/guovern/iptv-api
# # 3. 源路径
# https://gitee.com/wml_1994/iptv/raw/master/output/result.m3u
