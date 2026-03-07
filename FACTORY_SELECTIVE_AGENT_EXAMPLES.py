"""
Selective Agent Factory - Implementation Examples

Real-world usage patterns and integration scenarios for the enhanced 
AgentFactory selective agent initialization feature.
"""

import asyncio
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.services.agent_factory import AgentFactory

logger = logging.getLogger(__name__)


# ============================================================================
# EXAMPLE 1: Basic Selective Loading
# ============================================================================

async def example_basic_selective_loading(db: Session):
    """
    Load only specific agents from the database.
    """
    factory = AgentFactory(db=db)
    
    # Scenario: We want only Data Analysis and Reporting agents
    selected_agents = ["DataAnalysis", "ReportGeneration"]
    
    agents, stats = await factory.create_agents_from_database(
        actor_id="user-123",
        session_id="session-456",
        selected_agents=selected_agents
    )
    
    print(f"✅ Loaded {len(agents)} agents")
    print(f"Mode: {stats['mode']}")
    print(f"Not found: {stats['not_found']}")
    
    return agents


# ============================================================================
# EXAMPLE 2: Dynamic Agent Selection Based on Workflow
# ============================================================================

async def example_workflow_based_selection(db: Session, workflow_type: str):
    """
    Select agents dynamically based on workflow type.
    """
    factory = AgentFactory(db=db)
    
    # Define agent selections per workflow
    workflow_agents = {
        "data_analysis": ["DataProcessor", "DataValidator", "ReportGenerator"],
        "approval": ["ApprovalGateway", "NotificationService", "AuditLogger"],
        "export": ["DataExtractor", "FormatConverter", "FileUploader"],
    }
    
    # Get agents for the workflow
    selected_agents = workflow_agents.get(workflow_type, [])
    
    if not selected_agents:
        logger.error(f"Unknown workflow type: {workflow_type}")
        return []
    
    agents, stats = await factory.create_agents_from_database(
        actor_id="system",
        session_id=f"workflow-{workflow_type}",
        selected_agents=selected_agents
    )
    
    print(f"🔄 Workflow '{workflow_type}' initialized with {len(agents)} agents")
    return agents


# ============================================================================
# EXAMPLE 3: Mixed ID and Name Selection
# ============================================================================

async def example_mixed_selection(db: Session):
    """
    Select agents using both IDs and names.
    """
    factory = AgentFactory(db=db)
    
    # Mix of agent IDs and names
    selected_agents = [
        1,                      # Agent with ID 1
        2,                      # Agent with ID 2
        "CustomAgent",          # Agent by name
        "DataProcessor",        # Agent by name
    ]
    
    agents, stats = await factory.create_agents_from_database(
        actor_id="user-456",
        session_id="session-789",
        selected_agents=selected_agents
    )
    
    print(f"✅ Created {stats['successfully_created']} agents")
    print(f"⚠️ Not found: {stats['not_found']}")
    
    return agents


# ============================================================================
# EXAMPLE 4: Error Handling and Retry Logic
# ============================================================================

async def example_error_handling(db: Session, max_retries: int = 3):
    """
    Demonstrate error handling with retry logic.
    """
    factory = AgentFactory(db=db)
    selected_agents = ["Agent1", "Agent2", "Agent3"]
    
    for attempt in range(max_retries):
        try:
            agents, stats = await factory.create_agents_from_database(
                actor_id="user-123",
                session_id="session-456",
                selected_agents=selected_agents
            )
            
            # Check for errors
            if stats["not_found"]:
                logger.warning(f"⚠️ Agents not found: {stats['not_found']}")
            
            if stats["failed"]:
                logger.error(f"❌ Failed agents: {stats['failed']}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
            
            return agents, stats
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise
    
    return [], {"error": "Max retries exceeded"}


# ============================================================================
# EXAMPLE 5: Bedrock Runtime Integration
# ============================================================================

class BedrockAgentRuntime:
    """
    Bedrock agent runtime with selective agent initialization.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.factory = AgentFactory(db=db)
        self.agents = {}
        self.stats = {}
    
    async def initialize(
        self,
        actor_id: str,
        session_id: str,
        requested_agents: Optional[List[str]] = None
    ):
        """
        Initialize runtime with selected agents.
        
        Args:
            actor_id: User/actor ID
            session_id: Session ID
            requested_agents: List of agents to load (None = load all)
        """
        logger.info(f"🚀 Initializing Bedrock runtime...")
        
        # Create agents
        agents, stats = await self.factory.create_agents_from_database(
            actor_id=actor_id,
            session_id=session_id,
            selected_agents=requested_agents
        )
        
        # Store agents by name for easy lookup
        self.agents = {agent.name: agent for agent in agents}
        self.stats = stats
        
        logger.info(
            f"✅ Runtime initialized: {len(agents)} agents, "
            f"Mode: {stats['mode']}"
        )
        
        return agents, stats
    
    def get_agent(self, agent_name: str):
        """Get agent by name."""
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[str]:
        """List all loaded agent names."""
        return list(self.agents.keys())
    
    def get_statistics(self):
        """Get initialization statistics."""
        return self.stats


# ============================================================================
# EXAMPLE 6: Configuration-Driven Selection
# ============================================================================

async def example_config_driven_selection(
    db: Session,
    config: dict
):
    """
    Load agents based on configuration file/dict.
    """
    factory = AgentFactory(db=db)
    
    # Configuration structure
    # {
    #   "agents": ["Agent1", "Agent2"],
    #   "actor_id": "user-123",
    #   "session_id": "session-456"
    # }
    
    selected_agents = config.get("agents", [])
    actor_id = config.get("actor_id", "system")
    session_id = config.get("session_id", "default")
    
    agents, stats = await factory.create_agents_from_database(
        actor_id=actor_id,
        session_id=session_id,
        selected_agents=selected_agents if selected_agents else None
    )
    
    logger.info(f"✅ Loaded {len(agents)} agents from config")
    return agents, stats


# ============================================================================
# EXAMPLE 7: Multi-Tenant Agent Isolation
# ============================================================================

async def example_multi_tenant_isolation(
    db: Session,
    tenant_id: str,
    user_id: str
):
    """
    Load tenant-specific agents for multi-tenant systems.
    """
    factory = AgentFactory(db=db)
    
    # In a real system, you'd query which agents belong to this tenant
    # For now, we'll use a naming convention: "tenant_{tenant_id}_agent_{agent_name}"
    tenant_agents = [
        f"tenant_{tenant_id}_data_processor",
        f"tenant_{tenant_id}_report_generator",
    ]
    
    agents, stats = await factory.create_agents_from_database(
        actor_id=user_id,
        session_id=f"tenant-{tenant_id}-session",
        selected_agents=tenant_agents
    )
    
    print(f"🏢 Loaded {len(agents)} agents for tenant {tenant_id}")
    return agents


# ============================================================================
# EXAMPLE 8: Gradual Rollout / A/B Testing
# ============================================================================

async def example_ab_testing_rollout(
    db: Session,
    user_id: str,
    is_test_group: bool = False
):
    """
    Use different agents for A/B testing.
    """
    factory = AgentFactory(db=db)
    
    # Control group uses standard agents
    control_agents = ["StandardDataProcessor", "StandardReporter"]
    
    # Test group uses new experimental agents
    test_agents = ["ExperimentalDataProcessor", "ExperimentalReporter"]
    
    selected = test_agents if is_test_group else control_agents
    
    agents, stats = await factory.create_agents_from_database(
        actor_id=user_id,
        session_id=f"ab_test_{'treatment' if is_test_group else 'control'}",
        selected_agents=selected
    )
    
    group_name = "Treatment (Test)" if is_test_group else "Control"
    logger.info(f"📊 {group_name} group: {len(agents)} agents loaded")
    
    return agents


# ============================================================================
# EXAMPLE 9: Performance Testing - Batch Loading
# ============================================================================

async def example_batch_loading(
    db: Session,
    batch_size: int = 5
):
    """
    Load agents in batches for performance testing.
    """
    factory = AgentFactory(db=db)
    
    # List all available agents
    all_agent_configs = factory.list_agents()
    all_agents = [config["name"] for config in all_agent_configs]
    
    print(f"📊 Total agents available: {len(all_agents)}")
    
    # Load in batches
    for i in range(0, len(all_agents), batch_size):
        batch = all_agents[i:i+batch_size]
        
        agents, stats = await factory.create_agents_from_database(
            actor_id="perf-test",
            session_id=f"batch-{i//batch_size}",
            selected_agents=batch
        )
        
        print(f"Batch {i//batch_size + 1}: {len(agents)} agents loaded")


# ============================================================================
# EXAMPLE 10: Request Handler Integration
# ============================================================================

async def example_request_handler(
    db: Session,
    request_body: dict
):
    """
    Typical FastAPI/web framework integration.
    """
    factory = AgentFactory(db=db)
    
    try:
        # Extract from request
        agent_names = request_body.get("agents", [])
        actor_id = request_body.get("user_id")
        session_id = request_body.get("session_id")
        
        if not actor_id or not session_id:
            return {
                "success": False,
                "error": "Missing user_id or session_id"
            }
        
        # Initialize agents
        agents, stats = await factory.create_agents_from_database(
            actor_id=actor_id,
            session_id=session_id,
            selected_agents=agent_names if agent_names else None
        )
        
        # Return response
        return {
            "success": len(agents) > 0,
            "agents_count": len(agents),
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error in request handler: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# MAIN: Run Examples
# ============================================================================

async def main():
    """
    Run all examples (requires database setup).
    """
    from app.db.database import get_db
    
    db = next(get_db())
    
    print("🚀 Running Selective Agent Factory Examples\n")
    
    # Example 1
    print("=" * 60)
    print("Example 1: Basic Selective Loading")
    print("=" * 60)
    await example_basic_selective_loading(db)
    
    # Example 2
    print("\n" + "=" * 60)
    print("Example 2: Workflow-Based Selection")
    print("=" * 60)
    await example_workflow_based_selection(db, "data_analysis")
    
    print("\n✅ Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
