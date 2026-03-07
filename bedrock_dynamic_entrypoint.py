"""
Updated Bedrock Entrypoint with Dynamic Agent Management and Runtime Database Integration

This entrypoint loads agents dynamically from the database and supports selective
agent initialization via database-managed Bedrock runtime configurations.

Key features:
- Dynamic agent loading from database
- Selective agent initialization (not all agents)
- Database-driven runtime configuration
- Full conversation memory integration
- Graceful error handling and logging
"""
import os
import asyncio
from typing import Optional, List
from strands import Agent
from strands.multiagent import Swarm
from bedrock_agentcore.memory import MemoryClient
from strands.hooks import AgentInitializedEvent, HookProvider, HookRegistry, MessageAddedEvent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.types.exceptions import MCPClientInitializationError

# Import dynamic agent factory and database
from app.services.agent_factory import AgentFactory
from app.services.bedrock_runtime_service import BedrockRuntimeService
from app.db.database import get_db

app = BedrockAgentCoreApp()
log = app.logger

MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID")
REGION = os.getenv("AWS_REGION", "us-east-1")


class SwarmMemoryHook(HookProvider):
    """Custom hook for managing conversation memory in Swarm agents"""
    
    def __init__(self, memory_client: MemoryClient, memory_id: str):
        self.memory_client = memory_client
        self.memory_id = memory_id
    
    def on_agent_initialized(self, event: AgentInitializedEvent):
        """Load recent conversation history when agent starts"""
        print(event)
        try:
            # Get session info from agent state
            actor_id = event.agent.state.get("actor_id")
            session_id = event.agent.state.get("session_id")
            
            if not actor_id or not session_id:
                print("Missing actor_id or session_id in agent state")
                return
            
            # Get last 5 conversation turns
            recent_turns = self.memory_client.get_last_k_turns(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id=session_id,
                k=5,
                branch_name="main"
            )
            
            if recent_turns:
                # Format conversation history for context
                context_messages = []
                for turn in recent_turns:
                    for message in turn:
                        role = message['role'].lower()
                        content = message['content']['text']
                        context_messages.append(f"{role.title()}: {content}")
                
                context = "\n".join(context_messages)
                print(f"Context from memory: {context}")
                
                # Add context to agent's system prompt
                if not event.agent.system_prompt:
                    event.agent.system_prompt = ""
                event.agent.system_prompt += f"\n\nRecent conversation history:\n{context}\n\nContinue the conversation naturally based on this context."
                
                print(f"✅ Loaded {len(recent_turns)} recent conversation turns")
            else:
                print("No previous conversation history found")
        
        except Exception as e:
            print(f"Failed to load conversation history: {e}")
    
    def on_message_added(self, event: MessageAddedEvent):
        """Store conversation turns in memory including tools"""
        messages = event.agent.messages
        last_message = messages[-1]
        print(last_message)
        
        try:
            # Get session info from agent state
            actor_id = event.agent.state.get("actor_id")
            session_id = event.agent.state.get("session_id")
            print(actor_id)
            print(session_id)
            
            if not actor_id or not session_id:
                print("Missing actor_id or session_id in agent state")
                return
            
            # Collect all text and tool events in the message
            role = last_message["role"]
            
            for item in last_message.get("content", []):
                if "text" in item:
                    text = item["text"]
                elif "toolUse" in item:
                    text = item["toolUse"]["name"] + ": " + text
                elif "toolResult" in item:
                    role = "tool"
                    status = item["toolResult"]["status"]
                    text = status + ":" + item["toolResult"]["content"][0]["text"]
            
            # Store in memory
            text = text[:8500] + " Trimmed..." if len(text) > 9000 else text
            self.memory_client.create_event(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id=session_id,
                messages=[(text, role)]
            )
        
        except Exception as e:
            print(f"Failed to store message: {e}")
    
    def register_hooks(self, registry: HookRegistry) -> None:
        """Register memory hooks"""
        registry.add_callback(MessageAddedEvent, self.on_message_added)
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)
        log.info("🔗 Memory hooks registered")


def _load_agents_from_runtime(
    db,
    runtime_id: Optional[int] = None,
    runtime_name: Optional[str] = None,
    actor_id: Optional[str] = None,
    session_id: Optional[str] = None,
    selected_agent_ids: Optional[List[int]] = None,
    selected_agent_names: Optional[List[str]] = None,
    memory_client: Optional[MemoryClient] = None,
    memory_hooks: Optional[List] = None
):
    """
    Load agents either from database runtime configuration or from explicit selections.
    
    Supports three modes:
    1. Load from Bedrock runtime config by ID or name
    2. Load specific agents by IDs or names
    3. Load all enabled agents (default fallback)
    """
    factory = AgentFactory(db, memory_client)
    
    # Mode 1: Load from Bedrock runtime configuration
    if runtime_id or runtime_name:
        log.info("📦 Loading agents from Bedrock runtime configuration...")
        
        runtime_service = BedrockRuntimeService(db)
        
        if runtime_id:
            runtime = runtime_service.get_runtime_by_id(runtime_id)
        else:
            runtime = runtime_service.get_runtime_by_name(runtime_name)
        
        if not runtime:
            log.warning(f"⚠️ Runtime not found: {runtime_id or runtime_name}")
            log.info("📦 Falling back to loading all enabled agents...")
            return factory.create_agents_from_database(
                actor_id=actor_id,
                session_id=session_id,
                enabled_only=True,
                hooks=memory_hooks
            )
        
        log.info(f"✅ Found runtime: {runtime.name} (status: {runtime.status})")
        
        # Get selected agents from runtime config
        selected_agent_ids = runtime.selected_agent_ids or []
        selected_agent_names = runtime.selected_agent_names or []
        
        log.info(f"🎯 Runtime has {len(selected_agent_ids)} selected agent IDs and {len(selected_agent_names)} agent names")
        
        # Load specific agents from runtime config
        return factory.create_agents_from_database(
            actor_id=actor_id,
            session_id=session_id,
            selected_agents=selected_agent_ids + selected_agent_names,
            enabled_only=True,
            hooks=memory_hooks
        )
    
    # Mode 2: Load specific agents by IDs or names
    elif selected_agent_ids or selected_agent_names:
        log.info("📦 Loading specific selected agents...")
        
        selected = (selected_agent_ids or []) + (selected_agent_names or [])
        log.info(f"🎯 Loading {len(selected)} selected agent(s)...")
        
        return factory.create_agents_from_database(
            actor_id=actor_id,
            session_id=session_id,
            selected_agents=selected,
            enabled_only=True,
            hooks=memory_hooks
        )
    
    # Mode 3: Load all enabled agents (fallback)
    else:
        log.info("📦 Loading all enabled agents (default mode)...")
        
        return factory.create_agents_from_database(
            actor_id=actor_id,
            session_id=session_id,
            enabled_only=True,
            hooks=memory_hooks
        )


@app.async_task
async def run_swarm_in_background(payload, context):
    """
    Run the Swarm agents in background with dynamic and selective agent loading.
    
    Agents can be loaded in three ways:
    1. From Bedrock runtime configuration (database-managed)
    2. From explicit selected agent IDs/names in payload
    3. Default: all enabled agents
    """
    # Log full payload for debugging
    log.info(f"📦 Full payload keys: {list(payload.keys())}")
    
    actor_id = payload.get("actor_id") or payload.get("user_id") or 'default-user'
    session_id = payload.get("session_id") or getattr(context, 'session_id', None) or 'default'
    user_message = payload.get("prompt", "Hello! How can I help you today?")
    
    # 🎯 NEW: Selective agent initialization from payload
    runtime_id = payload.get("runtime_id")  # Bedrock runtime ID
    runtime_name = payload.get("runtime_name")  # Bedrock runtime name
    selected_agent_ids = payload.get("selected_agent_ids")  # Specific agent IDs
    selected_agent_names = payload.get("selected_agent_names")  # Specific agent names
    
    # 🔒 SESSION MANAGEMENT
    log.info(f"🚀 Swarm invoked with session_id={session_id}, actor_id={actor_id}")
    log.info(f"🔒 Session type: CONTINUING (will load history for session: {session_id})")
    log.info(f"💬 User message: {user_message}")
    
    # Log agent selection mode
    if runtime_id or runtime_name:
        log.info(f"🎯 Agent mode: RUNTIME CONFIG (runtime: {runtime_id or runtime_name})")
    elif selected_agent_ids or selected_agent_names:
        log.info(f"🎯 Agent mode: SELECTIVE (IDs: {selected_agent_ids}, Names: {selected_agent_names})")
    else:
        log.info("🎯 Agent mode: DEFAULT (all enabled agents)")
    
    # Health ping handler for long-running tasks
    async def ping_handler():
        while True:
            await context.ping(status="HEALTHY_BUSY")
            await asyncio.sleep(45)
    
    # Start ping handler
    ping_task = asyncio.create_task(ping_handler())
    
    try:
        # Load conversation memory ONCE upfront
        conversation_context = ""
        memory_client = None
        memory_hook = None
        
        if MEMORY_ID:
            try:
                memory_client = MemoryClient(region_name=REGION)
                log.info(f"📚 Loading conversation history for session: {session_id}...")
                
                recent_turns = memory_client.get_last_k_turns(
                    memory_id=MEMORY_ID,
                    actor_id=actor_id,
                    session_id=session_id,
                    k=5,
                    branch_name="main"
                )
                
                if recent_turns:
                    context_messages = []
                    ticket_numbers = []
                    message_count = 0
                    
                    for turn in recent_turns:
                        for message in turn:
                            message_count += 1
                            role = message['role'].lower()
                            content = message['content']['text']
                            
                            # Extract ticket numbers (INC/RITM)
                            import re
                            tickets = re.findall(r'((?:INC|RITM)\d{7,})', content)
                            ticket_numbers.extend(tickets)
                            
                            context_messages.append(f"[{message_count}] {role.upper()}: {content[:500]}")
                    
                    conversation_context = "\n\n".join(context_messages)
                    
                    if ticket_numbers:
                        unique_tickets = list(dict.fromkeys(ticket_numbers))
                        conversation_context = f"🎫 **Active Tickets in This Conversation:** {', '.join(unique_tickets)}\n\n{conversation_context}"
                    
                    log.info(f"✅ Loaded {len(recent_turns)} conversation turns ({message_count} messages)")
                else:
                    log.info("📭 No previous conversation history in this session (starting fresh)")
                
                # Create hook for storing new messages
                memory_hook = SwarmMemoryHook(memory_client, MEMORY_ID)
            
            except Exception as e:
                log.warning(f"⚠️ Memory loading failed (continuing without): {e}")
        else:
            log.warning("⚠️ MEMORY_ID not set. No conversation memory.")
        
        # 🆕 SELECTIVE AGENT LOADING WITH RUNTIME DATABASE SUPPORT
        log.info("📚 Loading agents (selective mode with database support)...")
        
        db = next(get_db())
        
        # Load agents using selective mode with runtime configuration support
        agents = _load_agents_from_runtime(
            db=db,
            runtime_id=runtime_id,
            runtime_name=runtime_name,
            actor_id=actor_id,
            session_id=session_id,
            selected_agent_ids=selected_agent_ids,
            selected_agent_names=selected_agent_names,
            memory_client=memory_client,
            memory_hooks=[memory_hook] if memory_hook else None
        )
        
        if not agents:
            log.warning("⚠️ No agents found! Check agent configuration or runtime settings.")
            log.warning("   Use POST /agents to create agents")
            log.warning("   Use POST /bedrock-runtimes to create runtime configurations")
        else:
            log.info(f"✅ Loaded {len(agents)} agent(s) for execution")
        
        # Create Swarm with agents
        log.info(f"🐝 Initializing Swarm with {len(agents)} agent(s)...")
        swarm = Swarm(
            agents,
            execution_timeout=900.0,
            node_timeout=900.0
        )
        
        # Execute Swarm
        log.info("🚀 Starting Swarm execution...")
        result = await swarm.invoke_async(user_message)
        
        log.info("✅ Swarm execution completed")
        
        # Enhanced debugging - Log result structure
        log.info(f"🔍 DEBUG: Result has {len(result.results)} node results")
        for node_id, node_result in result.results.items():
            log.info(f"🔍 DEBUG: Node {node_id} has {len(list(node_result.get_agent_results()))} agent results")
        
        # Format and return results
        response_parts = []
        all_messages_debug = []
        
        for node_id, node_result in result.results.items():
            log.info(f"🔍 Processing node: {node_id}")
            agent_results = list(node_result.get_agent_results())
            
            for idx, agent_result in enumerate(agent_results):
                log.info(f"🔍 Agent result #{idx}: has_message={bool(agent_result.message)}")
                
                if agent_result.message and "content" in agent_result.message:
                    log.info(f"🔍 Message content has {len(agent_result.message['content'])} parts")
                    
                    for part_idx, part in enumerate(agent_result.message["content"]):
                        if "text" in part:
                            text = part['text'].strip()
                            all_messages_debug.append(f"[Node:{node_id}, Result:{idx}, Part:{part_idx}] {text[:100]}")
                            
                            if text and not text.startswith('Tool #') and not text.startswith('🔧'):
                                response_parts.append(text)
                                log.info(f"📝 Adding response part ({len(text)} chars)")
                            else:
                                log.info(f"⏭️ Skipping internal log")
        
        # Join all parts with double line breaks
        final_response = "\n\n".join(response_parts) if response_parts else "Task completed successfully."
        
        log.info(f"📊 Total response parts: {len(response_parts)}")
        log.info(f"📤 Returning response ({len(final_response)} chars)")
        
        # Clean up ping task
        ping_task.cancel()
        
        return final_response
    
    except MCPClientInitializationError as e:
        if str(e) == "the client session is currently running":
            log.warning("⚠️ MCP client session warning (can be ignored)")
        else:
            log.error(f"❌ MCP initialization error: {e}")
            ping_task.cancel()
            raise
    except Exception as e:
        log.error(f"❌ Swarm execution error: {e}")
        ping_task.cancel()
        raise
    finally:
        # Ensure cleanup
        try:
            ping_task.cancel()
        except:
            pass


@app.entrypoint
async def invoke(payload, context):
    """
    Entrypoint that starts Swarm in background with selective agent initialization.
    
    Supports three agent loading modes via payload:
    1. runtime_id / runtime_name: Load agents from database Bedrock runtime config
    2. selected_agent_ids / selected_agent_names: Load specific agents
    3. Default: Load all enabled agents
    
    Example payloads:
    
    Mode 1 - Runtime config:
    {
        "prompt": "Hello",
        "runtime_id": 1,
        "actor_id": "user-123"
    }
    
    Mode 2 - Selective agents:
    {
        "prompt": "Hello",
        "selected_agent_ids": [1, 2, 3],
        "actor_id": "user-123"
    }
    
    Mode 3 - Default (all enabled):
    {
        "prompt": "Hello",
        "actor_id": "user-123"
    }
    """
    log.info("🎯 Entrypoint called - starting Swarm with selective agent support")
    log.info("📌 Agent loading modes:")
    log.info("   1. Runtime config: runtime_id or runtime_name in payload")
    log.info("   2. Selective agents: selected_agent_ids or selected_agent_names")
    log.info("   3. Default: All enabled agents")
    log.info("💡 Manage agents: POST /agents")
    log.info("💡 Manage runtimes: POST /bedrock-runtimes")
    
    # Start background task
    task = asyncio.create_task(run_swarm_in_background(payload, context))
    
    # Wait for completion and stream results
    result = await task
    
    # Return result
    return result


if __name__ == "__main__":
    app.run()
