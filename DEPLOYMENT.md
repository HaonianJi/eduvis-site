# EduVis Site - Vercel 部署指南

## 概述

本项目现已适配 Vercel 部署，支持完整的 v0 生成功能。与 GitHub Pages 静态部署不同，Vercel 支持无服务器函数，可以运行后端逻辑。

## 项目适配修改

### 1. Next.js 配置修改
- 移除了 `output: 'export'` 静态导出配置
- 移除了 `basePath` 和 `assetPrefix`，因为 Vercel 不需要这些配置

### 2. API 架构调整
- 创建了 `/api/v0-python-pipeline.py` 作为 Vercel Python 函数
- 修改了 `/app/api/v0-generate/route.ts` 以调用 Python 函数而非本地脚本
- 更新了前端组件以处理文件响应格式

### 3. 新增配置文件
- `vercel.json`: Vercel 部署配置
- `api/requirements.txt`: Python 函数依赖

## 部署步骤

### 第一步：推送代码到 GitHub

```bash
git add .
git commit -m "Adapt project for Vercel deployment"
git push
```

### 第二步：连接 Vercel

1. 访问 [vercel.com](https://vercel.com) 并登录
2. 点击 "New Project"
3. 选择您的 GitHub 仓库 `eduvis-site`
4. Vercel 会自动检测这是一个 Next.js 项目

### 第三步：配置环境变量

在 Vercel 项目设置中添加环境变量：
- `V0_API_KEY`: 您的 v0 API 密钥

设置步骤：
1. 进入项目 Settings → Environment Variables
2. 添加 `V0_API_KEY` 变量
3. 将值设置为您的实际 API 密钥

### 第四步：部署

1. 点击 "Deploy" 按钮
2. 等待构建完成（通常需要 1-3 分钟）
3. 部署成功后，您将获得一个 `.vercel.app` 域名

## 功能差异对比

| 功能 | GitHub Pages | Vercel |
|------|--------------|---------|
| 静态页面 | ✅ | ✅ |
| API 路由 | ❌ | ✅ |
| v0 生成功能 | ❌ | ✅ |
| Python 脚本 | ❌ | ✅ |
| 自定义域名 | ✅ | ✅ |
| 部署速度 | 快 | 快 |
| 免费额度 | 无限 | 100GB/月 |

## 技术架构

### Vercel 无服务器架构

```
用户请求 → Next.js API 路由 → Python 函数 → v0 API → 返回生成文件
```

### 与本地开发的区别

- **本地**: 生成完整项目并启动开发服务器
- **Vercel**: 直接返回生成的文件内容，适合静态展示

## 环境变量配置

### 必需环境变量
- `V0_API_KEY`: v0 平台的 API 密钥

### 可选环境变量
- `NODE_ENV`: 自动设置为 `production`

## 故障排除

### 常见问题

1. **Python 函数超时**
   - Vercel 免费版限制 10 秒执行时间
   - Pro 版本支持最长 60 秒

2. **API 密钥错误**
   - 检查环境变量是否正确设置
   - 确认 v0 API 密钥有效

3. **构建失败**
   - 检查 `package.json` 中的依赖
   - 查看 Vercel 构建日志

### 调试步骤

1. 查看 Vercel Functions 日志
2. 检查 Next.js 构建输出
3. 验证环境变量配置

## 性能优化

### 建议配置

1. **函数超时设置**
   ```json
   {
     "functions": {
       "app/api/v0-generate/route.ts": { "maxDuration": 30 },
       "api/v0-python-pipeline.py": { "maxDuration": 25 }
     }
   }
   ```

2. **缓存策略**
   - Vercel 自动缓存静态资源
   - API 响应可考虑添加缓存头

## 维护建议

1. **定期更新依赖**
2. **监控函数执行时间**
3. **检查 API 密钥有效期**
4. **备份重要配置**

## 支持

如果遇到部署问题：
1. 检查 Vercel 控制台日志
2. 参考 [Vercel 文档](https://vercel.com/docs)
3. 查看项目 Issues
