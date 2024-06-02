import tempfile
import shutil
import pytest
from pathlib import Path
from xml.etree import ElementTree as ET
from ..utils.dmf_utils import SvgUtil


@pytest.fixture
def clean_svg():
    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copy('2x3device.svg', tmpdir)
        yield Path(tmpdir) / '2x3device.svg'


@pytest.fixture
def svg_root(clean_svg):
    tree = ET.parse(clean_svg)
    return tree.getroot()


@pytest.fixture
def svg_shape(svg_root):
    return svg_root[4][0]


@pytest.fixture
def svg_electrode_layer(svg_root):
    return svg_root[4]


def test_svg_util(clean_svg):
    SvgUtil(clean_svg)


def test_filename(clean_svg):
    svg = SvgUtil()
    svg.filename = clean_svg
    assert svg.filename == clean_svg


def test_set_fill_black(svg_electrode_layer):
    SvgUtil.set_fill_black(svg_electrode_layer)
    assert svg_electrode_layer[0].attrib['style'] == 'fill:#000000'


def test_svg_to_electrodes(svg_electrode_layer):
    svg = SvgUtil()
    assert len(svg.svg_to_electrodes(svg_electrode_layer)) == 92
