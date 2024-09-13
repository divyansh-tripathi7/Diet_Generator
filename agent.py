from agents import ChiefEditorAgent

# Create a new instance of ChiefEditorAgent with updated task parameters
chief_editor = ChiefEditorAgent({
    "query": "Personalized diet plan",
    "max_sections": 5,
    "publish_formats": {
        "markdown": True,
        "pdf": True,
        "docx": True
    },
    "follow_guidelines": True,
    # "model": "gpt-4o",
    "model": "gpt-3.5-turbo",
    "guidelines": [
        "The diet plan must be personalized to the user's health conditions and dietary goals.",
        "Include relevant research for the diet plan.",
        "Each section must be evidence-based, and sources must be cited with hyperlinks.",
        "The report must be clear and written in plain language."
    ],
    "user_profile": {
        "goals": "weight loss",
        "health_issues": ["diabetes"],
        "location": "Bangalore"
    },
    "verbose": True
})

# Initialize and compile the workflow graph with the new settings
graph = chief_editor.init_research_team()
graph = graph.compile()
