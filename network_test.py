#!/usr/bin/env python3
import subprocess
import requests
import json
import socket
import time
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import threading

app = FastAPI(title="Network Connectivity Test")

# Store test results
test_results = {}

def run_command(cmd, description):
    """Run a shell command and capture output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "description": description,
            "command": cmd,
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "description": description,
            "command": cmd,
            "success": False,
            "stdout": "",
            "stderr": "Command timed out after 30 seconds",
            "return_code": -1
        }
    except Exception as e:
        return {
            "description": description,
            "command": cmd,
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "return_code": -1
        }

def test_http_request(url, description):
    """Test HTTP/HTTPS requests"""
    try:
        response = requests.get(url, timeout=30)
        return {
            "description": description,
            "url": url,
            "success": True,
            "status_code": response.status_code,
            "response_size": len(response.content),
            "headers": dict(response.headers),
            "content_preview": response.text[:500] if response.text else "No content"
        }
    except Exception as e:
        return {
            "description": description,
            "url": url,
            "success": False,
            "error": str(e),
            "status_code": None,
            "response_size": 0,
            "headers": {},
            "content_preview": ""
        }

def run_network_tests():
    """Run comprehensive network tests"""
    print("Starting network connectivity tests...")
    
    tests = {}
    
    # Basic connectivity tests
    tests["ping_google"] = run_command("ping -c 4 8.8.8.8", "Ping Google DNS")
    tests["ping_cloudflare"] = run_command("ping -c 4 1.1.1.1", "Ping Cloudflare DNS")
    
    # DNS resolution tests
    tests["dns_google"] = run_command("nslookup google.com", "DNS lookup for google.com")
    tests["dns_secret_lcd"] = run_command("nslookup lcd.mainnet.secretsaturn.net", "DNS lookup for Secret LCD")
    tests["dns_secret_rpc"] = run_command("nslookup rpc.mainnet.secretsaturn.net", "DNS lookup for Secret RPC")
    
    # Network interface info
    tests["interfaces"] = run_command("ip addr show", "Network interfaces")
    tests["routes"] = run_command("ip route show", "Routing table")
    
    # HTTP/HTTPS connectivity tests
    tests["http_google"] = test_http_request("http://google.com", "HTTP request to Google")
    tests["https_google"] = test_http_request("https://google.com", "HTTPS request to Google")
    
    # Secret Network specific tests
    tests["secret_lcd_node_info"] = test_http_request(
        "https://lcd.mainnet.secretsaturn.net/cosmos/base/tendermint/v1beta1/node_info",
        "Secret Network LCD node info"
    )
    tests["secret_rpc_status"] = test_http_request(
        "https://rpc.mainnet.secretsaturn.net/status",
        "Secret Network RPC status"
    )
    
    # Alternative Secret Network endpoints
    tests["secret_lcd_scrt"] = test_http_request(
        "https://lcd.secret.express/cosmos/base/tendermint/v1beta1/node_info",
        "Secret Network LCD (secret.express)"
    )
    
    # Test specific contract query endpoint that's failing
    tests["secret_contract_query"] = test_http_request(
        "https://lcd.mainnet.secretsaturn.net/compute/v1beta1/contract/secret1rh8qc6hx6lqhqfglhzqzcklazrm8xmgdqqxrfp",
        "Secret Network contract query"
    )
    
    # Certificate and TLS tests
    tests["openssl_google"] = run_command(
        "echo | openssl s_client -connect google.com:443 -servername google.com 2>/dev/null | openssl x509 -noout -dates",
        "TLS certificate check for Google"
    )
    tests["openssl_secret"] = run_command(
        "echo | openssl s_client -connect lcd.mainnet.secretsaturn.net:443 -servername lcd.mainnet.secretsaturn.net 2>/dev/null | openssl x509 -noout -dates",
        "TLS certificate check for Secret LCD"
    )
    
    # Environment info
    tests["env_vars"] = run_command("env | grep -E '(HTTP|PROXY|DNS)'", "HTTP/Proxy environment variables")
    tests["resolv_conf"] = run_command("cat /etc/resolv.conf", "DNS resolver configuration")
    
    return tests

def periodic_tests():
    """Run tests periodically"""
    global test_results
    while True:
        timestamp = datetime.now().isoformat()
        print(f"Running network tests at {timestamp}")
        
        results = run_network_tests()
        test_results[timestamp] = results
        
        # Print summary to logs
        successful_tests = sum(1 for test in results.values() if test.get('success', False))
        total_tests = len(results)
        print(f"Test summary: {successful_tests}/{total_tests} tests passed")
        
        # Print failed tests
        for name, result in results.items():
            if not result.get('success', False):
                print(f"FAILED: {name} - {result.get('description', '')}")
                if 'error' in result:
                    print(f"  Error: {result['error']}")
                elif 'stderr' in result:
                    print(f"  Stderr: {result['stderr']}")
        
        time.sleep(300)  # Run tests every 5 minutes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main dashboard"""
    if not test_results:
        return "<h1>Network Test Dashboard</h1><p>Tests are running... Please wait a moment and refresh.</p>"
    
    latest_timestamp = max(test_results.keys())
    latest_results = test_results[latest_timestamp]
    
    successful_tests = sum(1 for test in latest_results.values() if test.get('success', False))
    total_tests = len(latest_results)
    
    html = f"""
    <html>
    <head>
        <title>Network Connectivity Test</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .success {{ color: green; }}
            .failure {{ color: red; }}
            .test-result {{ margin: 10px 0; padding: 10px; border: 1px solid #ccc; }}
            .summary {{ background: #f0f0f0; padding: 15px; margin-bottom: 20px; }}
            pre {{ background: #f8f8f8; padding: 10px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h1>Network Connectivity Test Dashboard</h1>
        <div class="summary">
            <h2>Test Summary</h2>
            <p><strong>Last Run:</strong> {latest_timestamp}</p>
            <p><strong>Status:</strong> {successful_tests}/{total_tests} tests passed</p>
        </div>
        
        <h2>Test Results</h2>
    """
    
    for name, result in latest_results.items():
        status_class = "success" if result.get('success', False) else "failure"
        status_text = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        
        html += f"""
        <div class="test-result">
            <h3 class="{status_class}">{result.get('description', name)} {status_text}</h3>
        """
        
        if 'command' in result:
            html += f"<p><strong>Command:</strong> <code>{result['command']}</code></p>"
        if 'url' in result:
            html += f"<p><strong>URL:</strong> <code>{result['url']}</code></p>"
        
        if result.get('success', False):
            if 'stdout' in result and result['stdout']:
                html += f"<pre>{result['stdout'][:1000]}</pre>"
            elif 'content_preview' in result:
                html += f"<pre>{result['content_preview']}</pre>"
        else:
            if 'error' in result:
                html += f"<p><strong>Error:</strong> {result['error']}</p>"
            elif 'stderr' in result:
                html += f"<p><strong>Error:</strong> {result['stderr']}</p>"
        
        html += "</div>"
    
    html += """
        </body>
    </html>
    """
    
    return html

@app.get("/api/results")
async def get_results():
    """Get raw test results as JSON"""
    return test_results

@app.get("/api/latest")
async def get_latest():
    """Get latest test results as JSON"""
    if not test_results:
        return {"error": "No test results available yet"}
    
    latest_timestamp = max(test_results.keys())
    return {
        "timestamp": latest_timestamp,
        "results": test_results[latest_timestamp]
    }

if __name__ == "__main__":
    # Start periodic testing in background
    test_thread = threading.Thread(target=periodic_tests, daemon=True)
    test_thread.start()
    
    # Run initial test
    print("Running initial network tests...")
    initial_results = run_network_tests()
    test_results[datetime.now().isoformat()] = initial_results
    
    print("Starting web server on port 8080...")
    uvicorn.run(app, host="0.0.0.0", port=8080)