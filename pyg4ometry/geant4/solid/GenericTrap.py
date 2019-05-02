from SolidBase import SolidBase as _SolidBase
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon

import logging as _log

import numpy as _np

class GenericTrap(_SolidBase):
    def __init__(self, name, v1x, v1y, v2x, v2y, v3x, v3y, v4x, v4y,
                 v5x, v5y, v6x, v6y, v7x, v7y, v8x, v8y, dz, registry=None, nstack=20):
        """
        Constructs an arbitrary trapezoid using two quadrilaterals sitting
        on two parallel planes. Vertices 1-4 define the quadrilateral at -dz and
        vertices 5-8 define the quadrilateral at +dz. This solid is called Arb8
        in GDML notation.

        Inputs:
          name:  string, name of the volume
          v1x:   float, vertex 1 x position
          v1y:   float, vertex 1 y position
          v2x:   float, vertex 2 x position
          v2y:   float, vertex 2 y position
          v3x:   float, vertex 3 x position
          v3y:   float, vertex 3 y position
          v4x:   float, vertex 4 x position
          v4y:   float, vertex 4 y position
          v5x:   float, vertex 5 x position
          v5y:   float, vertex 5 y position
          v6x:   float, vertex 6 x position
          v6y:   float, vertex 6 y position
          v7x:   float, vertex 7 x position
          v7y:   float, vertex 7 y position
          v8x:   float, vertex 8 x position
          v8y:   float, vertex 8 y position
          dz:    float, half length along z
        """
        self.type = 'GenericTrap'
        self.name = name
        self.dz = dz
        self.nstack = nstack

        vars_in = locals()
        for i in range(1, 9):
            setattr(self, "v{}x".format(i), vars_in["v{}x".format(i)])
            setattr(self, "v{}y".format(i), vars_in["v{}y".format(i)])

        self.dependents = []
        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return "Generic Trapezoid : {}".format(self.name)

    def polygon_area(self,vertices):
        # Using the shoelace formula
        xy = _np.array(vertices).T
        x = xy[0]
        y = xy[1]
        signed_area = 0.5*(_np.dot(x,_np.roll(y,1))-_np.dot(y,_np.roll(x,1)))
        if not signed_area:
            raise ValueError("Zero area quadrilateral not allowed.")
        return signed_area

    def get_vertex(self, index):
        sign_z = -1 if index <= 4 else 1
        vertex = (float(getattr(self, "v{}x".format(index))),
                  float(getattr(self, "v{}y".format(index))),
                  sign_z*float(self.dz))
        return vertex

    def makeLayers(self, verts_bot, verts_top):

        layers = []

        z1 = 2*float(self.dz)
        z0 = -float(self.dz)

        for i in range(self.nstack+1):
            z = z0 + i*z1/self.nstack
            dz = (z - z0) / (z1 - z0)

            verts_i = []
            for k in range(4):
                v_bot = verts_bot[k]
                v_top = verts_top[k]

                # Linearly interpolate
                x = v_bot[0] + (dz * (v_top[0] - v_bot[0]))
                y = v_bot[1] + (dz * (v_top[1] - v_bot[1]))

                verts_i.append(_Vertex(_Vector(x, y, z), None))

            layers.append(verts_i)

        return layers



    def pycsgmesh(self):
        _log.info('arb8.pycsgmesh> antlr')

        verts_top = []
        verts_bot = []
        for i in range(1,9):
            vert = self.get_vertex(i)
            if i <=4:
                verts_bot.append(vert)
            else:
                verts_top.append(vert)

        # Correct ordering enures correct surface normals
        if self.polygon_area(verts_top) > 0:
            verts_top = list(reversed(verts_top))

        if self.polygon_area(verts_bot) > 0:
            verts_bot = list(reversed(verts_bot))

        all_verts = self.makeLayers(verts_bot, verts_top)

        _log.info('arb8.pycsgmesh> mesh')
        polygons = []

        # Mesh top and bottom pieces
        polygons.append(_Polygon([all_verts[0][3], all_verts[0][2],
                                  all_verts[0][1], all_verts[0][0]])) # Bot

        polygons.append(_Polygon([all_verts[-1][0], all_verts[-1][1],
                                  all_verts[-1][2], all_verts[-1][3]])) # Top

        # Mesh the sides
        for i0 in range(len(all_verts)-1):
            i1 = i0 + 1
            vts_l = all_verts[i0]
            vts_u = all_verts[i1]

            for k0 in range(4): # 4 vertexes
                k1 = (k0+1) % 4
                polygons.append(_Polygon([vts_l[k0], vts_l[k1], vts_u[k1], vts_u[k0]]))

        mesh  = _CSG.fromPolygons(polygons)
        return mesh