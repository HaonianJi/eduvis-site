from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import parse_qs

# Add the toolkit to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v0_automation_toolkit')))

# Now we can import from the toolkit
from v0_api_integration import run_pipeline_from_prompt

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            body = json.loads(post_data.decode('utf-8'))
            prompt = body.get('prompt')
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

            # Run the actual pipeline logic
            result = run_pipeline_from_prompt(prompt, api_key)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        return
