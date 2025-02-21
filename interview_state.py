import os
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WikipediaLoader
from langchain_core.messages import get_buffer_string
from langgraph.graph import StateGraph,START,END
from PIL import Image
import io
import getpass
import os

# ---------local-imports---------------

from schema import InterviewState,SearchQuery
from create_analyst import llm,tavily_key
from prompt import question_instruction,search_instructions,answer_instruction,section_writer_instructions




os.environ["TAVILY_API_KEY"] = tavily_key



tavily_search = TavilySearchResults(max_results=3)

def generate_question(state:InterviewState):
    
    print(state," --------------------- ")
    
    
    analyst = state["analyst"]
    messages = state["messages"]
    
    
    system_msg = question_instruction.format(goals=analyst.persona)
    question = llm.invoke([SystemMessage(content=system_msg)]+messages)
    
    # print("_"*90,question)
    
    return {"messages":question}


def search_web(state:InterviewState):
    
    structured_llm = llm.with_structured_output(SearchQuery)
    

    
    search_query = structured_llm.invoke([SystemMessage(content=search_instructions)]+state["messages"])
    
    print("_|"*120)
    print(search_query)
    print("_|"*120)

    
    search_docs = tavily_search.invoke(search_query.search_query)
    
    formatted_search_docs = "\n\n----\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )
    
    return {"context":[formatted_search_docs]}


def search_wikipedia(state:InterviewState):
    
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([SystemMessage(content=search_instructions)]+state["messages"])
    
    search_docs = WikipediaLoader(query=search_query.search_query,load_max_docs=2).load()
    
    formatted_search_docs = "\n\n-----\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page","")}"/>\n {doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )
    
    return {"context":[formatted_search_docs]}


def generate_answer(state:InterviewState):
    analyst = state["analyst"]
    messages = state["messages"]
    context = state["context"]
    
    system_msg = answer_instruction.format(goals=analyst.persona,context=context)
    answer = llm.invoke([SystemMessage(content=system_msg)] + messages)
    
    answer.name = "expert"
    return {"messages":[answer]}

def save_interview(state:InterviewState):
    messages = state["messages"]
    interview = get_buffer_string(messages)
    
    return {"interview":interview}


def route_messages(state:InterviewState,name:str="expert"):
    messages = state["messages"]
    max_num_turns = state["max_num_turns"]
    
    
    num_response = len(
        [m for m in messages if isinstance(m,AIMessage) and m.name==name]
    )
    
    if num_response>=max_num_turns:
        return "save_interview"
    
    last_question = messages[-2]
    
    if "Thank you so much for your help" in last_question.content:
        return "save-interveiw"
    return "ask_question"


def write_section(state:InterviewState):
    
    interview = state["interview"]
    context = state["context"]
    analyst = state["analyst"]
    
    system_msg = section_writer_instructions.format(focus=analyst.description)
    section = llm.invoke([SystemMessage(content=system_msg)] + [HumanMessage(content=f"use this source to write your section: {context}")])
    
    return {"section":[section.content]}



interview_builder = StateGraph(InterviewState)

interview_builder.add_node("ask_question",generate_question)
interview_builder.add_node("search_web",search_web)
interview_builder.add_node("search_wikipedia",search_wikipedia)
interview_builder.add_node("answer_question",generate_answer)
interview_builder.add_node("save_interview",save_interview)
interview_builder.add_node("write_section",write_section)

interview_builder.add_edge(START,"ask_question")
interview_builder.add_edge("ask_question","search_web")
interview_builder.add_edge("ask_question","search_wikipedia")
interview_builder.add_edge("search_web","answer_question")
interview_builder.add_edge("search_wikipedia","answer_question")
interview_builder.add_conditional_edges("answer_question",route_messages,['ask_question','save_interview'])
interview_builder.add_edge("save_interview","write_section")
interview_builder.add_edge("write_section",END)

# interview_graph = interview_builder.compile(checkpointer=memory).with_config(run_name="conduct_interview")


# # --------------graph-image ------------------
# # png_bytes = interview_graph.get_graph().draw_mermaid_png()
# # image = Image.open(io.BytesIO(png_bytes))
# # graph_path = "interview_graph_builder.png"
# # image.save(graph_path)

# # image.show()
# # ---------------------------------------------

