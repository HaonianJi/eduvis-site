#!/usr/bin/env python3
"""
V0 API Integration Script for Next.js Backend
专门用于与Node.js API后端集成的非交互式版本
"""

import os
import sys
import json
import time
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from v0_api_call import call_v0
from auto_project_builder import AutoProjectBuilder


class V0ApiIntegration:
    def __init__(self):
        self.project_builder = AutoProjectBuilder()
        
    def load_prompt_template(self):
        """加载prompt模板"""
        try:
            prompt_file = Path(__file__).parent / "prompt.txt"
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"❌ 无法加载prompt模板: {e}", file=sys.stderr)
            return ""
    
    def create_full_prompt(self, problem_content):
        """创建完整的prompt"""
        template = self.load_prompt_template()
        if not template:
            # Fallback prompt if template loading fails
            template = """请根据以下问题创建一个交互式教育网页：

问题：{problem}

要求：
1. 使用Next.js和React创建
2. 包含交互式元素
3. 提供步骤式教学
4. 包含可视化图表
5. 适合教学使用"""
        
        return template.format(problem=problem_content)
    
    def run_pipeline(self, problem_content, api_key=None):
        """运行完整管道 - 非交互式版本"""
        try:
            print("🚀 启动v0自动化管道...", file=sys.stderr)
            
            # 获取API密钥
            if not api_key:
                api_key = os.environ.get('V0_API_KEY')
            
            if not api_key:
                print("❌ 错误: 未提供API密钥", file=sys.stderr)
                return {"success": False, "error": "Missing API key"}
            
            print(f"🔑 使用API密钥: ...{api_key[-6:]}", file=sys.stderr)
            
            # 创建完整prompt
            full_prompt = self.create_full_prompt(problem_content)
            print("✅ 成功生成完整prompt", file=sys.stderr)
            
            # 调用v0 API
            print("🔥 正在调用v0 API...", file=sys.stderr)
            
            # 设置环境变量供v0_api_call.py使用
            os.environ['V0_API_KEY'] = api_key
            
            response_text = call_v0(full_prompt)
            
            # 尝试解析为JSON，如果失败则包装为简单格式
            try:
                response = json.loads(response_text)
            except json.JSONDecodeError:
                response = {"content": response_text}
            
            if not response:
                print("❌ v0 API调用失败", file=sys.stderr)
                return {"success": False, "error": "V0 API call failed"}
            
            print("✅ v0 API调用成功", file=sys.stderr)
            
            # 保存响应
            timestamp = int(time.time())
            response_file = f"generated_{timestamp}.json"
            response_path = Path(__file__).parent / "responses" / response_file
            response_path.parent.mkdir(exist_ok=True)
            
            with open(response_path, 'w', encoding='utf-8') as f:
                json.dump(response, f, ensure_ascii=False, indent=2)
            
            print(f"💾 响应已保存: {response_path}", file=sys.stderr)
            
            # 构建项目
            print("🏗️ 开始构建项目...", file=sys.stderr)
            
            # 创建输出目录
            toolkit_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(toolkit_dir, "generated_projects")
            os.makedirs(output_dir, exist_ok=True)
            
            project_path = self.project_builder.build_project(str(response_path), output_dir)
            if not project_path:
                print("❌ 项目构建失败", file=sys.stderr)
                return {"success": False, "error": "Project build failed"}
            
            print(f"✅ 项目构建成功: {project_path}", file=sys.stderr)
            
            # 启动开发服务器
            print("🚀 启动开发服务器...", file=sys.stderr)
            port = self.start_dev_server(project_path)
            
            if not port:
                print("❌ 服务器启动失败", file=sys.stderr)
                return {"success": False, "error": "Dev server start failed"}
            
            project_url = f"http://localhost:{port}"
            print(f"🎉 项目成功运行在: {project_url}", file=sys.stderr)
            
            # 输出成功结果到stdout供Node.js读取
            result = {
                "success": True,
                "projectUrl": project_url,
                "projectPath": str(project_path),
                "port": port,
                "message": f"项目成功生成并运行在端口 {port}"
            }
            
            print(json.dumps(result))
            return result
            
        except Exception as e:
            print(f"❌ 管道执行失败: {str(e)}", file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    def start_dev_server(self, project_path):
        """启动开发服务器"""
        import subprocess
        import time
        import socket
        
        # 找到可用端口
        def find_free_port(start_port=3002):
            for port in range(start_port, start_port + 100):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('localhost', port))
                        return port
                except OSError:
                    continue
            return None
        
        port = find_free_port()
        if not port:
            print("❌ 无法找到可用端口", file=sys.stderr)
            return None
        
        try:
            # 启动开发服务器
            env = os.environ.copy()
            env['PORT'] = str(port)
            
            process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=project_path,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # 等待服务器启动
            time.sleep(5)
            
            # 检查进程是否还在运行
            if process.poll() is None:
                print(f"✅ Dev server started on port {port} (PID: {process.pid})", file=sys.stderr)
                return port
            else:
                print("❌ Dev server failed to start", file=sys.stderr)
                return None
                
        except Exception as e:
            print(f"❌ 启动服务器时出错: {e}", file=sys.stderr)
            return None


def main():
    """主函数 - 从stdin读取参数"""
    try:
        # 从stdin读取问题内容
        problem_content = input().strip()
        
        if not problem_content:
            print(json.dumps({"success": False, "error": "No problem content provided"}))
            return
        
        # 从环境变量获取API密钥
        api_key = os.environ.get('V0_API_KEY')
        
        # 运行管道
        integration = V0ApiIntegration()
        result = integration.run_pipeline(problem_content, api_key)
        
        if not result.get("success"):
            print(json.dumps(result))
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(json.dumps({"success": False, "error": "Process interrupted"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
