#!/bin/env python
# from https://github.com/abvijaykumar/crewai-blogs/tree/main, 
# https://abvijaykumar.medium.com/multi-agent-system-crew-ai-3773356b8c3e
# https://abvijaykumar.medium.com/

from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from crewai_tools import WebsiteSearchTool
import sys
import gvars as g
from model_select import ModelSelect
from crewai.project import CrewBase, agent, crew, task
from langchain.agents import tool
from crewai_tools import SerperDevTool
import dotenv
import os
from colorama import Fore, Back

dotenv.load_dotenv(g.crew_env)
# search_tool = DuckDuckGoSearchRun()
web_tool = WebsiteSearchTool()
thismodel = ModelSelect()


# llm = Ollama(model="mistral:latest", verbose=True)
#llm  = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo")

llm = thismodel.local_llama()

# ╔═════════════════════════════════════════════════════════════
# ║ Serper Search Tools Class
# ╚═════════════════════════════════════════════════════════════
class SerperSearch():
    @tool
    def search(query: str):
        """Search the web for information on a given topic"""
        try:
            rs = SerperDevTool(api_key=os.environ["SERPER_API_KEY"]).run(query)
            print(Fore.WHITE+Back.RED+f"{query}")
            print(Fore.WHITE+Back.BLUE+f"{rs}"+Fore.RESET+Back.RESET)
            return rs
        except Exception as e:
            raise e
    def tools():
        return [SerperSearch.search]
search_tool = SerperDevTool(api_key=os.environ["SERPER_API_KEY"])


def kickoffTheCrew(topic): 
    researcher = Agent(
        role = "Internet Research",
        goal = f"Perform research on the {topic}, and find and explore about {topic} ",
        verbose = True,
        llm=llm,
        backstory = """You are an expert Internet Researcher
        Who knows how to search the internet for detailed content on {topic}
        Include any code examples with documentation"""
    )
    
    blogger = Agent(
        role='Blogger',
        goal="""Write engaging and interesting blog in maximum 2000 words. Add relevant emojis""",
        verbose=True,
        allow_delegation=True,  
        llm=llm,         
        backstory="""You are an Expert Blogger on Internet.
                    Include code examples, and provide tutorial type instructions for the readers."""
    )
    
    task_search = Task(
        description="""Search for all the details about the  {topic}
                    Your final answer MUST be a consolidated content that can be used for blogging
                    This content should be well organized, and should be very easy to read.  Set the input parameter as:search_query""",
        expected_output='A comprehensive 10000 words information about {topic}.',
        max_inter=3,
        tools=[search_tool, web_tool],           
        agent=researcher)
    
    task_post = Task(
        description="""Write a well structured blog and at max 10000 words.
                    The Blog should also include sample programs and codes, tutorials, and all the content that is useful for the readers
                    Also explain the concepts, architecture in detail
                    Once the blog is created, create a new file called blog.md, and save the blog in that file
                    """,
        expected_output='A comprehensive 20 paragraph blog on {topic} in markdown format',
        agent=blogger)
    
    crew = Crew(
        agents=[researcher, blogger],
        tasks=[task_search, task_post],
        verbose=2,
        process=Process.sequential )
    
    result = crew.kickoff()
    return result


n = len(sys.argv)

if n == 2 :
    topic = sys.argv[1]
    # inputs = {
    #     'topic': topic
    # }
    topic = topic
    result = kickoffTheCrew(topic)

    print (result)
else :
    print ("Please pass topic as parameter. Usage python3 blogger.py topic")
