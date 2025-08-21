#!/usr/bin/env python3
"""
EduVis Content Generation API Server
用于部署在您的服务器上的后端API服务

使用方法:
1. 将此文件和 v0_automation_toolkit 目录上传到您的服务器
2. 安装依赖: pip install flask flask-cors
3. 设置环境变量: export V0_API_KEY=your_api_key
4. 运行: python server-example.py
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
import os
import sys
import time
from pathlib import Path

app = Flask(__name__)
CORS(app, origins=["*"])  # 生产环境中应限制到具体域名

# 配置路径
TOOLKIT_DIR = Path("v0_automation_toolkit")
GENERATED_PROJECTS_DIR = Path("v0_generated_projects")

@app.route('/api/v0-generate', methods=['POST'])
def generate_content():
    """生成教育内容的API端点"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not prompt:
            return jsonify({
                "success": False,
                "error": "No prompt provided",
                "fallback": True
            }), 400

        # 设置环境变量
        env = os.environ.copy()
        if api_key:
            env['V0_API_KEY'] = api_key

        # 准备输入数据
        input_data = json.dumps({
            "problem": prompt,
            "type": "educational_content"
        })

        # 调用 v0_automation_toolkit (本地测试路径)
        toolkit_root = Path(__file__).parent / "v0_automation_toolkit"
        integration_script = toolkit_root / "v0_api_integration.py"
        
        if not integration_script.exists():
            return jsonify({
                "success": False,
                "error": f"v0_api_integration.py not found at {integration_script}",
                "fallback": True
            }), 500

        # 执行生成脚本
        result = subprocess.run([
            sys.executable, str(integration_script)
        ], 
        input=input_data, 
        capture_output=True, 
        text=True, 
        env=env,
        timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                
                # 如果生成成功，提供项目URL
                if response.get('success') and response.get('project_path'):
                    project_url = f"https://your-server.com/projects/{response['project_name']}"
                    response['projectUrl'] = project_url
                    
                return jsonify(response)
            except json.JSONDecodeError:
                print(f"Invalid JSON output: {result.stdout}")
                return jsonify({
                    "success": False,
                    "error": "Invalid response format",
                    "fallback": True
                }), 500
        else:
            print(f"Script failed: {result.stderr}")
            return jsonify({
                "success": False,
                "error": f"Generation failed: {result.stderr}",
                "fallback": True
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "Generation timeout (5 minutes)",
            "fallback": True
        }), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({
            "success": False, 
            "error": f"Server error: {str(e)}",
            "fallback": True
        }), 500

@app.route('/projects/<project_name>/')
def serve_project(project_name):
    """为生成的项目提供静态文件服务"""
    try:
        project_dir = GENERATED_PROJECTS_DIR / project_name / "out"
        if project_dir.exists():
            return send_from_directory(project_dir, "index.html")
        else:
            return "Project not found", 404
    except Exception as e:
        return f"Error serving project: {e}", 500

@app.route('/projects/<project_name>/<path:filename>')
def serve_project_files(project_name, filename):
    """为生成的项目提供静态资源文件"""
    try:
        project_dir = GENERATED_PROJECTS_DIR / project_name / "out"
        if project_dir.exists():
            return send_from_directory(project_dir, filename)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error serving file: {e}", 500

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "toolkit_exists": TOOLKIT_DIR.exists(),
        "projects_dir_exists": GENERATED_PROJECTS_DIR.exists()
    })

@app.route('/')
def root():
    """根路径说明"""
    return jsonify({
        "service": "EduVis Content Generation API",
        "version": "1.0",
        "endpoints": {
            "/api/v0-generate": "POST - Generate educational content",
            "/projects/<name>/": "GET - Access generated projects",
            "/health": "GET - Health check"
        }
    })

if __name__ == '__main__':
    print("Starting EduVis Content Generation API Server...")
    print(f"Toolkit directory: {TOOLKIT_DIR.absolute()}")
    print(f"Generated projects directory: {GENERATED_PROJECTS_DIR.absolute()}")
    
    # 确保必要目录存在
    GENERATED_PROJECTS_DIR.mkdir(exist_ok=True)
    
    # 检查 v0_automation_toolkit
    if not TOOLKIT_DIR.exists():
        print("Warning: v0_automation_toolkit directory not found!")
        print("Please ensure the toolkit is in the same directory as this script.")
    
    app.run(
        host='0.0.0.0', 
        port=int(os.environ.get('PORT', 5001)),
        debug=os.environ.get('DEBUG', 'False').lower() == 'true'
    )
