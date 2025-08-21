#!/usr/bin/env python3
"""
完整的 v0 到网站部署管道
从用户输入 -> v0 API 调用 -> 项目构建 -> 自动部署 -> 浏览器打开
"""

import os
import sys
import json
import time
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional

# 导入现有的 v0 API 和项目构建器
try:
    from v0_api_call import call_v0, _extract_json
    from auto_project_builder import AutoProjectBuilder
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保 v0_api_call.py 和 auto_project_builder.py 在同一目录下")
    sys.exit(1)

class V0CompletePipeline:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.prompt_template = self.base_dir / "prompt.txt"
        self.responses_dir = self.base_dir / "可能的响应"
        self.projects_dir = self.base_dir / "v0_generated_projects"
        self.ui_path = self.base_dir / "ui"
        
        # 确保目录存在
        self.responses_dir.mkdir(exist_ok=True)
        self.projects_dir.mkdir(exist_ok=True)

    def get_user_inputs(self) -> tuple[str, str]:
        """获取用户输入的 API key 和问题内容"""
        print("🚀 v0 完整自动化管道")
        print("=" * 50)
        
        # 获取 API Key
        api_key = input("请输入你的 v0 API Key: ").strip()
        if not api_key:
            print("❌ API Key 不能为空")
            sys.exit(1)
        
        print("\n请输入要可视化的化学问题:")
        print("(输入多行内容，最后输入空行结束)")
        problem_lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            problem_lines.append(line)
        
        problem_content = "\n".join(problem_lines).strip()
        if not problem_content:
            print("❌ 问题内容不能为空")
            sys.exit(1)
            
        return api_key, problem_content

    def create_full_prompt(self, problem_content: str) -> str:
        """将问题内容插入到 prompt 模板中"""
        if not self.prompt_template.exists():
            print(f"❌ 找不到 prompt 模板文件: {self.prompt_template}")
            sys.exit(1)
            
        try:
            with open(self.prompt_template, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # 将问题内容插入到 <problem> 标签中
            full_prompt = template.replace("<problem>", f"<problem>\n{problem_content}\n</problem>")
            
            print("✅ 成功生成完整 prompt")
            return full_prompt
            
        except Exception as e:
            print(f"❌ 读取 prompt 模板失败: {e}")
            sys.exit(1)

    def call_v0_api(self, api_key: str, prompt: str) -> str:
        """调用 v0 API 生成响应"""
        print("\n🔥 正在调用 v0 API...")
        
        # 设置环境变量
        os.environ["V0_API_KEY"] = api_key
        
        try:
            response = call_v0(prompt)
            print("✅ v0 API 调用成功")
            return response
        except Exception as e:
            print(f"❌ v0 API 调用失败: {e}")
            sys.exit(1)

    def save_response(self, response: str) -> Path:
        """保存 v0 响应到文件"""
        timestamp = int(time.time())
        response_file = self.responses_dir / f"generated_{timestamp}.json.raw.txt"
        
        try:
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(response)
            print(f"✅ 响应已保存到: {response_file}")
            return response_file
        except Exception as e:
            print(f"❌ 保存响应失败: {e}")
            sys.exit(1)

    def build_project(self, response_file: Path) -> Optional[Path]:
        """使用现有的项目构建器构建项目"""
        print("\n🏗️  开始构建 Next.js 项目...")
        
        timestamp = int(time.time())
        project_name = f"chemistry_webapp_{timestamp}"
        
        try:
            builder = AutoProjectBuilder(ui_path=str(self.ui_path) if self.ui_path.exists() else None)
            project_path = builder.build_project(
                input_file=str(response_file),
                output_dir=str(self.projects_dir),
                project_name=project_name
            )
            
            if project_path:
                print(f"✅ 项目构建成功: {project_path}")
                return Path(project_path)
            else:
                print("❌ 项目构建失败")
                return None
                
        except Exception as e:
            print(f"❌ 项目构建错误: {e}")
            return None

    def start_dev_server(self, project_path: Path) -> Optional[int]:
        """启动开发服务器并返回端口号"""
        print("\n🚀 启动开发服务器...")
        
        # 寻找可用端口
        import socket
        for port in range(3000, 3100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(("127.0.0.1", port))
                    break
            except OSError:
                continue
        else:
            print("❌ 找不到可用端口")
            return None
        
        try:
            print(f"📦 正在运行: cd {project_path} && npm run dev")
            
            # 由于我们已经配置了 package.json 的 dev 脚本为 "next dev --turbopack"
            # 我们需要指定端口参数
            proc = subprocess.Popen(
                ['npm', 'run', 'dev', '--', '-p', str(port)],
                cwd=str(project_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            print(f"🌐 开发服务器正在启动... 端口: {port}")
            print("⏳ 等待服务器就绪...")
            
            # 实时读取输出，等待 Ready 标记
            ready_found = False
            start_time = time.time()
            timeout = 30  # 30秒超时
            
            while time.time() - start_time < timeout:
                if proc.poll() is not None:
                    # 进程已结束
                    stdout, _ = proc.communicate()
                    print(f"❌ 服务器启动失败:")
                    print(stdout)
                    return None
                
                try:
                    # 非阻塞读取一行
                    line = proc.stdout.readline()
                    if line:
                        print(f"  {line.strip()}")
                        if "Ready in" in line or "Local:" in line:
                            ready_found = True
                            break
                except:
                    pass
                    
                time.sleep(0.5)
            
            if ready_found:
                print(f"✅ 开发服务器已启动: http://localhost:{port}")
                # 保存进程ID到文件，方便后续管理
                pid_file = project_path / '.dev_server.pid'
                with open(pid_file, 'w') as f:
                    f.write(str(proc.pid))
                return port
            else:
                print("❌ 服务器启动超时")
                proc.terminate()
                return None
                
        except Exception as e:
            print(f"❌ 启动开发服务器失败: {e}")
            return None

    def open_browser(self, port: int):
        """在浏览器中打开网站"""
        url = f"http://localhost:{port}"
        print(f"\n🌐 正在打开浏览器: {url}")
        
        try:
            webbrowser.open(url)
            print("✅ 浏览器已打开")
        except Exception as e:
            print(f"⚠️  自动打开浏览器失败: {e}")
            print(f"请手动访问: {url}")

    def run_complete_pipeline(self):
        """运行完整的管道"""
        try:
            # 1. 获取用户输入
            api_key, problem_content = self.get_user_inputs()
            
            # 2. 生成完整 prompt
            full_prompt = self.create_full_prompt(problem_content)
            
            # 3. 调用 v0 API
            response = self.call_v0_api(api_key, full_prompt)
            
            # 4. 保存响应
            response_file = self.save_response(response)
            
            # 5. 构建项目
            project_path = self.build_project(response_file)
            if not project_path:
                return
            
            # 6. 启动开发服务器
            port = self.start_dev_server(project_path)
            if not port:
                print(f"⚠️  服务器启动失败，请手动运行:")
                print(f"cd {project_path} && npm run dev")
                return
            
            # 7. 打开浏览器
            self.open_browser(port)
            
            # 8. 保持运行
            print("\n" + "="*60)
            print("🎉 完整流程已完成！")
            print(f"📁 项目路径: {project_path}")
            print(f"🌐 网站地址: http://localhost:{port}")
            print("📝 按 Ctrl+C 停止服务器")
            print("="*60)
            
            # 保持程序运行
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 再见！")
                
        except KeyboardInterrupt:
            print("\n👋 用户取消操作")
        except Exception as e:
            print(f"\n❌ 管道运行失败: {e}")

def main():
    """主函数"""
    pipeline = V0CompletePipeline()
    pipeline.run_complete_pipeline()

if __name__ == "__main__":
    main()
