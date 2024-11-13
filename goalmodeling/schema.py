"""
Generating refinement graphs in goal modeling to see in Mermaid.
Author(s): ateeq@cmu.edu

2024-09-02: Minor cleanup; AS
2024-08-03: Initial version; AS.
"""
from enum import IntEnum

NODE_COUNT = 0


def _get_new_node_id():
    """
    Used internally to generate a unique id for a new node in the graph.
    :return int: Returns a new node id.
    """
    global NODE_COUNT
    current_val = NODE_COUNT
    NODE_COUNT += 1
    return current_val


class VertexType(IntEnum):
    """
    The different types of vertices that may exist in a refinement graph.
    """
    NODE_TYPE_GOAL = 0
    NODE_TYPE_REFINEMENT = 1
    NODE_TYPE_OBSTACLE = 2
    NODE_TYPE_AGENT = 3
    NODE_TYPE_OPERATION = 4
    NODE_TYPE_DOMAIN_PROPERTY = 5


class EdgeType(IntEnum):
    """
    The different types of edges that may exist in a refinement graph.
    """
    REFINEMENT = 0
    RESPONSIBILITY = 1
    PERFORMANCE = 2
    CONFLICT = 3
    OBSTRUCTION = 4
    RESOLUTION = 5


class AgentType(IntEnum):
    """
    The different types of agents that may exist in a refinement graph.
    """
    ENVIRONMENT_AGENT = 0
    SOFTWARE_AGENT = 1


class OperationCategory(IntEnum):
    """
    An operation may either be an environment operation or a software-to-be operation.
    """
    ENVIRONMENT_OPERATION = 0
    SOFTWARE_TO_BE_OPERATION = 1


class GoalType(IntEnum):
    """
    The different types of supported goals.
    """
    BEHAVIORAL_GOAL = 0
    SOFT_GOAL = 1


class RefinementType(IntEnum):
    """
    Supported refinements.
    """
    AND_REFINEMENT = 0
    OR_REFINEMENT = 1


class BehavioralGoalType(IntEnum):
    """
    The types of behavioral goals.
    """
    ACHIEVE_GOAL = 0
    MAINTAIN_GOAL = 1


class SoftGoalType(IntEnum):
    """
    Types of soft goals, which cannot be satisfied but satisficed.
    """
    IMPROVE = 0
    INCREASE = 1
    MAXIMIZE = 2
    REDUCE = 3
    MINIMIZE = 4


class GoalCategory(IntEnum):
    """
    Categories a goal may belong.
    """
    SATISFACTION = 0
    INFORMATION = 1
    STIMULUS_RESPONSE = 2
    ACCURACY = 3
    QOS_SAFETY = 4
    QOS_SECURITY_CONFIDENTIALITY = 5
    QOS_SECURITY_INTEGRITY = 6
    QOS_SECURITY_AVAILABILITY = 7
    QOS_PERFORMANCE_TIME = 8
    QOS_PERFORMANCE_SPACE = 9
    # many more


class Vertex:
    """
    The base class for vertices in a refinement graph.
    """
    def __init__(self, vertex_type: VertexType, leaf=False, annotation: str = ""):
        self.vertex_type = vertex_type
        self.node_id = _get_new_node_id()
        self.leaf = leaf
        self.annotation = annotation

    def get_node_id(self):
        """
        Get the node id as a string.

        :return str: The node id prefixed with "node"
        """
        return f"node{self.node_id}"

    def to_tree(self):
        if self.annotation:
            return (f'annotation{self.get_node_id()}["{self.annotation}"]:::stroke'
                    f' -.- {self.get_node_id()}\n')
        return ""

    def to_string(self):
        pass


class Edge:
    """
    The base class for edges in a refinement graph.
    """
    def __init__(self, edge_type: EdgeType):
        self.edge_type = edge_type

    def to_string(self):
        return ""


class Operation(Vertex):
    """
    An operation that an agent performs resulting in satisfying or satisficing a goal.
    """
    def __init__(self, name: str, category: OperationCategory, annotation: str = ""):
        """
        Initialize the operation.
        :param str name: The name of the operation.
        :param OperationCategory category: The category of the operation.
        :param str annotation: An optional annotation.
        """
        super().__init__(VertexType.NODE_TYPE_OPERATION, annotation=annotation)
        self.name = name
        self.category = category

    def to_string(self):
        return f'{self.get_node_id()}(["{self.name}"])'


class Agent(Vertex):
    """
    An agent that contributes to the satisfaction or satisficing of a goal.
    """
    def __init__(
            self,
            name: str,
            agent_type: AgentType,
            annotation: str = ""):
        """
        Initialize the agent.
        :param str name: The name of the agent.
        :param AgentType agent_type: The type of the agent.
        :param str annotation: An optional annotation.
        """
        super().__init__(VertexType.NODE_TYPE_AGENT, annotation=annotation)
        self.name = name
        self.type = agent_type

    def to_string(self):
        """
        Return the agent represented as a person icon in Mermaid.
        :return str: The Mermaid js diagram definition for the agent returned as a hexagon.
        """
        figure = "fa:fa-person " if self.type == AgentType.ENVIRONMENT_AGENT else ""
        return f'{self.get_node_id()}' + "{{" + f'{figure}{self.name}' + "}}"


class PerformanceLink(Edge):
    def __init__(self, agent: Agent, operation: Operation or None):
        super().__init__(EdgeType.PERFORMANCE)
        self.agent = agent
        self.operation = operation


class Refinement(Vertex):
    """
    Represents a refinement of a goal or an obstacle.
    """
    def __init__(self,
                 complete: bool,
                 children: list[Vertex],
                 annotation: str = ""):
        """
        Initialize a refinement.
        :param bool complete: True if complete refinement, False otherwise.
        :param list[Vertex] children: The children of the refinement.
        :param str annotation: An optional annotation.
        """
        super().__init__(VertexType.NODE_TYPE_REFINEMENT, annotation=annotation)
        self.refinement_type = RefinementType.AND_REFINEMENT
        self.complete = complete
        self.children = children


class DomainProperty(Vertex):
    """
    Represents a domain property.
    """
    def __init__(self,
                 name: str,
                 leaf: bool = False,
                 annotation: str = ""):
        """
        Initialize the domain property.
        :param str name: The name of the domain property. Can be in markdown.
        :param bool leaf: Use True if you want to bold the trapezoid in the graph, False otherwise.
        :param str annotation: An optional annotation.
        """
        super().__init__(VertexType.NODE_TYPE_DOMAIN_PROPERTY, leaf, annotation)
        self.name = name

    def to_string(self):
        """
        Return the domain property represented as a trapezoid in Mermaid.
        :return str: The Mermaid js diagram definition for the domain property as a trapezoid.
        """
        return f'{self.get_node_id()}[/"{self.name}"\\]'


class Goal(Vertex):
    """
    The base goal, which is to be extended.
    """
    def __init__(self,
                 name: str,
                 goal_type: GoalType,
                 performs: list[PerformanceLink] or None = None,
                 refinements: list[Refinement] or None = None,
                 leaf: bool = False,
                 annotation: str = ""):
        super().__init__(VertexType.NODE_TYPE_GOAL, leaf, annotation)
        self.name = name
        self.goal_type = goal_type
        self.performs = performs if performs else []
        self.disjunctions = refinements if refinements else []

    def to_string(self):
        """
        Return the goal represented as a right-leaning parallelogram in Mermaid.
        :return str: The Mermaid js diagram definition for the goal.
        """
        return f'{self.get_node_id()}[/"{self.name}"/]'  # [/"name"/]

    def to_tree(self):
        """
        Generate the Mermaid js diagram definition for the refinement graph with this goal as root.
        :return str: The Mermaid diagram definition.
        """
        node_diagram = self.to_string()
        result = super().to_tree()

        if len(self.disjunctions) == 0 and len(self.performs) == 0:
            return result + "\n"

        for disjunction in self.disjunctions:
            current_disjunction = disjunction.get_node_id()
            current_disjunction_diagram = f'{current_disjunction}((" "))'
            filled = ":::filled" if disjunction.complete else ""
            result += disjunction.to_tree()

            if disjunction.children[0].vertex_type == VertexType.NODE_TYPE_OBSTACLE:
                arrowhead = "x"
            else:
                arrowhead = ">"

            link_to_parent = f"{current_disjunction_diagram}{filled} ==={arrowhead} {self.get_node_id()}"
            result += link_to_parent

            result += "\n"

            for child in disjunction.children:
                child_diagram = child.to_string()
                bold = ":::bold" if child.leaf else ""
                link_to_refinement = f'{child_diagram}{bold} --- {current_disjunction}'
                result += link_to_refinement
                result += "\n"

                result += child.to_tree()

            result += "\n"

        for perform in self.performs:
            agent_link = f'{perform.agent.to_string()} --- {self.get_node_id()}'
            result += agent_link
            result += "\n"

            if perform.operation:
                perform_link = f'{perform.operation.to_string()} --- {perform.agent.get_node_id()}'
                result += perform_link
                result += "\n"
                result += perform.agent.to_tree()

        result += node_diagram + "\n"

        return result


class Obstacle(Vertex):
    """
    An obstacle that prevents the satisfaction of a goal.
    """
    def __init__(self,
                 name: str,
                 refinements: list[Refinement] or None = None,
                 annotation: str = ""):
        """
        Initialize the obstacle.
        :param str name: The name of the obstacle.
        :param list[Refinement] refinements: The refinements of the obstacle.
        :param str annotation: An optional annotation.
        """
        super().__init__(VertexType.NODE_TYPE_OBSTACLE, False, annotation)
        self.name = name
        self.refinements = refinements if refinements else []

    def to_string(self):
        """
        Return the obstacle represented as a left-leaning parallelogram in Mermaid.
        :return str: The Mermaid js diagram definition for the obstacle.
        """
        return f'{self.get_node_id()}[\\"{self.name}"\\]'

    def to_tree(self):
        """
        Generate the Mermaid js diagram definition for the refinement graph with this obstacle as root.
        :return str: The Mermaid diagram definition.
        """
        node_diagram = self.to_string()
        result = super().to_tree()

        for disjunction in self.refinements:
            current_disjunction = disjunction.get_node_id()
            current_disjunction_diagram = f'{current_disjunction}((" "))'
            filled = ":::filled" if disjunction.complete else ""
            link_to_parent = f"{current_disjunction_diagram}{filled} ===> {node_diagram}"
            result += link_to_parent

            result += "\n"

            for child in disjunction.children:
                child_diagram = child.to_string()
                bold = ":::bold" if child.leaf else ""
                link_to_refinement = f'{child_diagram}{bold} --- {current_disjunction}'
                result += link_to_refinement
                result += "\n"

                result += child.to_tree()

            result += "\n"

        return result


class ConflictLink(Edge):
    """
    Represents a conflict link between two goals.
    """
    def __init__(self, goal1: Goal, goal2: Goal):
        """
        Initialize the conflict link.
        :param Goal goal1: The first goal.
        :param Goal goal2: The second goal.
        """
        super().__init__(EdgeType.CONFLICT)
        self.goal1 = goal1
        self.goal2 = goal2

    def to_string(self):
        """
        Return the conflict link represented as a dashed line with a lightning in Mermaid.
        """
        return (f'{self.goal1.get_node_id()} --"#128498;"--- {self.goal2.get_node_id()}\n'
                f'{self.goal2.to_string()}\n'
                f'{self.goal1.to_string()}\n')


class ObstructionLink(Edge):
    """
    Represent an obstruction link between an obstacle and a goal.
    """
    def __init__(self, goal: Goal, obstacle: Obstacle):
        """
        Initialize the obstruction link.
        :param Goal goal: The goal.
        :param Obstacle obstacle: The obstacle.
        """
        super().__init__(EdgeType.OBSTRUCTION)
        self.goal = goal
        self.obstacle = obstacle

    def to_string(self):
        """
        Return the obstruction link represented as a dashed line with a cross in Mermaid.
        """
        return f'{self.obstacle.get_node_id()} ---x {self.goal.get_node_id()}\n{self.obstacle.to_string()}\n'


class ResolutionLink(Edge):
    """
    To represent a resolution to an obstacle.
    """
    def __init__(self, goal: Goal, obstacle: Obstacle):
        """
        Initialize the resolution link.
        :param Goal goal: The goal.
        :param Obstacle obstacle: The obstacle.
        """
        super().__init__(EdgeType.RESOLUTION)
        self.goal = goal
        self.obstacle = obstacle

    def to_string(self):
        """
        Return the resolution link represented as a dashed line with a cross in Mermaid.
        """
        return (f'{self.goal.get_node_id()} ---x {self.obstacle.get_node_id()}\n'
                f'{self.goal.to_string()}\n'
                f'{self.obstacle.to_string()}\n')


class BehavioralGoal(Goal):
    """
    To represent a behavioral goal.
    """
    def __init__(self,
                 name: str,
                 performs: list[PerformanceLink] or None = None,
                 refinements: list[Refinement] or None = None,
                 leaf: bool = False,
                 annotation: str = ""):
        super().__init__(name, GoalType.BEHAVIORAL_GOAL, performs, refinements, leaf, annotation)


class AchieveGoal(BehavioralGoal):
    """
    To represent an achievement goal.
    """
    def __init__(self,
                 name: str,
                 performs: list[PerformanceLink] or None = None,
                 refinements: list[Refinement] or None = None,
                 leaf: bool = False,
                 annotation: str = ""):
        """
        Initialize the achievement goal.
        :param str name: The name of the goal.
        :param list[PerformanceLink] performs: The performances that satisfy the goal.
        :param list[Refinement] refinements: A list of refinements of the goal.
        :param bool leaf: True will result the goal's border being bold in the graph.
        :param str annotation: An optional annotation.
        """
        super().__init__(name, performs, refinements, leaf, annotation)
        self.goal_type = AchieveGoal

    def to_string(self):
        """
        Return the achievement goal represented as a right-leaning parallelogram in Mermaid.
        """
        return f'{self.get_node_id()}[/"Achieve[{self.name}]"/]'  # [/Achieve[name]/]


class CeaseGoal(AchieveGoal):
    """
    The dual of an achievement goal.
    """
    def __init__(self,
                 name: str,
                 performs: list[PerformanceLink] or None = None,
                 refinements: list[Refinement] or None = None,
                 leaf: bool = False,
                 annotation: str = ""):
        """
        Initialize the cease goal.
        :param str name: The name of the goal.
        :param list[PerformanceLink] performs: The performances that satisfy the goal.
        :param list[Refinement] refinements: A list of refinements of the goal.
        :param bool leaf: True will result the goal's border being bold in the graph.
        :param str annotation: An optional annotation.
        """
        super().__init__(name, performs, refinements, leaf, annotation)
        self.goal_type = CeaseGoal

    def to_string(self):
        """
        Return the cease goal represented as a right-leaning parallelogram in Mermaid.
        """
        return f'{self.get_node_id()}[/"Cease[{self.name}]"/]'  # [/Cease[name]/]


class MaintainGoal(BehavioralGoal):
    """
    To represent a maintenance goal.
    """
    def __init__(self,
                 name: str,
                 performs: list[PerformanceLink] or None = None,
                 refinements: list[Refinement] or None = None,
                 leaf: bool = False,
                 annotation: str = ""):
        """
        Initialize the maintenance goal.
        :param str name: The name of the goal.
        :param list[PerformanceLink] performs: The performances that satisfy the goal.
        :param list[Refinement] refinements: A list of refinements of the goal.
        :param bool leaf: True will result the goal's border being bold in the graph.
        :param str annotation: An optional annotation.
        """
        super().__init__(name, performs, refinements, leaf, annotation)
        self.goal_type = MaintainGoal

    def to_string(self):
        """
        Return the maintenance goal represented as a right-leaning parallelogram in Mermaid.
        """
        return f'{self.get_node_id()}[/"Maintain[{self.name}]"/]'  # [/Maintain[name]/]


class AvoidGoal(MaintainGoal):
    """
    The dual of a maintenance goal.
    """
    def __init__(self,
                 name: str,
                 performs: list[PerformanceLink] or None = None,
                 refinements: list[Refinement] or None = None,
                 leaf: bool = False,
                 annotation: str = ""):
        """
        Initialize the avoid goal.
        :param str name: The name of the goal.
        :param list[PerformanceLink] performs: The performances that satisfy the goal.
        :param list[Refinement] refinements: A list of refinements of the goal.
        :param bool leaf: True will result the goal's border being bold in the graph.
        :param str annotation: An optional annotation.
        """
        super().__init__(name, performs, refinements, leaf, annotation)
        self.goal_type = AvoidGoal

    def to_string(self):
        """
        Return the avoid goal represented as a right-leaning parallelogram in Mermaid.
        """
        return f'{self.get_node_id()}[/"Avoid[{self.name}]"/]'  # [/Avoid[name]/]


class SoftGoal(Goal):
    """
    To represent a soft goal.
    """
    def __init__(self,
                 name: str,
                 performs: list[PerformanceLink] or None = None,
                 refinements: list[Refinement] or None = None,
                 leaf: bool = False,
                 annotation: str = ""):
        """
        Initialize the soft goal.
        :param str name: The name of the goal.
        :param list[PerformanceLink] performs: The performances that satisfy the goal.
        :param list[Refinement] refinements: A list of refinements of the goal.
        :param bool leaf: True will result the goal's border being bold in the graph.
        :param str annotation: An optional annotation.
        """
        super().__init__(name, GoalType.SOFT_GOAL, performs, refinements, leaf, annotation)


def diagram_startup():
    """
    Generate the Mermaid js diagram definition for the start of the diagram.
    :return str: Returns the flowchart bottom-to-top statement.
    """
    return "flowchart BT\n"


def diagram_teardown():
    """
    Generate the Mermaid js diagram definition for the end of the diagram.
    :return str: Returns the class definitions used in the graph.
    """
    return """
classDef bold stroke-width:3,stroke:#000
classDef filled fill:#000;
classDef nostroke stroke-width:0,fill-opacity:0.0
classDef stroke stroke-dasharray: 5 5,fill-opacity:0.0,text-align:left\n
    """


def generate_pako_link(
        text: str,
        mode: str = "view",
        host: str = "https://mermaid.live",
        config: dict = {"theme": "neutral"}):
    """
    Generate a Mermaid pako link for the given graph represented as text.
    :param str text:
    :param str mode: "view" or "edit"
    :param str host: The host to use for the pako link, default is mermaid.js       live
    :param dict config: Additional configuration. The field theme can be
     "default", "neutral", "forest", "dark", etc.
    The default is neutral and may be best for refinement graphs.
    :return str: pako link
    """
    import base64
    import json
    import zlib

    graph = {"code": text, "mermaid": config}
    output = json.dumps(graph)
    compress = zlib.compressobj(9, zlib.DEFLATED, 15, 8, zlib.Z_DEFAULT_STRATEGY)
    compressed = compress.compress(output.encode('utf-8')) + compress.flush()
    pako = base64.b64encode(compressed, b"-_").decode("utf-8")
    url = f"{host}/{mode}#pako:{pako}"
    return url


def generate_graph(goals: list[Goal], links: list[ObstructionLink or ConflictLink] = None):
    """
    Generate a Mermaid js diagram for the given goals and obstructions.
    :param list[Goal] goals: The goals in the graph.
    :param list[ObstructionLink or ConflictLink] links: The conflicts and obstructions in the graph.
    """
    output = diagram_startup()

    for goal in goals:
        output += goal.to_tree()

    if links is None:
        links = []

    for link in links:
        output += link.to_string()
        output += "\n"

    output += diagram_teardown()

    return output


if __name__ == "__main__":
    pass
    # print(gen_pako_link("flowchart TD\n[A]"))

    # obstacles()
    # conflicts()
    # actors()
    # achievement()
