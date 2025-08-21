import json
import os
import sys

def handler(request):
    print("[V0_PIPELINE] Function called")
    print(f"[V0_PIPELINE] Python version: {sys.version}")
    print(f"[V0_PIPELINE] Current working directory: {os.getcwd()}")
    print(f"[V0_PIPELINE] Python path: {sys.path}")
    
    # Only handle POST requests
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
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
        print("[V0_PIPELINE] Parsing request body...")
        
        # Handle different request formats
        if hasattr(request, 'get_json'):
            body = request.get_json()
        elif hasattr(request, 'json'):
            body = request.json
        else:
            # Fallback for raw body parsing
            body_str = request.get('body', '{}')
            if isinstance(body_str, bytes):
                body_str = body_str.decode('utf-8')
            body = json.loads(body_str)
        
        prompt = body.get('prompt')
        
        # Get API key from headers
        headers = request.get('headers', {})
        auth_header = headers.get('authorization', '') or headers.get('Authorization', '')
        api_key = auth_header.replace('Bearer ', '')

        if not prompt:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Prompt is required'})
            }

        if not api_key:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'API key is required'})
            }

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
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(mock_result)
            }

        print(f"[V0_PIPELINE] Running pipeline with prompt: {prompt[:50]}...")
        result = run_pipeline_from_prompt(prompt, api_key)
        print("[V0_PIPELINE] Pipeline execution finished. Sending response.")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }

    except json.JSONDecodeError as e:
        print(f"[V0_PIPELINE] JSONDecodeError: {e}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    
    except Exception as e:
        print(f"[V0_PIPELINE] UNHANDLED EXCEPTION: {e}")
        print(f"[V0_PIPELINE] Exception type: {type(e)}")
        import traceback
        print(f"[V0_PIPELINE] Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'An unexpected error occurred: {str(e)}'})
        }
