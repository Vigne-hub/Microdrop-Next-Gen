import pytest

from envisage_sample.widgets.device_viewer_widget.electrodes_model import Electrode, Electrodes

def test_electrode():
    electrode = Electrode(channel=1, path=[[1, 1], [2, 2], [3, 3]])
    assert electrode.channel == 1
    assert electrode.path == [[1, 1], [2, 2], [3, 3]]
    assert electrode.state == False
    assert electrode.metastate == None

    electrode.state = True
    assert electrode.state == True

    electrode.metastate = 'droplet'
    assert electrode.metastate == 'droplet'

if __name__ == "__main__":
    pytest.main(['-vv', '-s', __file__])