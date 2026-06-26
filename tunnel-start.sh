#!/bin/bash
# 运营RUSH Cloudflare Tunnel 自动启动脚本
REPO="/home/oiio/橙子的工作台/运营RUSH"

# 启动HTTP服务器
cd "$REPO"
python3 -m http.server 8888 &
HTTP_PID=$!
sleep 1

# 启动Cloudflare Tunnel，输出URL到文件
cloudflared tunnel --url http://localhost:8888 2>&1 | tee /tmp/tunnel_url.log &
TUNNEL_PID=$!

# 等待URL出现
for i in $(seq 1 30); do
  URL=$(grep -o 'https://[^ ]*trycloudflare.com' /tmp/tunnel_url.log 2>/dev/null | head -1)
  if [ -n "$URL" ]; then
    echo "$URL" > /tmp/tunnel_current_url.txt
    echo "✅ Tunnel ready: $URL"
    break
  fi
  sleep 1
done

# 保持运行
wait
