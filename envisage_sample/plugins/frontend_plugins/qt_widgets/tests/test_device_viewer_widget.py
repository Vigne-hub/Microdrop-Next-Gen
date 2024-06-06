import pytest
import numpy as np
from envisage_sample.plugins.frontend_plugins.qt_widgets import Electrode, Electrodes
from traits.trait_errors import TraitError

correct_path_array = np.array(

    [
        [[29.03221, 74.702264]],
        [[23.051897, 74.702264]],
        [[23.051897, 80.861713]],
        [[29.03221, 80.861713]]
    ]
)


def test_electrode_creation_traits_check_fail():
    try:
        Electrode(channel=1, path=[[1, 1], [2, 2], [3, 3]])
    except Exception as e:
        assert isinstance(e, TraitError)

    try:
        Electrode(channel="1", path=correct_path_array)
    except Exception as e:
        assert isinstance(e, TraitError)


def test_electrode_creation_traits_check_path_pass():
    test_electrode = Electrode(channel=1, path=correct_path_array)

    assert test_electrode.channel == 1 and np.array_equal(test_electrode.path, correct_path_array)


def test_electrodes_creation_traits_check_fail():
    try:
        Electrodes(electrodes={"1": Electrode(channel=1, path=correct_path_array),
                               "2": Electrode(channel=2, path=[[1, 1], [2, 2], [3, 3]])})
    except Exception as e:
        assert isinstance(e, TraitError)

    try:
        Electrodes(electrodes={"1": Electrode(channel=1, path=correct_path_array),
                               "2": Electrode(channel="2", path=correct_path_array)})
    except Exception as e:
        assert isinstance(e, TraitError)


def test_electrodes_creation_traits_check_pass():
    electrodes = Electrodes(electrodes={"1": Electrode(channel=1, path=correct_path_array),
                                        "2": Electrode(channel=2, path=correct_path_array)})
    assert isinstance(electrodes.electrodes, dict) and len(electrodes.electrodes) == 2


if __name__ == "__main__":
    pytest.main(['-vv', '-s', __file__])
