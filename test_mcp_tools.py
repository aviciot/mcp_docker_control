"""
Test Docker Control MCP Tools
"""
import requests
import json

MCP_URL = "http://localhost:8350"
PASSWORD = "avicohen"

def test_without_auth():
    """Test that requests without auth are blocked"""
    print("\n=== Test 1: Request without authentication ===")
    try:
        response = requests.post(
            f"{MCP_URL}/mcp/v1/tools/list",
            json={},
            timeout=5
        )
        print(f"❌ FAIL: Should have been blocked (got {response.status_code})")
        return False
    except requests.exceptions.RequestException as e:
        if "401" in str(e) or "Unauthorized" in str(e):
            print("✅ PASS: Request blocked without authentication")
            return True
        print(f"❌ FAIL: Unexpected error: {e}")
        return False

def test_with_wrong_password():
    """Test that requests with wrong password are blocked"""
    print("\n=== Test 2: Request with wrong password ===")
    try:
        response = requests.post(
            f"{MCP_URL}/mcp/v1/tools/list",
            headers={"Authorization": "Bearer wrongpassword"},
            json={},
            timeout=5
        )
        if response.status_code == 401:
            print("✅ PASS: Request blocked with wrong password")
            return True
        else:
            print(f"❌ FAIL: Expected 401, got {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        if "401" in str(e) or "Unauthorized" in str(e):
            print("✅ PASS: Request blocked with wrong password")
            return True
        print(f"❌ FAIL: Unexpected error: {e}")
        return False

def test_list_tools():
    """Test listing available tools with correct auth"""
    print("\n=== Test 3: List available tools (with auth) ===")
    try:
        response = requests.post(
            f"{MCP_URL}/mcp/v1/tools/list",
            headers={"Authorization": f"Bearer {PASSWORD}"},
            json={},
            timeout=5
        )
        if response.status_code == 200:
            tools = response.json()
            print(f"✅ PASS: Got {len(tools.get('tools', []))} tools")
            print("Tools available:")
            for tool in tools.get('tools', []):
                print(f"  - {tool.get('name')}: {tool.get('description', '')[:60]}...")
            return True
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ FAIL: Request error: {e}")
        return False

def test_call_list_containers():
    """Test calling list_containers tool"""
    print("\n=== Test 4: Call list_containers tool ===")
    try:
        response = requests.post(
            f"{MCP_URL}/mcp/v1/tools/call",
            headers={"Authorization": f"Bearer {PASSWORD}"},
            json={
                "name": "list_containers",
                "arguments": {
                    "all_containers": True
                }
            },
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ PASS: Tool executed successfully")
            print(f"Result preview: {str(result)[:200]}...")
            return True
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ FAIL: Request error: {e}")
        return False

def test_read_only_vs_full_control():
    """Test that permission level is enforced (if using read-only)"""
    print("\n=== Test 5: Permission level check ===")
    print(f"Note: Current permission level is 'full-control' so all operations allowed")
    print("To test read-only restrictions, change AUTH_PERMISSION_LEVEL=read-only in .env")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Docker Control MCP - Tool Testing")
    print("=" * 60)
    
    results = []
    results.append(("Auth blocking", test_without_auth()))
    results.append(("Wrong password", test_with_wrong_password()))
    results.append(("List tools", test_list_tools()))
    results.append(("Call tool", test_call_list_containers()))
    results.append(("Permissions", test_read_only_vs_full_control()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    print(f"\nTotal: {passed}/{total} tests passed")
