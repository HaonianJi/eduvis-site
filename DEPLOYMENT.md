# EduVis Site - GitHub Pages 部署指南

## 部署架构

本项目采用前后端分离的架构：

### 前端 (GitHub Pages)
- **EduVis 主站**: 静态网站，包含主页、About、媒体演示等
- **部署平台**: GitHub Pages
- **技术栈**: Next.js 静态导出

### 后端 (您的服务器)
- **内容生成服务**: Python API 服务，运行 v0_automation_toolkit
- **部署平台**: 您的服务器
- **技术栈**: Python + Flask/FastAPI

## 部署步骤

### 1. GitHub Pages 部署

#### 准备工作
1. 将此项目推送到 GitHub 仓库
2. 在 GitHub 仓库设置中配置 GitHub Pages
3. 在仓库的 Settings > Secrets and variables > Actions 中添加环境变量：
   ```
   API_URL = https://your-server.com/api/v0-generate
   ```

#### 自动部署
- 推送到 `main` 分支时会自动触发部署
- GitHub Actions 会自动构建并部署到 GitHub Pages
- 访问地址: `https://your-username.github.io/eduvis-site`

### 2. 服务器后端部署

#### 创建后端 API 服务
在您的服务器上创建一个 Python API 服务：

```python
# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/api/v0-generate', methods=['POST'])
def generate_content():
    try:
        data = request.json
        prompt = data.get('prompt')
        
        # 调用 v0_automation_toolkit
        result = subprocess.run([
            'python', 'v0_api_integration.py'
        ], input=json.dumps({"problem": prompt}), 
           capture_output=True, text=True)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            return jsonify(response)
        else:
            return jsonify({
                "success": False,
                "error": "Generation failed",
                "fallback": True
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e),
            "fallback": True
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### 部署后端服务
1. 将 `v0_automation_toolkit` 目录上传到您的服务器
2. 安装依赖: `pip install -r requirements.txt`
3. 设置环境变量: `export V0_API_KEY=your_api_key`
4. 运行服务: `python server.py`
5. 配置反向代理 (Nginx) 以提供 HTTPS

## 环境配置

### 前端环境变量
创建 `.env.local` 文件：
```bash
NEXT_PUBLIC_API_URL=https://your-server.com/api/v0-generate
```

### 后端环境变量
```bash
V0_API_KEY=your_v0_api_key
PORT=5000
```

## 本地开发

### 启动前端
```bash
cd eduvis-site
npm install
npm run dev
```

### 启动后端
```bash
cd v0_automation_toolkit
pip install -r requirements.txt
export V0_API_KEY=your_key
python server.py
```

## 新项目部署流程

当后端生成新的教育项目后，可以通过以下方式部署：

1. **手动部署**: 将生成的项目推送到新的 GitHub 仓库并启用 GitHub Pages
2. **自动部署**: 扩展后端服务，自动创建 GitHub 仓库并部署生成的项目

## 故障排除

### 常见问题
1. **CORS 错误**: 确保后端服务配置了正确的 CORS 策略
2. **API 调用失败**: 检查 `NEXT_PUBLIC_API_URL` 环境变量配置
3. **构建失败**: 检查 Next.js 静态导出配置

### 调试方法
- 查看 GitHub Actions 构建日志
- 检查浏览器开发者工具的网络请求
- 查看后端服务器日志
