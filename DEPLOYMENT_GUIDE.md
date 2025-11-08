# HF-Mirror 部署详细教程

## 目录

1. [系统要求](#系统要求)
2. [安装 Caddy](#安装-caddy)
3. [环境配置](#环境配置)
4. [目录准备](#目录准备)
5. [启动服务](#启动服务)
6. [验证部署](#验证部署)
7. [常见问题](#常见问题)
8. [维护说明](#维护说明)

---

## 系统要求

### 硬件要求

- **CPU**: 2 核或以上（推荐 4 核）
- **内存**: 2GB 或以上（推荐 4GB）
- **磁盘**: 至少 10GB 可用空间（用于日志和静态文件）
- **带宽**: 根据预期访问量，建议至少 100Mbps

### 软件要求

- **操作系统**: Linux (Ubuntu 20.04+, Debian 10+, CentOS 7+), macOS, Windows
- **权限**: 需要 root 权限或 sudo 权限（用于绑定 80/443 端口）
- **域名**: 需要拥有一个域名（用于 HTTPS 证书）
- **DNS**: 域名需要配置 DNS 解析（如果使用 Cloudflare DNS，需要 API Token）

---

## 安装 Caddy

### 方法一：官方下载（推荐）

#### 步骤 1: 访问下载页面

访问 Caddy 官方下载页面，选择包含以下插件的版本：

- `github.com/caddyserver/replace-response` - 内容替换插件（必需）
- `github.com/caddyserver/transform-encoder` - 编码转换插件（必需）
- `github.com/caddy-dns/cloudflare` - Cloudflare DNS 插件（可选，用于自动证书）

**直接下载链接**:
```
https://caddyserver.com/download?package=github.com%2Fcaddyserver%2Freplace-response&package=github.com%2Fcaddy-dns%2Fcloudflare&package=github.com%2Fcaddyserver%2Ftransform-encoder
```

#### 步骤 2: 选择操作系统

根据你的操作系统选择对应的版本：

- **Linux**: 选择 `linux` + `amd64` 或 `arm64`
- **macOS**: 选择 `darwin` + `amd64` 或 `arm64`
- **Windows**: 选择 `windows` + `amd64`

#### 步骤 3: 下载并安装

**Linux/macOS**:
```bash
# 下载（替换 URL 中的版本和架构）
wget https://caddyserver.com/download/linux/amd64?plugins=replace-response,transform-encoder,caddy-dns/cloudflare -O caddy

# 或使用 curl
curl -L "https://caddyserver.com/download/linux/amd64?plugins=replace-response,transform-encoder,caddy-dns/cloudflare" -o caddy

# 添加执行权限
chmod +x caddy

# 移动到系统路径（需要 sudo）
sudo mv caddy /usr/local/bin/

# 验证安装
caddy version
```

**Windows**:
```powershell
# 下载到当前目录
# 从浏览器下载或使用 Invoke-WebRequest

# 添加到 PATH 环境变量
# 或直接使用完整路径运行
```

### 方法二：使用 xcaddy 构建（高级）

如果你需要自定义插件或特定版本，可以使用 xcaddy：

```bash
# 安装 xcaddy
go install github.com/caddyserver/xcaddy/cmd/xcaddy@latest

# 构建 Caddy（包含所需插件）
xcaddy build \
  --with github.com/caddyserver/replace-response \
  --with github.com/caddyserver/transform-encoder \
  --with github.com/caddy-dns/cloudflare

# 构建完成后，会在当前目录生成 caddy 可执行文件
```

### 方法三：使用包管理器

**Ubuntu/Debian**:
```bash
# 注意：官方仓库的 Caddy 可能不包含所需插件
# 建议使用官方下载或 xcaddy 构建

sudo apt update
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# 但这种方式安装的 Caddy 不包含插件，需要重新构建
```

**macOS (Homebrew)**:
```bash
# Homebrew 安装的 Caddy 也不包含插件
brew install caddy

# 需要重新构建或使用官方下载版本
```

---

## 环境配置

### 步骤 1: 创建 .env 文件

在 `scripts/caddy/` 目录下创建 `.env` 文件：

```bash
cd /path/to/hf-mirror-sync/scripts/caddy
cp .env.template .env  # 如果存在模板文件
# 或直接创建
nano .env
```

### 步骤 2: 配置环境变量

编辑 `.env` 文件，填入以下内容：

```bash
# 镜像站主域名（必填）
MIRROR_HOST=your-domain.com

# Cloudflare API Token（如果使用 Cloudflare DNS 验证，必填）
# 获取方式：https://dash.cloudflare.com/profile/api-tokens
# 权限：Zone - Zone Settings - Read, Zone - DNS - Edit
CF_TOKEN=your_cloudflare_api_token_here

# API Key（当前未使用，可以留空）
API_KEY=
```

**重要说明**:

1. **MIRROR_HOST**: 
   - 替换为你的实际域名，例如 `hf-mirror.com`
   - 不要包含 `https://` 前缀
   - 确保域名已经解析到服务器 IP

2. **CF_TOKEN** (如果使用 Cloudflare DNS):
   - 登录 Cloudflare Dashboard
   - 进入 Profile → API Tokens
   - 创建 Token，需要以下权限：
     - `Zone` → `Zone Settings` → `Read`
     - `Zone` → `DNS` → `Edit`
   - 复制生成的 Token 填入配置

3. **如果不使用 Cloudflare DNS**:
   - 可以删除 `CF_TOKEN` 或留空
   - Caddy 会使用 HTTP-01 验证（需要开放 80 端口）
   - 或者使用其他 DNS 提供商（需要在 Caddyfile 中修改 DNS 插件）

### 步骤 3: 设置文件权限

```bash
# 保护 .env 文件，防止泄露敏感信息
chmod 600 .env

# 确保只有所有者可以读取
```

---

## 目录准备

### 步骤 1: 创建静态文件目录

```bash
# 创建 Web 根目录
sudo mkdir -p /var/www/html/your-domain.com

# 将 dist/ 目录内容复制到 Web 根目录
sudo cp -r /path/to/hf-mirror-sync/dist/* /var/www/html/your-domain.com/

# 设置权限（根据你的 Web 服务器用户调整）
sudo chown -R www-data:www-data /var/www/html/your-domain.com
sudo chmod -R 755 /var/www/html/your-domain.com
```

**注意**: 将 `your-domain.com` 替换为你的实际域名（与 `.env` 中的 `MIRROR_HOST` 一致）

### 步骤 2: 创建日志目录

```bash
# 创建日志目录
sudo mkdir -p /var/log/caddy/your-domain.com

# 设置权限
sudo chown -R caddy:caddy /var/log/caddy
# 或如果使用其他用户
sudo chown -R www-data:www-data /var/log/caddy
sudo chmod -R 755 /var/log/caddy
```

### 步骤 3: 验证目录结构

```bash
# 检查静态文件目录
ls -la /var/www/html/your-domain.com/
# 应该看到: index.html, scripts.js, styles.css 等文件

# 检查日志目录
ls -la /var/log/caddy/your-domain.com/
# 目录应该存在且可写
```

---

## 启动服务

### 方法一：前台运行（测试）

适合首次部署和测试：

```bash
cd /path/to/hf-mirror-sync

# 前台运行，可以看到实时日志
sudo caddy run \
  --envfile ./scripts/caddy/.env \
  --config ./scripts/caddy/Caddyfile
```

**优点**:
- 可以看到实时日志
- 方便调试问题
- Ctrl+C 可以停止

**缺点**:
- 终端关闭后服务停止
- 不适合生产环境

### 方法二：后台运行（生产）

#### 选项 A: 使用 systemd（推荐 - Linux）

**1. 创建 systemd 服务文件**:

```bash
sudo nano /etc/systemd/system/caddy-hf-mirror.service
```

**2. 写入以下内容**（替换路径为实际路径）:

```ini
[Unit]
Description=Caddy HTTP/2 web server for HF Mirror
Documentation=https://caddyserver.com/docs/
After=network.target network-online.target
Requires=network-online.target

[Service]
Type=notify
User=www-data
Group=www-data
ExecStart=/usr/local/bin/caddy run --envfile /path/to/hf-mirror-sync/scripts/caddy/.env --config /path/to/hf-mirror-sync/scripts/caddy/Caddyfile
ExecReload=/usr/local/bin/caddy reload --config /path/to/hf-mirror-sync/scripts/caddy/Caddyfile --force
TimeoutStopSec=5s
LimitNOFILE=1048576
LimitNPROC=512
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
ReadWritePaths=/var/log/caddy /var/www/html
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
```

**3. 启用并启动服务**:

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable caddy-hf-mirror

# 启动服务
sudo systemctl start caddy-hf-mirror

# 查看状态
sudo systemctl status caddy-hf-mirror

# 查看日志
sudo journalctl -u caddy-hf-mirror -f
```

**4. 常用命令**:

```bash
# 启动
sudo systemctl start caddy-hf-mirror

# 停止
sudo systemctl stop caddy-hf-mirror

# 重启
sudo systemctl restart caddy-hf-mirror

# 重新加载配置（不中断服务）
sudo systemctl reload caddy-hf-mirror

# 查看状态
sudo systemctl status caddy-hf-mirror

# 禁用开机自启
sudo systemctl disable caddy-hf-mirror
```

#### 选项 B: 使用 nohup

```bash
# 后台运行
cd /path/to/hf-mirror-sync
nohup sudo caddy run \
  --envfile ./scripts/caddy/.env \
  --config ./scripts/caddy/Caddyfile \
  > /var/log/caddy/caddy.log 2>&1 &

# 查看进程
ps aux | grep caddy

# 停止（需要找到 PID）
sudo kill <PID>
```

#### 选项 C: 使用 screen 或 tmux

```bash
# 安装 screen
sudo apt install screen  # Ubuntu/Debian
brew install screen      # macOS

# 创建新的 screen 会话
screen -S caddy

# 在 screen 中运行
sudo caddy run --envfile ./scripts/caddy/.env --config ./scripts/caddy/Caddyfile

# 分离会话: Ctrl+A, 然后 D
# 重新连接: screen -r caddy
```

### 方法三：使用 Docker（高级）

如果需要使用 Docker 部署，可以创建 Dockerfile：

```dockerfile
FROM caddy:builder AS builder

RUN xcaddy build \
  --with github.com/caddyserver/replace-response \
  --with github.com/caddyserver/transform-encoder \
  --with github.com/caddy-dns/cloudflare

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
COPY scripts/caddy/ /etc/caddy/
COPY dist/ /var/www/html/

EXPOSE 80 443

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--envfile", "/etc/caddy/.env"]
```

---

## 验证部署

### 步骤 1: 检查服务状态

```bash
# 如果使用 systemd
sudo systemctl status caddy-hf-mirror

# 检查进程
ps aux | grep caddy

# 检查端口监听
sudo netstat -tlnp | grep -E ':(80|443)'
# 或使用 ss
sudo ss -tlnp | grep -E ':(80|443)'
```

### 步骤 2: 检查日志

```bash
# 访问日志
tail -f /var/log/caddy/your-domain.com/access.log

# 错误日志
tail -f /var/log/caddy/your-domain.com/error.log

# 如果使用 systemd
sudo journalctl -u caddy-hf-mirror -f
```

### 步骤 3: 测试访问

```bash
# 测试 HTTP 访问（应该自动跳转到 HTTPS）
curl -I http://your-domain.com

# 测试 HTTPS 访问
curl -I https://your-domain.com

# 测试静态文件
curl https://your-domain.com/favicon.ico

# 测试反向代理（访问一个模型页面）
curl -I https://your-domain.com/gpt2
```

### 步骤 4: 浏览器测试

1. 打开浏览器访问 `https://your-domain.com`
2. 检查 SSL 证书是否有效（应该自动申请）
3. 测试首页功能（搜索、热门排行等）
4. 测试访问一个模型页面，检查内容替换是否生效

### 步骤 5: 验证功能

**测试项目**:
- [ ] 首页可以正常访问
- [ ] SSL 证书自动申请成功
- [ ] 静态文件（JS、CSS）正常加载
- [ ] 搜索功能正常
- [ ] 热门排行正常显示
- [ ] 模型页面可以访问
- [ ] 内容替换生效（"Hugging Face" → "HF Mirror"）
- [ ] 域名替换生效（链接指向镜像站）
- [ ] 文件下载可以正常代理

---

## 常见问题

### Q1: Caddy 启动失败，提示 "bind: address already in use"

**原因**: 80 或 443 端口被占用

**解决方法**:
```bash
# 查找占用端口的进程
sudo lsof -i :80
sudo lsof -i :443

# 停止占用端口的服务（例如 Apache、Nginx）
sudo systemctl stop apache2
sudo systemctl stop nginx

# 或者修改 Caddyfile，使用其他端口（不推荐）
```

### Q2: SSL 证书申请失败

**可能原因**:
1. 域名 DNS 未正确解析
2. 防火墙阻止 80/443 端口
3. Cloudflare API Token 权限不足
4. 使用 Cloudflare 代理（需要关闭代理，使用 DNS only）

**解决方法**:
```bash
# 检查 DNS 解析
dig your-domain.com
nslookup your-domain.com

# 检查防火墙
sudo ufw status
sudo firewall-cmd --list-all

# 开放端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 如果使用 Cloudflare，确保 DNS 设置为 "DNS only"（灰色云朵）
```

### Q3: 访问网站显示 "502 Bad Gateway"

**原因**: 反向代理无法连接到上游服务器

**检查**:
```bash
# 检查网络连接
ping huggingface.co

# 检查 DNS 解析
nslookup huggingface.co

# 查看错误日志
tail -f /var/log/caddy/your-domain.com/error.log
```

### Q4: 静态文件 404 错误

**原因**: 文件路径不正确或权限不足

**解决方法**:
```bash
# 检查文件是否存在
ls -la /var/www/html/your-domain.com/

# 检查权限
sudo chown -R www-data:www-data /var/www/html/your-domain.com
sudo chmod -R 755 /var/www/html/your-domain.com

# 检查 Caddyfile 中的路径配置
```

### Q5: 日志文件过大

**原因**: 日志轮转配置可能未生效

**解决方法**:
```bash
# 手动清理旧日志
sudo find /var/log/caddy -name "*.log.*" -mtime +30 -delete

# 检查日志轮转配置（在 Caddyfile 中）
# roll_size, roll_keep, roll_keep_for 是否正确配置
```

### Q6: 内容替换不生效

**检查**:
1. 确认 `replace-response` 插件已安装
2. 检查 Caddyfile 中的 `order replace after encode` 配置
3. 查看错误日志是否有相关错误

**验证插件**:
```bash
caddy list-modules | grep replace
```

### Q7: 环境变量未生效

**检查**:
```bash
# 验证 .env 文件路径
ls -la scripts/caddy/.env

# 检查环境变量
caddy run --envfile ./scripts/caddy/.env --config ./scripts/caddy/Caddyfile --print

# 确保 .env 文件格式正确（无空格、无引号）
```

---

## 维护说明

### 日常维护

#### 1. 查看日志

```bash
# 实时查看访问日志
tail -f /var/log/caddy/your-domain.com/access.log

# 查看错误日志
tail -f /var/log/caddy/your-domain.com/error.log

# 分析访问量（前 10 个 IP）
awk '{print $1}' /var/log/caddy/your-domain.com/access.log | sort | uniq -c | sort -rn | head -10
```

#### 2. 监控资源使用

```bash
# CPU 和内存使用
top -p $(pgrep -f caddy)

# 或使用 htop
htop -p $(pgrep -f caddy)
```

#### 3. 更新配置

```bash
# 修改配置文件后，重新加载（不中断服务）
sudo systemctl reload caddy-hf-mirror

# 或使用 Caddy 命令
sudo caddy reload --config ./scripts/caddy/Caddyfile

# 验证配置语法
sudo caddy validate --config ./scripts/caddy/Caddyfile
```

#### 4. 更新 Caddy

```bash
# 下载新版本
wget https://caddyserver.com/download/... -O caddy-new

# 停止服务
sudo systemctl stop caddy-hf-mirror

# 备份旧版本
sudo cp /usr/local/bin/caddy /usr/local/bin/caddy.backup

# 替换新版本
sudo mv caddy-new /usr/local/bin/caddy
sudo chmod +x /usr/local/bin/caddy

# 验证版本
caddy version

# 启动服务
sudo systemctl start caddy-hf-mirror
```

### 备份

#### 备份配置

```bash
# 备份整个配置目录
tar -czf caddy-config-backup-$(date +%Y%m%d).tar.gz \
  scripts/caddy/ \
  dist/

# 备份日志（可选）
tar -czf caddy-logs-backup-$(date +%Y%m%d).tar.gz \
  /var/log/caddy/
```

#### 备份 SSL 证书

```bash
# Caddy 的证书通常存储在
# ~/.local/share/caddy/certificates/ (用户模式)
# 或 /var/lib/caddy/.local/share/caddy/certificates/ (系统模式)

# 备份证书目录
sudo tar -czf caddy-certificates-backup-$(date +%Y%m%d).tar.gz \
  /var/lib/caddy/.local/share/caddy/certificates/
```

### 性能优化

#### 1. 调整日志级别

如果不需要详细日志，可以调整日志级别：

```caddy
log hf_access {
    level INFO  # 或 WARN
    # ...
}
```

#### 2. 限制并发连接

在 Caddyfile 中添加：

```caddy
limits {
    max_connections 1000
}
```

#### 3. 启用缓存

对于静态资源，可以配置更长的缓存时间：

```caddy
header /front/* Cache-Control "public, max-age=604800"  # 7天
```

---

## 快速参考

### 常用命令

```bash
# 启动
sudo systemctl start caddy-hf-mirror

# 停止
sudo systemctl stop caddy-hf-mirror

# 重启
sudo systemctl restart caddy-hf-mirror

# 重新加载配置
sudo systemctl reload caddy-hf-mirror

# 查看状态
sudo systemctl status caddy-hf-mirror

# 查看日志
sudo journalctl -u caddy-hf-mirror -f

# 验证配置
sudo caddy validate --config ./scripts/caddy/Caddyfile

# 查看配置解析结果
sudo caddy adapt --config ./scripts/caddy/Caddyfile
```

### 重要路径

```
配置文件: /path/to/hf-mirror-sync/scripts/caddy/
静态文件: /var/www/html/your-domain.com/
访问日志: /var/log/caddy/your-domain.com/access.log
错误日志: /var/log/caddy/your-domain.com/error.log
Caddy 证书: /var/lib/caddy/.local/share/caddy/certificates/
```

---

## 获取帮助

- **Caddy 官方文档**: https://caddyserver.com/docs/
- **Caddy 社区论坛**: https://caddy.community/
- **GitHub Issues**: https://github.com/caddyserver/caddy/issues
- **本项目文档**: 查看 `ARCHITECTURE.md` 和 `CADDYFILE_GUIDE.md`
