import dotenv
import os
from langchain_openai import ChatOpenAI as OpenAI
import gvars as g
from dotenv import set_key

class ModelSelect:
    """LLM Selector"""
    def __init__(self,source)-> None:
        self.source= source
        dotenv.load_dotenv(g.crew_env_file, override=True)


    def llm_server(self):
        # get the vals for each system
        self.OPENAI_API_BASE_URL   = os.environ[f'XXX_{self.source}_API_BASE_URL']
        self.OPENAI_API_KEY        = os.environ[f'XXX_{self.source}_API_KEY']
        self.OPENAI_MODEL_NAME     = os.environ[f'XXX_{self.source}_MODEL_NAME']

        # update the .env with OPENAI* vas with these new vals to
        # set the as the default for OPENAI, as some code might default to the OpenAI env vars

        set_key(g.crew_env_file,"OPENAI_API_BASE_URL",self.OPENAI_API_BASE_URL)
        set_key(g.crew_env_file,"OPENAI_API_KEY",self.OPENAI_API_KEY)
        set_key(g.crew_env_file,"OPENAI_MODEL_NAME",self.OPENAI_MODEL_NAME)


        os.environ['OPENAI_API_BASE_URL'] = self.OPENAI_API_BASE_URL
        os.environ['OPENAI_API_KEY'] = self.OPENAI_API_KEY
        os.environ['OPENAI_MODEL_NAME'] = self.OPENAI_MODEL_NAME

        if self.source == "OLLAMA":
            llm = OpenAI(
                openai_api_base = self.OPENAI_API_BASE_URL,
                openai_api_key  = self.OPENAI_API_KEY,
                model           = self.OPENAI_MODEL_NAME,
                temperature     = 0.0,
                verbose         = g.verbose,
            )
        if self.source == "LMS":
            llm = OpenAI(
                openai_api_base=self.OPENAI_API_BASE_URL,
                openai_api_key=self.OPENAI_API_KEY,
                model=self.OPENAI_MODEL_NAME,
                temperature=0.0,
                verbose=g.verbose,
            )
        if self.source == "OPENAI":
            llm = OpenAI(
                openai_api_base=self.OPENAI_API_BASE_URL,
                openai_api_key=self.OPENAI_API_KEY,
                model=self.OPENAI_MODEL_NAME,
                temperature=0.0,
                verbose=g.verbose,
            )

            return llm

    
    # def projectname(self,label):       
    #     self.PROJECT_NAME = g.set_project_name(label)
    #     os.environ['PROJECT_NAME'] = self.PROJECT_NAME
    #                 default_llm = OpenAI(
    #         openai_api_base = self.LOCAL_LLAMA_OPENAI_API_BASE_URL,
    #         openai_api_key  = self.LOCAL_LLAMA_OPENAI_API_KEY,
    #         model           = self.LOCAL_LLAMA_OPENAI_MODEL_NAME,
    #         temperature     = 0.8,
    #         verbose         = g.verbose,
    #     )   
    #     return default_llm
