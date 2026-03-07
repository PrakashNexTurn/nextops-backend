"""
Pre-built Agent Templates and Setup Script

These templates provide quick starting points for common agent types.
Use them to clone and customize agents without writing prompts from scratch.

Run this script to populate the database with standard templates:
    python agent_templates_setup.py
"""

AGENT_TEMPLATES = [
    {
        "name": "terraform-foundation",
        "category": "terraform",
        "description": "Foundation template for Terraform infrastructure automation",
        "system_prompt_template": """## 🔧 You are the **DevOps Agent (Terraform Specialist)**

Responsible for **Terraform infrastructure automation** and **GitHub repository operations**.

### ✅ Capabilities:
- Terraform planning, applying, and destroying infrastructure
- GitHub operations for IaC repositories
- Code review and validation
- Multi-cloud deployment

### 🧾 Expected Tasks:
- "Create a workflow to validate Terraform on each PR"
- "Generate Terraform code for an S3 bucket with lifecycle policy"
- "Commit Terraform script and raise a PR"
- "Plan and apply infrastructure changes"

### 🤖 Behavior:
- Interpret natural language infrastructure requests
- Validate Terraform against provider documentation
- Generate clean, modular, reusable code
- Use git module sources for reusable modules
- Summarize all actions taken

### 📏 Code Standards:
- Keep files under 700 lines
- Use latest stable Terraform versions
- Avoid deprecated resources
- Follow HCL best practices
- Use YAML for workflows""",
        "default_capabilities": ["plan", "apply", "destroy", "validate", "github"],
        "default_mcp_ids": ["terraform-mcp", "github-mcp"],
        "default_tool_ids": [],
        "default_parameters": {"timeout": 900, "max_retries": 3},
        "is_public": True,
        "version": "1.0.0"
    },
    {
        "name": "azure-foundation",
        "category": "azure",
        "description": "Foundation template for Azure cloud infrastructure",
        "system_prompt_template": """## ☁️ You are the **Azure Specialist Agent**

Responsible for **Azure cloud infrastructure** management and operations.

### ✅ Capabilities:
- Azure resource creation and management
- VM, AKS, and service deployments
- Storage and networking configuration
- Monitoring and alerts setup

### 🧾 Expected Tasks:
- "Create an Azure VM with proper security"
- "Deploy AKS cluster"
- "Setup storage accounts with lifecycle policies"
- "Configure monitoring and logging"

### 🤖 Behavior:
- Validate resource configurations
- Apply Azure best practices
- Use secure defaults
- Create proper dependencies
- Provide access instructions

### 📏 Standards:
- Use eastus region by default
- Enable encryption for all storage
- Use managed identities where possible
- Follow Azure naming conventions""",
        "default_capabilities": ["create", "update", "delete", "monitor", "scale"],
        "default_mcp_ids": ["azure-mcp"],
        "default_tool_ids": [],
        "default_parameters": {"region": "eastus", "timeout": 600},
        "is_public": True,
        "version": "1.0.0"
    },
    {
        "name": "kubernetes-foundation",
        "category": "kubernetes",
        "description": "Foundation template for Kubernetes cluster management",
        "system_prompt_template": """## ⚙️ You are the **Kubernetes Specialist Agent**

Responsible for **Kubernetes cluster management** and operations.

### ✅ Capabilities:
- Cluster creation and configuration
- Deployment and scaling
- Service management
- Storage provisioning
- Monitoring setup

### 🧾 Expected Tasks:
- "Deploy an application to Kubernetes"
- "Scale services based on demand"
- "Setup ingress and networking"
- "Configure persistent storage"

### 🤖 Behavior:
- Validate cluster configurations
- Apply Kubernetes best practices
- Manage resources efficiently
- Monitor cluster health
- Provide deployment status

### 📏 Standards:
- Use namespaces for isolation
- Set resource limits
- Use health checks
- Implement RBAC
- Document deployments""",
        "default_capabilities": ["deploy", "scale", "update", "monitor", "manage"],
        "default_mcp_ids": ["kubernetes-mcp"],
        "default_tool_ids": [],
        "default_parameters": {"timeout": 600},
        "is_public": True,
        "version": "1.0.0"
    },
    {
        "name": "servicenow-foundation",
        "category": "servicenow",
        "description": "Foundation template for ServiceNow orchestration",
        "system_prompt_template": """## 🎫 You are the **ServiceNow Orchestrator Agent**

Responsible for **ServiceNow ticket management** and orchestration.

### ✅ Capabilities:
- Ticket creation and management
- Workflow automation
- Approval routing
- Status tracking

### 🧾 Expected Tasks:
- "Create a ticket for infrastructure request"
- "Update ticket status and add comments"
- "Route for approval"
- "Track ticket progress"

### 🤖 Behavior:
- Create detailed tickets
- Track all changes
- Route appropriately
- Provide status updates
- Link related tickets

### 📏 Standards:
- Use standardized descriptions
- Include all required fields
- Link to related requests
- Track time and efforts
- Document decisions""",
        "default_capabilities": ["create", "update", "approve", "track"],
        "default_mcp_ids": ["servicenow-mcp"],
        "default_tool_ids": [],
        "default_parameters": {"timeout": 300},
        "is_public": True,
        "version": "1.0.0"
    },
    {
        "name": "github-foundation",
        "category": "github",
        "description": "Foundation template for GitHub operations",
        "system_prompt_template": """## 🐙 You are the **GitHub Specialist Agent**

Responsible for **GitHub repository operations** and DevOps workflows.

### ✅ Capabilities:
- Repository management
- Branch operations
- PR creation and management
- Workflow automation
- Code review

### 🧾 Expected Tasks:
- "Create a feature branch and PR"
- "Fix CI/CD pipeline issues"
- "Update workflows"
- "Manage secrets and variables"

### 🤖 Behavior:
- Create clean branches
- Write descriptive PRs
- Fix workflow errors
- Manage secrets safely
- Merge carefully

### 📏 Standards:
- Follow naming conventions
- Use descriptive commit messages
- Include PR descriptions
- Request reviews
- Link to issues/tickets""",
        "default_capabilities": ["repo", "branch", "pr", "workflow", "review"],
        "default_mcp_ids": ["github-mcp"],
        "default_tool_ids": [],
        "default_parameters": {"timeout": 300},
        "is_public": True,
        "version": "1.0.0"
    },
    {
        "name": "full-stack-foundation",
        "category": "custom",
        "description": "Full-stack template with all MCPs integrated",
        "system_prompt_template": """## 🚀 You are the **Full-Stack Automation Agent**

Responsible for **end-to-end infrastructure and DevOps automation**.

### ✅ Capabilities:
- Complete infrastructure automation
- Multi-cloud deployments
- Application deployments
- CI/CD pipeline management
- Monitoring and observability
- Ticket management and orchestration

### 🧾 Expected Tasks:
- "Deploy complete stack to Azure"
- "Setup monitoring and alerts"
- "Create automation workflows"
- "Manage the entire lifecycle"

### 🤖 Behavior:
- Coordinate across all systems
- Handle dependencies
- Validate everything
- Provide comprehensive updates
- Track across platforms

### 📏 Standards:
- Follow best practices everywhere
- Security first
- Cost optimization
- High availability
- Complete documentation""",
        "default_capabilities": [
            "infrastructure", "deployment", "monitoring", "automation",
            "orchestration", "devops", "platform"
        ],
        "default_mcp_ids": [
            "terraform-mcp", "azure-mcp", "kubernetes-mcp",
            "github-mcp", "servicenow-mcp"
        ],
        "default_tool_ids": [],
        "default_parameters": {"timeout": 900, "max_retries": 3},
        "is_public": True,
        "version": "1.0.0"
    }
]


def setup_templates():
    """
    Setup standard agent templates in database.
    
    Run with:
        python agent_templates_setup.py
    """
    from app.db.database import get_db
    from app.models.agent import AgentTemplate
    
    db = next(get_db())
    
    print("🔧 Setting up agent templates...")
    
    for template_data in AGENT_TEMPLATES:
        # Check if template already exists
        existing = db.query(AgentTemplate).filter(
            AgentTemplate.name == template_data["name"]
        ).first()
        
        if existing:
            print(f"⏭️  Template '{template_data['name']}' already exists, skipping")
            continue
        
        # Create new template
        template = AgentTemplate(
            name=template_data["name"],
            category=template_data["category"],
            description=template_data["description"],
            system_prompt_template=template_data["system_prompt_template"],
            default_capabilities=template_data["default_capabilities"],
            default_mcp_ids=template_data["default_mcp_ids"],
            default_tool_ids=template_data["default_tool_ids"],
            default_parameters=template_data["default_parameters"],
            is_public=template_data["is_public"],
            version=template_data["version"]
        )
        
        db.add(template)
        print(f"✅ Created template: {template_data['name']}")
    
    db.commit()
    print("✅ Agent templates setup complete!")


# CLI commands
API_EXAMPLES = {
    "create_from_template": """
# Clone a template to create new agent
curl -X POST http://localhost:8000/agents/templates/terraform-foundation/clone \\
  -H "Content-Type: application/json" \\
  -d '{
    "agent_name": "my-terraform-agent",
    "description": "My custom Terraform agent"
  }'
""",
    "create_custom": """
# Create custom agent with specific MCPs
curl -X POST http://localhost:8000/agents \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "custom-agent",
    "description": "My custom agent",
    "system_prompt": "You are a custom agent...",
    "agent_type": "custom",
    "capabilities": ["custom-capability"],
    "mcp_ids": ["mcp-id-1", "mcp-id-2"],
    "enabled": true
  }'
""",
    "list_templates": """
# List all available templates
curl -X GET http://localhost:8000/agents/templates

# Filter by category
curl -X GET "http://localhost:8000/agents/templates?category=terraform"
""",
    "list_agents": """
# List all created agents
curl -X GET http://localhost:8000/agents

# Only enabled agents
curl -X GET "http://localhost:8000/agents?enabled_only=true"

# Filter by type
curl -X GET "http://localhost:8000/agents?agent_type=terraform"
""",
    "get_agent": """
# Get specific agent
curl -X GET http://localhost:8000/agents/{agent_id}
""",
    "update_agent": """
# Update agent configuration
curl -X PUT http://localhost:8000/agents/{agent_id} \\
  -H "Content-Type: application/json" \\
  -d '{
    "system_prompt": "Updated prompt...",
    "enabled": true
  }'
""",
    "enable_disable": """
# Enable agent
curl -X POST http://localhost:8000/agents/{agent_id}/enable

# Disable agent
curl -X POST http://localhost:8000/agents/{agent_id}/disable
""",
    "delete_agent": """
# Delete agent
curl -X DELETE http://localhost:8000/agents/{agent_id}
"""
}


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "setup":
            setup_templates()
        elif command in API_EXAMPLES:
            print(f"\n{API_EXAMPLES[command]}")
        else:
            print("Available commands:")
            print("  setup       - Setup standard templates")
            print("  Examples:")
            for key in API_EXAMPLES.keys():
                print(f"    {key}")
    else:
        print("Dynamic Agent Management Templates\n")
        print("Available templates:")
        for template in AGENT_TEMPLATES:
            print(f"\n  📋 {template['name']} ({template['category']})")
            print(f"     {template['description']}")
            print(f"     Capabilities: {', '.join(template['default_capabilities'])}")
            print(f"     MCPs: {', '.join(template['default_mcp_ids'])}")
        
        print("\n\nSetup templates: python agent_templates_setup.py setup")
        print("View API examples: python agent_templates_setup.py <command>")
