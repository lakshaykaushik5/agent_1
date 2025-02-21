import os
from dotenv import load_dotenv
from PIL import Image
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import io

# ---------------local imports------------------------

from schema import Analyst, Perspective, GenerateAnalystsState
from prompt import analyst_instruction


load_dotenv()

tavily_key = os.getenv("TAVILY_KEY")
groq_key = os.getenv("GROQ_KEY")
langsmith_key = os.getenv("LANGSMITH_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_key)


def create_analysts(state: GenerateAnalystsState):
    topic = state["topic"]
    max_analysts = state["max_analysts"]
    human_analyst_feedback = state.get("human_analyst_feedback", None)

    structured_llm = llm.with_structured_output(Perspective)
    system_msg = analyst_instruction.format(
        topic=topic,
        human_analyst_feedback=human_analyst_feedback,
        max_analysts=max_analysts,
    )
    
    analysts = structured_llm.invoke(
        [SystemMessage(content=system_msg)]
        + [HumanMessage(content="Generate the set of the Analysts")]
    )
    return {"analysts": analysts.analysts}


def human_feedback(state: GenerateAnalystsState):
    pass


def should_continue(state: GenerateAnalystsState):

    human_feedback = state.get("human_analyst_feedback", None)
    if human_feedback:
        return "create_analysts"
    return END


# builder = StateGraph(GenerateAnalystsState)

# builder.add_node("create_analysts", create_analysts)
# builder.add_node("human_feedback", human_feedback)

# builder.add_edge(START, "create_analysts")
# builder.add_edge("create_analysts", "human_feedback")
# builder.add_conditional_edges(
#     "human_feedback", should_continue, ["create_analysts", END]
# )


# memory = MemorySaver()
# graph = builder.compile(interrupt_before=["human_feedback"], checkpointer=memory)

# --------------graph-image ------------------
# png_bytes = graph.get_graph().draw_mermaid_png()
# image = Image.open(io.BytesIO(png_bytes))
# graph_path = "graph_builder.png"
# image.save(graph_path)

# image.show()
# ---------------------------------------------


# max_analysts = 3
# topic = """The benefits of adopting Langgraph as an agent framework"""
# thread = {"configurable": {"thread_id": "1"}}

# for event in graph.stream(
#     {"topic": topic, "max_analysts": max_analysts}, thread, stream_mode="values"
# ):
#     analysts = event.get("analysts", "")
#     if analysts:
#         for analyst in analysts:
#             print(f"Name : {analyst.name}")
#             print(f"Affiliation : {analyst.affiliation}")
#             print(f"Role : {analyst.role}")
#             print(f"Description : {analyst.description}")
#             print(" _ " * 50, "\n\n\n")


# state = graph.get_state(thread)
# print(state.next)

# graph.update_state(
#     thread,
#     {
#         "human_analyst_feedback": "Add two more person one with senior devloper perspective and one with tech startup perspective"
#     },
#     as_node="human_feedback",
# )


# print(
#     "--------------------------------------------with-human-feedback----------------------------------------------"
# )

# for event in graph.stream(None, thread, stream_mode="values"):
#     analysts = event.get("analysts", "")
#     if analysts:
#         for analyst in analysts:
#             print(f"Name : {analyst.name}")
#             print(f"Affiliation : {analyst.affiliation}")
#             print(f"Role : {analyst.role}")
#             print(f"Description : {analyst.description}")
#             print(" _ " * 50, "\n\n\n")


# further_feedback = None
# graph.update_state(
#     thread, {"human_analyst_feedback": further_feedback}, as_node="human_feedback"
# )

# for event in graph.stream(None, thread, stream_mode="updates"):
#     print("----Node---")
#     node_name = next(iter(event.keys()))
#     print(node_name)


# final_state = graph.get_state(thread)
# analysts = final_state.values.get("analysts")

# final_state.next

# print("------------------------------------final------------------------------------------------")

# for analyst in analysts:
#     print(f"Name : {analyst.name}")
#     print(f"Affiliation : {analyst.affiliation}")
#     print(f"Role : {analyst.role}")
#     print(f"Description : {analyst.description}")
#     print("_" * 50, "\n\n\n")


# ____________________________________________________INTERVIEW_STATE__________________________________________________________