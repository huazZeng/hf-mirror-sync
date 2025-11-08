# Mirror site of huggingface

Public version: [https://hf-mirror.com/](https://hf-mirror.com/)

## 项目文档

- **[📖 完整部署教程](DEPLOYMENT_GUIDE.md)** - 详细的安装、配置和启动指南
- **[🏗️ 架构说明文档](ARCHITECTURE.md)** - 项目结构和设计原理
- **[⚙️ Caddyfile 配置详解](CADDYFILE_GUIDE.md)** - Caddyfile 语法和配置说明

## 快速开始

### 前置要求

- 安装 Caddy（包含 `replace-response`、`transform-encoder` 插件）
- 拥有一个域名并配置 DNS 解析
- （可选）Cloudflare API Token（用于自动证书申请）

### 快速部署

1. **安装 Caddy**

   下载包含所需插件的 Caddy：
   - [官方下载链接](https://caddyserver.com/download?package=github.com%2Fcaddyserver%2Freplace-response&package=github.com%2Fcaddy-dns%2Fcloudflare&package=github.com%2Fcaddyserver%2Ftransform-encoder)
   - 或使用 [xcaddy](https://github.com/caddyserver/xcaddy) 构建

2. **配置环境变量**

   创建 `scripts/caddy/.env` 文件：
   ```bash
   MIRROR_HOST=your-domain.com
   CF_TOKEN=your_cloudflare_api_token
   API_KEY=
   ```

3. **准备目录**

   ```bash
   # 创建静态文件目录
   sudo mkdir -p /var/www/html/your-domain.com
   sudo cp -r dist/* /var/www/html/your-domain.com/
   
   # 创建日志目录
   sudo mkdir -p /var/log/caddy/your-domain.com
   ```

4. **启动服务**

   ```bash
   # 前台运行（测试）
   sudo caddy run --envfile ./scripts/caddy/.env --config ./scripts/caddy/Caddyfile
   
   # 或使用 systemd（生产环境）
   # 详见 DEPLOYMENT_GUIDE.md
   ```

## 详细文档

更多详细信息请查看：

- **[完整部署教程](DEPLOYMENT_GUIDE.md)** - 包含不同操作系统的安装方法、systemd 配置、Docker 部署等
- **[架构说明文档](ARCHITECTURE.md)** - 了解项目架构、工作流程和技术特点
- **[Caddyfile 配置详解](CADDYFILE_GUIDE.md)** - 学习 Caddyfile 语法和配置项说明

## 功能特性

- ✅ 自动 HTTPS 证书申请和续期
- ✅ 内容替换（域名、品牌名称、Logo）
- ✅ 安全防护（防盗链、机器人过滤）
- ✅ 静态资源本地缓存
- ✅ 反向代理到 Hugging Face
- ✅ 支持 WebSeed（BitTorrent 下载）

## 许可证

本项目为开源项目，遵循相应开源许可证。