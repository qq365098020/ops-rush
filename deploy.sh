#!/bin/bash
# 床头柜整理清单自动部署脚本
# 用法: bash deploy.sh "提交信息"
set -e

REPO="$(cd "$(dirname "$0")" && pwd)"
COMMIT_MSG="${1:-auto deploy}"

# 1. 生成时间戳（北京时间）
TZ=Asia/Shanghai
TIMESTAMP=$(TZ=$TZ date +"%Y%m%d-%H%M")

# 2. 更新manifest.json版本号
sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$TIMESTAMP\"/" "$REPO/manifest.json"
# 更新manifest.json的start_url带版本号
sed -i "s|\"start_url\": \"[^\"]*\"|\"start_url\": \"./index.html?v=$TIMESTAMP\"|" "$REPO/manifest.json"
# 更新version.json版本号
printf '{"version":"%s"}\n' "$TIMESTAMP" > "$REPO/version.json"

# 3. 更新HTML中的meta version标签
sed -i "s|<meta name=\"version\" content=\"[^\"]*\">|<meta name=\"version\" content=\"$TIMESTAMP\">|" "$REPO/index.html"

# 4. 提交并推送
cd "$REPO"
git add -A
git commit -m "v${TIMESTAMP}: ${COMMIT_MSG}"

TOKEN=$(strings -e l ~/桌面/各种API\ Key.wps 2>/dev/null | grep 'ghp_' | head -1)
git push "https://qq365098020:${TOKEN}@github.com/qq365098020/ops-rush.git" master 2>&1
# 同步到main分支（GitHub Pages部署源）
git checkout main && git reset --hard master && git push "https://qq365098020:${TOKEN}@github.com/qq365098020/ops-rush.git" main --force 2>&1 && git checkout master 2>&1

# 4. 输出链接
echo ""
echo "✅ 部署成功"
echo "📱 链接: https://qq365098020.github.io/ops-rush/?v=${TIMESTAMP}"
