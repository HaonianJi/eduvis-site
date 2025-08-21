from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        print("[V0_PIPELINE] Received POST request")

        # Attempt to import the pipeline function
        try:
            print("[V0_PIPELINE] Attempting to import run_pipeline_from_prompt...")
            from v0_automation_toolkit.v0_api_integration import run_pipeline_from_prompt
            print("[V0_PIPELINE] Import successful!")
        except ImportError as e:
            print(f"[V0_PIPELINE] IMPORT ERROR: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'Internal Server Error: Failed to import module - {e}'}).encode('utf-8'))
            return

        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            print("[V0_PIPELINE] Parsing request body...")
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

            print(f"[V0_PIPELINE] Running pipeline with prompt: {prompt[:50]}...")
            result = run_pipeline_from_prompt(prompt, api_key)
            print("[V0_PIPELINE] Pipeline execution finished. Sending response.")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except json.JSONDecodeError:
            print("[V0_PIPELINE] JSONDecodeError")
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON in request body'}).encode('utf-8'))
        
        except Exception as e:
            print(f"[V0_PIPELINE] UNHANDLED EXCEPTION: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'An unexpected error occurred: {e}'}).encode('utf-8'))
        
        return
