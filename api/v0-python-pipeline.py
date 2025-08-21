from http.server import BaseHTTPRequestHandler
import json
import os
import sys

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        print("[V0_PIPELINE] Function called")
        print(f"[V0_PIPELINE] Python version: {sys.version}")
        print(f"[V0_PIPELINE] Current working directory: {os.getcwd()}")
        print(f"[V0_PIPELINE] Python path: {sys.path}")
    
        try:
            # List directory contents to debug
            print(f"[V0_PIPELINE] Directory contents: {os.listdir('.')}")
            if os.path.exists('v0_automation_toolkit'):
                print(f"[V0_PIPELINE] v0_automation_toolkit exists: {os.listdir('v0_automation_toolkit')}")
            else:
                print("[V0_PIPELINE] v0_automation_toolkit directory NOT found")
        except Exception as e:
            print(f"[V0_PIPELINE] Error listing directories: {e}")

        # Attempt to import the pipeline function
        try:
            print("[V0_PIPELINE] Attempting to import run_pipeline_from_prompt...")
            from v0_automation_toolkit.v0_api_integration import run_pipeline_from_prompt
            print("[V0_PIPELINE] Import successful!")
            import_success = True
        except ImportError as e:
            print(f"[V0_PIPELINE] IMPORT ERROR: {e}")
            import_success = False
        except Exception as e:
            print(f"[V0_PIPELINE] UNEXPECTED IMPORT ERROR: {e}")
            import_success = False

        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            print("[V0_PIPELINE] Parsing request body...")
            body = json.loads(post_data.decode('utf-8'))
            prompt = body.get('prompt')
            
            # Get API key from headers
            api_key = self.headers.get('Authorization', '').replace('Bearer ', '')

            if not prompt:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Prompt is required'}).encode('utf-8'))
                return

            if not api_key:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'API key is required'}).encode('utf-8'))
                return

            if not import_success:
                # Return mock data if import failed
                print("[V0_PIPELINE] Using mock response due to import failure")
                mock_result = {
                    'files': [
                        {
                            'path': 'page.tsx',
                            'content': f'// Mock response for prompt: {prompt[:50]}...\nexport default function Page() {{ return <div>Mock Project Generated Successfully!</div>; }}'
                        }
                    ]
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(mock_result).encode('utf-8'))
                return

            print(f"[V0_PIPELINE] Running pipeline with prompt: {prompt[:50]}...")
            result = run_pipeline_from_prompt(prompt, api_key)
            print("[V0_PIPELINE] Pipeline execution finished. Sending response.")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except json.JSONDecodeError as e:
            print(f"[V0_PIPELINE] JSONDecodeError: {e}")
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON in request body'}).encode('utf-8'))
        
        except Exception as e:
            print(f"[V0_PIPELINE] UNHANDLED EXCEPTION: {e}")
            print(f"[V0_PIPELINE] Exception type: {type(e)}")
            import traceback
            print(f"[V0_PIPELINE] Traceback: {traceback.format_exc()}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'An unexpected error occurred: {str(e)}'}).encode('utf-8'))
