from typing import TypedDict

from llm import get_llm
from langgraph.graph import StateGraph, END

from agent.tools import (
    search_pdf,
    calculate,
    web_search,
)


class AgentState(TypedDict):
    question: str
    source: str
    tool: str
    result: str
    answer: str
    sources: list[int]


def choose_tool(state: AgentState):
    question = state["question"]
    source = state["source"]

    if source == "PDF":
        return {"tool": "PDF"}

    if source == "WEB":
        return {"tool": "WEB"}

    llm = get_llm()

    prompt = f"""
You are a routing classifier for EduPilot,
an AI study assistant with an uploaded PDF document.

Choose exactly ONE routing label.

ROUTE_PDF
- Use this when the question can be answered from
  the uploaded PDF.
- Use this for questions about the document.
- Use this for general academic concepts, definitions,
  explanations, summaries, or topics that could
  reasonably be answered from the document.
- When uncertain, choose ROUTE_PDF.

ROUTE_CALCULATOR
- Use this only when the user asks you to perform
  a mathematical calculation.

ROUTE_WEB
- Use this only when the question explicitly requires
  current, external, or web-based information.

Important:
The uploaded PDF should be preferred whenever the
question can reasonably be answered from it.
Do not choose ROUTE_WEB merely because the question
is general or because you do not know the PDF contents.

Student question:

{question}

Return ONLY one of these labels:

ROUTE_PDF
ROUTE_CALCULATOR
ROUTE_WEB
"""

    response = llm.invoke(prompt)
    route = response.content.strip().upper()

    route_map = {
        "ROUTE_PDF": "PDF",
        "ROUTE_CALCULATOR": "CALCULATOR",
        "ROUTE_WEB": "WEB",
    }

    return {"tool": route_map.get(route, "PDF")}
def create_graph(vector_store):

    def pdf_node(state: AgentState):
        result = search_pdf(vector_store, state["question"])

        return {
            "result": result["context"],
            "sources": result["sources"],
        }

    def calculator_node(state: AgentState):
        llm = get_llm()

        prompt = f"""
Convert the following mathematical question
into ONLY a valid mathematical expression
that numexpr can evaluate.

Question:

{state["question"]}

Examples:

"What is 25% of 480?"
→ 25 / 100 * 480

"Calculate 15 * 12 + 30"
→ 15 * 12 + 30

"What is 120 divided by 8?"
→ 120 / 8

Return ONLY the expression.

Do not include explanation.
"""

        response = llm.invoke(prompt)
        expression = response.content.strip()
        result = calculate(expression)

        return {
            "result": result,
            "sources": [],
        }

    def web_node(state: AgentState):
        result = web_search(state["question"])

        return {
            "result": result,
            "sources": [],
        }

    def route_tool(state: AgentState):
        return state["tool"]

    def final_answer(state: AgentState):
        llm = get_llm()

        prompt = f"""
You are EduPilot, an AI study assistant.

Answer the student's question using the tool result below.

Student question:

{state["question"]}

Tool used:

{state["tool"]}

Tool result:

{state["result"]}

Instructions:

- Give a clear, concise, student-friendly answer.
- Use simple Markdown.
- Do NOT use HTML tags such as <br>.
- Do NOT use LaTeX delimiters such as \\( \\), \\[ \\], or \\displaystyle.
- Write mathematical formulas in plain text.
  Example: Y = beta0 + beta1 X + epsilon
- Avoid complex Markdown tables.
- Prefer short headings and bullet points.
- For PDF questions, use ONLY the provided document information.
- For calculations, clearly state the numerical result.
- For web questions, summarize the useful information.
- Do not invent information.

Return only the final answer.
"""

        response = llm.invoke(prompt)

        return {
            "answer": response.content,
        }

    graph = StateGraph(AgentState)

    graph.add_node("choose_tool", choose_tool)
    graph.add_node("pdf", pdf_node)
    graph.add_node("calculator", calculator_node)
    graph.add_node("web", web_node)
    graph.add_node("final_answer", final_answer)

    graph.set_entry_point("choose_tool")

    graph.add_conditional_edges(
        "choose_tool",
        route_tool,
        {
            "PDF": "pdf",
            "CALCULATOR": "calculator",
            "WEB": "web",
        },
    )

    graph.add_edge("pdf", "final_answer")
    graph.add_edge("calculator", "final_answer")
    graph.add_edge("web", "final_answer")

    graph.add_edge("final_answer", END)

    return graph.compile()