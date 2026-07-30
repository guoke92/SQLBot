#!/bin/bash

SQLBOT_BASE=/opt

read -r -p "即将卸载 AI智能问数服务，包括删除运行目录、数据及相关镜像，是否继续? [Y/n] " input

case $input in
   [yY][eE][sS]|[yY])
      echo "Yes"
      ;;
   [nN][oO]|[nN])
      echo "No"
      exit 1
      ;;
   *)
      echo "无效输入..."
      exit 1
      ;;
esac

echo "停止 AI智能问数服务"
sctl stop >/dev/null 2>&1

if [ -f /usr/bin/sctl ]; then
# 获取已安装的 AI智能问数的运行目录
   SQLBOT_BASE=$(grep "^SQLBOT_BASE=" /usr/bin/sctl | cut -d'=' -f2)
fi

# 清理 AI智能问数相关镜像
if test ! -z "$(docker images -f dangling=true -q)"; then
   echo "清理虚悬镜像"
   docker rmi $(docker images -f dangling=true -q)
fi

if test -n "$(docker images | grep 'registry.cn-qingdao.aliyuncs.com/dataease/sqlbot')"; then
   echo "清理 AI智能问数镜像"
   docker rmi $(docker images | grep "registry.cn-qingdao.aliyuncs.com/dataease/sqlbot" | awk -F' ' '{print $1":"$2}')
fi

# 清理 AI智能问数运行目录及命令行工具 sctl
rm -rf ${SQLBOT_BASE}/sqlbot /usr/bin/sctl

echo "AI智能问数服务卸载完成"
