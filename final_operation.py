from langgraph.constants import Send
from langchain_core.messages import HumanMessage,SystemMessage

# -----------local-imports-----------

from schema import ResearchGraphState
from prompt import report_writer_instructions,intro_conclusion_instructions
from create_analyst import llm


def initiate_all_interviews(state: ResearchGraphState):
    human_analyst_feedback = state.get("human_analyst_feedback")

    if human_analyst_feedback:
        return "create_analyst"

    topic = state["topic"]

    print("-"*50)

    print(state["analysts"])
    
    print("-"*50)
    
    return [
        Send(
            "conduct_interview",
            {
                "analyst": analyst,
                "max_num_turns":3,
                "topic": topic,
                "messages": [
                    HumanMessage(
                        content=f"so you said your were writing an article on {topic}?"
                    )
                ],
            },
        )
        for analyst in state["analysts"]
    ]

def write_introduction(state: ResearchGraphState):
    sections = state["sections"]
    topic = state["topic"]

    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
        
    instructions = intro_conclusion_instructions.format(topic=topic, formatted_str_sections=formatted_str_sections)    
    intro = llm.invoke([instructions]+[HumanMessage(content=f"Write the report introduction")]) 
    return {"introduction": intro.content}


def write_report(state:ResearchGraphState):
    sections = state["sections"]
    topic = state["topic"]
    
    formatted_str_sections = "\n\n---\n\n".join([
        f"{section}" for section in sections
    ])
    
    system_msg = report_writer_instructions.format(topic=topic,context=formatted_str_sections)
    
    report = llm.invoke([SystemMessage(content=system_msg)]+[HumanMessage(content="Write a report based upon these memos. ")])
    
    return {"content":report.content}


def write_conclustion(state:ResearchGraphState):
    sections = state["sections"]
    topic = state["topic"]
    
    formatted_str_sections = "\n\n--\n\n".join([
        f"{section}" for section in sections
    ])
    
    instructions = intro_conclusion_instructions.format(topic=topic,formatted_str_sections=formatted_str_sections)
    conclusion = llm.invoke([instructions]+[HumanMessage(content=f"Write the report conclusion")])
    
    return {"conclusion":conclusion}


def finalize_report(state:ResearchGraphState):
    content = state["content"]
    if content.startswith("## Insight"):
        content = content.strip("## Insight")
    if "## Sources" in content:
        try:
            content,sources = content.split("\n## Sources \n")
        except:
            sources = None
    else:
        sources=None
    
    final_report = state["introduction"] + "\n\n---\n\n" + content + "\n\n---\n\n"+state["conclusion"]
    
    if sources is not None:
        final_report += "\n\n## Sources\n" +sources
    return {"final_report":final_report}
    