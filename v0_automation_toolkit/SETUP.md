# 🔧 V0自动化工具包详细安装指南

## 📋 系统要求

### 必需环境
- **Python**: 3.8+ (推荐3.11+)
- **Node.js**: 18+ (推荐20+)
- **npm**: 9+ 或 yarn 1.22+
- **操作系统**: macOS, Linux, Windows

### 磁盘空间
- 工具包本体: ~50MB
- 每个生成项目: ~200-500MB
- 建议预留: 5GB+

## 🚀 安装步骤

### 1. 下载工具包
```bash
# 从GitHub下载（推荐）
git clone https://github.com/your-username/v0-automation-toolkit.git
cd v0-automation-toolkit

# 或直接下载ZIP包解压
```

### 2. 安装Python依赖
```bash
# 使用pip安装
pip install -r requirements.txt

# 或使用conda
conda install --file requirements.txt
```

### 3. 验证Node.js环境
```bash
# 检查版本
node --version  # 应显示 v18.0.0+
npm --version   # 应显示 9.0.0+

# 全局安装create-next-app
npm install -g create-next-app@latest
```

### 4. 设置v0 API Key
获取API Key: https://v0.dev/settings/api-keys

```bash
# 方法1: 运行时输入（推荐）
python v0_complete_pipeline.py
# 然后在提示时输入API Key

# 方法2: 环境变量
export V0_API_KEY="your_api_key_here"

# 方法3: .env文件（需安装python-dotenv）
echo "V0_API_KEY=your_api_key_here" > .env
```

## 🧪 测试安装

### 快速测试
```bash
# 运行完整管道测试
python v0_complete_pipeline.py
```

输入测试问题：
```
测试化学问题：
水的电解反应 H2O → H2 + O2
请设计简单的交互式教学页面展示电解过程
```

### 预期结果
```bash
✅ v0 API调用成功
✅ 项目构建完成
✅ 开发服务器启动: http://localhost:3000
✅ 浏览器自动打开
```

## 🔧 故障排除

### 常见问题1: Python模块导入错误
```bash
ImportError: No module named 'requests'
```
**解决方案:**
```bash
pip install requests --upgrade
```

### 常见问题2: Node.js版本过低
```bash
Error: create-next-app requires Node.js 18.17.0+
```
**解决方案:**
```bash
# 使用nvm更新Node.js
nvm install 20
nvm use 20
```

### 常见问题3: 端口被占用
```bash
Error: listen EADDRINUSE: address already in use :::3000
```
**解决方案:**
```bash
# 方法1: 杀死占用进程
lsof -ti:3000 | xargs kill -9

# 方法2: 使用其他端口
cd your_project && npm run dev -- -p 3001
```

### 常见问题4: API Key无效
```bash
❌ v0 API调用失败: 401 Unauthorized
```
**解决方案:**
1. 确认API Key正确复制
2. 检查账户余额和权限
3. 重新生成API Key

## 🔍 高级配置

### 自定义输出目录
```bash
# 修改默认输出路径
mkdir custom_projects
python auto_project_builder.py input.txt -o custom_projects
```

### 配置代理（如需要）
```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### 批量处理配置
创建批处理脚本 `batch_process.sh`:
```bash
#!/bin/bash
for problem in problems/*.txt; do
    echo "处理: $problem"
    python v0_complete_pipeline.py < "$problem"
    sleep 10  # 避免API限流
done
```

## 📊 性能优化

### 加速构建
```bash
# 使用yarn替代npm（更快）
npm install -g yarn
# 修改auto_project_builder.py中的npm为yarn

# 启用并行处理
export NODE_OPTIONS="--max-old-space-size=8192"
```

### 缓存优化
```bash
# 预缓存shadcn-ui组件
mkdir -p ~/.cache/v0-automation
cp -r ui ~/.cache/v0-automation/
```

## 🎯 验证清单

安装完成后，请确认以下功能正常：

- [ ] ✅ Python脚本可以正常运行
- [ ] ✅ v0 API调用成功
- [ ] ✅ Next.js项目可以创建
- [ ] ✅ shadcn-ui组件正常加载
- [ ] ✅ 开发服务器可以启动
- [ ] ✅ 浏览器可以正常访问

## 🆘 获取帮助

如果遇到其他问题：

1. 检查 `README.md` 中的常见用法
2. 查看 `examples/` 中的示例项目
3. 运行测试用例验证环境
4. 提交Issue描述具体错误信息

---

**🎉 安装完成，开始享受AI自动化教学网页生成的魅力吧！**
