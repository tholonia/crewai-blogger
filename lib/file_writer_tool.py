from crewai_tools import BaseTool
import gvars as g
# ╔═════════════════════════════════════════════════════════════
# ║ FileWriter
# ╚═════════════════════════════════════════════════════════════


class FileWriterTool(BaseTool):
    name: str = "FileWriter"
    description: str = "Writes given content to a specified file."
    
    # @trace
    def _run(self, filename: str, content: str) -> str:
        
        # Open the specified file in write mode and write the content
        filename = f"k-{filename}-{g.counter}"
        g.counter += 1
       
        
        # see 'traceback' below for the call stack at this point in the code
        
        with open(filename, 'a') as file:
            file.write(content)
        return f"Content successfully written to {filename}"
