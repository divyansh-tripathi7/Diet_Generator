from datetime import datetime
from .utils.views import print_agent_output
from .utils.llms import call_model
from langgraph.graph import StateGraph, END
import asyncio
import json

from memory.draft import DraftState
from .reviser import ReviserAgent
from .reviewer import ReviewerAgent
from .researcher import ResearchAgent

class EditorAgent:
    def __init__(self):
        pass

    def plan_research(self, research_state: dict):
        """
        Curate relevant sections for a diet plan and eateries recommendations.
        :param research_state:
        :return:
        """

        initial_research = research_state.get("initial_research")
        task = research_state.get("task")
        max_sections = task.get("max_sections")
        user_profile = task.get("user_profile", {})

        prompt = [{
            "role": "system",
            "content": "You are an expert diet plan and eateries recommendation curator. Your goal is to create an outline for a personalized diet plan and eateries recommendations."
        }, {
            "role": "user",
            "content": f"Today's date is {datetime.now().strftime('%d/%m/%Y')}\n."
                       f"Initial research: '{initial_research}'\n\n"
                       f"Your task is to generate an outline of sections for a diet plan and eateries recommendations based on the initial research and user profile.\n"
                       f"You must generate a maximum of {max_sections} sections.\n"
                       f"Focus on including personalized dietary advice, addressing health issues, goals, and local eateries.\n"
                       f"Return nothing but a JSON with the fields 'title' (str) and 'sections' (maximum {max_sections} section headers) with the following structure: "
                       f"'{{title: string, date: today's date, sections: ['section header 1', 'section header 2', 'section header 3' ...]}}.\n"
        }]

        print_agent_output(f"Planning an outline layout based on initial research and user profile...", agent="EDITOR")
        response = call_model(prompt=prompt, model=task.get("model"), response_format="json")
        plan = json.loads(response)

        return {
            "title": plan.get("title"),
            "date": plan.get("date"),
            "sections": plan.get("sections")
        }

    async def run_parallel_research(self, research_state: dict):
        research_agent = ResearchAgent()
        reviewer_agent = ReviewerAgent()
        reviser_agent = ReviserAgent()
        queries = research_state.get("sections")
        title = research_state.get("title")
        workflow = StateGraph(DraftState)

        workflow.add_node("researcher", research_agent.run_depth_research)
        workflow.add_node("reviewer", reviewer_agent.run)
        workflow.add_node("reviser", reviser_agent.run)

        # set up edges researcher->reviewer->reviser->reviewer...
        workflow.set_entry_point("researcher")
        workflow.add_edge('researcher', 'reviewer')
        workflow.add_edge('reviser', 'reviewer')
        workflow.add_conditional_edges('reviewer',
                                       (lambda draft: "accept" if draft['review'] is None else "revise"),
                                       {"accept": END, "revise": "reviser"})

        chain = workflow.compile()

        # Execute the graph for each query in parallel
        print_agent_output(f"Running the following research tasks in parallel: {queries}...", agent="EDITOR")
        final_drafts = [chain.ainvoke({"task": research_state.get("task"), "topic": query, "title": title})
                        for query in queries]
        research_results = [result['draft'] for result in await asyncio.gather(*final_drafts)]

        return {"research_data": research_results}
