"""
Updated Bedrock Entrypoint with Dynamic Agent Management

This entrypoint loads agents dynamically from the database instead of using
hardcoded agent functions. Agents are configured via REST API without requiring
code changes or redeployment.
"""
import os
import asyncio
from strands import Agent
from strands.multiagent import Swarm
from bedrock_agentcore.memory import MemoryClient
from strands.hooks import AgentInitializedEvent, HookProvider, HookRegistry, MessageAddedEvent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.types.exceptions import MCPClientInitializationError

# Import dynamic agent factory and database
from app.services.agent_factory import AgentFactory
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


@app.async_task
async def run_swarm_in_background(payload, context):
    """
    Run the Swarm agents in background with dynamic agent loading.
    
    Agents are loaded from the database, not hardcoded.
    This allows adding new agents via REST API without code changes.
    """
    # Log full payload for debugging
    log.info(f"📦 Full payload keys: {list(payload.keys())}")
    
    actor_id = payload.get("actor_id") or payload.get("user_id") or 'default-user'
    session_id = payload.get("session_id") or getattr(context, 'session_id', None) or 'default'
    user_message = payload.get("prompt", "Hello! How can I help you today?")
    
    # 🔒 SESSION MANAGEMENT: Always maintain conversation history for the same session_id
    log.info(f"🚀 Swarm invoked with session_id={session_id}, actor_id={actor_id}")
    log.info(f"🔒 Session type: CONTINUING (will load history for session: {session_id})")
    log.info(f"💬 User message: {user_message}")
    
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
        
        # 🆕 DYNAMIC AGENT LOADING
        log.info("📚 Loading agents dynamically from database...")
        
        db = next(get_db())
        factory = AgentFactory(db, memory_client)
        
        # Create agents from database configuration
        agents = await factory.create_agents_from_database(
            actor_id=actor_id,
            session_id=session_id,
            enabled_only=True,  # Only load enabled agents
            hooks=[memory_hook] if memory_hook else None
        )
        
        if not agents:
            log.warning("⚠️ No agents found in database! Check agent configuration.")
            log.warning("   Use POST /agents to create agents dynamically")
        else:
            log.info(f"✅ Loaded {len(agents)} agent(s) from database")
        
        # Create Swarm with dynamic agents
        log.info(f"🐝 Initializing Swarm with {len(agents)} dynamic agent(s)...")
        swarm = Swarm(
            agents,
            execution_timeout=900.0,
            node_timeout=900.0
        )
        
        # Execute Swarm with the enhanced message
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
    Entrypoint that starts Swarm in background and returns immediately
    """
    log.info("🎯 Entrypoint called - starting Swarm in background")
    log.info("📌 All agents are now loaded dynamically from database!")
    log.info("💡 To add new agents, use: POST /agents")
    
    # Start background task
    task = asyncio.create_task(run_swarm_in_background(payload, context))
    
    # Wait for completion and stream results
    result = await task
    
    # Return result
    return result


if __name__ == "__main__":
    app.run()
