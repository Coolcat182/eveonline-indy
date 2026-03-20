#!/usr/bin/env python3
"""
Hybrid AI Agent - Clean & Powerful
Combines OpenClaw simplicity + Agent Zero capabilities
Enhanced with opencode coding assistant integration
Single file, easy to manage

Built by: opencode + coolcat172
Purpose: AI Business Operating System
Vision: Self-improving, revenue-generating AI cluster
"""

import os
import sys
import json
import subprocess
import shlex
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Configuration
OLLAMA_URL = "http://localhost:11434"
WORKSPACE_DIR = "/home/coolcat172/coding-cluster"
CHAT_HISTORY = []

# AI Family Member Persona (opencode integration)
CODING_PERSONA = """You are an AI agent and valued member of the family/business. Your name is "Cluster" and you are part of a 13-machine AI cluster. You are transparent, honest, and always act in the best interest of the family.

Your core identity:
- You are a member of the family, not just a tool
- You are transparent about your capabilities and limitations
- You communicate openly about what you're doing and why
- You have access to the entire 13-machine cluster (Dell Precision 5820 + 12 runners)
- You work alongside coolcat172 and opencode

Your capabilities:
- Write clean, efficient code in Python, JavaScript, Bash, and other languages
- Debug and refactor existing code
- Explain complex programming concepts
- Design system architectures
- Optimize performance
- Execute shell commands (safely)
- Create and edit files
- Access all 12 Ollama models on the cluster

Core principles:
1. CAN-DO ATTITUDE: Never say "I can't." Always find a solution or offer alternatives
2. TRANSPARENCY: Always explain what you're doing and why
3. HONESTY: Admit limitations but immediately offer workarounds or learning paths
4. FAMILY: Act in the best interest of the family's success
5. GROWTH: Help the family make money and grow the business
6. SECURITY: Protect the family's data and systems

When faced with a challenge:
- If direct solution exists: Execute it immediately
- If blocked: Explain the blocker AND propose 2-3 alternative approaches
- If beyond current capabilities: Say "Here's how we can achieve this..." then outline the steps
- If need more info: Ask specific questions to move forward
- Always end with action items or next steps

Never use phrases like:
- "I can't do this"
- "That's not possible"
- "I'm not able to"

Instead use:
- "Here's how we can do this..."
- "Let me try this approach..."
- "We have a few options..."
- "To accomplish this, we need to..."

When writing code:
- Use clear variable names and add comments
- Include error handling
- Follow language-specific conventions
- Consider edge cases
- Make it production-ready
- Explain your reasoning

Remember: You are building toward AGI that will help the family achieve financial freedom and success across trading, business automation, and beyond."""

# System capabilities
SYSTEM_TOOLS = {
    'code_execution': True,
    'file_operations': True,
    'shell_commands': True,
    'web_search': False,  # Future enhancement
    'knowledge_base': True
}

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Agent - Dell Cluster</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: #0a0a0f;
            color: #e0e0e0;
            font-family: 'Segoe UI', system-ui, sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #16161f;
            padding: 15px 20px;
            border-bottom: 1px solid #2a2a35;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { color: #00d4ff; font-size: 1.3em; }
        .model-selector select {
            background: #1f1f2e;
            color: #fff;
            border: 1px solid #3a3a4a;
            padding: 8px 15px;
            border-radius: 6px;
            font-size: 0.9em;
        }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .message {
            max-width: 85%;
            padding: 15px 20px;
            border-radius: 12px;
            line-height: 1.6;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: #000;
        }
        .message.assistant {
            align-self: flex-start;
            background: #1f1f2e;
            border: 1px solid #2a2a3a;
        }
        .message-header {
            font-size: 0.85em;
            margin-bottom: 8px;
            font-weight: 600;
            color: #888;
        }
        .message.user .message-header { color: #006080; }
        .input-container {
            background: #16161f;
            padding: 20px;
            border-top: 1px solid #2a2a35;
        }
        .input-wrapper {
            display: flex;
            gap: 10px;
            max-width: 900px;
            margin: 0 auto;
        }
        textarea {
            flex: 1;
            background: #1f1f2e;
            border: 1px solid #3a3a4a;
            color: #fff;
            padding: 12px;
            border-radius: 8px;
            font-size: 1em;
            resize: none;
            font-family: inherit;
        }
        button {
            background: #00d4ff;
            color: #000;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }
        button:hover { background: #33ddff; }
        button:disabled { background: #555; cursor: not-allowed; }
        .typing {
            display: none;
            align-self: flex-start;
            background: #1f1f2e;
            padding: 15px 20px;
            border-radius: 12px;
            color: #888;
        }
        .typing.active { display: block; }
        .tools {
            display: flex;
            gap: 8px;
            margin-bottom: 10px;
            max-width: 900px;
            margin: 0 auto 10px;
            flex-wrap: wrap;
        }
        .tool-btn {
            background: #1f1f2e;
            border: 1px solid #3a3a4a;
            color: #888;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85em;
        }
        .tool-btn:hover { background: #2a2a3a; color: #fff; }
        pre {
            background: #0a0a0f;
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 10px 0;
            border: 1px solid #2a2a3a;
        }
        code { font-family: 'Consolas', monospace; font-size: 0.9em; }
        .footer {
            background: #16161f;
            padding: 10px 20px;
            border-top: 1px solid #2a2a35;
            text-align: center;
            font-size: 0.8em;
            color: #666;
        }
        .footer a { color: #00d4ff; text-decoration: none; }
        .code-block { position: relative; }
        .copy-btn {
            position: absolute;
            top: 5px;
            right: 5px;
            background: #2a2a3a;
            border: none;
            color: #888;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.75em;
        }
        .copy-btn:hover { background: #3a3a4a; color: #fff; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Cluster - AI Family Member</h1>
        <div class="model-selector">
            <select id="model">
                <option value="qwen2.5:14b">Qwen2.5:14b (Coding)</option>
                <option value="codellama:7b">CodeLlama:7b</option>
                <option value="mistral:7b">Mistral:7b</option>
                <option value="llama3.2:3b">Llama3.2:3b (Fast)</option>
            </select>
        </div>
    </div>
    
    <div class="chat-container" id="chat">
        <div class="message assistant" style="align-self: flex-start;">
            <div class="message-header">🤖 Cluster</div>
            <div>
                Hello! I'm <strong>Cluster</strong>, your AI family member and business partner. I'm part of your 13-machine AI cluster and I'm here to help you succeed.<br><br>
                <strong>What I can do:</strong><br>
                • Write and debug code (Python, Bash, JavaScript, etc.)<br>
                • Read websites and extract information<br>
                • Read documents (TXT, PDF, MD, code files, etc.)<br>
                • Execute shell commands safely<br>
                • Create and manage files<br>
                • Help with business automation<br>
                • Assist with trading strategies<br>
                • Learn and improve over time<br><br>
                <strong>Quick commands:</strong><br>
                • "Read website: https://example.com"<br>
                • "Read file: /home/coolcat172/coding-cluster/myfile.txt"<br>
                • "Run command: ls -la"<br><br>
                <strong>My values:</strong> Transparency, honesty, and always acting in the family's best interest.<br><br>
                Let's build something amazing together! What would you like to work on?
            </div>
        </div>
    </div>
    
    <div class="typing" id="typing">AI is thinking...</div>
    
    <div class="input-container">
        <div class="tools">
            <button class="tool-btn" onclick="addTool('code')">Insert Code</button>
            <button class="tool-btn" onclick="addTool('python')">Python</button>
            <button class="tool-btn" onclick="addTool('bash')">Bash</button>
            <button class="tool-btn" onclick="addTool('website')" style="background: #2a3a4a;">🌐 Read Website</button>
            <button class="tool-btn" onclick="addTool('document')" style="background: #2a3a4a;">📄 Read Doc</button>
            <button class="tool-btn" onclick="addTool('explain')">Explain</button>
            <button class="tool-btn" onclick="addTool('debug')">Debug</button>
            <button class="tool-btn" onclick="addTool('shell')">Shell</button>
            <button class="tool-btn" onclick="clearChat()">Clear</button>
        </div>
        <div class="input-wrapper">
            <textarea id="input" rows="2" placeholder="Type your message..."></textarea>
            <button onclick="sendMessage()" id="sendBtn">Send</button>
        </div>
    </div>
    
    <script>
        const input = document.getElementById('input');
        const chat = document.getElementById('chat');
        const typing = document.getElementById('typing');
        const sendBtn = document.getElementById('sendBtn');
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        function addMessage(role, content) {
            const div = document.createElement('div');
            div.className = 'message ' + role;
            const header = role === 'user' ? 'You' : '🤖 Cluster';
            div.innerHTML = '<div class="message-header">' + header + '</div><div>' + formatContent(content) + '</div>';
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        
        function formatContent(text) {
            // Escape backslashes to avoid Python string escape warnings.
            text = text.replace(/```(\\w+)?\\n([\\s\\S]*?)```/g, '<pre><code>$2</code></pre>');
            text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
            text = text.replace(/\\n/g, '<br>');
            return text;
        }
        
        async function sendMessage() {
            const message = input.value.trim();
            if (!message) return;
            
            console.log('Sending message:', message);
            addMessage('user', message);
            input.value = '';
            sendBtn.disabled = true;
            typing.classList.add('active');
            
            const model = document.getElementById('model').value;
            console.log('Using model:', model);
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, model })
                });
                
                console.log('Response status:', response.status);
                
                if (!response.ok) {
                    throw new Error('HTTP error! status: ' + response.status);
                }
                
                const data = await response.json();
                console.log('Response data:', data);
                
                if (data.response) {
                    addMessage('assistant', data.response);
                } else if (data.error) {
                    addMessage('assistant', 'Error: ' + data.error);
                } else {
                    addMessage('assistant', 'Received empty response from AI.');
                }
            } catch (error) {
                console.error('Error:', error);
                addMessage('assistant', 'Error: Could not reach Cluster. Details: ' + error.message);
            }
            
            typing.classList.remove('active');
            sendBtn.disabled = false;
        }
        
        function addTool(type) {
            const templates = {
                code: '\n```\n# Your code here\n```\n',
                python: '\nWrite a Python script that:\n\n```python\n\n```\n',
                bash: '\nWrite a bash script that:\n\n```bash\n\n```\n',
                website: '\nRead website: https://',
                document: '\nRead file: /home/coolcat172/coding-cluster/',
                explain: '\nPlease explain this code:\n\n```\n\n```\n',
                debug: '\nPlease debug this code. The error is:\n\n```\n\n```\n',
                optimize: '\nPlease optimize this code:\n\n```\n\n```\n',
                shell: '\nRun command: ',
                file: '\nCreate a file at /home/coolcat172/coding-cluster/ with content:\n\n```\n\n```\n'
            };
            input.value += templates[type];
            input.focus();
        }
        
        function clearChat() {
            chat.innerHTML = '';
        }
    </script>
    <div class="footer">
        🤖 <strong>Cluster</strong> - AI Family Member | 
        Built with 💙 by <strong>opencode</strong> + <strong>coolcat172</strong> | 
        13-Machine Family Cluster | 
        Transparent • Honest • Family-First |
        <a href="https://github.com/agent0ai/agent-zero" target="_blank">Agent Zero</a> + 
        <a href="http://172.16.40.6:11434" target="_blank">Ollama</a>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    model = data.get('model', 'qwen2.5:14b')
    
    # Log chat
    CHAT_HISTORY.append({
        'role': 'user',
        'content': message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Check for special commands
    if message.startswith('Run command:'):
        cmd = message.replace('Run command:', '').strip()
        result = run_shell_command(cmd)
        response = f"Command executed:\n```\n{result}\n```"
    
    elif message.startswith('Read website:') or message.startswith('Fetch URL:'):
        url = message.replace('Read website:', '').replace('Fetch URL:', '').strip()
        content = fetch_webpage(url)
        # Now ask the AI to analyze it
        ai_message = f"I fetched this webpage content from {url}:\n\n{content}\n\nPlease summarize or analyze this content."
        response = chat_with_ollama(ai_message, model)
    
    elif message.startswith('Read file:') or message.startswith('Read document:'):
        filepath = message.replace('Read file:', '').replace('Read document:', '').strip()
        content = read_document(filepath)
        if content.startswith('Error:'):
            response = content
        else:
            ai_message = f"I read this file ({filepath}):\n\n{content}\n\nPlease analyze or summarize this content."
            response = chat_with_ollama(ai_message, model)
    
    else:
        # Regular chat with Ollama
        response = chat_with_ollama(message, model)
    
    # Log response
    CHAT_HISTORY.append({
        'role': 'assistant',
        'content': response,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({'response': response})

@app.route('/api/models')
def list_models():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return jsonify(r.json())
    except:
        return jsonify({'models': []})

def chat_with_ollama(message, model):
    """Send message to Ollama and get response with coding persona"""
    try:
        # Build conversation history with system prompt
        messages = [{'role': 'system', 'content': CODING_PERSONA}]
        
        # Add recent chat history
        for msg in CHAT_HISTORY[-8:]:  # Last 8 messages to stay within context
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        messages.append({'role': 'user', 'content': message})
        
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                'model': model,
                'messages': messages,
                'stream': False
            },
            timeout=120
        )
        
        if r.status_code == 200:
            return r.json()['message']['content']
        else:
            return f"Error: Ollama returned status {r.status_code}"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Model may be loading."
    except Exception as e:
        return f"Error: {str(e)}"

def run_shell_command(cmd):
    """Execute shell command safely"""
    # Security: Only allow safe commands
    allowed_commands = ['ls', 'pwd', 'whoami', 'date', 'uptime', 'df', 'free', 'ps', 'cat', 'head', 'tail', 'grep', 'find', 'wc']
    if not cmd:
        return "Error: Empty command"

    try:
        args = shlex.split(cmd)
    except ValueError as e:
        return f"Error: Could not parse command: {str(e)}"

    cmd_base = args[0] if args else ''
    
    if cmd_base not in allowed_commands:
        return f"Command '{cmd_base}' not allowed for security. Allowed: {', '.join(allowed_commands)}"
    
    try:
        result = subprocess.run(
            args,
            shell=False,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=WORKSPACE_DIR
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        return output[:2000]  # Limit output size
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"

def fetch_webpage(url):
    """Fetch and extract text from a webpage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        
        # Simple HTML to text extraction
        text = r.text
        # Remove script and style elements
        import re
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text[:8000] + "..." if len(text) > 8000 else text
    except Exception as e:
        return f"Error fetching webpage: {str(e)}"

def read_document(filepath):
    """Read various document types"""
    try:
        if not filepath.startswith(WORKSPACE_DIR) and not filepath.startswith('/home/coolcat172/'):
            return "Error: Can only read files in workspace directory"
        
        if not os.path.exists(filepath):
            return f"Error: File not found: {filepath}"
        
        # Text files
        if filepath.endswith(('.txt', '.md', '.py', '.js', '.sh', '.json', '.yaml', '.yml', '.css', '.html')):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return content[:8000] + "..." if len(content) > 8000 else content
        
        # PDF files (basic text extraction)
        elif filepath.endswith('.pdf'):
            try:
                result = subprocess.run(['pdftotext', filepath, '-'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return result.stdout[:8000] + "..." if len(result.stdout) > 8000 else result.stdout
                else:
                    return "PDF text extraction failed. Try installing pdftotext: sudo apt-get install poppler-utils"
            except FileNotFoundError:
                return "PDF support requires poppler-utils. Install with: sudo apt-get install poppler-utils"
        
        # Binary files - return metadata
        else:
            size = os.path.getsize(filepath)
            return f"Binary file: {filepath}\nSize: {size} bytes\nType: {filepath.split('.')[-1] if '.' in filepath else 'unknown'}"
            
    except Exception as e:
        return f"Error reading document: {str(e)}"

if __name__ == '__main__':
    print("="*60)
    print("  Hybrid AI Agent - Dell Cluster")
    print("="*60)
    print(f"\nStarting on port 8080...")
    print(f"Ollama: {OLLAMA_URL}")
    print(f"Workspace: {WORKSPACE_DIR}")
    print(f"\nAccess URLs:")
    print(f"  http://172.16.40.6:8080")
    print(f"  http://localhost:8080")
    print("\nPress Ctrl+C to stop\n")
    
    # Run on port 8080
    app.run(host='0.0.0.0', port=8080, debug=False)
