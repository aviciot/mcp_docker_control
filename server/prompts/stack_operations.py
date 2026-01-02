"""
Stack Operations Prompt
========================
Guide for managing Docker Compose stacks efficiently
"""

import logging
from mcp_app import mcp

logger = logging.getLogger(__name__)


@mcp.prompt(
    name="stack_operations",
    description="CRITICAL: Guide for Docker Compose stack management with STRICT password handling rules. NEVER guess passwords - always ask user explicitly. Use this when user asks about stacks, projects, or wants to manage multiple related containers together."
)
def stack_operations():
    """
    Stack operations workflow guide
    
    Returns:
        str: Stack management instructions
    """
    
    return """# Docker Stack Operations - PASSWORD RULES

## CRITICAL: Password Authentication

**ALL control operations require password authentication.**

### Operations That Need Password:
- restart_stack() - Restart entire stack
- restart_container() - Restart single container  
- start_container() - Start container
- stop_container() - Stop container
- compose_up/down/restart() - Compose operations

### Password Handling Rules:

**RULE 1: Never guess passwords**
- NO default passwords ("admin", "password", "docker")
- NO common passwords
- NO making up passwords

**RULE 2: Check user's request first**
- If password IN request → Use it immediately
- If password NOT in request → Ask and wait

**RULE 3: Ask clearly and wait**
When no password provided:
1. Ask: "To restart [name], I need the password. What is the password?"
2. WAIT for user response
3. Then execute with provided password

### Correct Examples:

**Example 1 - No password provided:**
```
User: "Restart omni2 stack"
You: "To restart the omni2 stack, I need the password. What is the password?"
[WAIT]
User: "avicohen"
You: [Call restart_stack("omni2-bridge", "avicohen")]
```

**Example 2 - Password in request:**
```
User: "Restart omni2 stack with password avicohen"
You: [Call restart_stack("omni2-bridge", "avicohen") immediately]
```

**Example 3 - Password separately mentioned:**
```
User: "Restart omni2, password is avicohen"
You: [Call restart_stack("omni2-bridge", "avicohen") immediately]
```

## Stack Operations

### View Operations (No password needed):

**list_stacks()** - Show all Docker Compose stacks
- Usage: "Show all stacks", "What stacks are running?"
- Fast overview of all projects

**get_container_stack(container_name)** - Details for one stack
- Usage: "Show me the omni2 stack details"
- Lists all containers in specific stack

### Control Operations (Password required):

**restart_stack(container_name, password)** - Restart entire stack
- Usage: After getting password, restart all containers in stack
- Can provide any container name from the stack

## Quick Reference

| User Says | Password in Request? | Action |
|-----------|---------------------|---------|
| "Restart omni2" | NO | Ask for password, wait, then call tool |
| "Restart omni2 with password xyz" | YES | Call restart_stack immediately |
| "Show stacks" | N/A (read-only) | Call list_stacks immediately |

Remember: When in doubt about password → Ask and wait. Never guess.
"""
