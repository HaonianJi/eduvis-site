import json
import os
import sys
import tempfile
from http.server import BaseHTTPRequestHandler
import requests
import re
import time
from typing import Dict, Any

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            data = json.loads(post_data.decode('utf-8'))
            prompt = data.get('prompt', '')
            api_key = os.environ.get('V0_API_KEY', '')
            
            if not prompt.strip():
                self.send_error_response(400, "Prompt is required")
                return
                
            if not api_key:
                self.send_error_response(400, "V0_API_KEY environment variable is required")
                return
            
            # Process the request
            result = self.generate_v0_project(prompt, api_key)
            
            # Send response
            self.send_json_response(result)
            
        except Exception as e:
            print(f"Error processing request: {e}")
            self.send_error_response(500, f"Internal server error: {str(e)}")
    
    def generate_v0_project(self, prompt: str, api_key: str) -> Dict[str, Any]:
        """
        Generate v0 project using the API
        """
        try:
            # Call v0 API
            v0_response = self.call_v0_api(prompt, api_key)
            
            if not v0_response.get('success'):
                return {
                    'success': False,
                    'error': v0_response.get('error', 'Failed to generate project'),
                    'fallback': True
                }
            
            # Extract project files from response
            files = self.extract_files_from_response(v0_response.get('data', ''))
            
            if not files:
                return {
                    'success': False,
                    'error': 'No files generated from v0 response',
                    'fallback': True
                }
            
            # For Vercel deployment, we'll return the generated files
            # instead of starting a server
            return {
                'success': True,
                'files': files,
                'message': 'Project generated successfully',
                'note': 'Files generated for static hosting'
            }
            
        except Exception as e:
            print(f"Error in generate_v0_project: {e}")
            return {
                'success': False,
                'error': f'Generation failed: {str(e)}',
                'fallback': True
            }
    
    def call_v0_api(self, prompt: str, api_key: str) -> Dict[str, Any]:
        """
        Call the v0 API with the given prompt
        """
        try:
            url = "https://api.v0.dev/chat"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "v0",
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            }
            
            print(f"🚀 Calling v0 API with prompt: {prompt[:100]}...")
            
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            
            if response.status_code == 401:
                return {'success': False, 'error': 'Invalid API key'}
            elif response.status_code != 200:
                return {'success': False, 'error': f'API error: {response.status_code}'}
            
            result = response.json()
            
            # Extract the generated content
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                return {'success': True, 'data': content}
            else:
                return {'success': False, 'error': 'No content in API response'}
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'API request timed out'}
        except Exception as e:
            return {'success': False, 'error': f'API call failed: {str(e)}'}
    
    def extract_files_from_response(self, content: str) -> list:
        """
        Extract files from v0 API response
        """
        files = []
        
        try:
            # Look for code blocks with file paths
            file_pattern = r'```(?:tsx?|jsx?|css|html|json)\s*(?://\s*(.+?)\n)?(.*?)```'
            matches = re.findall(file_pattern, content, re.DOTALL)
            
            for i, (filename, file_content) in enumerate(matches):
                if not filename:
                    # Generate default filename based on content
                    if 'export default' in file_content and 'tsx' in content:
                        filename = f'component-{i}.tsx'
                    elif 'function' in file_content:
                        filename = f'page-{i}.tsx'  
                    else:
                        filename = f'file-{i}.txt'
                
                files.append({
                    'path': filename.strip(),
                    'content': file_content.strip()
                })
            
            # If no files found with pattern, try to extract any code blocks
            if not files:
                code_blocks = re.findall(r'```\w*\n(.*?)\n```', content, re.DOTALL)
                for i, code in enumerate(code_blocks):
                    files.append({
                        'path': f'generated-{i}.tsx',
                        'content': code.strip()
                    })
            
            print(f"📁 Extracted {len(files)} files from response")
            return files
            
        except Exception as e:
            print(f"Error extracting files: {e}")
            return []
    
    def send_json_response(self, data: Dict[str, Any]):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data)
        self.wfile.write(response.encode('utf-8'))
    
    def send_error_response(self, status_code: int, message: str):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = json.dumps({
            'success': False,
            'error': message
        })
        self.wfile.write(error_response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
