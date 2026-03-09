import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
gemini_flash = LLM(model="gemini/gemini-3-flash-preview",
api_key= os.getenv("GEMINI_API_KEY"))

# --- 1. Define the Crew (The Department) ---
class NewsroomCrew:
    def __init__(self,topic, feedback):
        self.topic = topic
        self.feedback = feedback
        # Workers
        self.researcher = Agent(
            role="Fact Researcher",
            goal="Find 2 verifiable facts about {topic}",
            backstory="Analytic and skeptical. You only provide cited data.",
            llm=gemini_flash
        )
        self.writer = Agent(
            role="News Writer",
            goal="Write a 20 word summary of the research.Incorporate this feedback if it exists: {feedback}",
            backstory="Professional journalist for a major news blog.",
            llm=gemini_flash
        )
    
    def get_crew(self):
        return Crew(
            agents=[self.researcher, self.writer],
            tasks=[
                Task(
                    description="Research {topic}", 
                    expected_output="2 facts", 
                    agent=self.researcher
                    ),
                Task(
                    description="Write summary on {topic} based on research and feedback{feedback}", 
                    expected_output="Professional summary of 20 words", 
                    agent=self.writer
                    )
            ],
            process=Process.hierarchical, 
            manager_llm=gemini_flash
        )

# --- 2. Define the Flow (The Orchestrator) ---
class NewsState(BaseModel):
    topic: str = ""
    draft: str = ""
    feedback: str = ""
    retry_count: int = 0

class FactCheckedFlow(Flow[NewsState]):
    
    @start()
    def generate_draft(self):
        print(f"🚀 [Attempt {self.state.retry_count + 1}] Calling Newsroom Department...")
        newsroom = NewsroomCrew(topic=self.state.topic, feedback=self.state.feedback)
        crew = newsroom.get_crew()
        result = crew.kickoff(
            inputs=
            {
            "topic": self.state.topic, 
            "feedback": self.state.feedback
            }
        )
        self.state.draft = result.raw
        return result.raw

    @router(generate_draft)
    def quality_review(self):
        print("🕵️ Reviewer is reviewing the department's output...")
        
        review_prompt = f"""
        Review this draft: {self.state.draft}
        Does it have less than 30 words? (Yes/No). 
        Format: Result: [Yes/No] | Feedback: [Your feedback]
        """
        review_result = gemini_flash.call(review_prompt)
        
        if "yes" in review_result.lower():
            return "success"
        else:
            self.state.feedback = review_result
            self.state.retry_count += 1
            return "failed"

    @listen("failed")
    def retry_logic(self):
        if self.state.retry_count < 2:
            print(f"❌ Feedback sent back to Newsroom: {self.state.feedback}")
            return self.generate_draft() # Loop back
        else:
            print("⚠️ Max retries reached. Moving to final.")
            return "success"

    @listen("success")
    def final_output(self):
        print("\n✅ Final Approved Draft:\n", self.state.draft)
# --- 3. Execute ---
flow = FactCheckedFlow()
flow.state.topic = "T20 World Cup finals 2026 "
flow.kickoff()