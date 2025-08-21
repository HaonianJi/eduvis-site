import json
import os
import requests
import re

def handler(request):
    """Vercel Python function handler for v0 API integration"""
    try:
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            }
        
        if request.method != 'POST':
            return {
                'statusCode': 405,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'Method not allowed'})
            }
        
        # Parse request body
        try:
            if hasattr(request, 'get_json'):
                body = request.get_json()
            else:
                body = json.loads(request.data.decode('utf-8'))
        except:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'Invalid JSON body'})
            }
            
        prompt = body.get('prompt', '').strip()
        api_key = os.environ.get('V0_API_KEY', '').strip()
        
        if not prompt:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'Prompt is required'})
            }
            
        if not api_key:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'V0_API_KEY not configured'})
            }
        
        # Generate project
        result = generate_v0_project(prompt, api_key)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': f'Server error: {str(e)}'})
        }

def generate_v0_project(prompt, api_key):
    """Generate v0 project using the API"""
    try:
        # Call v0 API
        v0_response = call_v0_api(prompt, api_key)
        
        if not v0_response.get('success'):
            return {
                'success': False,
                'error': v0_response.get('error', 'Failed to generate project'),
                'fallback': True
            }
        
        # Extract project files from response
        files = extract_files_from_response(v0_response.get('data', ''))
        
        if not files:
            return {
                'success': False,
                'error': 'No files generated from v0 response',
                'fallback': True
            }
        
        return {
            'success': True,
            'files': files,
            'message': 'Project generated successfully',
            'note': 'Files generated for static hosting'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Generation failed: {str(e)}',
            'fallback': True
        }

def call_v0_api(prompt, api_key):
    """Call the v0 API with the given prompt"""
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
        
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        
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

def extract_files_from_response(content):
    """Extract files from v0 API response"""
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
        
        return files
        
    except Exception as e:
        return []
