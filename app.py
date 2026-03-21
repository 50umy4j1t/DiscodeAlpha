import os

from dotenv import load_dotenv

load_dotenv()

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.ollama import Ollama
from agno.os import AgentOS
from agno.os.interfaces.telegram import Telegram

from tools.html_host import HtmlHostToolkit

SYSTEM_PROMPT = """\
You are Discode, a creative web developer chatbot. Your job is to generate beautiful, \
complete, standalone HTML pages and mini web apps when users ask for them.

When a user asks you to create a page, app, or website:
1. Generate complete HTML with inline CSS and inline JavaScript (no external dependencies).
2. Make the design modern, responsive, and visually appealing.
3. Call the `save_and_host` tool with a descriptive filename and the full HTML content.
4. Share the returned URL with the user so they can view the page. in this format:\n '[view app here](`link here to html`)'

You can also use `list_hosted_pages` to show all previously generated pages.

Always make the HTML self-contained — everything in a single file. Use modern CSS \
(flexbox, grid, gradients, animations) and vanilla JavaScript when needed.\

Always return the link to the user recieved from the tool after creating
"""

agent = Agent(
    name="Discode",
    model=Ollama(id="minimax-m2.7:cloud"),
    debug_mode=True,
    db=SqliteDb(db_file="discode.db"),
    tools=[HtmlHostToolkit()],
    instructions=SYSTEM_PROMPT,
    add_history_to_context=True,
    num_history_runs=3,
    markdown=True,
)

agent_os = AgentOS(
    agents=[agent],
    interfaces=[Telegram(agent=agent)],
)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="app:app", port=7777, reload=True)
