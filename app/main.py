# app/main.py
import os
from google import genai
from google.genai import types

from app.config import Config
from app.database import initialize_db
from app.tools import fetch_unread_emails, create_task_from_email, view_current_task_list

# A local registry dictionary to map tool names to their actual Python function implementations
TOOL_REGISTRY = {
    "fetch_unread_emails": fetch_unread_emails,
    "create_task_from_email": create_task_from_email,
    "view_current_task_list": view_current_task_list
}

class AgentHarness:
    def __init__(self):
        Config.validate()
        self.client = genai.Client()
        self.model = Config.LLM_MODEL
        
        # System instructions to give the agent its core mission parameters
        self.system_instruction = (
            "You are an autonomous executive assistant. Your goal is to triage the user's unread emails "
            "and extract actionable items into their prioritized task list database.\n\n"
            "CRITICAL PROTOCOL:\n"
            "1. ALWAYS fetch unread emails first.\n"
            "2. Evaluate each email. If an email contains a task, deadline, or explicit request, "
            "use the 'create_task_from_email' tool to save it.\n"
            "3. If an email is just a newsletter or informational with no action required, ignore it.\n"
            "4. Once completely done triaging, review the final list with 'view_current_task_list' and summarize your work to the user."
        )
        
        # Register the python functions as tools in the Gemini Config
        self.config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            tools=list(TOOL_REGISTRY.values()),
            temperature=0.0, # 0.0 forces deterministic reasoning (for inital debugging)
        )

    def run_triage_loop(self, user_prompt: str):
        print(f"\n🚀 Starting Agent Session...")
        
        # We manage the conversation state manually using Gemini's Content tracking structures
        conversation_history = [
            types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])
        ]
        
        # Read the max loop iterations from the config to prevent infinite API spend crashes
        max_iterations = int(os.getenv("MAX_ITERATIONS", "5"))
        
        for step in range(max_iterations):
            print(f"\n🔄 [Loop Step {step + 1}/{max_iterations}] Sending history to Gemini...")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=conversation_history,
                config=self.config
            )
            
            # Extract the model's response block and append it to our historical state
            model_turn = response.candidates[0].content
            conversation_history.append(model_turn)
            
            first_part = model_turn.parts[0]
            
            # --- CASE A: Gemini wants to run a tool ---
            if first_part.function_call:
                call = first_part.function_call
                tool_name = call.name
                tool_args = call.args
                
                print(f"🤔 [Agent Thought] I need to execute tool: '{tool_name}'")
                print(f"📥 [Tool Arguments] {tool_args}")
                
                if tool_name in TOOL_REGISTRY:
                    # Execute your local Python tool function by unpacking the arguments Gemini provided
                    tool_function = TOOL_REGISTRY[tool_name]
                    execution_result = tool_function(**tool_args)
                    
                    print(f"📤 [Tool Observation] Result: {execution_result}")
                    
                    # Package the execution result into a specialized 'tool' role block
                    # and feed it straight back into the history array for the next loop turn
                    tool_turn = types.Content(
                        role="tool",
                        parts=[
                            types.Part.from_function_response(
                                name=tool_name,
                                response={"result": execution_result}
                            )
                        ]
                    )
                    conversation_history.append(tool_turn)
                else:
                    print(f"❌ ERROR: Model requested tool '{tool_name}' which is not in our registry.")
                    break
                    
            # --- CASE B: Gemini returned a final text response ---
            elif first_part.text:
                print(f"\n🏁 [Final Agent Response]\n{first_part.text}")
                return first_part.text

        print("\n⚠️ WARNING: Loop terminated because it hit MAX_ITERATIONS limits.")

if __name__ == "__main__":
    # Initialize your SQLite table inside the container
    initialize_db()
    
    # Instantiate and trigger your custom ReAct loop execution
    harness = AgentHarness()
    harness.run_triage_loop("Please triage my inbox and update my task manager based on what you find.")