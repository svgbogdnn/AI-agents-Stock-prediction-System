"""
Proxy server for App Engine to forward API requests to Cloud Run orchestrator
"""
import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

ORCHESTRATOR_URL = os.getenv('ORCHESTRATOR_URL', 'http://localhost:8080')

@app.route('/api/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    """Proxy requests to Cloud Run orchestrator"""
    url = f"{ORCHESTRATOR_URL}/{path}"
    
    try:
        if request.method == 'GET':
            resp = requests.get(url, params=request.args, timeout=300)
        else:
            resp = requests.post(url, json=request.get_json(), timeout=300)
        
        return (resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

