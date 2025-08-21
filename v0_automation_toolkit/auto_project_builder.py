#!/usr/bin/env python3
"""
自动化V0项目构建器 - 完整构建可运行的Next.js项目

这个工具能够：
1. 创建标准Next.js项目骨架
2. 初始化shadcn-ui和安装所需组件
3. 提取和整合v0 API响应中的文件
4. 生成完全可运行的项目
"""

import os
import re
import json
import shutil
import subprocess
from pathlib import Path
import argparse
from typing import Dict, List, Tuple, Optional, Set
import socket
import time
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

class AutoProjectBuilder:
    def __init__(self, ui_path: Optional[str] = None):
        self.ui_path = ui_path
        self.setup_commands = []
        self.extracted_dependencies = []
        self.extracted_shadcn_commands = []
        
    def create_nextjs_skeleton(self, project_path: Path) -> bool:
        """创建Next.js项目骨架并安装shadcn-ui"""
        print(f"🏗️  正在创建Next.js项目骨架: {project_path}")

        # 清理旧目录
        if project_path.exists():
            print(f"  - 发现旧的项目目录，正在清理: {project_path}")
            try:
                shutil.rmtree(project_path)
            except OSError as e:
                print(f"  - 无法删除目录 {project_path}: {e}")
                print("  - 请检查是否有进程（如 'npm run dev'）正在使用该目录。")
                return False
        
        try:
            project_path.parent.mkdir(parents=True, exist_ok=True)
            if project_path.exists():
                shutil.rmtree(project_path)
            
            # 1. 创建Next.js项目
            print("  - Step 1: Running create-next-app...")
            result = subprocess.run([
                'npx', 'create-next-app@latest', str(project_path.name),
                '--typescript', '--eslint', '--tailwind', '--app', '--turbopack', '--yes'
            ], capture_output=True, text=True, timeout=180, cwd=str(project_path.parent))
            
            if result.returncode != 0:
                print(f"❌ create-next-app 失败: {result.stderr}")
                return False
            print("  ✅ Next.js项目创建成功")

            # 2. 手动配置shadcn-ui
            print("  - Step 2: Manually configuring shadcn-ui...")
            # 2a. 创建 components.json
            components_json_path = project_path / 'components.json'
            components_json_content = {
              "$schema": "https://ui.shadcn.com/schema.json",
              "style": "default",
              "rsc": True,
              "tsx": True,
              "tailwind": {
                "config": "tailwind.config.ts",
                "css": "app/globals.css",
                "baseColor": "slate",
                "cssVariables": True
              },
              "aliases": {
                "components": "@/components",
                "utils": "@/lib/utils"
              }
            }
            with open(components_json_path, 'w') as f:
                json.dump(components_json_content, f, indent=2)
            print("    ✅ components.json created.")

            # 2b. 修改 tsconfig.json
            tsconfig_path = project_path / 'tsconfig.json'
            with open(tsconfig_path, 'r') as f:
                tsconfig = json.load(f)
            
            tsconfig['compilerOptions']['baseUrl'] = "."
            # The default paths from create-next-app are fine with baseUrl
            # tsconfig['compilerOptions']['paths'] = {
            #     "@/*": ["./*"]
            # }

            with open(tsconfig_path, 'w') as f:
                json.dump(tsconfig, f, indent=2)
            print("    ✅ tsconfig.json updated with baseUrl.")

            # 手动配置 Tailwind CSS
            self._configure_tailwind(project_path)
        
            # 配置 dev 脚本使用 Turbopack
            self._configure_dev_script(project_path)
        
            # 配置 Next.js 图片域名
            self._configure_next_config(project_path)
        
            # 安装 shadcn-ui 核心依赖 + 常用动画库
            print("  - Step 3: Installing shadcn-ui core dependencies + common animation libraries...")
            dependencies = [
                'class-variance-authority', 'clsx', 'tailwind-merge', 'tailwindcss-animate',
                'framer-motion', 'lucide-react', '@radix-ui/react-icons',  # 添加常用的动画和图标库
                '@radix-ui/react-accordion',
                '@radix-ui/react-alert-dialog',
                '@radix-ui/react-aspect-ratio',
                '@radix-ui/react-avatar',
                '@radix-ui/react-checkbox',
                '@radix-ui/react-collapsible',
                '@radix-ui/react-context-menu',
                '@radix-ui/react-dialog',
                '@radix-ui/react-dropdown-menu',
                '@radix-ui/react-hover-card',
                '@radix-ui/react-label',
                '@radix-ui/react-menubar',
                '@radix-ui/react-navigation-menu',
                '@radix-ui/react-popover',
                '@radix-ui/react-progress',
                '@radix-ui/react-radio-group',
                '@radix-ui/react-scroll-area',
                '@radix-ui/react-select',
                '@radix-ui/react-separator',
                '@radix-ui/react-slider',
                '@radix-ui/react-slot',
                '@radix-ui/react-switch',
                '@radix-ui/react-tabs',
                '@radix-ui/react-toast',
                '@radix-ui/react-toggle',
                '@radix-ui/react-toggle-group',
                '@radix-ui/react-tooltip',
                # Other common dependencies
                'cmdk',
                'date-fns',
                'react-day-picker',
                'embla-carousel-react',
                'recharts',
                'vaul'
            ]
            result = subprocess.run(
                ['npm', 'install'] + dependencies,
                capture_output=True, text=True, timeout=180, cwd=str(project_path)
            )

            if result.returncode != 0:
                print(f"⚠️  安装shadcn-ui核心依赖失败: {result.stderr}")
            else:
                print("  ✅ shadcn-ui核心依赖安装成功")
            
            # 安装所有常用的shadcn-ui组件（一次性批量安装，大幅提升速度）
            print("  - Step 3c: Installing ALL essential shadcn-ui components (bulk install for speed)...")
            
            # 所有常用组件一次性安装（更快，减少网络请求）
            all_components = [
                'button', 'input', 'card', 'label', 'accordion', 'tabs', 'separator', 'alert',
                'checkbox', 'select', 'dialog', 'popover', 'badge', 'avatar', 'progress', 'toast',
                'table', 'dropdown-menu', 'hover-card', 'tooltip', 'sheet', 'slider', 'switch',
                'textarea', 'radio-group', 'calendar', 'date-picker', 'command', 'context-menu'
            ]
            
            installed_count = 0
            try:
                print(f"    Installing {len(all_components)} components in one batch...")
                # 尝试一次性安装所有组件（最快方式）
                result = subprocess.run(
                    ['npx', 'shadcn@latest', 'add', '--yes'] + all_components,
                    capture_output=True, text=True, timeout=180, cwd=str(project_path)  # 3分钟超时
                )
                
                if result.returncode == 0:
                    installed_count = len(all_components)
                    print(f"    ✅ ALL {installed_count} components installed successfully in one batch!")
                else:
                    print(f"    ⚠️ Bulk install failed, falling back to smaller batches...")
                    # 如果一次性安装失败，分成4批安装
                    batches = [
                        all_components[0:8],   # 基础组件
                        all_components[8:16],  # 表单组件
                        all_components[16:24], # 交互组件
                        all_components[24:]    # 其他组件
                    ]
                    
                    for i, batch in enumerate(batches, 1):
                        try:
                            print(f"      Batch {i}/4: {', '.join(batch[:3])}...")
                            batch_result = subprocess.run(
                                ['npx', 'shadcn@latest', 'add', '--yes'] + batch,
                                capture_output=True, text=True, timeout=90, cwd=str(project_path)
                            )
                            
                            if batch_result.returncode == 0:
                                installed_count += len(batch)
                                print(f"      ✅ Batch {i} installed ({len(batch)} components)")
                            else:
                                print(f"      ⚠️ Batch {i} failed, skipping...")
                        except Exception as e:
                            print(f"      ❌ Batch {i} exception: {e}")
                    
            except Exception as e:
                print(f"    ❌ Bulk installation exception: {e}")
                installed_count = 0
                    
            print(f"  🚀 Successfully installed {installed_count} shadcn-ui components ({installed_count}/{len(all_components)})")
            
            # 安装从v0响应中提取的依赖
            if hasattr(self, 'extracted_dependencies') and self.extracted_dependencies:
                print("  - Step 3b: Installing extracted dependencies...")
                for dep_cmd in self.extracted_dependencies:
                    # 解析npm install命令
                    if dep_cmd.startswith('npm install '):
                        packages = dep_cmd.replace('npm install ', '').split()
                        if packages:
                            print(f"    Installing: {' '.join(packages)}")
                            try:
                                result = subprocess.run(['npm', 'install'] + packages,
                                                      cwd=project_path, check=True, capture_output=True, text=True, timeout=180)
                                print(f"    ✅ 成功安装: {' '.join(packages)}")
                            except subprocess.CalledProcessError as e:
                                print(f"    ⚠️ 安装失败: {' '.join(packages)} - {e.stderr}")
                            except Exception as e:
                                print(f"    ⚠️ 安装异常: {' '.join(packages)} - {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建项目骨架时出错: {e}")
            return False

    def _configure_tailwind(self, project_path: Path):
        """根据项目中的 tailwindcss 版本生成对应配置 (v3 或 v4)。"""
        print("  - Step 2c: Configuring Tailwind...")
        # 读取 package.json 判断 tailwindcss 版本
        pkg_path = project_path / 'package.json'
        tailwind_version = '3'
        try:
            with open(pkg_path, 'r') as f:
                pkg = json.load(f)
            tw = pkg.get('devDependencies', {}).get('tailwindcss') or pkg.get('dependencies', {}).get('tailwindcss')
            if tw and tw.strip().startswith('^4') or tw.strip().startswith('4'):
                tailwind_version = '4'
        except Exception:
            pass

        if tailwind_version == '4':
            self._configure_tailwind_v4(project_path)
        else:
            self._configure_tailwind_v3(project_path)

    def _configure_dev_script(self, project_path: Path):
        """修改 package.json 的 dev 脚本使用 Turbopack"""
        print("  - Step 2d: Configuring dev script to use Turbopack...")
        pkg_path = project_path / 'package.json'
        try:
            with open(pkg_path, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
            
            # 修改 dev 脚本使用 Turbopack
            if 'scripts' in pkg and 'dev' in pkg['scripts']:
                pkg['scripts']['dev'] = 'next dev --turbopack'
                
            with open(pkg_path, 'w', encoding='utf-8') as f:
                json.dump(pkg, f, indent=2, ensure_ascii=False)
            
            print("    ✅ Dev script configured to use Turbopack")
        except Exception as e:
            print(f"    ⚠️  Failed to configure dev script: {e}")

    def _configure_next_config(self, project_path: Path):
        """生成 next.config.js 配置文件，支持常见的外部图片域名"""
        print("  - Step 2e: Configuring next.config.js for external images...")
        
        # 常见的 v0 使用的图片域名
        common_image_domains = [
            'placehold.co',
            'via.placeholder.com', 
            'picsum.photos',
            'images.unsplash.com',
            'source.unsplash.com',
            'cdn.pixabay.com',
            'images.pexels.com',
            'avatars.githubusercontent.com',
            'github.com',
            'raw.githubusercontent.com'
        ]
        
        next_config_content = f'''/** @type {{import('next').NextConfig}} */
const nextConfig = {{
  images: {{
    domains: [
{chr(10).join([f'      "{domain}",' for domain in common_image_domains])}
    ],
    remotePatterns: [
      {{
        protocol: 'https',
        hostname: '**',
      }},
    ],
  }},
  experimental: {{
    turbo: {{
      rules: {{
        '*.svg': {{
          loaders: ['@svgr/webpack'],
          as: '*.js',
        }},
      }},
    }},
  }},
}};

export default nextConfig;
'''
        
        try:
            config_path = project_path / 'next.config.js'
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(next_config_content)
            
            print("    ✅ next.config.js configured with common image domains")
        except Exception as e:
            print(f"    ⚠️  Failed to configure next.config.js: {e}")

    def _configure_tailwind_v3(self, project_path: Path):
        print("    • Detected Tailwind v3 – writing tailwind.config.ts and @tailwind globals.css")
        # 配置 tailwind.config.ts (v3)
        tailwind_config_content = """\
import type { Config } from "tailwindcss"

const config = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
	],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config

export default config
"""
        with open(project_path / 'tailwind.config.ts', 'w') as f:
            f.write(tailwind_config_content)
        print("    ✅ tailwind.config.ts configured (v3).")

        # 配置 app/globals.css (v3)
        globals_css_content = """\
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}

@layer base {
  body {
    @apply bg-background text-foreground;
  }
}
"""
        with open(project_path / 'app' / 'globals.css', 'w') as f:
            f.write(globals_css_content)
        print("    ✅ app/globals.css configured (v3).")

        # PostCSS (v3)
        postcss_cfg = """export default {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n};\n"""
        with open(project_path / 'postcss.config.mjs', 'w') as f:
            f.write(postcss_cfg)
        print("    ✅ postcss.config.mjs configured (v3).")

    def _configure_tailwind_v4(self, project_path: Path):
        print("    • Detected Tailwind v4 – using @import and @theme in globals.css")
        # v4: tailwind.config.ts 通常不需要，但保留空的导出以兼容工具
        with open(project_path / 'tailwind.config.ts', 'w') as f:
            f.write('export default {}\n')
        print("    ✅ tailwind.config.ts (stub) written (v4).")

        globals_css_content = """\
@import "tailwindcss";

@theme {
  --color-background: hsl(var(--background));
  --color-foreground: hsl(var(--foreground));
  --color-border: hsl(var(--border));
  --color-input: hsl(var(--input));
  --color-ring: hsl(var(--ring));
  --color-primary: hsl(var(--primary));
  --color-primary-foreground: hsl(var(--primary-foreground));
  --color-secondary: hsl(var(--secondary));
  --color-secondary-foreground: hsl(var(--secondary-foreground));
  --color-destructive: hsl(var(--destructive));
  --color-destructive-foreground: hsl(var(--destructive-foreground));
  --color-muted: hsl(var(--muted));
  --color-muted-foreground: hsl(var(--muted-foreground));
  --color-accent: hsl(var(--accent));
  --color-accent-foreground: hsl(var(--accent-foreground));
  --color-popover: hsl(var(--popover));
  --color-popover-foreground: hsl(var(--popover-foreground));
  --color-card: hsl(var(--card));
  --color-card-foreground: hsl(var(--card-foreground));
}

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}

@layer base {
  body { @apply bg-background text-foreground; }
}
"""
        with open(project_path / 'app' / 'globals.css', 'w') as f:
            f.write(globals_css_content)
        print("    ✅ app/globals.css configured (v4).")

        # PostCSS (v4)
        with open(project_path / 'postcss.config.mjs', 'w') as f:
            f.write('export default {\n  plugins: ["@tailwindcss/postcss"],\n};\n')
        print("    ✅ postcss.config.mjs configured (v4).")
    
    def extract_files_from_response(self, file_path: str) -> Dict[str, Dict]:
        """从v0响应文件中提取所有文件"""
        print(f"📄 正在解析文件: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        files = {}
        
        # 首先尝试解析JSON包装格式的响应
        content = raw_content
        try:
            data = json.loads(raw_content)
            if 'content' in data and isinstance(data['content'], str):
                print("📋 检测到JSON包装格式，提取content字段")
                content = data['content']
                
                # 处理新的v0 API格式：跳过<Thinking>标签内容
                if content.startswith('<Thinking>'):
                    print("📋 检测到v0新格式，跳过思考过程")
                    # 查找</Thinking>标签结束位置
                    thinking_end = content.find('</Thinking>')
                    if thinking_end != -1:
                        content = content[thinking_end + 12:].strip()  # +12 for </Thinking>
                        print(f"📋 提取实际内容，长度: {len(content)}")
                    else:
                        # 如果没有找到结束标签，尝试查找实际代码开始的地方
                        # 通常代码会在一些常见标记后开始
                        markers = ['Here\'s the implementation:', 'I\'ll create', '```', 'Let me create']
                        for marker in markers:
                            marker_pos = content.find(marker)
                            if marker_pos != -1:
                                content = content[marker_pos:].strip()
                                print(f"📋 从标记'{marker}'开始提取，长度: {len(content)}")
                                break
                        else:
                            print("⚠️  未找到合适的内容开始位置，使用原始内容")
                            
        except json.JSONDecodeError:
            print("📋 非JSON包装格式，直接解析")
        
        # 首先提取依赖安装命令
        self._extract_dependency_commands(content)
        
        # 然后尝试新的JSON格式
        try:
            # 寻找JSON代码块
            json_match = re.search(r'```json\s*\n(\{.*?\n\})\s*\n```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                # 检查是否有files数组
                if 'files' in data and isinstance(data['files'], list):
                    print("📋 检测到新的JSON格式")
                    for file_obj in data['files']:
                        if 'path' in file_obj and 'content' in file_obj:
                            path = file_obj['path']
                            content = file_obj['content']
                            
                            # 推断语言类型
                            lang = self._infer_language_from_path(path)
                            
                            files[path] = {
                                'content': content.strip(),
                                'language': lang,
                                'source': 'json_format'
                            }
                    
                    print(f"📊 提取了 {len(files)} 个文件")
                    return files
        except (json.JSONDecodeError, KeyError) as e:
            print(f"📋 JSON格式解析失败，尝试传统Markdown格式: {e}")
        
        # 回退到传统的Markdown解析
        print("📋 使用传统Markdown格式解析")
        processed_code_blocks = set()
        
        # 定义解析模式（优先级从高到低）
        patterns = [
            # 1. 带 file="" 属性的代码块
            (r'```(\w+)\s+file="([^"]+)"\s*\n(.*?)\n```', 'explicit_file'),
            # 2. Markdown标题定义的代码块
            (r'####\s*`([^`]+)`\s*\n```(\w+)?\s*\n(.*?)\n```', 'markdown_header'),
            # 3. Shell命令块
            (r'```(?:sh|bash)\s*\n(.*?)\n```', 'shell_commands'),
            # 4. package.json
            (r'```json\s*\n(\{.*?"name":.*?\})\s*\n```', 'package_json'),
            # 5. TSX组件
            (r'```tsx\s*\n(.*?)\n```', 'tsx_component'),
            # 6. TypeScript文件
            (r'```(?:ts|typescript)\s*\n(.*?)\n```', 'typescript_file'),
            # 7. CSS文件
            (r'```css\s*\n(.*?)\n```', 'css_file'),
        ]
        
        for pattern, source_type in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            
            for match in matches:
                if source_type == 'explicit_file':
                    lang, filename, code = match
                elif source_type == 'markdown_header':
                    filename, lang, code = match
                    lang = lang or 'tsx'
                elif source_type == 'shell_commands':
                    code = match
                    self.setup_commands.extend(code.strip().split('\n'))
                    continue
                elif source_type == 'package_json':
                    code = match
                    filename = 'package.json'
                    lang = 'json'
                else:
                    code = match
                    filename = None  # 需要推断
                    lang = source_type.split('_')[0]
                
                clean_code = code.strip()
                if not clean_code or clean_code in processed_code_blocks:
                    continue
                
                processed_code_blocks.add(clean_code)
                
                # 推断文件名（如果没有明确指定）
                if not filename:
                    if source_type == 'tsx_component':
                        filename = self._infer_component_filename(clean_code, len(files))
                    elif source_type == 'typescript_file':
                        if 'utils' in clean_code.lower() or 'cn(' in clean_code:
                            filename = 'lib/utils.ts'
                        else:
                            filename = f'lib/helpers-{len(files)}.ts'
                    elif source_type == 'css_file':
                        if '@tailwind' in clean_code:
                            filename = 'app/globals.css'
                        else:
                            filename = f'styles/style-{len(files)}.css'
                
                if filename and filename not in files:
                    files[filename] = {
                        'content': clean_code,
                        'language': lang,
                        'source': source_type
                    }
        
        print(f"📊 提取了 {len(files)} 个文件")
        return files
    
    def _infer_language_from_path(self, path: str) -> str:
        """根据文件路径推断语言类型"""
        extension = Path(path).suffix.lower()
        lang_map = {
            '.tsx': 'tsx',
            '.ts': 'typescript', 
            '.js': 'javascript',
            '.jsx': 'jsx',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.py': 'python',
            '.html': 'html'
        }
        return lang_map.get(extension, 'text')
    
    def _extract_dependency_commands(self, content: str):
        """从 v0 响应中提取依赖安装命令"""
        dependency_commands = []
        shadcn_commands = []
        
        # 提取所有 bash 代码块
        bash_pattern = r'```bash\s*\n(.*?)\n```'
        bash_blocks = re.findall(bash_pattern, content, re.DOTALL)
        
        for block in bash_blocks:
            lines = block.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # npm install 命令
                if line.startswith('npm install '):
                    dependency_commands.append(line)
                    print(f"📦 发现依赖安装命令: {line}")
                
                # shadcn-ui 相关命令
                elif 'shadcn' in line.lower() or 'shadcn-ui' in line.lower():
                    shadcn_commands.append(line)
                    print(f"🎨 发现 shadcn-ui 命令: {line}")
        
        # 存储提取的命令供后续使用
        self.extracted_dependencies = dependency_commands
        self.extracted_shadcn_commands = shadcn_commands
        
        if dependency_commands:
            print(f"📋 提取了 {len(dependency_commands)} 条依赖安装命令")
        if shadcn_commands:
            print(f"📋 提取了 {len(shadcn_commands)} 条 shadcn-ui 命令")
    
    def _infer_component_filename(self, code: str, file_count: int) -> str:
        """从TSX内容推断组件文件名"""
        # 尝试从export default或function名称推断
        export_match = re.search(r'export\s+default\s+function\s+(\w+)', code)
        if export_match:
            component_name = export_match.group(1)
            return f'components/{self._camel_to_kebab(component_name)}.tsx'
        
        # 尝试从函数定义推断
        function_match = re.search(r'function\s+(\w+)', code)
        if function_match:
            component_name = function_match.group(1)
            return f'components/{self._camel_to_kebab(component_name)}.tsx'
        
        # 如果找不到，使用默认名称
        return f'components/component-{file_count}.tsx'
    
    def _camel_to_kebab(self, name: str) -> str:
        """将CamelCase转换为kebab-case"""
        return re.sub(r'([A-Z])', r'-\1', name).lower().lstrip('-')
    
    def _fix_styled_jsx(self, content: str) -> str:
        """自动修复 styled-jsx 问题，转换为 Tailwind CSS"""
        
        # 常见的 styled-jsx 到 Tailwind CSS 的转换规则
        animation_replacements = {
            # 气泡动画替换为 Tailwind 内置动画
            'animate-bubble-up-1': 'animate-bounce',
            'animate-bubble-up-2': 'animate-pulse', 
            'animate-bubble-up-3': 'animate-ping',
            'animate-bubble-up': 'animate-bounce',
            # 其他常见自定义动画
            'animate-fade-in': 'animate-pulse',
            'animate-slide-up': 'animate-bounce',
            'animate-float': 'animate-pulse',
        }
        
        # 1. 移除整个 <style jsx> 块
        content = re.sub(r'<style jsx>\{`[^`]*`\}</style>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style jsx>\{`[^`]*`\}</style>\s*\n', '', content, flags=re.DOTALL)
        
        # 2. 替换自定义动画类名为 Tailwind 内置动画
        for custom_class, tailwind_class in animation_replacements.items():
            # 直接替换动画类名
            content = content.replace(custom_class, tailwind_class)
            # 使用正则表达式替换 className 中的动画类
            content = re.sub(rf'\b{re.escape(custom_class)}\b', tailwind_class, content)
        
        # 3. 清理多余的空行和格式
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # 合并多个空行
        content = re.sub(r'</div>\s*\n\s*\);', '</div>\n);', content)  # 清理结尾格式
        
        return content
    
    def _fix_import_conflicts(self, content: str) -> str:
        """自动修复导入名称冲突，特别是 Tooltip 组件冲突"""
        
        # 检测冲突：同时存在 recharts 和 ui/tooltip 导入，且都包含 Tooltip
        recharts_import_match = re.search(r'import\s*\{\s*([^}]*)\s*\}\s*from\s*[\'"]recharts[\'"];', content)
        ui_tooltip_import_match = re.search(r'import\s*\{\s*([^}]*)\s*\}\s*from\s*[\'"]@/components/ui/tooltip[\'"];', content)
        
        if not (recharts_import_match and ui_tooltip_import_match):
            return content  # 没有冲突
            
        recharts_imports = [imp.strip() for imp in recharts_import_match.group(1).split(',') if imp.strip()]
        ui_tooltip_imports = [imp.strip() for imp in ui_tooltip_import_match.group(1).split(',') if imp.strip()]
        
        # 检查是否存在 Tooltip 冲突
        has_recharts_tooltip = any('Tooltip' in imp and ' as ' not in imp for imp in recharts_imports)
        has_ui_tooltip = any(imp.startswith('Tooltip') and ' as ' not in imp for imp in ui_tooltip_imports)
        
        if not (has_recharts_tooltip and has_ui_tooltip):
            return content  # 没有 Tooltip 冲突
            
        print("    - 检测到 Tooltip 导入冲突，正在自动修复...")
        
        # 1. 修复 recharts 导入：Tooltip -> Tooltip as RechartsTooltip
        new_recharts_imports = []
        for imp in recharts_imports:
            if imp.strip() == 'Tooltip':
                new_recharts_imports.append('Tooltip as RechartsTooltip')
            elif imp.strip() == 'Legend':
                new_recharts_imports.append('Legend as RechartsLegend')
            else:
                new_recharts_imports.append(imp)
                
        new_recharts_line = f"import {{ {', '.join(new_recharts_imports)} }} from 'recharts';"
        content = re.sub(r'import\s*\{\s*[^}]*\s*\}\s*from\s*[\'"]recharts[\'"];', new_recharts_line, content)
        
        # 2. 修复 ui/tooltip 导入：各组件添加 UI 前缀
        new_ui_imports = []
        for imp in ui_tooltip_imports:
            imp = imp.strip()
            if ' as ' in imp:
                new_ui_imports.append(imp)  # 已有别名，保持不变
            else:
                new_ui_imports.append(f"{imp} as UI{imp}")
                
        new_ui_line = f"import {{ {', '.join(new_ui_imports)} }} from '@/components/ui/tooltip';"
        content = re.sub(r'import\s*\{\s*[^}]*\s*\}\s*from\s*[\'"]@/components/ui/tooltip[\'"];', new_ui_line, content)
        
        # 3. 更新使用处：<Tooltip -> <RechartsTooltip（仅在图表上下文中）
        if 'LineChart' in content or 'BarChart' in content or 'PieChart' in content:
            content = re.sub(r'<Tooltip(?=\s|>|/)', '<RechartsTooltip', content)
            content = re.sub(r'</Tooltip>', '</RechartsTooltip>', content)
        
        return content
    
    def _fix_variable_scope_errors(self, content: str) -> str:
        """自动修复常见的变量作用域错误 - 更精确版本"""
        
        # 只修复 generateTrajectory 函数中的特定错误
        # 这是从实际遇到的错误中总结的模式
        if 'generateTrajectory' in content:
            # 查找有问题的行：使用了未定义的 initialVelocity, angle, initialHeight
            problematic_pattern = r'(initialVelocity|angle|initialHeight)(?!\s*[,}:])'
            
            # 但要排除这些情况：
            # 1. 接口定义：export interface ProjectileState { initialVelocity: number }
            # 2. 解构赋值：const { initialVelocity, angle } = state
            # 3. 已经有 state. 前缀的：state.initialVelocity
            
            lines = content.split('\n')
            modified = False
            
            for i, line in enumerate(lines):
                # 跳过接口定义行
                if 'interface' in line or 'const {' in line or 'state.' in line:
                    continue
                    
                # 只在特定上下文中修复（generateTrajectory 函数内部）
                if ('initialVelocity' in line and 'state.initialVelocity' not in line and 
                    not line.strip().endswith(': number;') and 'const {' not in line):
                    
                    # 修复这一行中的未定义变量
                    original_line = line
                    line = re.sub(r'\binitialVelocity\b(?!\s*[,}:])', 'state.initialVelocity', line)
                    line = re.sub(r'\bangle\b(?!\s*[,}:])', 'state.angle', line)  
                    line = re.sub(r'\binitialHeight\b(?!\s*[,}:])', 'state.initialHeight', line)
                    
                    if line != original_line:
                        lines[i] = line
                        modified = True
            
            if modified:
                content = '\n'.join(lines)
        
        return content
    
    def _apply_safe_fixes_only(self, content: str, filepath: str) -> str:
        """超级保守的修复策略 - 只修复100%确定安全的问题"""
        
        # 白名单：只修复这些精确的已知问题模式
        safe_fixes = []
        
        # 1. 只修复明确的导入冲突（手动验证过的模式）
        if 'components/projectile-simulator.tsx' in filepath:
            # 修复特定的 Tooltip 导入冲突
            if ('from \'recharts\'' in content and 'from \'@/components/ui/tooltip\'' in content 
                and 'Tooltip,' in content):
                
                # 非常精确的替换，只修复这一个具体的导入行
                content = re.sub(
                    r'import \{ ([^}]*), Tooltip, ([^}]*) \} from \'recharts\';',
                    r'import { \1, Tooltip as RechartsTooltip, \2 } from \'recharts\';',
                    content
                )
                
                content = re.sub(
                    r'import \{ Tooltip, ([^}]*) \} from \'@/components/ui/tooltip\';',
                    r'import { Tooltip as UITooltip, \1 } from \'@/components/ui/tooltip\';',
                    content  
                )
                
                # 更新使用处
                if 'LineChart' in content:
                    content = re.sub(r'<Tooltip ', '<RechartsTooltip ', content)
                    content = re.sub(r'</Tooltip>', '</RechartsTooltip>', content)
                
                print("    - 应用了安全的导入冲突修复")
        
        # 2. 只修复physics.ts中的特定错误
        if 'lib/physics.ts' in filepath:
            # 修复generateTrajectory函数中的具体错误行
            problematic_line = r'const t_final = \(initialVelocity \* Math\.sin\(toRadians\(angle\)\) \+ Math\.sqrt\(Math\.pow\(initialVelocity \* Math\.sin\(toRadians\(angle\)\), 2\) \+ 2 \* G \* initialHeight\)\) / G;'
            fixed_line = 'const t_final = (state.initialVelocity * Math.sin(toRadians(state.angle)) + Math.sqrt(Math.pow(state.initialVelocity * Math.sin(toRadians(state.angle)), 2) + 2 * G * state.initialHeight)) / G;'
            
            if re.search(problematic_line, content):
                content = re.sub(problematic_line, fixed_line, content)
                print("    - 应用了安全的变量作用域修复")
        
        return content
    
    def _fix_variable_scope_errors_conservative(self, content: str) -> str:
        """保守的变量作用域错误修复 - 只修复明确识别的问题"""
        
        # 只修复非常特定的已知错误模式，避免破坏正确的代码
        # 基于实际遇到的错误案例进行精确匹配
        
        specific_fixes = [
            # 修复 generateTrajectory 函数中 t_final 计算行的错误
            {
                'pattern': r'const t_final = \(initialVelocity \* Math\.sin\(toRadians\(angle\)\)',
                'replacement': r'const t_final = (state.initialVelocity * Math.sin(toRadians(state.angle))',
                'context': 'generateTrajectory'
            }
        ]
        
        for fix in specific_fixes:
            if fix['context'] in content:
                if re.search(fix['pattern'], content):
                    content = re.sub(fix['pattern'], fix['replacement'], content)
                    print(f"    - 应用了保守修复: {fix['context']}")
        
        return content
    
    def _fix_import_conflicts_robust(self, content: str) -> str:
        """超强导入冲突修复 - 基于成功手动修复案例的精确自动化"""
        
        # 简化检测逻辑：直接检查是否同时存在这两个导入模式
        recharts_import = re.search(r'import\s*\{[^}]*\bTooltip\b[^}]*\}\s*from\s*[\'"]recharts[\'"];', content)
        ui_tooltip_import = re.search(r'import\s*\{[^}]*\bTooltip\b[^}]*\}\s*from\s*["\']@/components/ui/tooltip["\'];', content)
        
        if recharts_import and ui_tooltip_import:
            print("    - 检测到Tooltip导入冲突，正在自动修复...")
            
            # 1. 修复recharts导入 - 精确模式匹配
            recharts_line = recharts_import.group(0)
            # 替换 Tooltip 为 Tooltip as RechartsTooltip
            fixed_recharts = recharts_line.replace('Tooltip', 'Tooltip as RechartsTooltip')
            content = content.replace(recharts_line, fixed_recharts)
            
            # 2. 修复ui/tooltip导入 - 使用精确的一次性替换
            ui_line = ui_tooltip_import.group(0)
            # 使用精确的模式匹配，基于成功的手动修复案例
            # 目标：{ Tooltip, TooltipContent, TooltipTrigger, TooltipProvider }
            # 转换：{ Tooltip as UITooltip, TooltipContent as UITooltipContent, ... }
            
            # 提取import内容
            import_match = re.search(r'import\s*\{\s*([^}]+)\s*\}', ui_line)
            if import_match:
                imports_str = import_match.group(1)
                imports = [imp.strip() for imp in imports_str.split(',')]
                
                # 为每个导入添加UI前缀别名
                new_imports = []
                for imp in imports:
                    imp = imp.strip()
                    if ' as ' not in imp:  # 没有别名的才添加
                        new_imports.append(f"{imp} as UI{imp}")
                    else:
                        new_imports.append(imp)  # 已有别名保持不变
                
                # 重新构建导入语句
                new_ui_line = f"import {{ {', '.join(new_imports)} }} from \"@/components/ui/tooltip\";"
                content = content.replace(ui_line, new_ui_line)
            
            # 3. 更新使用处 - 只更新图表中的Tooltip
            if 'LineChart' in content or 'BarChart' in content:
                # 使用更精确的替换模式
                content = re.sub(r'<Tooltip\s+formatter=', '<RechartsTooltip formatter=', content)
                content = re.sub(r'<Tooltip\s*/>', '<RechartsTooltip />', content)
                content = re.sub(r'<Tooltip>', '<RechartsTooltip>', content)
                content = re.sub(r'</Tooltip>', '</RechartsTooltip>', content)
        
        return content
    
    def _fix_variable_scope_errors_robust(self, content: str) -> str:
        """超强变量作用域修复 - 只修复generateTrajectory函数中的特定错误"""
        
        # 只在physics相关文件中进行修复
        if 'generateTrajectory' not in content:
            return content
            
        # 修复具体的错误行：t_final计算中的变量作用域问题
        # 匹配模式：const t_final = (initialVelocity * Math.sin...
        error_pattern = r'const t_final = \(initialVelocity \* Math\.sin\(toRadians\(angle\)\)'
        if re.search(error_pattern, content):
            print("    - 检测到generateTrajectory中的变量作用域错误，正在修复...")
            
            # 精确替换：将未定义的变量改为state.变量
            content = re.sub(
                r'const t_final = \(initialVelocity \* Math\.sin\(toRadians\(angle\)\) \+ Math\.sqrt\(Math\.pow\(initialVelocity \* Math\.sin\(toRadians\(angle\)\), 2\) \+ 2 \* G \* initialHeight\)\) / G;',
                'const t_final = (state.initialVelocity * Math.sin(toRadians(state.angle)) + Math.sqrt(Math.pow(state.initialVelocity * Math.sin(toRadians(state.angle)), 2) + 2 * G * state.initialHeight)) / G;',
                content
            )
        
        return content
    
    def _detect_and_install_missing_dependencies(self, project_path):
        """自动检测并安装缺失的依赖包"""
        print("  - 🔍 检测项目依赖需求...")
        
        # 常见的依赖映射（包含更多动画和可视化库）
        dependency_map = {
            'framer-motion': ['framer-motion'],
            'three': ['three', '@types/three'],
            '@react-three/fiber': ['@react-three/fiber', 'three', '@types/three'],
            '@react-three/drei': ['@react-three/drei'],
            'recharts': ['recharts'],
            'd3': ['d3', '@types/d3'],
            'mathjs': ['mathjs'],
            'plotly.js': ['plotly.js'],
            'react-spring': ['react-spring'],
            'lottie-react': ['lottie-react'],
        }
        
        detected_deps = set()
        
        # 扫描所有代码文件查找导入语句
        print(f"    📂 扫描 {project_path.name} 中的代码文件...")
        for ext in ['tsx', 'ts', 'js', 'jsx']:
            for filepath in project_path.glob(f'**/*.{ext}'):
                if 'node_modules' in str(filepath) or '.next' in str(filepath):
                    continue
                    
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 更强大的导入检测 - 支持多种 import 语法
                    for package_name in dependency_map.keys():
                        # 检测所有可能的导入格式：
                        patterns = [
                            rf"import\s+.*?\s+from\s+['\"]({re.escape(package_name)})['\"]",  # import ... from 'package'
                            rf"import\s*\{{.*?\}}\s*from\s+['\"]({re.escape(package_name)})['\"]",  # import { ... } from 'package' 
                            rf"import\s+\*\s+as\s+\w+\s+from\s+['\"]({re.escape(package_name)})['\"]",  # import * as ... from 'package'
                            rf"const\s+.*?\s*=\s*require\(['\"]({re.escape(package_name)})['\"]\)",  # require('package')
                        ]
                        
                        for pattern in patterns:
                            if re.search(pattern, content, re.MULTILINE):
                                detected_deps.update(dependency_map[package_name])
                                print(f"    ✅ 在 {filepath.name} 中发现: {package_name}")
                                break
                                
                except Exception as e:
                    print(f"    ⚠️ 读取文件失败 {filepath.name}: {e}")
                    continue
        
        if detected_deps:
            print(f"  - 📦 需要安装的依赖: {', '.join(sorted(detected_deps))}")
            try:
                # 安装缺失的依赖
                result = subprocess.run(
                    ['npm', 'install'] + list(detected_deps),
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=180  # 3分钟超时
                )
                
                if result.returncode == 0:
                    print(f"  - ✅ 成功安装 {len(detected_deps)} 个依赖包!")
                else:
                    print(f"  - ❌ 依赖安装失败:")
                    print(f"    Error: {result.stderr.strip()[:300]}")
                    
            except subprocess.TimeoutExpired:
                print(f"  - ⚠️ 依赖安装超时（超过3分钟）")
            except Exception as e:
                print(f"  - ⚠️ 依赖安装异常: {e}")
        else:
            print("  - ✅ 未检测到额外依赖需求")
    
    def _add_default_files(self, files: Dict[str, Dict]):
        """添加必需的默认文件"""
        # 添加默认的 lib/utils.ts 文件（如果不存在）
        if 'lib/utils.ts' not in files:
            print("📝 未找到 lib/utils.ts，添加默认的 utils 文件")
            files['lib/utils.ts'] = {
                'content': '''import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}''',
                'language': 'typescript',
                'source': 'default_utils'
            }
        
        # 可以在这里添加其他必需的默认文件
        print(f"✅ 默认文件处理完成，当前文件总数：{len(files)}")
    
    def save_files_to_project(self, files: Dict[str, Dict], project_path: Path):
        """保存提取的文件到目标项目中，并保护关键文件不被覆盖"""
        protected_paths = {
            'tailwind.config.ts',
            'app/globals.css',
            'postcss.config.mjs',
        }

        saved_files = []
        for filename, file_info in files.items():
            if filename in protected_paths:
                print(f"⏭️  跳过覆盖受保护文件: {filename}")
                continue
            file_path = project_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_info['content'])
            
            saved_files.append(str(file_path))
            print(f"✅ 保存文件: {filename}")
        
        return saved_files
    
    def copy_ui_components(self, project_path: Path):
        """复制本地UI组件"""
        if not self.ui_path or not os.path.isdir(self.ui_path):
            print("⚠️  未提供UI组件路径或路径不存在")
            return
        
        ui_target_path = project_path / 'components' / 'ui'
        print(f"🎨 正在复制UI组件从 {self.ui_path} 到 {ui_target_path}")
        
        try:
            if ui_target_path.exists():
                shutil.rmtree(ui_target_path)
            shutil.copytree(self.ui_path, ui_target_path)
            print("✅ UI组件复制成功")
        except Exception as e:
            print(f"⚠️  UI组件复制失败: {e}")

    def _post_process_files(self, project_path):
        print("\n🔧 正在对项目文件进行后处理和修复...")
        # 检测并安装缺失的依赖
        self._detect_and_install_missing_dependencies(project_path)
        
        # 常见的JSX标签修复
        replacements = {
            '</Title>': '</CardTitle>',
            # You can add more replacement rules here in the future.
        }

        # 需要自动注入的 shadcn-ui 组件导入
        shadcn_imports = [
            {
                'name': 'alert',
                'tags': ['Alert', 'AlertTitle', 'AlertDescription'],
                'import_line': 'import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";'
            },
            {
                'name': 'button',
                'tags': ['Button'],
                'import_line': 'import { Button } from "@/components/ui/button";'
            },
            {
                'name': 'card',
                'tags': ['Card', 'CardHeader', 'CardTitle', 'CardDescription', 'CardContent', 'CardFooter'],
                'import_line': 'import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";'
            },
            {
                'name': 'tooltip',
                'tags': ['Tooltip', 'TooltipContent', 'TooltipTrigger', 'TooltipProvider'],
                'import_line': 'import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from "@/components/ui/tooltip";'
            },
            {
                'name': 'dialog',
                'tags': ['Dialog', 'DialogContent', 'DialogHeader', 'DialogTitle', 'DialogDescription', 'DialogFooter', 'DialogTrigger', 'DialogClose'],
                'import_line': 'import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogTrigger, DialogClose } from "@/components/ui/dialog";'
            },
        ]

        # 常见的 lucide-react 图标自动导入（解决 BrainCircuit 等图标缺失问题）
        lucide_icons = [
            'ArrowRight', 'CheckCircle', 'Lightbulb', 'Microscope', 'Scale', 'Target', 'GraduationCap',
            'BrainCircuit', 'Beaker', 'FlaskConical', 'TestTube', 'BookOpen', 'Calculator', 'ChevronDown',
            'ChevronRight', 'Info', 'AlertCircle', 'Check', 'X', 'Plus', 'Minus', 'Star', 'Heart',
            'Eye', 'EyeOff', 'Search', 'Filter', 'Settings', 'Menu', 'Home', 'User', 'Mail', 'Phone',
            'Calendar', 'Clock', 'MapPin', 'Edit', 'Trash', 'Download', 'Upload', 'Share', 'Copy',
            'ExternalLink', 'Zap', 'Cpu', 'Database', 'Server', 'Code', 'Terminal', 'Globe'
        ]

        # 遍历所有 .tsx 和 .ts 文件
        for ext in ['tsx', 'ts']:
            for filepath in project_path.glob(f'**/*.{ext}'):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    changed = False
                    
                    # 1. 自动移除重复导入
                    content, duplicate_removed = self._remove_duplicate_imports(content)
                    if duplicate_removed:
                        changed = True
                    
                    # 2. 文本替换修复
                    for old, new in replacements.items():
                        if old in content:
                            content = content.replace(old, new)
                            changed = True

                    # 3. 仅对 TSX 执行组件导入注入
                    if filepath.suffix == '.tsx':
                        # 3a. shadcn-ui 组件自动导入
                        for rule in shadcn_imports:
                            # 如果文件中使用了这些标签
                            if any(re.search(rf"<\s*{tag}\b", content) for tag in rule['tags']):
                                # 检查是否已存在任何形式的导入（更全面的检测）
                                has_import = False
                                for tag in rule['tags']:
                                    # 检查多种导入格式：
                                    # import { Button } from ...
                                    # import { Button, ... } from ...
                                    # import {..., Button, ...} from ...
                                    patterns = [
                                        rf"import\s*\{{[^}}]*\b{tag}\b[^}}]*\}}\s*from\s*['\"][^'\"]*{rule['name']}['\"]",
                                        rf"import\s*\{{[^}}]*\b{tag}\b[^}}]*\}}\s*from\s*['\"][^'\"]*ui/{rule['name']}['\"]",
                                        rf"import\s*\{{[^}}]*\b{tag}\b[^}}]*\}}\s*from\s*['\"]\.\.?/.*ui/{rule['name']}['\"]"
                                    ]
                                    if any(re.search(pattern, content, re.MULTILINE) for pattern in patterns):
                                        has_import = True
                                        break
                                
                                # 只有在完全没有相关导入时才添加
                                if not has_import:
                                    # 将导入插入到首个非注释行之前或现有 import 之后
                                    lines = content.splitlines()
                                    insert_idx = 0
                                    for i, line in enumerate(lines):
                                        if line.strip().startswith('import '):
                                            insert_idx = i + 1
                                    lines.insert(insert_idx, rule['import_line'])
                                    content = "\n".join(lines) + ("\n" if not content.endswith("\n") else "")
                                    changed = True

                        # 3b. lucide-react 图标自动导入（智能检测，避免重复导入）
                        used_icons = []
                        for icon in lucide_icons:
                            # 检查图标是否在代码中使用（JSX标签形式或className中）
                            icon_patterns = [
                                rf"<\s*{icon}\b",  # <BrainCircuit
                                rf"\b{icon}\s*className", # BrainCircuit className
                                rf"const\s+\w+\s*=\s*{icon}\b", # const icon = BrainCircuit
                            ]
                            if any(re.search(pattern, content) for pattern in icon_patterns):
                                used_icons.append(icon)
                        
                        if used_icons:
                            # 检查所有现有导入，避免重复导入
                            all_imported_icons = set()
                            
                            # 扫描所有现有的导入语句，提取已导入的图标名称
                            import_lines = re.findall(r'import\s*\{([^}]*)\}\s*from\s*[\'"][^\'"]*[\'"]', content)
                            for import_line in import_lines:
                                imported_names = [name.strip() for name in import_line.split(',')]
                                all_imported_icons.update(imported_names)
                            
                            # 过滤掉已经导入的图标（无论从哪里导入）
                            truly_missing_icons = [icon for icon in used_icons if icon not in all_imported_icons]
                            
                            if truly_missing_icons:
                                # 检查是否已存在 lucide-react 导入
                                lucide_import_pattern = r"import\s*\{([^}]*)\}\s*from\s*['\"]lucide-react['\"]"
                                lucide_match = re.search(lucide_import_pattern, content)
                                
                                if lucide_match:
                                    # 已存在 lucide-react 导入，添加缺失的图标
                                    existing_lucide_imports = [imp.strip() for imp in lucide_match.group(1).split(',')]
                                    new_imports = existing_lucide_imports + truly_missing_icons
                                    new_import_line = f"import {{ {', '.join(new_imports)} }} from 'lucide-react';"
                                    content = content.replace(lucide_match.group(0), new_import_line)
                                    changed = True
                                    print(f"    ✅ 添加缺失的 lucide 图标: {', '.join(truly_missing_icons)}")
                                else:
                                    # 创建新的 lucide-react 导入
                                    new_import_line = f"import {{ {', '.join(truly_missing_icons)} }} from 'lucide-react';"
                                    lines = content.splitlines()
                                    insert_idx = 0
                                    for i, line in enumerate(lines):
                                        if line.strip().startswith('import '):
                                            insert_idx = i + 1
                                    lines.insert(insert_idx, new_import_line)
                                    content = "\n".join(lines) + ("\n" if not content.endswith("\n") else "")
                                    changed = True
                                    print(f"    ✅ 自动添加 lucide-react 导入: {', '.join(truly_missing_icons)}")
                            else:
                                if used_icons:
                                    print(f"    ℹ️ 图标已存在导入，跳过: {', '.join(used_icons)}")

                    # 4. styled-jsx 自动修复（仅对 TSX 文件）
                    if filepath.suffix == '.tsx' and '<style jsx>' in content:
                        print(f"  - 检测到 styled-jsx，正在自动转换为 Tailwind CSS: {filepath.relative_to(project_path)}")
                        content = self._fix_styled_jsx(content)
                        changed = True
                    
                    # 5. 完全自动修复系统 - 重新启用并改进
                    if filepath.suffix == '.tsx':
                        original_content = content
                        content = self._fix_import_conflicts_robust(content)
                        if content != original_content:
                            print(f"  - 修复了导入冲突: {filepath.relative_to(project_path)}")
                            changed = True
                    
                    # 6. 变量作用域错误自动修复 - 更精确的版本
                    if filepath.suffix in ['.tsx', '.ts']:
                        original_content = content
                        content = self._fix_variable_scope_errors_robust(content)
                        if content != original_content:
                            print(f"  - 修复了变量作用域错误: {filepath.relative_to(project_path)}")
                            changed = True

                    if changed:
                        print(f"  - 修复了文件: {filepath.relative_to(project_path)}")
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                except Exception as e:
                    print(f"  - 修复文件失败 {filepath}: {e}")
        print("✅ 后处理完成")
    
    def _find_free_port(self, start_port: int = 3000, max_tries: int = 50) -> int:
        port = start_port
        for _ in range(max_tries):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    s.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    port += 1
        return port

    def _wait_http_ok(self, url: str, timeout_sec: int = 40) -> Tuple[bool, Optional[int]]:
        start = time.time()
        last_code = None
        while time.time() - start < timeout_sec:
            try:
                with urlopen(url, timeout=5) as resp:
                    last_code = resp.getcode()
                    if 200 <= last_code < 400:
                        return True, last_code
            except HTTPError as e:
                last_code = e.code
            except URLError:
                pass
            time.sleep(1)
        return False, last_code

    def run_smoke_test(self, project_path: Path, base_port: Optional[int] = None, timeout_sec: int = 45) -> bool:
        port = self._find_free_port(base_port or 3000)
        log_file = project_path / '.smoke.log'
        print(f"🧪 正在运行 Smoke Test: http://localhost:{port}")
        proc = subprocess.Popen(
            ['npx', 'next', 'dev', '--turbopack', '-p', str(port)],
            cwd=str(project_path),
            stdout=open(log_file, 'w'),
            stderr=subprocess.STDOUT,
        )
        ok, code = self._wait_http_ok(f"http://localhost:{port}/", timeout_sec=timeout_sec)
        # 尝试关闭
        try:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        except Exception:
            pass
        if ok:
            print(f"✅ Smoke Test 通过 (HTTP {code})")
            return True
        else:
            print(f"❌ Smoke Test 失败 (HTTP {code})，请查看日志: {log_file}")
            return False
    
    def _generate_project_info(self, project_path: Path, files: Dict, file_count: int):
        """生成项目信息文件"""
        info = {
            'project_name': project_path.name,
            'created_at': str(Path().absolute()),
            'file_count': file_count,
            'files': list(files.keys()),
            'setup_commands': self.setup_commands,
            'next_steps': [
                f'cd {project_path}',
                'npm run dev',
                '# 然后在浏览器中访问 http://localhost:3000'
            ]
        }
        
        with open(project_path / 'project-info.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)

    def _remove_duplicate_imports(self, content: str) -> tuple[str, bool]:
        """自动检测和移除重复的导入语句"""
        lines = content.splitlines()
        import_lines = []
        other_lines = []
        seen_imports = set()
        duplicates_found = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import ') and ' from ' in stripped:
                # 标准化导入语句进行比较
                # 提取导入的组件和来源路径
                import_match = re.match(r'import\s*\{([^}]+)\}\s*from\s*[\'"]([^\'"]+)[\'"]', stripped)
                if import_match:
                    components = set(c.strip() for c in import_match.group(1).split(','))
                    from_path = import_match.group(2)
                    
                    # 标准化路径（处理相对路径和绝对路径的等效情况）
                    normalized_path = from_path
                    if from_path.startswith('../'):
                        # 相对路径转换为标准形式
                        if 'ui/' in from_path:
                            ui_component = from_path.split('ui/')[-1]
                            normalized_path = f"@/components/ui/{ui_component}"
                    elif from_path.startswith('./'):
                        if 'ui/' in from_path:
                            ui_component = from_path.split('ui/')[-1]
                            normalized_path = f"@/components/ui/{ui_component}"
                    
                    # 创建唯一的导入标识符
                    for component in components:
                        import_key = f"{component.strip()}:{normalized_path}"
                        if import_key in seen_imports:
                            duplicates_found = True
                            # 跳过重复的导入行
                            continue
                        seen_imports.add(import_key)
                    
                    # 检查整行是否重复
                    line_key = f"{sorted(components)}:{normalized_path}"
                    if line_key not in [l[1] for l in import_lines]:
                        import_lines.append((line, line_key))
                    else:
                        duplicates_found = True
                else:
                    import_lines.append((line, None))
            else:
                other_lines.append(line)
        
        if duplicates_found:
            # 重新构建内容
            result_lines = [line[0] for line in import_lines] + other_lines
            return '\n'.join(result_lines), True
        
        return content, False
    
    def build_project(self, input_file: str, output_dir: str, project_name: str = None):
        """构建完整项目"""
        if not project_name:
            project_name = f"chemistry_project_{Path(input_file).stem.replace('output_', '').replace('.json.raw', '')}"
        
        output_path = Path(output_dir)
        project_path = output_path / project_name
        
        print(f"🚀 开始构建项目: {project_name}")
        print(f"📁 输入文件: {input_file}")
        print(f"📁 输出路径: {project_path}")
        
        # 1. 提取文件
        files = self.extract_files_from_response(input_file)
        if not files:
            print("❌ 未找到可提取的文件")
            return None
        
        try:
            project_path = output_path / project_name
            if not self.create_nextjs_skeleton(project_path):
                raise Exception("项目骨架创建失败")
            self._add_default_files(files)
            self.save_files_to_project(files, project_path)
            self.copy_ui_components(project_path)
            self._post_process_files(project_path)
            
            print(f"✅ 项目构建完成: {project_path}")
            print(f"📊 包含 {len(files)} 个提取的文件")
            return project_path
            
        except Exception as e:
            print(f"❌ 项目构建失败: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="自动化V0项目构建器")
    parser.add_argument("input_file", help="v0响应文件路径")
    parser.add_argument("-o", "--output", default="auto_projects", help="输出目录")
    parser.add_argument("--project-name", help="项目名称")
    parser.add_argument("--ui-path", help="本地UI组件路径")
    parser.add_argument("--smoke-test", action="store_true", help="构建后运行一次本地编译+首页请求健康检查")
    parser.add_argument("--port", type=int, default=None, help="Smoke Test 起始端口(可选)")
    
    args = parser.parse_args()
    
    builder = AutoProjectBuilder(ui_path=args.ui_path)
    
    try:
        result = builder.build_project(
            input_file=args.input_file,
            output_dir=args.output,
            project_name=args.project_name
        )
        
        if result:
            print(f"\n✅ 项目构建成功！")
            print(f"项目路径: {result}")
            if args.smoke_test:
                builder.run_smoke_test(result, base_port=args.port)
        else:
            print(f"\n❌ 项目构建失败")
            
    except Exception as e:
        return True
    
    def _detect_potential_issues_and_guide(self, project_path):
        """检测潜在问题并提供修复指导"""
        print("\n🔍 检测潜在问题...")
        
        issues_found = []
        
        # 检测常见的导入冲突
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.tsx'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # 检测 Tooltip 导入冲突
                        if ('from \'recharts\'' in content and 'from \'@/components/ui/tooltip\'' in content 
                            and 'Tooltip' in content and 'Tooltip as' not in content):
                            issues_found.append({
                                'type': 'import_conflict',
                                'file': os.path.relpath(file_path, project_path),
                                'issue': 'Tooltip 导入名称冲突',
                                'fix': '将 recharts 的 Tooltip 改为 "Tooltip as RechartsTooltip"'
                            })
                            
                        # 检测变量作用域问题
                        if ('generateTrajectory' in content and 'initialVelocity' in content 
                            and 'state.initialVelocity' not in content):
                            issues_found.append({
                                'type': 'scope_error', 
                                'file': os.path.relpath(file_path, project_path),
                                'issue': '变量作用域错误',
                                'fix': '将 initialVelocity 改为 state.initialVelocity'
                            })
                    except Exception:
                        continue
        
        if issues_found:
            print("⚠️  发现以下潜在问题:")
            for i, issue in enumerate(issues_found, 1):
                print(f"  {i}. {issue['file']}: {issue['issue']}")
                print(f"     修复方法: {issue['fix']}")
            
            print(f"\n💡 修复建议:")
            print(f"   1. 运行 'cd {project_path} && npm run dev'")
            print(f"   2. 查看编译错误信息") 
            print(f"   3. 根据上述指导手动修复")
            print(f"   4. 或者使用 VS Code 的自动修复功能")
        else:
            print("✅ 未检测到明显问题，项目应该可以直接运行")
    
if __name__ == "__main__":
    main()
