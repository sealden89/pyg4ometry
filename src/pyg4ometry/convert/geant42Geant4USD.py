from pxr import Usd, UsdGeom, Gf, Sdf, G4


def geant4Reg2Geant4USDStage(reg, usdFileName="test.usda"):

    # get world volume
    worldVolume = reg.getWorldVolume()

    # open stage
    stage = Usd.Stage.CreateNew(usdFileName)

    # convert materials
    geant4Material2USDMaterials(stage, Sdf.Path("/Materials"), reg.materialDict)

    # convert pv-lv to scene tree
    geant4Logical2USDLogical(stage, Sdf.Path("/"), worldVolume)

    # save stage
    stage.Save()


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
    physical_prim = G4.Physical.Define(stage, physical_path)

    # create logical
    geant4Logical2USDLogical(stage, physical_path, physical.logicalVolume)

    # make transformation
    xform = UsdGeom.Xformable(physical_prim)
    xform.AddTranslateOp().Set(Gf.Vec3d(*physical.position.eval()))
    xform.AddRotateZYXOp().Set(Gf.Vec3d(*physical.rotation.eval()))

    return physical.name


def geant4Solid2UsdSolid(stage, path, solid):
    if solid.type == "Box":
        solid_path = path.AppendPath(solid.name)
        solid_prim = G4.Box.Define(stage, solid_path)
        # set parameters
        solid_prim.GetPrim().GetAttribute("x").Set(solid.pX.eval() / 2)
        solid_prim.GetPrim().GetAttribute("y").Set(solid.pY.eval() / 2)
        solid_prim.GetPrim().GetAttribute("z").Set(solid.pZ.eval() / 2)
        solid_prim.Update()
        return solid.name


def geant4Material2USDMaterials(stage, path, materials):
    pass


def geant4Material2UsdMaterial(stage, path, material):
    pass
