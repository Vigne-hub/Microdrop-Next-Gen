from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import pygraphviz as pgv
import json


# Define the Step model
class Step(BaseModel):
    id: str = ""
    name: str
    parameters: Dict[str, Any]


# Define the Group model
class Group(BaseModel):
    id: str = ""
    name: str
    steps: Optional[List[Step]] = Field(default_factory=list)
    sub_groups: Optional[List['Group']] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)

    @staticmethod
    def generate_step_id(parent_id: str, index: int) -> str:
        return f"{parent_id}.{index}"

    def add_step(self, step: Step):
        step.id = f"{self.id}.{len(self.steps) + 1}"
        self.steps.append(step)

    def add_sub_group(self, group: 'Group'):
        group.id = f"{self.id}.group"
        self.sub_groups.append(group)

    def update_step_parameters(self, step_id: str, new_parameters: Dict[str, Any]):
        for step in self.steps:
            if step.id == step_id:
                step.parameters.update(new_parameters)
                return

        for sub_group in self.sub_groups:
            sub_group.update_step_parameters(step_id, new_parameters)

    def find_step(self, step_id: str) -> Optional[Step]:
        for step in self.steps:
            if step.id == step_id:
                return step
        for sub_group in self.sub_groups:
            found_step = sub_group.find_step(step_id)
            if found_step:
                return found_step
        return None

    def find_group(self, group_id: str) -> Optional['Group']:
        if self.id == group_id:
            return self
        for sub_group in self.sub_groups:
            found_group = sub_group.find_group(group_id)
            if found_group:
                return found_group
        return None

    def visualize(self, file_name="tree_data.png") -> pgv.AGraph:
        G = pgv.AGraph(directed=True)
        G.add_node(self.id)

        def add_nodes_edges(graph, parent):

            # first create nodes for the root layer:
            for step in parent.steps:
                step_label = f"{step.name}\nParameters: {json.dumps(step.parameters, indent=2)}"
                graph.add_node(step.id, label=step_label)
                graph.add_edge(parent.id, step.id)

            # next repeat the same for each subgroup and recursively within them
            for idx, sub_group in enumerate(parent.sub_groups):
                group_label = sub_group.name
                graph.add_node(sub_group.id, label=group_label)
                graph.add_edge(parent.id, sub_group.id)
                add_nodes_edges(graph, sub_group)

        add_nodes_edges(G, self)
        G.layout()
        G.draw(file_name, prog="dot")
        return G


def serialize_group(group: Group) -> str:
    return group.json()


def deserialize_group(json_data: str) -> Group:
    return Group.parse_raw(json_data)


if __name__ == "__main__":
    # Create initial group structure
    step1 = Step(name="Step1", parameters={"param1": "value1"})
    group = Group(id="root", name="Group1")
    group.add_step(step1)

    sub_group = Group(name="SubGroup1")
    group.add_sub_group(sub_group)

    step2 = Step(name="Step2", parameters={"param2": "value2"})
    sub_group.add_step(step2)

    sub_sub_group = Group(name="SubSubGroup1")
    sub_group.add_sub_group(sub_sub_group)

    step3 = Step(name="Step3", parameters={"param3": "value3"})
    sub_sub_group.add_step(step3)

    step1 = Step(name="newStep1", parameters={"newparam2": "value2", "newparam3": "value3"})
    group.add_step(step1)

    step2 = Step(name="NewStep2", parameters={"Newparam2": "Newvalue2"})
    sub_group.add_step(step2)

    step3 = Step(name="NewStep3", parameters={"Newparam3": "Newvalue3"})
    group.find_group(group_id="root.group.group").add_step(step3)

    group.visualize()
