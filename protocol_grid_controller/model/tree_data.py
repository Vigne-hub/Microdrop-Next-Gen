from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import json


# Define the Step model
class ProtocolStep(BaseModel):
    id: str = ""
    name: str
    parameters: Dict[str, Any]


# Define the Group model
class ProtocolGroup(BaseModel):
    group_id: str = ""
    group_name: str

    steps: Optional[List[ProtocolStep]] = Field(default_factory=list)
    sub_groups: Optional[List['ProtocolGroup']] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)

    @property
    def id(self):
        return self.group_id

    @id.setter
    def id(self, value):
        self.group_id = value

        # this group has been added to a super group. update its subgroups, and steps to reflect the new structure
        for sub_group in self.sub_groups:
            sub_group.id = f"{value}.{sub_group.id}"

        for steps in self.steps:
            steps.id = f"{value}.{steps.id}"

    def add_step(self, new_step: ProtocolStep):
        new_step_id = f"step{len(self.steps) + 1}"

        # add the self id to the subgroup id if it exists.
        if self.id:
            new_step.id = f"{self.id}.{new_step_id}"
        else:
            new_step.id = new_step_id

        self.steps.append(new_step)

    def add_sub_group(self, new_subgroup: 'ProtocolGroup'):
        sub_group_id = f"group{len(self.sub_groups) + 1}"

        # add the self id to the subgroup id if it exists.
        if self.id:
            new_subgroup.id = f"{self.id}.{sub_group_id}"
        else:
            new_subgroup.id = sub_group_id

        self.sub_groups.append(new_subgroup)

    def update_step_parameters(self, step_id: str, new_parameters: Dict[str, Any]):
        for step in self.steps:
            if step.id == step_id:
                step.parameters.update(new_parameters)
                return

        for sub_group in self.sub_groups:
            sub_group.update_step_parameters(step_id, new_parameters)

    def get_step(self, step_id: str) -> Optional[ProtocolStep]:
        for step in self.steps:
            if step.id == step_id:
                return step
        for sub_group in self.sub_groups:
            found_step = sub_group.get_step(step_id)
            if found_step:
                return found_step
        return None

    def get_group(self, group_id: str) -> Optional['ProtocolGroup']:
        if self.id == group_id:
            return self
        for sub_group in self.sub_groups:
            found_group = sub_group.get_group(group_id)
            if found_group:
                return found_group
        return None
