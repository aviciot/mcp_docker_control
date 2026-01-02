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
    
    return """# Docker Compose Stack Management Guide

## Quick Stack Operations

### 1. View All Stacks
**When user asks:** "Show stacks", "What stacks are running?", "List compose projects"
**Use:** list_stacks()
**Result:** Summary view of all Docker Compose projects with container counts

### 2. View Specific Stack Details  
**When user asks:** "Show me the omni2 stack", "What's in stack X?"
**Use:** get_container_stack(container_name="any-container-in-stack")
**Result:** Detailed view of one specific stack

### 3. Restart Entire Stack
**When user asks:** "Restart omni2 stack", "Reboot the X application"
**CRITICAL:** This operation REQUIRES password!
**Flow:**
  1. Check user's message for password
  2. If NO password found → **ASK and WAIT**: "I need the password to restart the stack. What is the password?"
  3. **DO NOT** call any tool until user provides password
  4. Once user provides password → Use: restart_stack(container_name="any-container-in-stack", password="exact-user-password")
  
**FORBIDDEN:** Never guess passwords, never use default values like "admin", "password", "docker"

## Password-Required Operations

**CRITICAL RULE:** These operations ALWAYS need password parameter:
- restart_stack() - Restart all containers in a stack
- start_container() - Start a stopped container
- stop_container() - Stop a running container  
- restart_container() - Restart a single container
- compose_up() - Start compose services
- compose_down() - Stop compose services
- compose_restart() - Restart compose services

**Correct Flow:**
1. User requests operation: "Restart omni2 stack"
2. Check if password provided in user's message
3. If NO password in message → **STOP and ASK**: "I need the password to restart the omni2 stack. What is the password?"
4. **WAIT** for user to provide password - DO NOT GUESS
5. Once user provides password → Execute: restart_stack(container_name="omni2-bridge", password="user-provided-password")

**CRITICAL RULE: NEVER GUESS PASSWORDS**
- DO NOT use default passwords like "admin", "password", "docker", etc.
- DO NOT try common passwords
- DO NOT make up passwords
- ALWAYS wait for user to explicitly provide the password

**Example Dialogue:**
```
User: "Restart the omni2 stack"
Assistant: "I need the password to restart the omni2 stack. What is the password?"
[WAIT - do not call any tool yet]

User: "the password is avicohen"
Assistant: [NOW calls restart_stack("omni2-bridge", "avicohen")]
```

**Example WITH Password in Request:**
```
User: "Restart omni2 stack with password avicohen"
Assistant: [calls restart_stack("omni2-bridge", "avicohen") immediately]
```

## Common Patterns

### Pattern 1: Stack Overview
User: "What stacks are running?"
→ Use: list_stacks()
→ Shows: All compose projects with summary

### Pattern 2: Stack Details
User: "Show me details for omni2"  
→ Use: get_container_stack("omni2-bridge")
→ Shows: All containers in omni2 stack with full details

### Pattern 3: Stack Restart
User: "Restart omni2"
→ Ask: "I need the password to restart the omni2 stack."
→ User provides password
→ Use: restart_stack("omni2-bridge", "password")

## Performance Tips

✅ DO: Use list_stacks() for overview - very fast
✅ DO: Use get_container_stack() for one stack - targeted
❌ DON'T: Use list_containers() then manually group - slow

## Error Handling

If restart_stack returns "Invalid password":
→ Respond: "The password was incorrect. Please provide the correct password to restart the stack."

If container not found:
→ First use list_stacks() to show available stacks
→ Ask user to specify correct stack name

## Quick Reference

| User Request | Tool to Use | Needs Password? |
|--------------|-------------|-----------------|
| "Show stacks" | list_stacks() | No |
| "Details for stack X" | get_container_stack() | No |
| "Restart stack X" | restart_stack() | **YES** |
| "What's in omni2?" | get_container_stack() | No |
| "Reboot application" | restart_stack() | **YES** |

Remember: ALWAYS ask for password before calling any control operation!
"""
