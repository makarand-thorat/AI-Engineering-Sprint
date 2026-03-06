import os
from dotenv import load_dotenv
from crewai import Agent, Task,Crew,Process
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import SerperDevTool

load_dotenv()

llm=ChatGoogleGenerativeAI(
    model="gemini/gemini-3-flash-preview",
    api_key = os.getenv("GEMINI_API_KEY")
)


#TOOLS
search_tool = SerperDevTool()


#AGENT DEFINING
researcher = Agent(
    role='Senior Research Analyst',
    goal='Uncover cutting-edge developments in {topic}',
    backstory="""You are a world-class researcher. You excel at finding 
    the most relevant information and summarizing it into concise points.""",
    tools=[search_tool],
    verbose=True,
    allow_delegation=False,
    llm=llm
)

writer = Agent(
    role='Tech Content Strategist',
    goal='Draft a compelling blog post about {topic}',
    backstory="""You are a renowned tech writer. You take complex 
    research and turn it into engaging, easy-to-read articles.""",
    verbose=True,
    llm=llm
)

#Define the Tasks
task1 = Task(
    description="Analyze the latest trends in {topic}. Focus on 2026 breakthroughs.",
    expected_output="A bulleted list of 3 key findings.",
    agent=researcher
)

task2 = Task(
    description="Using the researcher's findings, write a 3 points.",
    expected_output="A markdown formatted blog post.",
    agent=writer,
    output_file="crew_report.md"
)

# Assemble the Crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
    process=Process.sequential # Task 1 must finish before Task 2 starts
)

# 5. Kick it off!
result = crew.kickoff(inputs={'topic': 'AI Agentic Workflows'})

print("\n\n########################")
print("## FINAL OUTPUT ##")
print("########################\n")
print(result)