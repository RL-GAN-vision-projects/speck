__all__ = ['GradientColour', 'CmapColour', 'KMeansColour', 'GreyscaleMeanColour']

import numpy as np
import matplotlib as mpl
from typing import Union, Iterable, List, Tuple
import cv2


class Colour:
    def __call__(self, m: int) -> Iterable[Tuple]:
        raise NotImplementedError

    def __eq__(self, other):
        return hash(self) == hash(other)


class GradientColour(Colour):
    def __init__(self, colour_list: List[str]):
        self.colour_list = colour_list
        self.cmap = mpl.colors.LinearSegmentedColormap.from_list("", colour_list)

    def __call__(self, m: int) -> Iterable[Tuple]:
        return [self.cmap(x) for x in np.linspace(0, 1, m, endpoint=False)]

    def __hash__(self):
        return hash(tuple(self.colour_list))


class CmapColour(Colour):
    def __init__(self, cmap: Union[str, mpl.colors.Colormap]):
        self.cmap = mpl.cm.get_cmap(cmap) if isinstance(cmap, str) else cmap

    def __call__(self, m: int) -> Iterable[Tuple]:
        return [self.cmap(x) for x in np.linspace(0, 1, m, endpoint=False)]

    def __hash__(self):
        return hash(str(self.cmap))


class KMeansColour(Colour):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    def __init__(self, speck_plot, k: int = 5):
        if speck_plot.image.mode != 'RGB':
            raise AssertionError('KMeansColour requires RGB image mode')

        self.k = k
        self.im = np.array(speck_plot.image)

    def _kmeans_colour(self, row: np.ndarray) -> Tuple:
        _, labels, palette = cv2.kmeans(
            row, self.k, None, self.criteria, 10, self.flags
        )
        _, counts = np.unique(labels, return_counts=True)

        return palette[np.argmax(counts)] / 255

    def __call__(self, m: int) -> Iterable[Tuple]:
        return np.squeeze(
            np.apply_along_axis(self._kmeans_colour, 1, np.float32(self.im))
        )


class GreyscaleMeanColour(Colour):
    def __init__(self, speck_plot):
        self.im = speck_plot.im

    def __call__(self, m: int) -> Iterable[Tuple]:
        return [(c, c, c) for c in np.array(self.im).mean(1) / 255.0]
