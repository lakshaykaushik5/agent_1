from typing import List, TypedDict, Annotated
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState
import operator

class Analyst(BaseModel):
    affiliation:str = Field(
        description="Primary affiliation of the analyst"
    )
    name:str = Field(
        description="Name of the analyst"
    )
    role:str = Field(
        description="Role of the Analyst in context of the topic"
    )
    description:str = Field(
        description="Description of the analyst focus,concerns and motives"
    )
    @property
    def persona(self)->str:
        return f"Name:{self.name}\n Role:{self.role}\n Description:{self.description}\n Affiliation:{self.affiliation}"


class Perspective(BaseModel):
    analysts: List[Analyst] = Field(
        description="Comprehensive list of the analysts with there role and affiliations"
    )


class GenerateAnalystsState(TypedDict):
    topic:str
    max_analysts:int
    human_analyst_feedback:str
    analysts:List[Analyst]
    

class InterviewState(MessagesState):
    max_num_turns:int
    context:Annotated[list,operator.add]
    analyst:Analyst
    interview:str
    sections:list
    

class SearchQuery(BaseModel):
    search_query:str = Field(
        description="Search query for retrieval"
    )
    

class ResearchGraphState(TypedDict):
    topic:str
    max_analysts:int
    human_analyst_feedback:str
    analysts:List[Analyst]
    sections:Annotated[list,operator.add]
    introduction:str
    content:str
    conclusion:str
    final_report:str    