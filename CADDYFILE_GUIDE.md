# Caddyfile 配置详解指南

## 目录

1. [Caddy 简介](#caddy-简介)
2. [Caddyfile 基础语法](#caddyfile-基础语法)
3. [三个配置文件详解](#三个配置文件详解)
   - [Caddyfile（主配置文件）](#1-caddyfile主配置文件)
   - [hf-mirror.com.Caddyfile（主站配置）](#2-hf-mirrorcomcaddyfile主站配置)
   - [lfs.hf-mirror.com.Caddyfile（LFS CDN 配置）](#3-lfshf-mirrorcomcaddyfilelfs-cdn-配置)

---

## Caddy 简介

Caddy 是现代化的 Web 服务器，支持自动 HTTPS、反向代理和丰富的插件系统。本项目需要以下插件：
- `replace-response` - 内容替换（必需）
- `transform-encoder` - 编码转换（必需）
- `caddy-dns/cloudflare` - Cloudflare DNS 验证（可选）

---

## Caddyfile 基础语法

### 1. 基本结构

Caddyfile 的基本结构类似于 Nginx，但更简洁：

```caddy
# 注释使用 # 号

# 全局配置块（可选）
{
    # 全局设置
}

# 站点配置：域名 { ... }
example.com {
    # 站点配置
}

# 通配符域名
*.example.com {
    # 配置
}
```

### 2. 指令（Directives）

指令是 Caddyfile 的核心，用于配置服务器行为。

#### 常见指令类型：

**a) 路径匹配器（Matchers）**
```caddy
@name {
    # 匹配条件
    path /api/*
    header User-Agent *bot*
}

# 使用匹配器
handle @name {
    respond "Matched!"
}
```

**b) 请求处理（Request Handlers）**
```caddy
# 静态文件服务
file_server

# 反向代理
reverse_proxy https://backend.com

# 重定向
redir https://new-site.com

# 返回响应
respond "Hello" 200

# 重写 URL
rewrite /old /new
```

**c) 响应修改（Response Modifiers）**
```caddy
# 设置响应头
header Cache-Control "max-age=3600"

# 替换响应内容
replace {
    "old text" "new text"
}

# 压缩响应
encode gzip zstd
```

### 3. 语法规则

#### 缩进和块
- **使用大括号 `{}` 定义块**
- **缩进使用 Tab 或空格**（本项目使用 Tab）
- **块内指令可以嵌套**

```caddy
example.com {
    # 第一层
    handle /api/* {
        # 第二层
        reverse_proxy backend {
            # 第三层
            header_up Authorization "Bearer token"
        }
    }
}
```

#### 指令参数
- **指令名**: 第一行
- **参数**: 空格分隔，可以有多个参数
- **子块**: 用大括号定义

```caddy
# 指令名 参数1 参数2 { ... }
reverse_proxy https://backend.com {
    header_up Host {host}
}
```

#### 变量和环境变量

```caddy
# 使用环境变量
{$MIRROR_HOST}          # 从 .env 文件读取 MIRROR_HOST

# 使用请求变量
{host}                  # 当前请求的 Host 头
{path}                  # 当前请求路径
{remote_ip}             # 客户端 IP
{upstream_hostport}     # 上游服务器地址
```

#### 片段（Snippets）

片段是可复用的配置块：

```caddy
# 定义一个片段（使用括号）
(tls_config) {
    tls {
        dns cloudflare {$CF_TOKEN}
    }
}

# 使用片段
example.com {
    import tls_config
}
```

### 4. 常用指令详解

| 指令 | 作用 | 示例 |
|------|------|------|
| `handle` | 处理匹配的请求 | `handle /api/* { ... }` |
| `reverse_proxy` | 反向代理到后端 | `reverse_proxy https://backend.com` |
| `file_server` | 提供静态文件服务 | `file_server` |
| `redir` | 重定向 | `redir https://new-site.com` |
| `rewrite` | URL 重写 | `rewrite /old /new` |
| `respond` | 直接返回响应 | `respond "OK" 200` |
| `header` | 设置/修改 HTTP 头 | `header Cache-Control "no-cache"` |
| `encode` | 压缩响应 | `encode gzip` |
| `log` | 配置日志 | `log output file /var/log/access.log` |
| `skip_log` | 跳过日志记录 | `skip_log` |

### 5. 匹配器（Matchers）

匹配器用于条件匹配：

```caddy
# 路径匹配
@name {
    path /api/*              # 匹配路径
    path_regexp /.*\.js$     # 正则匹配路径
}

# 头部匹配
@name {
    header User-Agent *bot*  # 匹配 User-Agent
    header_regexp Referer ^https://example.com
}

# 表达式匹配
@name {
    expression path('/api/*') && header('X-API-Key')
}

# 组合匹配
@name {
    path /api/*
    not header !Authorization  # 必须存在 Authorization 头
}
```

---

## 三个配置文件详解

### 1. Caddyfile（主配置文件）

**文件路径**: `scripts/caddy/Caddyfile`

**作用**: 这是入口配置文件，定义全局设置并导入其他配置文件。

#### 配置说明：

- **全局配置块** `{ }`: 定义全局设置
  - `order replace after encode`: 设置指令执行顺序
  - `log hf_access`: 访问日志配置（格式：IP、时间、请求方法、状态码、大小、Referer、User-Agent）
  - `log hf_error`: 错误日志配置（只记录 ERROR 级别）
  - 日志轮转：单文件最大 100M/200M，保留 5 个文件，保留 720 小时

- **`import *.Caddyfile`**: 导入当前目录下所有 `.Caddyfile` 文件

---

### 2. hf-mirror.com.Caddyfile（主站配置）

**文件路径**: `scripts/caddy/hf-mirror.com.Caddyfile`

**作用**: 配置主站点的所有功能，这是最复杂的配置文件。

#### 配置结构总览：

```
1. TLS 证书配置片段
2. 通配符域名处理
3. 主域名配置
   ├─ 安全防护（机器人过滤、Referer 检查）
   ├─ 静态资源处理
   ├─ 内容替换和重写
   ├─ 反向代理设置
   └─ WebSeed 支持
```

#### 配置说明：

**1. TLS 证书片段** `(tls_hf_com)`
- 使用 Cloudflare DNS 验证自动申请证书（支持通配符域名）

**2. 通配符域名** `*.{$MIRROR_HOST}`
- 所有子域名重定向到主域名

**3. 主域名配置** `{$MIRROR_HOST}`
- **安全防护**: 机器人过滤、Referer 检查、路径过滤、禁止登录
- **静态资源**: 本地文件服务、Logo 替换、缓存控制
- **内容替换**: JS 文件、项目页面中的域名和品牌名称替换
- **反向代理**: 代理到 `huggingface.co`，处理重定向
- **WebSeed**: 为 BitTorrent 工具提供支持（`/ws/*` 路径转换）
- **API 优化**: `/api/event` 和 `/cdn-cgi/rum` 直接返回固定响应

---

### 3. lfs.hf-mirror.com.Caddyfile（LFS CDN 配置）

**文件路径**: `scripts/caddy/lfs.hf-mirror.com.Caddyfile`

**作用**: 配置 Git LFS（Large File Storage）CDN 域名，用于处理大文件下载。

#### 配置说明：

**1. cdn-lfs 域名** `cdn-lfs.MIRROR_HOST`
- 根路径重定向到主站
- `/repos/*` 代理到 `cdn-lfs.huggingface.co`（负载均衡）
- Referer 检查防止无效访问
- 其他路径重定向到主站

**2. cdn-lfs-us-1 域名** `cdn-lfs-us-1.MIRROR_HOST`
- `/repos/*` 代理到 `cdn-lfs-us-1.huggingface.co`（美国区域 CDN）
- 其他路径重定向到主站

**注意**: 配置文件中使用了 `MIRROR_HOST` 字面量，实际应为 `{$MIRROR_HOST}`（需要手动替换）

---

## 常见问题

### Q1: 为什么有些配置使用 `handle`，有些使用 `route`？

- `handle`: 用于站点配置块内的路径匹配
- `route`: 用于路由块内的路径匹配（更细粒度控制）

在这个项目中，主站配置使用 `handle`，LFS CDN 配置使用 `route`。

### Q2: `replace stream` 和普通 `replace` 有什么区别？

- `replace stream`: 流式替换，边接收边替换，不等待完整响应（内存占用低）
- `replace`: 等待完整响应后再替换（需要完整加载到内存）

对于大文件，应该使用 `replace stream`。

### Q3: `header_up` 和 `header_down` 是什么意思？

- `header_up`: 修改**向上游**（原站）发送的请求头
- `header_down`: 修改**向下游**（客户端）返回的响应头

### Q4: `{$VARIABLE}` 和 `{variable}` 有什么区别？

- `{$VARIABLE}`: 环境变量（从 `.env` 文件或系统环境变量读取）
- `{variable}`: 请求变量（从当前请求中获取，如 `{host}`, `{path}`）

### Q5: 如何调试配置？

```bash
# 验证配置语法
caddy validate --config ./scripts/caddy/Caddyfile

# 查看配置解析结果
caddy adapt --config ./scripts/caddy/Caddyfile

# 测试运行（前台运行，方便查看日志）
caddy run --config ./scripts/caddy/Caddyfile
```

---

## 参考资源

- **Caddy 官方文档**: https://caddyserver.com/docs/caddyfile
- **Caddy 指令列表**: https://caddyserver.com/docs/caddyfile/directives
- **Matchers 文档**: https://caddyserver.com/docs/caddyfile/matchers

