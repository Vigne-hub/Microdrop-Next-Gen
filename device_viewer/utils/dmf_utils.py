# -*- coding: utf-8 -*-
import re
import numpy as np
import xml.etree.ElementTree as ET

from pathlib import Path
from typing import Union, TypedDict
from shapely.geometry import Polygon
from nptyping import NDArray, Float, Shape


class ElectrodeDict(TypedDict):
    channel: int
    path: NDArray[Shape['*, 1, 1'], Float]


class SvgUtil:
    float_pattern = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
    path_commands = re.compile(r"(?P<move_command>[ML])\s+(?P<x>{0}),\s*(?P<y>{0})\s*|"
                               r"(?P<x_command>[H])\s+(?P<hx>{0})\s*|"
                               r"(?P<y_command>[V])\s+(?P<vy>{0})\s*|"
                               r"(?P<command>[Z])"
                               .format(float_pattern))
    style_pattern = re.compile(r"fill:#[0-9a-fA-F]{6}")

    def __init__(self, filename: Union[str, Path] = None):
        self._filename = filename
        self.max_x = None
        self.max_y = None
        self.min_x = None
        self.min_y = None
        self.multi_x = None
        self.multi_y = None
        self.x_shift = None
        self.y_shift = None
        self.neighbours: dict[str, list[str]] = {}
        self.roi: list[NDArray[Shape['*, 1, 1'], Float]] = []
        self.electrodes: dict[str, ElectrodeDict] = {}
        self.connections: list[NDArray[Shape['*, 1, 1'], Float]] = []

        if self._filename:
            self.get_device_paths(self._filename)

    @property
    def filename(self) -> Union[str, Path]:
        return self._filename

    @filename.setter
    def filename(self, filename: Union[str, Path]):
        self._filename = filename
        self.get_device_paths(self._filename)

    def get_device_paths(self, filename, modify=True):
        tree = ET.parse(filename)
        root = tree.getroot()

        for child in root:
            if "Device" in child.attrib.values():
                self.set_fill_black(child)
                self.electrodes = self.svg_to_electrodes(child)
            elif "ROI" in child.attrib.values():
                self.roi = self.svg_to_paths(child)
            elif "Connections" in child.attrib.values():
                pass
                # self.connections = self.svg_to_points(child)

        if len(self.connections) == 0 and len(self.electrodes) > 0:
            self.neighbours = self.find_neighbours_all()
            self.neighbours_to_points()

        if modify:
            tree.write(filename)

    def get_electrode_center(self, electrode: str) -> NDArray[Shape['*, 1, 1'], Float]:
        """
        Get the center of an electrode
        """
        return np.mean(self.electrodes[electrode]['path'], axis=0)

    def find_neighbours(self, path: NDArray[Shape['*, 1, 1'], Float], threshold: float = 10) -> list[str]:
        """
        Find the neighbours of a path
        """
        neighbours = []
        for k, v in self.electrodes.items():
            if np.linalg.norm(path[0, 0] - v['path'][0, 0]) < threshold:
                neighbours.append(k)
        return neighbours

    def get_electrode_polygons(self) -> dict[str, Polygon]:
        """
        Get the polygons of the electrodes
        """
        return {k: Polygon(v['path'].reshape(-1, 2)) for k, v in self.electrodes.items()}

    def find_neighbours_all(self, threshold: [float, None] = None) -> dict[str, list[str]]:
        """
        Find the neighbours of all paths
        """
        # if threshold is None then try to calculate it by finding the closest two electrodes centers
        if threshold is None:
            # Dilate the polygons
            polygons = self.get_electrode_polygons()
            distances = sorted([v1.buffer(-0.1).distance(v2.buffer(-0.1)) for k1, v1 in polygons.items()
                                for k2, v2 in polygons.items() if k1 != k2])
            average_distance = np.mean(distances[:len(self.electrodes)])

            # Dilate the polygons by the average distance
            polygons = {k: v.buffer(average_distance) for k, v in polygons.items()}

            # Find the intersecting polygons
            neighbours = {}
            for k1, v1 in polygons.items():
                for k2, v2 in polygons.items():
                    if k1 != k2:
                        intersection = v1.intersection(v2)
                        if intersection.area >= average_distance:
                            neighbours.setdefault(k1, []).append(k2)
        else:
            neighbours = {}
            for k, v in self.electrodes.items():
                neighbours[k] = self.find_neighbours(v['path'], threshold)
                # remove self from neighbours
                neighbours[k].remove(k)
        return neighbours

    def neighbours_to_points(self):
        # Scan the neighbours and create a list of unique connections
        self.connections = []
        connected = []
        for k, v in self.neighbours.items():
            for n in v:
                if (n, k) not in connected and (k, n) not in connected:
                    connected.append((k, n))
                    points = [self.get_electrode_center(k), self.get_electrode_center(n)]
                    self.connections.append(np.array(points).reshape((-1, 1, 2)))

    @staticmethod
    def set_fill_black(obj: ET.Element) -> None:
        """
        Sets the fill of the svg paths to black in place
        :param obj: The svg element
        """
        for element in obj:
            try:
                element.attrib['style'] = re.sub(SvgUtil.style_pattern, r"fill:#000000", element.attrib['style'])
            except KeyError:
                pass

    def svg_to_points(self, obj) -> list[NDArray[Shape['*, 1, 1'], Float]]:
        """
        Converts the svg file to points
        """

        paths = []
        for path in obj:
            points = [(path.attrib["x1"], path.attrib["y1"]),
                      (path.attrib["x2"], path.attrib["y2"])]

            paths.append(np.array(points).reshape((-1, 1, 2)).astype(float))

        return paths

    def svg_to_paths(self, obj) -> list[NDArray[Shape['*, 1, 1'], Float]]:
        """
        Converts the svg file to paths
        """

        paths = []
        for path in obj:
            path = path.attrib["d"]
            moves = []
            for match in self.path_commands.findall(path):
                if ("M" in match) or ("L" in match):
                    moves.append((float(match[1]), float(match[2])))
                elif "H" in match:
                    moves.append((float(match[4]), moves[-1][1]))
                elif "V" in match:
                    moves.append((moves[-1][0], (float(match[6]))))
                elif "Z" in match:
                    pass

            paths.append(np.array(moves).reshape((-1, 1, 2)))

        self.max_x = max([p[..., 0].max() for p in paths])
        self.max_y = max([p[..., 1].max() for p in paths])
        self.min_x = min([p[..., 0].min() for p in paths])
        self.min_y = min([p[..., 1].min() for p in paths])

        return paths

    def svg_to_electrodes(self, obj: ET.Element) -> dict[str, ElectrodeDict]:
        """
        Converts the svg file to paths
        """

        electrodes: dict[str, ElectrodeDict] = {}
        try:
            pattern = r"translate\((?P<x>-?\d+\.\d+),(?P<y>-?\d+\.\d+)\)"
            match = re.match(pattern, obj.attrib['transform'])
            x = float(match.group('x'))
            y = float(match.group('y'))
            transform = np.array([x, y])
        except KeyError:
            transform = np.array([0, 0])

        for element in list(obj):
            path = element.attrib["d"]
            moves = []
            for match in self.path_commands.findall(path):
                if ("M" in match) or ("L" in match):
                    moves.append((float(match[1]), float(match[2])))
                elif "H" in match:
                    moves.append((float(match[4]), moves[-1][1]))
                elif "V" in match:
                    moves.append((moves[-1][0], (float(match[6]))))
                elif "Z" in match:
                    pass

            try:
                electrodes[element.attrib['id']] = {'channel': int(element.attrib['data-channels']),
                                                    'path': (np.array(moves) + transform).reshape((-1, 2))}
            except KeyError:
                electrodes[element.attrib['id']] = {'channel': None,
                                                    'path': (np.array(moves) + transform).reshape((-1, 2))}

        self.max_x = max([e['path'][..., 0].max() for e in electrodes.values()])
        self.max_y = max([e['path'][..., 1].max() for e in electrodes.values()])
        self.min_x = min([e['path'][..., 0].min() for e in electrodes.values()])
        self.min_y = min([e['path'][..., 1].min() for e in electrodes.values()])

        return electrodes
