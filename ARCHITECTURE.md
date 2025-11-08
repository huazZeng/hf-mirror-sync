# HF-Mirror-Sync 项目架构说明文档

## 项目概述

`hf-mirror-sync` 是一个 Hugging Face 镜像站项目，用于为国内用户提供稳定、快速的 Hugging Face 资源访问服务。该项目使用 **Caddy** 作为反向代理服务器，通过代理转发的方式实现镜像功能。

**公开版本**: [https://hf-mirror.com/](https://hf-mirror.com/)

---

## 目录结构

```
hf-mirror-sync/
├── .git/                    # Git 仓库配置
├── .gitmodules              # Git 子模块配置（包含 hfd 工具）
├── README.md                # 项目说明文档
├── dist/                    # 前端静态资源目录
│   ├── hfd/                 # hfd 下载工具（Git 子模块）
│   ├── index.html           # 网站首页
│   ├── invalid_referer.html # 无效来源页面
│   ├── login_error.html     # 登录错误页面
│   ├── scripts.js           # 前端 JavaScript 逻辑
│   ├── styles.css           # 前端样式文件
│   ├── favicon.ico          # 网站图标
│   ├── logo.svg             # 网站 Logo
│   └── robots.txt           # 搜索引擎爬虫配置
└── scripts/                 # 服务器配置脚本
    └── caddy/               # Caddy 服务器配置
        ├── Caddyfile        # Caddy 主配置文件（导入其他配置）
        ├── hf-mirror.com.Caddyfile      # 主域名配置
        └── lfs.hf-mirror.com.Caddyfile  # LFS CDN 域名配置
```

---

## 核心组件说明

### 1. Caddy 服务器配置

#### 1.1 主配置文件 (`scripts/caddy/Caddyfile`)

- **作用**: 作为入口配置文件，导入其他具体的 Caddyfile
- **功能**:
  - 配置全局日志格式（访问日志、错误日志）
  - 日志轮转策略（单文件最大 100M/200M，保留 5 个文件，保留 720 小时）
  - 通过 `import *.Caddyfile` 导入所有子配置文件

#### 1.2 主域名配置 (`scripts/caddy/hf-mirror.com.Caddyfile`)

这是项目的核心配置文件，实现了以下功能：

**a) TLS 证书管理**
- 使用 Cloudflare DNS 进行自动证书申请和续期
- 支持通配符域名（`*.hf-mirror.com` 自动跳转到主域名）

**b) 安全防护**
- **机器人过滤**: 拦截 `SemrushBot`、`MJ12bot` 等爬虫
- **Referer 检查**: 禁止第三方站点外链模型下载链接（防止盗链）
- **路径过滤**: 屏蔽包含敏感关键词的路径请求
- **登录限制**: 镜像站禁止登录功能，重定向到错误页面

**c) 静态资源处理**
- 静态文件（HTML、CSS、JS、图片等）直接从本地文件系统提供
- 静态资源不缓存（`Cache-Control: no-cache`）
- 原站静态资源缓存 3 天（`max-age=259200`）

**d) 内容替换**
- 替换 Logo: `/front/assets/huggingface_logo-noborder.svg` → `/logo.svg`
- 替换网站名称: "Hugging Face" → "HF Mirror"
- 替换域名: `huggingface.co` → `hf-mirror.com`
- 替换 CDN 域名: `cdn-lfs.huggingface.co` → `cdn-lfs.hf-mirror.com`

**e) 反向代理**
- 将请求代理到 `https://huggingface.co`
- 处理响应头中的 Location 重定向
- 支持项目页面（模型、数据集、Spaces）的流式内容替换

**f) WebSeed 支持**
- 为 [hf-torrent](https://github.com/Lyken17/hf-torrent) 项目提供 WebSeed 支持
- 路径转换: `/ws/models--xxx--yyy/` → `/xxx/resolve/yyy/`

**g) API 优化**
- `/api/event`: 直接返回 "OK"，减少服务器压力
- `/cdn-cgi/rum`: 返回 204 状态码（No Content）

#### 1.3 LFS CDN 配置 (`scripts/caddy/lfs.hf-mirror.com.Caddyfile`)

- **作用**: 处理 Git LFS（Large File Storage）大文件的 CDN 请求
- **功能**:
  - `cdn-lfs.hf-mirror.com`: 代理到 `cdn-lfs.huggingface.co`
  - `cdn-lfs-us-1.hf-mirror.com`: 代理到 `cdn-lfs-us-1.huggingface.co`
  - Referer 检查，防止无效访问
  - 使用负载均衡（round_robin）策略

---

### 2. 前端静态资源 (`dist/`)

#### 2.1 首页 (`index.html`)

- **功能**: 提供镜像站的主页面
- **特性**:
  - 搜索框：支持模型和数据集搜索
  - 热门排行：展示热门模型和数据集
  - 使用教程：提供多种下载方式说明
  - 响应式设计：支持移动端和桌面端

#### 2.2 前端脚本 (`scripts.js`)

实现以下前端功能：

- **搜索功能**
  - 实时搜索建议（防抖 300ms）
  - 支持键盘导航（上下箭头、Enter）
  - 调用 `/api/quicksearch` API

- **热门排行**
  - 从 `/api/trending` API 获取数据
  - 支持分类切换（全部/模型/数据集）
  - 本地缓存（sessionStorage，1 分钟过期）
  - 响应式显示（移动端显示 3 项，桌面端显示 10 项）

- **交互功能**
  - 代码复制按钮
  - 展开/收起功能
  - 移动端二维码显示

#### 2.3 错误页面

- **`invalid_referer.html`**: 当检测到无效 Referer 时显示
- **`login_error.html`**: 当用户尝试登录时显示（镜像站不支持登录）

#### 2.4 子模块 (`dist/hfd/`)

- **hfd**: Hugging Face 专用下载工具
- 通过 Git 子模块引入（Gist: `697678ab8e528b85a2a7bddafea1fa4f`）
- 基于 `git + aria2` 实现稳定下载

---

## 工作流程

### 请求处理流程

```
用户请求
    ↓
Caddy 服务器接收
    ↓
检查 Referer、User-Agent、路径等安全策略
    ↓
判断请求类型:
    ├─ 静态资源 → 从本地文件系统提供
    ├─ API 请求 → 直接返回或代理
    ├─ 项目页面 → 代理到原站并替换内容
    └─ 文件下载 → 代理到原站并处理重定向
    ↓
返回响应（可能包含内容替换）
```

### 内容替换流程

1. **请求拦截**: Caddy 拦截对 Hugging Face 的请求
2. **反向代理**: 将请求转发到 `https://huggingface.co`
3. **内容处理**: 使用 `replace-response` 插件替换响应内容
   - 替换域名引用
   - 替换品牌名称
   - 替换 Logo 路径
4. **响应返回**: 返回处理后的内容给用户

---

## 技术特点

### 1. 反向代理架构

- 无需缓存文件，所有请求实时代理
- 减少存储成本
- 保证内容与源站同步

### 2. 内容替换技术

- 使用 Caddy 的 `replace-response` 插件
- 流式替换，内存占用低
- 支持正则表达式匹配

### 3. 安全机制

- Referer 检查防止盗链
- 机器人过滤减少无效请求
- 路径过滤防止恶意请求
- 禁止登录功能保障安全

### 4. 性能优化

- 静态资源压缩（gzip、zstd）
- 静态文件本地缓存
- API 请求简化（部分接口直接返回）
- 日志过滤（静态资源不记录日志）

---

## 域名配置

### 主域名

- `hf-mirror.com`: 主站点
- `*.hf-mirror.com`: 通配符域名，自动跳转到主域名

### LFS CDN 域名

- `cdn-lfs.hf-mirror.com`: 代理到 `cdn-lfs.huggingface.co`
- `cdn-lfs-us-1.hf-mirror.com`: 代理到 `cdn-lfs-us-1.huggingface.co`

---

## 使用场景

### 用户使用方式

1. **网页访问**: 直接访问 `https://hf-mirror.com` 浏览和下载
2. **命令行工具**:
   ```bash
   export HF_ENDPOINT=https://hf-mirror.com
   huggingface-cli download model_name
   ```
3. **Python 代码**:
   ```python
   import os
   os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
   ```

### 支持的下载工具

- `huggingface-cli`: 官方命令行工具
- `hfd`: 项目提供的专用下载工具
- `datasets` 库: 通过环境变量配置
- `transformers` 库: 通过环境变量配置

---

## 注意事项

1. **存储**: 镜像站不存储文件，所有请求实时代理
2. **登录**: 镜像站不支持登录功能，访问需要登录的资源需使用 Token
3. **带宽**: 所有文件下载都通过镜像站，需要足够的带宽支持
4. **证书**: 使用 Cloudflare DNS 验证，需要配置相应的 API Token
5. **日志**: 日志文件会不断增长，需要定期清理或配置轮转

---

## 相关链接

- **公开镜像站**: https://hf-mirror.com/
- **使用教程**: https://zhuanlan.zhihu.com/p/663712983
- **hfd 工具**: https://gist.github.com/padeoe/697678ab8e528b85a2a7bddafea1fa4f
- **Caddy 文档**: https://caddyserver.com/docs/

