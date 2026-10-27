from langgraph.graph import StateGraph, END, START
from src.agent.state.state import SocraticAgentState
from src.agent.nodes.diagnose_node import DiagnoseNode
from src.agent.nodes.questioner_node import QuestionerNode
from src.agent.nodes.human_input_node import HumanInputNode
from src.agent.nodes.evaluate_node import EvaluationNode
from src.agent.nodes.solution_node import SolutionNode

def decision_router(state: SocraticAgentState) -> str:
    if state.get("is_solved"):
        return "solution"
    if state.get("hint_level", 1) > 3:
        return "solution"
    return "questioner"


class SocraticGraph:
    @staticmethod
    def build_graph():
    # We will assemble nodes and edges here
        graph = StateGraph(SocraticAgentState)

        # add nodes
        graph.add_node("diagnose", DiagnoseNode.diagnose_node)
        graph.add_node("questioner", QuestionerNode.questioner_node)
        graph.add_node("human_input", HumanInputNode.human_input_node)
        graph.add_node("evaluate", EvaluationNode.evaluation_node)
        graph.add_node("solution", SolutionNode.solution_node)

        # edges
        graph.add_edge(START, "diagnose")
        graph.add_edge("diagnose", "questioner")
        graph.add_edge("questioner", "human_input")
        graph.add_edge("human_input", "evaluate")

        graph.add_conditional_edges(
            "evaluate",
            decision_router,
            {
                "solution": "solution",
                "questioner": "questioner",
            }
        )
        graph.add_edge("solution", END)

        return graph.compile()

