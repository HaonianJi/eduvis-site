# EduVis Site

一个基于AI的教育内容可视化平台，帮助创建交互式教育内容和可视化材料。

## ✨ 特性

- 🎓 **教育内容展示**: 展示EduVis研究项目和成果
- 🎬 **媒体演示**: 包含视频演示和交互式内容
- 🤖 **AI内容生成**: 通过AI自动生成教育可视化工具
- 📱 **响应式设计**: 支持多种设备和屏幕尺寸
- 🚀 **现代技术栈**: Next.js 15 + TypeScript + Tailwind CSS

## 🏗️ 架构

- **前端**: Next.js 静态网站，部署在 GitHub Pages
- **后端**: Python API 服务，运行在独立服务器上
- **集成**: 前后端分离架构，支持跨域API调用

## 🚀 快速开始

### 本地开发

```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 打开浏览器访问 http://localhost:3000
```

### 配置API服务

如需启用内容生成功能，请：

1. 复制环境配置文件：
```bash
cp local-config.env .env.local
```

2. 修改 `.env.local` 中的API地址：
```bash
NEXT_PUBLIC_API_URL=http://your-server.com/api/v0-generate
```

### 构建部署

```bash
# 构建静态文件
pnpm run build

# 生成的文件在 out/ 目录
```

## 📦 部署

### GitHub Pages 部署

1. 推送代码到 GitHub 仓库
2. 在仓库设置中启用 GitHub Pages
3. 设置 Actions secrets:
   - `API_URL`: 您的API服务器地址
4. 推送到 main 分支自动触发部署

### API 服务器部署

参考 `server-example.py` 和 `DEPLOYMENT.md` 文档。

## 🛠️ 技术栈

- **框架**: Next.js 15
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **UI组件**: shadcn/ui
- **图标**: Lucide React
- **后端**: Python + Flask
- **部署**: GitHub Pages + 自定义服务器

## 📄 项目结构

```
eduvis-site/
├── app/                    # Next.js App Router 页面
├── components/             # React 组件
├── lib/                    # 工具函数
├── v0_automation_toolkit/  # Python AI 生成工具
├── public/                 # 静态资源
└── out/                    # 构建输出
```

## 🤝 贡献

欢迎贡献代码和建议！请查看我们的贡献指南。

## 📝 许可证

本项目采用 MIT 许可证。
