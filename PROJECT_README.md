# 运营RUSH — 银行网点运营管理APP

## 基础信息

- **项目路径**：`/home/oiio/橙子的工作台/运营RUSH/`
- **仓库**：https://github.com/qq365098020/ops-rush
- **线上地址**：https://qq365098020.github.io/ops-rush/
- **技术栈**：单文件 HTML + CSS + JavaScript（零依赖，零构建工具）
- **部署方式**：GitHub Pages（源分支 `main`）
- **用户设备**：iPhone 16e，用 Edge 浏览器打开并固定到桌面（PWA）
- **服务器环境**：Ubuntu 台式机，用户已获 sudo 权限，工作目录 `/home/oiio/橙子的工作台/`

---

## 架构概要

### 单文件结构
整个 APP 是一个 `index.html`，内含：
1. `<head>` — PWA meta 标签、CSS 样式（全部内联）
2. `<body>` — 静态 HTML 结构（页面容器、弹窗、底部导航）
3. `<script>` — 全部 JavaScript（ES6 class，无模块加载）

### 页面结构
```
<div id="app">
  <header>                     — Logo + 日期
  <div class="page" id="pageDashboard">  — 首页（任务看板）
    <div class="tab-bar">      — 标签栏（待处理/进行中/已完成）
    <div class="tab-content">  — 标签内容
  <div class="page" id="pageTasks">      — 任务管理页
  <div class="page" id="pageSettings">   — 设置页
  <nav class="bottom-nav">     — 底部导航
</div>
<div class="modal-overlay">    — 详情弹窗
<div class="cal-overlay">      — 日历选择弹窗
<div class="toast">            — Toast提示
```

---

## 任务数据模型

每个任务定义在 `DEFAULT_TASKS` 数组（约 line 373），结构：

```javascript
{
  id: '任务标识符',               // 唯一ID，如 'safety_check'
  name: '任务名称',               // 显示名称
  type: '任务类型',               // 见下方类型列表
  severity: 'red'|'yellow'|'green',  // 严重等级，决定左边光晕颜色
  day: 1|-2|-1,                  // monthly_fixed专用：每月几号/-2月底/-1倒数第2天
  weekday: 0|1|...|6,            // weekly专用：周日0~周六6
  lastNDays: 4,                  // monthly_multi专用：最后N个非周六日
  postponeSat: true|'fri',       // 遇周六推迟至周日/提前至周五
  multiCompletion: true,         // 是否允许多次完成（旬、安全检查、monthly_multi）
  monthlyTarget: 4,              // multiCompletion的月目标次数
  weekStart: 1,                  // weekly任务从周一开始周期（安全检查专用）
  intervalDays: 2|4,             // rolling专用：每N天一次
  completionHistory: [],         // 完成记录 [{date,ts}] 或 ["dateStr"]
  completions: {},               // monthly_multi/旬专用：{key: timestamp} 或 {key: [{ts,date}]}
  partCompletions: {},           // monthly_range专用
  lastCompleted: ISO字符串|null,  // 上次完成时间
  manualResetDates: [],          // 手动重置记录（ATM清机专用）
  linkTo: '其他任务ID',           // 完成时联动重置另一个任务（每旬查库→ATM清机）
  linkedFrom: '其他任务ID',       // 被谁联动
  hasPersistentNote: true,       // 是否有常驻备注
  note: '',                      // 备注内容
  desc: '',                      // 说明文字
  typeLabel: '月度 · 最后4天',    // 显示的类型标签
  reviews: [],                   // 审核记录（保留字段）
}
```

### 任务类型（`type` 字段）

| type | 说明 | 代表任务 |
|------|------|----------|
| `rolling` | 滚动任务，间隔N天一次 | 反洗钱检查(2天)、ATM清机(4天) |
| `monthly_fixed` | 月度固定日期 | 科目打印(1号)、报警器(15号)、安保本(月底) |
| `monthly_multi` | 月度多次 | 打9999(最后4个非周六日) |
| `旬` | 每月3旬（1-10/11-20/21-月底） | 每旬查库 |
| `monthly_range` | 月度多段落 | 安保本学习记录(2篇/月) |
| `weekly` | 每周固定星期 | 计算机操作日志(周五) |
| `weekly` + `weekStart:1` | 每周一~周日周期 | 安全检查（4次/月） |

---

## 核心函数

### 状态计算（~line 485）
`getTaskStatus(task)` — 根据任务类型分发到不同逻辑：
- `rolling` → 计算间隔天数是否到期
- `monthly_fixed`/`monthly_multi` → `getMultiStatus()` 或按月计算
- `旬` → `getXunStatus()` 
- `weekly` + `weekStart` → `getWeekCycleStatus()`（安全检查专用）
- `weekly` → 标准每周到期计算

**状态返回值：**
```javascript
{status:'ok'|'overdue'|'today'|'pending'|'done'|'missed'|'soon',
 label:'显示文字',
 dueDate: Date对象,
 daysLeft: 数字,
 overdue: true|false}
```

### 渲染（~line 838）
- `render()` → `renderDashboard()` + `renderTasks()`
- `renderDashboard()` → 遍历所有任务，按状态分组到三个标签（待处理/进行中/已完成）
- `renderCard(task)` → 渲染单张任务卡片
- `openDetail(taskId)` → 打开详情弹窗

### 数据持久化（~line 404）
- `load()` → 从 `localStorage('opsrush_data')` 读取，合并 DEFAULT_TASKS 做迁移
- `save()` → 写入 localStorage

### 周六关门逻辑
- **提前到周五**：`postponeToFriday(d)` — `postponeSat:'fri'`
- **推迟到周日**：`postponeIfSaturday(d)` — `postponeSat:true`
- **滚动任务**：`if(isSaturday(dueDate)) dueDate=postponeToFriday(dueDate)`
- **打9999（monthly_multi）**：从月底往前数N个非周六日（跳周六）

### 周六不计数逻辑（v20260702）
- 安全检查：剩余天数不统计周六
- 每旬查库：剩余天数不统计周六
- 计算公式：从明天到截止日，跳过所有周六

---

## 数据流

```
用户操作 → onclick → class方法 → 更新this.tasks → save() → render()
   ↑                                                                |
   └──────────────── localStorage('opsrush_data') ← JSON.parse/stringify
```

数据只存在 iPhone 的 Edge 浏览器 localStorage 里。**不存服务器，不存云端。** 换设备/清缓存会丢数据，用户需定期用APP内"导出数据"备份。

---

## 关键UI交互

### 任务卡片
```
┌──────────────────────────────────────┐
│ │ 任务名称                         ✓ │
│ │ 剩余2天 · 0/4        [📅]        │
└──────────────────────────────────────┘
```
- 左边红色/黄色竖条 = `severity` 等级
- 点击卡片主体 = 打开详情弹窗 `openDetail(taskId)`
- 点击 📅 = 打开日历选择器 `openCalPicker(taskId)`（补签用）
- 点击 ✓ = 快速完成 `quickDone(taskId)`

### 底部导航
- 2个按钮：📊 任务、⚙️ 设置
- 设置页有：数据导出/导入、重置数据、版本号显示

### 详情弹窗
任务名称 + 类型标签 + 节点状态列表 + 小日历（显示完成记录） + 操作按钮

---

## 近期改动历史

| 版本 | 改动 |
|------|------|
| v20260702-1742 | 安全检查和每旬查库改为"剩余X天"显示（剔除周六）；倒计时颜色匹配严重等级光晕 |
| v20260702-1634 | 个人安保上月未完成改放到"待处理"标签 |
| v20260702-1628 | 修复 versionDisplay 元素缺失导致白屏 |
| v20260702-1123 | 修复初始空白：用 switchPage 替换 renderDashboard |
| v20260702-0935 | 版本号动态显示；移除30秒自动刷新；旬任务显示0/3；个人安保逾期标记 |
| v20260702-0853 | 修复 openDetail 报 today 未定义（大括号多了一个}) |
| v20260702-0805 | APP内部版本号显示 |

---

## 部署流程

```bash
cd /home/oiio/橙子的工作台/运营RUSH
bash deploy.sh "改动说明"
```

部署脚本自动：
1. 更新时间戳版本号（`version` meta + manifest.json）
2. git add/commit/push 到 master 分支
3. force push 到 main 分支（GitHub Pages 部署源）
4. 输出线上链接 `https://qq365098020.github.io/ops-rush/?v=YYYYMMDD-HHMM`

**注意**：GitHub Pages CDN 有缓存（最长10+分钟）。用户急测时需起 Cloudflare Tunnel：
```bash
cd /home/oiio/橙子的工作台/运营RUSH
python3 -m http.server 8888 &
cloudflared tunnel --url http://localhost:8888
# URL: https://<随机>.trycloudflare.com
```

---

## 调试须知

1. **大括号平衡**是最常见的坑。每次改 `index.html` 后必须验证：
```bash
node -e 'const fs=require("fs");const s=fs.readFileSync("index.html","utf8");let o=0,c=0;for(const ch of s){if(ch==="{")o++;if(ch==="}")c++};console.log((o===c?"BALANCED":"IMBALANCE")+" {"+o+" }"+c)'
```

2. **`patch` 工具**在处理含反引号和 `$` 的 JS 模板字面量时容易转义错误。改用 Python 写文件替换：
```python
with open('index.html','r') as f: src=f.read()
src = src.replace('旧字符串','新字符串')
with open('index.html','w') as f: f.write(src)
```

3. **用户偏好**：ios毛玻璃风格、周一为一周首日、周六不开门（提前到周五）、默认提醒用 Discord cron 而非滴答清单。

4. **用户沟通**：称呼"主人"，自称"橙子"。用户有数据洁癖，改之前逐个确认。改错比不改更糟。

---

## 待办 / 已知问题

- [ ] 无（当前版本稳定）
