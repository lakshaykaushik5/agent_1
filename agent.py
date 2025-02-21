from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver
from PIL import Image
import io
import os
# ---------local-imports------------------------

from create_analyst import create_analysts,human_feedback,should_continue
from final_operation import finalize_report, initiate_all_interviews, write_report,write_conclustion,write_introduction,initiate_all_interviews
from schema import ResearchGraphState
from interview_state import interview_builder


final_builder = StateGraph(ResearchGraphState)

final_builder.add_node("create_analyst",create_analysts)
final_builder.add_node("human_feedback",human_feedback)
final_builder.add_node("conduct_interview",interview_builder.compile())
final_builder.add_node("write_report",write_report)
final_builder.add_node("write_introduction",write_introduction)
final_builder.add_node("write_conclusion",write_conclustion)
final_builder.add_node("finalize_report",finalize_report)

# conduct_interview
final_builder.add_edge(START,"create_analyst")
final_builder.add_edge("create_analyst","human_feedback")
final_builder.add_conditional_edges("human_feedback",initiate_all_interviews,["create_analyst","conduct_interview"])
final_builder.add_edge("conduct_interview","write_report")
final_builder.add_edge("conduct_interview","write_conclusion")
final_builder.add_edge("conduct_interview","write_introduction")
final_builder.add_edge(["write_report","write_conclusion","write_introduction"],"finalize_report")
final_builder.add_edge("finalize_report",END)

memory = MemorySaver()
final_graph = final_builder.compile(interrupt_before=["human_feedback"],checkpointer=memory)


# --------------graph-image ------------------
# png_bytes = final_graph.get_graph().draw_mermaid_png()
# image = Image.open(io.BytesIO(png_bytes))
# graph_path = "final_graph_builder.png"
# image.save(graph_path)

# image.show()
# ---------------------------------------------


max_analysts = 3
topic = "The benefits for adapting Langgraph as an agent framework for junior dev"
thread = {"configurable":{"thread_id":"1"}}

for event in final_graph.stream({"topic":topic,
                                 "max_analysts":max_analysts,
                                 },thread,stream_mode="values"):
    analysts = event.get("analysts","")
    if analysts:
        for analyst in analysts:
            print(f"Name: {analyst.name}")
            print(f"Affiliation: {analyst.affiliation}")
            print(f"Role: {analyst.role}")
            print(f"Description: {analyst.description}")
            print("-" * 50)
            

final_graph.update_state(thread,{"max_analysts":5,
                                 "human_analyst_feedback":"Add two more agent one for startups jobs and one for high paying jobs"},as_node="human_feedback")


print("_"*50,"Human Feedback","_"*50)

for event in final_graph.stream(None, thread, stream_mode="values"):
    analysts = event.get('analysts', '')
    if analysts:
        for analyst in analysts:
            print(f"Name: {analyst.name}")
            print(f"Affiliation: {analyst.affiliation}")
            print(f"Role: {analyst.role}")
            print(f"Description: {analyst.description}")
            print("-" * 50)  
            

final_graph.update_state(thread, {"human_analyst_feedback": 
                            None}, as_node="human_feedback")


for event in final_graph.stream(None, thread, stream_mode="updates"):
    print("--Node--")
    node_name = next(iter(event.keys()))
    print(node_name)


final_state = final_graph.get_state(thread)
report = final_state.values.get("final_report")

print(report)