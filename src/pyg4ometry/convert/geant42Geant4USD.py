import numpy as _np
from ..gdml import Units as _Units

from pxr import Usd, UsdGeom, Gf, Sdf, G4


def geant4Reg2Geant4USDStage(reg):

    # get world volume
    worldVolume = reg.getWorldVolume()

    # open stage
    stage = Usd.Stage.CreateInMemory()

    # convert materials
    geant4Material2USDMaterials(stage, Sdf.Path("/Materials"), reg.materialDict)

    # convert pv-lv to scene tree
    geant4Logical2USDLogical(stage, Sdf.Path("/"), worldVolume)

    return stage
    # stage.GetRootLayer().Export("test.usda")


def geant4Logical2USDLogical(stage, path, logical):

    # create logical prim
    logical_path = path.AppendPath(logical.name)
    logical_prim = G4.Logical.Define(stage, logical_path)

    # create solid
    solid_path = geant4Solid2UsdSolid(stage, logical_path, logical.solid)
    logical_prim.GetPrim().GetAttribute("solidprim").Set(solid_path)

    # create daughters
    physical_path_list = []
    for daughter in logical.daughterVolumes:
        physical_path = geant4Physical2USDPhysical(stage, logical_path, daughter)
        physical_path_list.append(physical_path)
    logical_prim.GetPrim().GetAttribute("daughters").Set(physical_path_list)

    return logical.name


def geant4Physical2USDPhysical(stage, path, physical):

    # create physical prim
    physical_path = path.AppendPath(physical.name)
    physical_prim = G4.Placement.Define(stage, physical_path)

    # create logical
    geant4Logical2USDLogical(stage, physical_path, physical.logicalVolume)

    # make transformation
    xform = UsdGeom.Xformable(physical_prim)
    xform.AddTranslateOp().Set(Gf.Vec3d(*physical.position.eval()))
    xform.AddRotateZYXOp().Set(Gf.Vec3d(*physical.rotation.eval()))

    return physical.name


def geant4Solid2UsdSolid(stage, path, solid):
    if solid.type == "Box":
        return geant4Box2UsdBox(stage, path, solid)
    elif solid.type == "Subtraction":
        return geant4Subtraction2UsdSubtraction(stage, path, solid)
    elif solid.type == "Union":
        return geant4Union2UsdUnion(stage, path, solid)
    elif solid.type == "Intersection":
        return geant4Intersection2UsdIntersection(stage, path, solid)
    elif solid.type == "MultiUnion":
        return geant4MultiUnion2UsdMultiUnion(stage, path, solid)


def geant4Box2UsdBox(stage, path, solid):

    # create prims
    solid_path = path.AppendPath(solid.name)
    solid_prim = G4.Box.Define(stage, solid_path)

    # set parameters
    solid_prim.GetPrim().GetAttribute("x").Set(solid.pX.eval() / 2)
    solid_prim.GetPrim().GetAttribute("y").Set(solid.pY.eval() / 2)
    solid_prim.GetPrim().GetAttribute("z").Set(solid.pZ.eval() / 2)
    solid_prim.Update()
    return solid.name


def geant4Subtraction2UsdSubtraction(stage, path, solid):

    # create prims
    solid_path = path.AppendPath(solid.name)
    solid_prim = G4.Subtraction.Define(stage, solid_path)

    solid1_name = geant4Solid2UsdSolid(stage, solid_path, solid.obj1)
    solid2_name = geant4Displaced2UsdDisplaced(
        stage, solid_path, solid.obj2, solid.tra2[0].eval(), solid.tra2[1].eval()
    )
    result = UsdGeom.Mesh.Define(stage, solid_path.AppendPath("result"))

    solid_prim.GetPrim().GetAttribute("solid1prim").Set(solid1_name)
    solid_prim.GetPrim().GetAttribute("solid2prim").Set(solid2_name)
    solid_prim.GetPrim().GetAttribute("solid3prim").Set("result")

    # set solid1prim and solid2prim as invisible
    solid1_prim = solid_prim.GetPrim().GetChild(
        solid_prim.GetPrim().GetAttribute("solid1prim").Get()
    )
    solid2_prim = solid_prim.GetPrim().GetChild(
        solid_prim.GetPrim().GetAttribute("solid2prim").Get()
    )
    solid1_prim.GetPrim().GetAttribute("visibility").Set("invisible")
    solid2_prim.GetPrim().GetAttribute("visibility").Set("invisible")

    solid_prim.Update()

    return solid.name


def geant4Union2UsdUnion(stage, path, solid):

    # create prims
    solid_path = path.AppendPath(solid.name)
    solid_prim = G4.Union.Define(stage, solid_path)

    solid1_name = geant4Solid2UsdSolid(stage, solid_path, solid.obj1)
    solid2_name = geant4Displaced2UsdDisplaced(
        stage, solid_path, solid.obj2, solid.tra2[0].eval(), solid.tra2[1].eval()
    )
    result = UsdGeom.Mesh.Define(stage, solid_path.AppendPath("result"))

    solid_prim.GetPrim().GetAttribute("solid1prim").Set(solid1_name)
    solid_prim.GetPrim().GetAttribute("solid2prim").Set(solid2_name)
    solid_prim.GetPrim().GetAttribute("solid3prim").Set("result")

    # set solid1prim and solid2prim as invisible
    solid1_prim = solid_prim.GetPrim().GetChild(
        solid_prim.GetPrim().GetAttribute("solid1prim").Get()
    )
    solid2_prim = solid_prim.GetPrim().GetChild(
        solid_prim.GetPrim().GetAttribute("solid2prim").Get()
    )
    solid1_prim.GetPrim().GetAttribute("visibility").Set("invisible")
    solid2_prim.GetPrim().GetAttribute("visibility").Set("invisible")

    solid_prim.Update()

    return solid.name


def geant4Intersection2UsdIntersection(stage, path, solid):

    # create prims
    solid_path = path.AppendPath(solid.name)
    solid_prim = G4.Intersection.Define(stage, solid_path)

    solid1_name = geant4Solid2UsdSolid(stage, solid_path, solid.obj1)
    solid2_name = geant4Displaced2UsdDisplaced(
        stage, solid_path, solid.obj2, solid.tra2[0].eval(), solid.tra2[1].eval()
    )
    result = UsdGeom.Mesh.Define(stage, solid_path.AppendPath("result"))

    solid_prim.GetPrim().GetAttribute("solid1prim").Set(solid1_name)
    solid_prim.GetPrim().GetAttribute("solid2prim").Set(solid2_name)
    solid_prim.GetPrim().GetAttribute("solid3prim").Set("result")

    # set solid1prim and solid2prim as invisible
    solid1_prim = solid_prim.GetPrim().GetChild(
        solid_prim.GetPrim().GetAttribute("solid1prim").Get()
    )
    solid2_prim = solid_prim.GetPrim().GetChild(
        solid_prim.GetPrim().GetAttribute("solid2prim").Get()
    )
    solid1_prim.GetPrim().GetAttribute("visibility").Set("invisible")
    solid2_prim.GetPrim().GetAttribute("visibility").Set("invisible")

    solid_prim.Update()

    return solid.name


def geant4Displaced2UsdDisplaced(stage, path, solid, rotation, translation, index=None):
    solid_name = solid.name + "_displaced"

    if index is not None:
        solid_name += "_" + str(index)

    solid_path = path.AppendPath(solid_name)
    solid_prim = G4.DisplacedSolid.Define(stage, solid_path)

    solid_prim.GetRotationAttr().Set(Gf.Vec3d(*[a / _np.pi * 180 for a in rotation]))
    solid_prim.GetTranslationAttr().Set(Gf.Vec3d(*translation))

    geant4Solid2UsdSolid(stage, solid_prim.GetPrim().GetPath(), solid)

    solid_prim.Update()

    return solid_name


def geant4MultiUnion2UsdMultiUnion(stage, path, solid):
    solid_name = solid.name + "_multi"

    solid_path = path.AppendPath(solid_name)
    solid_prim = G4.MultiUnion.Define(stage, solid_path)

    # loop over deps
    displaced_solid_names = []
    for t, s, i in zip(solid.transformations, solid.objects, range(len(solid.objects))):
        lunit = _Units.unit(t[1].unit)
        aunit = _Units.unit(t[0].unit)

        r = [r / aunit for r in t[0].eval()]
        d = [d / lunit for d in t[1].eval()]

        displaced_solid_name = geant4Displaced2UsdDisplaced(stage, solid_path, s, r, d, i)
        displaced_solid_names.append(displaced_solid_name)

    # create result prim
    result = UsdGeom.Mesh.Define(stage, solid_path.AppendPath("result"))

    # set names
    solid_prim.GetPrim().GetAttribute("solidprims").Set(displaced_solid_names)
    solid_prim.GetPrim().GetAttribute("solid3prim").Set("result")

    # update
    solid_prim.Update()

    return solid_name


def geant4Material2USDMaterials(stage, path, materials):
    pass


def geant4Material2UsdMaterial(stage, path, material):
    pass
