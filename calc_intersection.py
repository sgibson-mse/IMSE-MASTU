import numpy as np
import matplotlib.pyplot as plt
from sympy import Point, Line

beam_axis = np.array([0.08383689, 0.99647949, 0])

lens_pos = np.array([-0.567767, -2.110233, 0.183])
wall_pos = np.array([0.469502, -1.026687, 0.183​])

p1, p2 = Point(-0.567767, -2.110233, 0.183), Point(0.469502, -1.026687, 0.183)
l1 = Line(p1, p2)
l1.ambient_dimension

b1, b2 = Point(11.13170255, -7.0860790822,0.)

