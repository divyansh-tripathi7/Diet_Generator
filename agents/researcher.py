from gpt_researcher import GPTResearcher
from colorama import Fore, Style
from .utils.views import print_agent_output
from typing import Dict, List

class ResearchAgent:
    def __init__(self):
        pass

    async def research(self, query: str, research_report: str = "research_report",
                       parent_query: str = "", verbose=True, source="web"):
        # Initialize the researcher
        researcher = GPTResearcher(query=query, report_type=research_report, parent_query=parent_query,
                                   verbose=verbose, report_source=source)
        # Conduct research on the given query
        await researcher.conduct_research()
        # Write the report
        report = await researcher.write_report()

        return report

    async def research_diet_and_eateries(self, user_profile: dict):
        goals = user_profile.get("goals", "")
        health_issues = ", ".join(user_profile.get("health_issues", []))
        location = user_profile.get("location", "")

        # Research diet plans based on user profile
        diet_query = f"Generate a personalized diet plan for someone who is aiming for {goals} and has the following health issues: {health_issues}."
        diet_report = await self.research(query=diet_query, research_report="diet_plan_report", source="web")

        # Research eateries that match the diet plan
        eateries_query = f"Find eateries in {location} that offer food suitable for a {goals} diet with the following considerations: {health_issues}."
        eateries_report = await self.research(query=eateries_query, research_report="eateries_report", source="web")

        return {
            "diet_plan": diet_report,
            "eateries": eateries_report
        }

    async def run_initial_research(self, research_state: dict):
        task = research_state.get("task")
        user_profile = task.get("user_profile", {})
        source = task.get("source", "web")
        print_agent_output(f"Running initial research for user profile: {user_profile}", agent="RESEARCHER")
        
        research_results = await self.research_diet_and_eateries(user_profile=user_profile)

        return {
            "task": task,
            "initial_research": research_results["diet_plan"],
            "eateries": research_results["eateries"]
        }

    async def run_depth_research(self, draft_state: dict):
        task = draft_state.get("task")
        topic = draft_state.get("topic")
        user_profile = task.get("user_profile", {})
        source = task.get("source", "web")
        verbose = task.get("verbose")
        
        print_agent_output(f"Running in-depth research for topic: {topic}", agent="RESEARCHER")
        
        # Conduct depth research related to diet and eateries
        research_results = await self.research_diet_and_eateries(user_profile=user_profile)
        research_draft = {
            "diet_plan": research_results["diet_plan"],
            "eateries": research_results["eateries"]
        }
        
        return {"draft": research_draft}
