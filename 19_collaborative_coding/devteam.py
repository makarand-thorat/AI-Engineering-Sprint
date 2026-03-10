import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
gemini_flash = LLM(model="gemini/gemini-3-flash-preview",
api_key=os.getenv("GEMINI_API_KEY"))

# --- 1. State: Tracking the Code and the "Bugs" ---
class DevState(BaseModel):
    code_snippet: str = ""
    review_feedback: str = ""
    is_code_secure: bool = False
    retry_count: int = 0

# --- 2. The Dev Team Department ---
class DevCrew:
    def __init__(self, requirement, feedback=""):
        self.requirement = requirement
        self.feedback = feedback

        self.coder = Agent(
            role="Senior Python Developer",
            goal="Write clean, efficient Python code for: {requirement}",
            backstory="Expert in PEP8 and clean code. Feedback to address: {feedback}",
            llm=gemini_flash
        )
        self.reviewer = Agent(
            role="Security Reviewer",
            goal="Find potential bugs or security holes in the code.",
            backstory="A paranoid security engineer who hates unoptimized code.",
            llm=gemini_flash
        )

    def get_crew(self):
        return Crew(
            agents=[self.coder, self.reviewer],
            tasks=[
                Task(description="Code the requirement: {requirement}", expected_output="A Python code block", agent=self.coder),
                Task(description="Review the code. Identify bugs.", expected_output="A list of issues or 'PASSED'", agent=self.reviewer)
            ],
            process=Process.hierarchical,
            manager_llm=gemini_flash
        )

# --- 3. The Orchestration ---
class SoftwareDevFlow(Flow[DevState]):
    
    @start()
    def create_initial_code(self):
        print(f"🚀 [Dev Phase] Attempt {self.state.retry_count + 1}: Coding...")
        dev_dept = DevCrew(requirement="A function to check if a password is strong", feedback=self.state.review_feedback)
        result = dev_dept.get_crew().kickoff(inputs={"requirement": "Strong Password Checker", "feedback": self.state.review_feedback})
        
        self.state.code_snippet = result.raw
        return result.raw

    @router(create_initial_code)
    def check_quality(self):
        print("🔍 Checking if Reviewer found issues...")
        if "passed" in self.state.code_snippet.lower() and self.state.retry_count > 0:
            return "deployable"
        
        
        if self.state.retry_count < 1: # Force at least one review loop for demo
            self.state.review_feedback = "Please add type hinting and a docstring."
            self.state.retry_count += 1
            return "needs_fix"
        
        return "deployable"

    @listen("needs_fix")
    def fix_code(self):
        print(f"🛠️ Fix Required: {self.state.review_feedback}")
        return self.create_initial_code()

    @listen("deployable")
    def production(self):
        print("\n✅ CODE DEPLOYED TO PRODUCTION:\n")
        print(self.state.code_snippet)

# --- Execute ---
flow = SoftwareDevFlow()
flow.kickoff()