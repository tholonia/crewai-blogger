
import sys
sys.path.append("/home/jw/src/crewai/lib")
from colorama import Fore, Back
from crewai_tools import tool, EXASearchTool
from exa_py import Exa
import os
import gvars as g
import dotenv

dotenv.load_dotenv(dotenv_path=g.crew_env_file)
# ╔═════════════════════════════════════════════════════════════
# ║ Exa Search Tools Class
# ╚═════════════════════════════════════════════════════════════

class ExaSearchTool:
    @tool
    def search(query: str):
        """Search for a webpage based on the query."""
        return ExaSearchTool._exa().search(
            f"{query}",
            use_autoprompt=True,
            num_results=3,
            start_published_date=g.from_date,
            end_published_date=g.to_date,
        )

    @tool
    def find_similar(url: str):
        """Search for webpages similar to a given URL.
        The url passed in should be a URL returned from `search`.
        """
        return ExaSearchTool._exa().find_similar(
            url,
            num_results=3,
            start_published_date=g.from_date,
            end_published_date=g.to_date,
        )
    
    @tool
    def search_and_contents(query: str):
        """Search for a webpage and get contents based on the query.""" 
        return ExaSearchTool._exa().search_and_contents(
            query,
            use_autoprompt=True,
            num_results=3,
            start_published_date=g.from_date,
            end_published_date=g.to_date,
        )

    def tools():   
        return [eExaSearchTool.search, ExaSearchTool.find_similar, ExaSearchTool.search_and_contents]  

    def _exa():   
        return Exa(api_key=os.environ["EXA_API_KEY"])

