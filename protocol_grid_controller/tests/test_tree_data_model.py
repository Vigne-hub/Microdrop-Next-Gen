import json
import pytest
from .common import VALID_OUTPUTS

from protocol_grid_controller.model.tree_data import ProtocolGroup, ProtocolStep


@pytest.fixture
def protocol_tree():
    root = ProtocolGroup(group_id="root", group_name="Root Group")
    step1 = ProtocolStep(name="Step1", parameters={"param1": "value1"})
    root.add_step(step1)

    # Level 1
    sub_group = ProtocolGroup(group_name="Level 1")
    step2 = ProtocolStep(name="Step2", parameters={"param2": "value2"})
    sub_group.add_step(step2)
    root.add_sub_group(sub_group)

    # Level 2
    sub_sub_group = ProtocolGroup(group_name="Level 2")
    step3 = ProtocolStep(name="Step3", parameters={"param3": "value3"})
    sub_group.add_sub_group(sub_sub_group)
    sub_sub_group.add_step(step3)

    # Additional steps
    new_step1 = ProtocolStep(name="newStep1", parameters={"newparam2": "value2", "newparam3": "value3"})
    root.add_step(new_step1)

    new_step2 = ProtocolStep(name="NewStep2", parameters={"Newparam2": "Newvalue2"})
    sub_group.add_step(new_step2)

    new_step3 = ProtocolStep(name="NewStep3", parameters={"Newparam3": "Newvalue3"})
    root.get_group(group_id="root.group1.group1").add_step(new_step3)

    # Parallel subgroup
    level2_group2 = ProtocolGroup(group_name="Level 2, group 2")
    level2_group2.add_step(step1.model_copy(update={"name": step1.name + "_copy"}))
    level2_group2.add_step(new_step1.model_copy(update={"name": new_step1.name + "_copy"}))
    root.get_group(group_id="root.group1").add_sub_group(level2_group2)

    return root


def test_json_serialization_matches_snapshot(protocol_tree):
    json_model = protocol_tree.model_dump_json(indent=4)
    with open(VALID_OUTPUTS / "tree_data_save.json") as f:
        expected = json.load(f)
    actual = json.loads(json_model)
    assert actual == expected


if __name__ == "__main__":
    pytest.main([__file__])
