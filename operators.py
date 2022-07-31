import bpy
import math
import random
import mathutils
import numpy
import bmesh
import os

def get_path():
    return os.path.dirname(os.path.realpath(__file__))


#get the name of the "base" folder
def get_name():
    print(__name__)
    print(__package__)
    print(get_path())
    print(os.path.basename(get_path()))
    return os.path.basename(get_path())

def get_transparent_material_output_inputSocket(material):
    node_outut_id = material.node_tree.nodes.find("Material Output")
    if node_outut_id != -1:
        thisNode = material.node_tree.nodes[node_outut_id]
        if len(thisNode.inputs[0].links) == 0:
            return thisNode.inputs[0]
        thisPreviousNode = thisNode.inputs[0].links[0].from_node
        connectedSocket = thisNode.inputs['Surface']
        if thisPreviousNode.type == "MIX_SHADER":
            thisUseMix = False
            thisOldConectedNode = thisPreviousNode  
            if thisPreviousNode.inputs[1].links[0].from_node.type == "BSDF_TRANSPARENT":
                if len(thisPreviousNode.inputs[2].links) == 0:
                    return thisPreviousNode.inputs[2]
                thisOldConectedNode = thisPreviousNode.inputs[2].links[0].from_node
                thisUseMix = True
                connectedSocket = thisPreviousNode.inputs[2]
                previouslyConnectedNodeSocketTo = thisPreviousNode.inputs[2]
                previouslyConnectedNodeSocketFrom = thisPreviousNode.inputs[2].links[0].from_socket
            elif thisPreviousNode.inputs[2].links[0].from_node.type == "BSDF_TRANSPARENT":
                thisOldConectedNode = thisPreviousNode.inputs[1].links[0].from_node
                thisUseMix = True
                connectedSocket = thisPreviousNode.inputs[1]
                previouslyConnectedNodeSocketTo = thisPreviousNode.inputs[1]
                previouslyConnectedNodeSocketFrom = thisPreviousNode.inputs[1].links[0].from_socket
            if thisUseMix == False:
                previouslyConnectedNodeSocketTo = thisNode.inputs['Surface']
                previouslyConnectedNodeSocketFrom = thisNode.inputs['Surface'].links[0].from_socket      
        return connectedSocket
    else:
        print(material.name + " Material has no Output")

def checkSurroundingPixels(thisX, thisY, pixels, output_image, list_with_new_pixels):
    if pixels[thisX+1][thisY+1][3] < 0.1:
        output_image[thisX+1][thisY+1] = (pixels[thisX][thisY][0],pixels[thisX][thisY][1],pixels[thisX][thisY][2],1)
        list_with_new_pixels.append([thisX+1, thisY+1])
    if pixels[thisX+1][thisY][3] < 0.1:
        output_image[thisX+1][thisY] = (pixels[thisX][thisY][0],pixels[thisX][thisY][1],pixels[thisX][thisY][2],1)
        list_with_new_pixels.append([thisX+1, thisY])
    if pixels[thisX+1][thisY-1][3] < 0.1:
        output_image[thisX+1][thisY-1] = (pixels[thisX][thisY][0],pixels[thisX][thisY][1],pixels[thisX][thisY][2],1)
        list_with_new_pixels.append([thisX+1, thisY-1])
    if pixels[thisX][thisY+1][3] < 0.1:
        output_image[thisX][thisY+1] = (pixels[thisX][thisY][0],pixels[thisX][thisY][1],pixels[thisX][thisY][2],1)
        list_with_new_pixels.append([thisX, thisY+1])
    if pixels[thisX][thisY-1][3] < 0.1:
        output_image[thisX][thisY-1] = (pixels[thisX][thisY][0],pixels[thisX][thisY][1],pixels[thisX][thisY][2],1)
        list_with_new_pixels.append([thisX, thisY-1])
    if pixels[thisX-1][thisY+1][3] < 0.1:
        output_image[thisX-1][thisY+1] = (pixels[thisX][thisY][0],pixels[thisX][thisY][1],pixels[thisX][thisY][2],1)
        list_with_new_pixels.append([thisX-1, thisY+1])
    if pixels[thisX-1][thisY][3] < 0.1:
        output_image[thisX-1][thisY] = (pixels[thisX][thisY][0],pixels[thisX][thisY][1],pixels[thisX][thisY][2],1)
        list_with_new_pixels.append([thisX-1, thisY])
    if pixels[thisX-1][thisY-1][3] < 0.1:
        output_image[thisX-1][thisY-1] = (pixels[thisX][thisY][0],pixels[thisX][thisY][1],pixels[thisX][thisY][2],1)
        list_with_new_pixels.append([thisX-1, thisY-1])
    return True

def blur(a):
    kernel = numpy.array([[1.0,2.0,3.0,2.0,1.0], [2.0,3.0,4.0,3.0,2.0], [3.0,4.0,5.0,4.0,3.0], [2.0,3.0,4.0,3.0,2.0], [1.0,2.0,3.0,2.0,1.0]])
    kernel = kernel / numpy.sum(kernel)
    arraylist = []
    for y in range(3):
        temparray = numpy.copy(a)
        temparray = numpy.roll(temparray, y - 1, axis=0)
        for x in range(3):
            temparray_X = numpy.copy(temparray)
            temparray_X = numpy.roll(temparray_X, x - 1, axis=1)*kernel[y,x]
            arraylist.append(temparray_X)

    arraylist = numpy.array(arraylist)
    arraylist_sum = numpy.sum(arraylist, axis=0)
    return arraylist_sum

def create_spere(collection, locX = 0.0, locY = 0.0, locZ = 0.0, scale = 1.0):
    # Create an empty mesh and the object.
    mesh = bpy.data.meshes.new('Basic_Sphere')
    basic_sphere = bpy.data.objects.new("Basic_Sphere", mesh)

    # Add the object into the scene.
    collection.objects.link(basic_sphere)

    # Select the newly created object
    #bpy.context.view_layer.objects.active = basic_sphere
    #basic_sphere.select_set(True)

    # Construct the bmesh sphere and assign it to the blender mesh.
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.5, calc_uvs=True)
    # bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=1)
    bm.to_mesh(mesh)
    bm.free()
    basic_sphere.location.x = locX
    basic_sphere.location.y = locY
    basic_sphere.location.z = locZ
    basic_sphere.scale = (scale, scale, scale)
    basic_sphere.rotation_euler = mathutils.Euler((0.0, 0.0, math.radians(locY)), 'XYZ')
    return basic_sphere

def polygonArea(X = [1], Y = [1], numPoints = 1):
    area = 0            # Accumulates area in the loop
    j = numPoints-1     # The last vertex is the 'previous' one to the first

    for i in range(0, numPoints, 1):
        area = area + (X[j] + X[i]) * (Y[j] - Y[i]) 
        j = i           #j is previous vertex to i

    return area / 2

def getUvArea(ob):
    fullArea = 0
    print(ob)
    for face in ob.polygons:
        xPts = []
        yPts = []
        # for faceVert in face.vertices:
        #     print(len(ob.data.uv_layers.active.data))
        #     xPts.append(ob.data.uv_layers.active.data[0].uv[0])
        #     yPts.append(ob.data.uv_layers.active.data[0].uv[1])
        # xPts[1], xPts[2] = xPts[2], xPts[1]
        # yPts[1], yPts[2] = yPts[2], yPts[1]
        # xPts[3], xPts[2] = xPts[2], xPts[3]
        # yPts[3], yPts[2] = yPts[2], yPts[3]
        #fullArea = fullArea + polygonArea(xPts, yPts, len(xPts))    
        fullArea = fullArea + face.area
    return fullArea

def CreateNodeGroupImpostor():
    groupNull = bpy.data.node_groups.get("ImpostorGroup") == None
    group = (bpy.data.node_groups.get("ImpostorGroup") or bpy.data.node_groups.new(type="ShaderNodeTree", name="ImpostorGroup"))
    if groupNull:
        group.inputs.new("NodeSocketColor", "Color")
        group.inputs.new("NodeSocketFloat", "Alpha")
        #group.inputs.new("NodeSocketFloat", "Metallic")
        #group.inputs.new("NodeSocketFloat", "Roughness")
        group.inputs.new("NodeSocketFloat", "Number")
        try:
            group.inputs.new("NodeSocketVector", "Normal")
        except:
            group.inputs.new("NodeSocketNormal", "Normal")

        node_g_input = group.nodes.new("NodeGroupInput")
        node_g_input.location = (-1500, 0)

        group.outputs.new("NodeSocketShader", "Out")
        node_g_output = group.nodes.new("NodeGroupOutput")
        node_g_output.location = (640, 58)

        # create Principled BSDF node
        node_g_principled = group.nodes.new(type='ShaderNodeBsdfPrincipled')
        node_g_principled.inputs[9].default_value = 0.75

        node_g_mix = group.nodes.new(type='ShaderNodeMixShader')
        node_g_mix.location = 400,65

        node_g_Transparent = group.nodes.new(type='ShaderNodeBsdfTransparent')
        node_g_Transparent.location = 60,100

        node_g_geometry = group.nodes.new(type='ShaderNodeNewGeometry')
        node_g_geometry.location = -1920,260

        node_g_SeparateXYZ = group.nodes.new(type='ShaderNodeSeparateXYZ')
        node_g_SeparateXYZ.location = -1700,160

        node_g_lessThan = group.nodes.new(type='ShaderNodeMath')
        node_g_lessThan.operation = 'LESS_THAN'
        node_g_lessThan.location = -280,260
    
        node_g_degrees = group.nodes.new(type='ShaderNodeMath')
        try:
            node_g_degrees.operation = 'DEGREES'
        except:
            node_g_degrees.operation = 'MULTIPLY'
            node_g_degrees.inputs[1].default_value = 57.295779513
        node_g_degrees.location = -500,300

        node_g_subtract = group.nodes.new(type='ShaderNodeMath')
        node_g_subtract.operation = 'MULTIPLY'
        node_g_subtract.inputs[0].default_value = 0.5
        node_g_subtract.location = -500,80

        node_g_divide = group.nodes.new(type='ShaderNodeMath')
        node_g_divide.operation = 'DIVIDE'
        node_g_divide.inputs[0].default_value = 360
        node_g_divide.location = -700,80

        node_g_arccosine = group.nodes.new(type='ShaderNodeMath')
        node_g_arccosine.operation = 'ARCCOSINE'
        node_g_arccosine.location = -700,300

        node_g_clamp = group.nodes.new(type='ShaderNodeClamp')
        try:
            node_g_clamp.clamp_type = 'MINMAX'
        except:
            print("Old Blender version")
        node_g_clamp.inputs[1].default_value = -1.0
        node_g_clamp.inputs[2].default_value = 1.0
        node_g_clamp.location = -900,300

        node_g_dotProduct = group.nodes.new(type='ShaderNodeVectorMath')
        node_g_dotProduct.operation = 'DOT_PRODUCT'
        node_g_dotProduct.location = -1100,300

        node_g_normalize1 = group.nodes.new(type='ShaderNodeVectorMath')
        node_g_normalize1.operation = 'NORMALIZE'
        node_g_normalize1.location = -1320,300

        node_g_normalize2 = group.nodes.new(type='ShaderNodeVectorMath')
        node_g_normalize2.operation = 'NORMALIZE'
        node_g_normalize2.location = -1320,160

        node_g_combine = group.nodes.new(type='ShaderNodeCombineXYZ')
        node_g_combine.location = -1500,160

        node_g_addDither = group.nodes.new(type='ShaderNodeMath')
        node_g_addDither.operation = 'ADD'
        node_g_addDither.location = -700,520

        node_g_subtractDither = group.nodes.new(type='ShaderNodeMath')
        node_g_subtractDither.operation = 'SUBTRACT'
        node_g_subtractDither.location = -900,520
        node_g_subtractDither.inputs[1].default_value = 0.13

        node_g_multiplyDither = group.nodes.new(type='ShaderNodeMath')
        node_g_multiplyDither.operation = 'MULTIPLY'
        node_g_multiplyDither.location = -1100,520
        node_g_multiplyDither.inputs[1].default_value = 0.2

        node_g_noiseDither = group.nodes.new(type='ShaderNodeTexNoise')
        node_g_noiseDither.inputs[2].default_value = 500
        node_g_noiseDither.location = -1320,520

        node_g_multiply = group.nodes.new(type='ShaderNodeMath')
        node_g_multiply.operation = 'MULTIPLY'
        node_g_multiply.location = 0,340

        # link
        group.links.new(node_g_input.outputs[0], node_g_principled.inputs[0])
        group.links.new(node_g_input.outputs[1], node_g_multiply.inputs[1])
        group.links.new(node_g_input.outputs[3], node_g_principled.inputs["Normal"])
        group.links.new(node_g_Transparent.outputs[0], node_g_mix.inputs[1])
        group.links.new(node_g_principled.outputs[0], node_g_mix.inputs[2])
        group.links.new(node_g_mix.outputs[0], node_g_output.inputs[0])
        group.links.new(node_g_SeparateXYZ.outputs[0], node_g_lessThan.inputs[0])
        group.links.new(node_g_multiply.outputs[0], node_g_mix.inputs[0])

        group.links.new(node_g_geometry.outputs[1], node_g_normalize1.inputs[0])
        group.links.new(node_g_geometry.outputs[4], node_g_SeparateXYZ.inputs[0])
        group.links.new(node_g_SeparateXYZ.outputs[0], node_g_combine.inputs[0])
        group.links.new(node_g_SeparateXYZ.outputs[1], node_g_combine.inputs[1])
        group.links.new(node_g_combine.outputs[0], node_g_normalize2.inputs[0])
        group.links.new(node_g_normalize1.outputs[0], node_g_dotProduct.inputs[0])
        group.links.new(node_g_normalize2.outputs[0], node_g_dotProduct.inputs[1])
        group.links.new(node_g_clamp.outputs[0], node_g_arccosine.inputs[0])
        group.links.new(node_g_dotProduct.outputs['Value'], node_g_clamp.inputs[0])
        group.links.new(node_g_arccosine.outputs[0], node_g_addDither.inputs[0])
        group.links.new(node_g_degrees.outputs[0], node_g_lessThan.inputs[0])
        group.links.new(node_g_subtract.outputs[0], node_g_lessThan.inputs[1])
        group.links.new(node_g_divide.outputs[0], node_g_subtract.inputs[1])
        group.links.new(node_g_input.outputs[2], node_g_divide.inputs[1])
        group.links.new(node_g_lessThan.outputs[0], node_g_multiply.inputs[0])
        group.links.new(node_g_noiseDither.outputs[0], node_g_multiplyDither.inputs[0])
        group.links.new(node_g_multiplyDither.outputs[0], node_g_subtractDither.inputs[0])
        group.links.new(node_g_subtractDither.outputs[0], node_g_addDither.inputs[1])
        group.links.new(node_g_addDither.outputs[0], node_g_degrees.inputs[0])
        return group

def CreateNodeGroupDepth(maxExtendsFromCenter = 10, scale = 1, yOffset = 0):
    groupDepthNull = bpy.data.node_groups.get("MeshDepth") == None
    if groupDepthNull == False:
        groupDepth = bpy.data.node_groups.get("MeshDepth")
    else:
        groupDepth = bpy.data.node_groups.new(type="ShaderNodeTree", name="MeshDepth")
        groupDepth.inputs.new("NodeSocketFloat", "Add")
        groupDepth.inputs.new("NodeSocketFloat", "Multiply")

        # create output
        groupDepth.outputs.new("NodeSocketShader", "Out")
        node_g1_output = groupDepth.nodes.new(type="NodeGroupOutput")
        node_g1_output.location = (200, 0)

        # create emission shader
        node_g1_emission = groupDepth.nodes.new(type="ShaderNodeEmission")
        node_g1_emission.location = 0, 0

        # create one minus to invert depth
        node_g1_subtract2 = groupDepth.nodes.new(type='ShaderNodeMath')
        node_g1_subtract2.operation = 'SUBTRACT'
        node_g1_subtract2.location = -200, 0
        node_g1_subtract2.inputs[0].default_value = 1

        # create separate
        node_g1_separate = groupDepth.nodes.new(type="ShaderNodeSeparateRGB")
        node_g1_separate.location = (-800, 0)

        # create multiply1
        node_g1_1multiply = groupDepth.nodes.new(type='ShaderNodeMath')
        node_g1_1multiply.operation = 'MULTIPLY'
        node_g1_1multiply.inputs[1].default_value = 1 / ((maxExtendsFromCenter * 2) * scale)
        node_g1_1multiply.location = -400, 0

        #Create group input
        node_g1_GroupInput = groupDepth.nodes.new(type='NodeGroupInput')
        node_g1_GroupInput.location = -800, -200

        # create add1
        node_g1_1add = groupDepth.nodes.new(type='ShaderNodeMath')
        node_g1_1add.operation = 'ADD'
        node_g1_1add.inputs[1].default_value = (yOffset - (maxExtendsFromCenter * scale))
        node_g1_1add.location = -600, 0

        # create Geometry
        node_g1_geometry = groupDepth.nodes.new(type='ShaderNodeNewGeometry')
        node_g1_geometry.location = -1000, 0


        # create ObjectInfo
        node_g1_ObjectInfo = groupDepth.nodes.new(type='ShaderNodeObjectInfo')
        node_g1_ObjectInfo.location = -1000, 300

        # create separate2
        node_g1_separate2 = groupDepth.nodes.new(type="ShaderNodeSeparateRGB")
        node_g1_separate2.location = (-800, 300)

        # create subtract
        node_g1_subtract = groupDepth.nodes.new(type='ShaderNodeMath')
        node_g1_subtract.operation = 'SUBTRACT'
        node_g1_subtract.location = -400, 300





        #create links
        groupDepth.links.new(node_g1_geometry.outputs[0], node_g1_separate.inputs[0])
        groupDepth.links.new(node_g1_separate.outputs[1], node_g1_subtract.inputs[0])
        groupDepth.links.new(node_g1_subtract.outputs[0], node_g1_1add.inputs[0])
        groupDepth.links.new(node_g1_1add.outputs[0], node_g1_1multiply.inputs[0])
        groupDepth.links.new(node_g1_1multiply.outputs[0], node_g1_subtract2.inputs[1])
        groupDepth.links.new(node_g1_subtract2.outputs[0], node_g1_emission.inputs[0])
        groupDepth.links.new(node_g1_emission.outputs[0], node_g1_output.inputs[0])
        groupDepth.links.new(node_g1_GroupInput.outputs[0], node_g1_1add.inputs[1])
        groupDepth.links.new(node_g1_GroupInput.outputs[1], node_g1_1multiply.inputs[1])
        groupDepth.links.new(node_g1_separate2.outputs[1], node_g1_subtract.inputs[1])
        groupDepth.links.new(node_g1_ObjectInfo.outputs[0], node_g1_separate2.inputs[0])
        
    return groupDepth

def get_group_normalize():
    group_normalize_isNULL = bpy.data.node_groups.get("Color_Normalize") == None
    group_normalize = (bpy.data.node_groups.get("Color_Normalize") or bpy.data.node_groups.new(type="CompositorNodeTree", name="Color_Normalize"))
    if group_normalize_isNULL:
        # create in and output
        group_normalize.outputs.new("NodeSocketColor", "Out")
        group_normalize.inputs.new("NodeSocketColor", "Color")

        cng_output = group_normalize.nodes.new(type="NodeGroupOutput")
        cng_output.location = (1600, 0)

        cng_input = group_normalize.nodes.new(type="NodeGroupInput")
        cng_input.location = (0, 0)

        cng_sepRGB = group_normalize.nodes.new(type="CompositorNodeSepRGBA")
        cng_sepRGB.location = (200, 0)

        cng_R_pow = group_normalize.nodes.new(type="CompositorNodeMath")
        cng_R_pow.location = (400, 160)
        cng_R_pow.operation = 'POWER'
        cng_R_pow.inputs[1].default_value = 2

        cng_G_pow = group_normalize.nodes.new(type="CompositorNodeMath")
        cng_G_pow.location = (400, 0)
        cng_G_pow.operation = 'POWER'
        cng_G_pow.inputs[1].default_value = 2

        cng_B_pow = group_normalize.nodes.new(type="CompositorNodeMath")
        cng_B_pow.location = (400, -160)
        cng_B_pow.operation = 'POWER'
        cng_B_pow.inputs[1].default_value = 2

        cng_add1 = group_normalize.nodes.new(type="CompositorNodeMath")
        cng_add1.location = (600, 80)
        cng_add1.operation = 'ADD'

        cng_add2 = group_normalize.nodes.new(type="CompositorNodeMath")
        cng_add2.location = (800, -80)
        cng_add2.operation = 'ADD'

        cng_root = group_normalize.nodes.new(type="CompositorNodeMath")
        cng_root.location = (1000, -80)
        cng_root.operation = 'POWER'
        cng_root.inputs[1].default_value = 0.5

        cng_divide = group_normalize.nodes.new(type="CompositorNodeMath")
        cng_divide.location = (1200, -80)
        cng_divide.operation = 'DIVIDE'
        cng_divide.inputs[0].default_value = 1

        cng_mixMul = group_normalize.nodes.new(type="CompositorNodeMixRGB")
        cng_mixMul.location = (1400, 0)
        cng_mixMul.blend_type = 'MULTIPLY'

        group_normalize.links.new(cng_input.outputs[0], cng_sepRGB.inputs[0])
        group_normalize.links.new(cng_sepRGB.outputs[0], cng_R_pow.inputs[0])
        group_normalize.links.new(cng_sepRGB.outputs[1], cng_G_pow.inputs[0])
        group_normalize.links.new(cng_sepRGB.outputs[2], cng_B_pow.inputs[0])
        group_normalize.links.new(cng_R_pow.outputs[0], cng_add1.inputs[0])
        group_normalize.links.new(cng_G_pow.outputs[0], cng_add1.inputs[1])
        group_normalize.links.new(cng_B_pow.outputs[0], cng_add2.inputs[1])
        group_normalize.links.new(cng_add1.outputs[0], cng_add2.inputs[0])
        group_normalize.links.new(cng_add2.outputs[0], cng_root.inputs[0])
        group_normalize.links.new(cng_root.outputs[0], cng_divide.inputs[1])
        group_normalize.links.new(cng_divide.outputs[0], cng_mixMul.inputs[2])
        group_normalize.links.new(cng_input.outputs[0], cng_mixMul.inputs[1])
        group_normalize.links.new(cng_mixMul.outputs[0], cng_output.inputs[0])
    return group_normalize

def CreateNodeGroupMeshNormal():
    groupMeshNormalNull = bpy.data.node_groups.get("MeshNormal") == None
    groupMeshNormal = (bpy.data.node_groups.get("MeshNormal") or bpy.data.node_groups.new(type="ShaderNodeTree", name="MeshNormal"))
    if groupMeshNormalNull:
        # create output
        groupMeshNormal.outputs.new("NodeSocketShader", "Out")
        node_g1_output = groupMeshNormal.nodes.new(type="NodeGroupOutput")
        node_g1_output.location = (760, 0)

        # create emission shader
        node_g1_emission = groupMeshNormal.nodes.new(type="ShaderNodeEmission")
        node_g1_emission.location = (580, 0)
        
        # create combine
        node_g1_combine = groupMeshNormal.nodes.new(type="ShaderNodeCombineRGB")
        node_g1_combine.location = (400, 0)

        # create separate
        node_g1_separate = groupMeshNormal.nodes.new(type="ShaderNodeSeparateRGB")
        node_g1_separate.location = (-240, 0)

        # create multiply1
        node_g1_1multiply = groupMeshNormal.nodes.new(type='ShaderNodeMath')
        node_g1_1multiply.operation = 'MULTIPLY'
        node_g1_1multiply.inputs[1].default_value = 0.5
        node_g1_1multiply.location = 180, 200

        # create multiply2
        node_g1_2multiply = groupMeshNormal.nodes.new(type='ShaderNodeMath')
        node_g1_2multiply.operation = 'MULTIPLY'
        node_g1_2multiply.inputs[1].default_value = 0.5
        node_g1_2multiply.location = 180, 0

        # create multiply3
        node_g1_3multiply = groupMeshNormal.nodes.new(type='ShaderNodeMath')
        node_g1_3multiply.operation = 'MULTIPLY'
        node_g1_3multiply.inputs[1].default_value = -1.0
        node_g1_3multiply.location = 120, -180

        # create add1
        node_g1_1add = groupMeshNormal.nodes.new(type='ShaderNodeMath')
        node_g1_1add.operation = 'ADD'
        node_g1_1add.inputs[1].default_value = 1.0
        node_g1_1add.location = 0, 200

        # create add2
        node_g1_2add = groupMeshNormal.nodes.new(type='ShaderNodeMath')
        node_g1_2add.operation = 'ADD'
        node_g1_2add.inputs[1].default_value = 1.0
        node_g1_2add.location = 0, 0

        # create VectorTransform
        node_g1_vectorTransform = groupMeshNormal.nodes.new(type='ShaderNodeVectorTransform')
        node_g1_vectorTransform.vector_type = 'NORMAL'
        node_g1_vectorTransform.convert_from = 'WORLD'
        node_g1_vectorTransform.convert_to = 'CAMERA'
        node_g1_vectorTransform.location = -420, 0

        # create Geometry
        node_g1_geometry = groupMeshNormal.nodes.new(type='ShaderNodeNewGeometry')
        node_g1_geometry.location = -620, 0

        #create links
        groupMeshNormal.links.new(node_g1_geometry.outputs[1], node_g1_vectorTransform.inputs[0])
        groupMeshNormal.links.new(node_g1_vectorTransform.outputs[0], node_g1_separate.inputs[0])
        groupMeshNormal.links.new(node_g1_separate.outputs[0], node_g1_1add.inputs[0])
        groupMeshNormal.links.new(node_g1_separate.outputs[1], node_g1_2add.inputs[0])
        groupMeshNormal.links.new(node_g1_separate.outputs[2], node_g1_3multiply.inputs[0])
        groupMeshNormal.links.new(node_g1_1add.outputs[0], node_g1_1multiply.inputs[0])
        groupMeshNormal.links.new(node_g1_2add.outputs[0], node_g1_2multiply.inputs[0])
        groupMeshNormal.links.new(node_g1_1multiply.outputs[0], node_g1_combine.inputs[0])
        groupMeshNormal.links.new(node_g1_2multiply.outputs[0], node_g1_combine.inputs[1])
        groupMeshNormal.links.new(node_g1_3multiply.outputs[0], node_g1_combine.inputs[2])
        groupMeshNormal.links.new(node_g1_combine.outputs[0], node_g1_emission.inputs[0])
        groupMeshNormal.links.new(node_g1_emission.outputs[0], node_g1_output.inputs[0])
        return groupMeshNormal

def CreateNodeGroupNormalMask():
    GroupNormalMaskNull = bpy.data.node_groups.get("NormalMask") == None
    GroupNormalMask = (bpy.data.node_groups.get("NormalMask") or bpy.data.node_groups.new(type="ShaderNodeTree", name="NormalMask"))
    if GroupNormalMaskNull:
        # create output
        #GroupNormalMask.outputs.new("NodeSocketShader", "Out")

        node_g1_output = GroupNormalMask.nodes.new(type="NodeGroupOutput")
        node_g1_output.location = (760, 0)

        # create Geometry
        node_g1_geometry = GroupNormalMask.nodes.new(type='ShaderNodeNewGeometry')
        node_g1_geometry.location = -620, 0

        # create SeparateXYZ
        node_g1_SeparateXYZ = GroupNormalMask.nodes.new(type='ShaderNodeSeparateXYZ')
        node_g1_SeparateXYZ.location = 0, 0

        # create multiply1
        node_g1_1multiply = GroupNormalMask.nodes.new(type='ShaderNodeMath')
        node_g1_1multiply.operation = 'MULTIPLY'
        node_g1_1multiply.inputs[1].default_value = 2
        node_g1_1multiply.location = 180, 200

        # create subtract
        node_g1_1subtract = GroupNormalMask.nodes.new(type='ShaderNodeMath')
        node_g1_1subtract.operation = 'SUBTRACT'
        node_g1_1subtract.inputs[1].default_value = 1.0
        node_g1_1subtract.location = 0, 200

        # create combine
        node_g1_combine = GroupNormalMask.nodes.new(type="ShaderNodeCombineXYZ")
        node_g1_combine.location = (400, 0)

        # create VectorMath
        node_g1_VectorMath = GroupNormalMask.nodes.new(type="ShaderNodeVectorMath")
        node_g1_VectorMath.operation = 'DOT_PRODUCT'
        node_g1_VectorMath.location = (400, 0)

        # create add1
        node_g1_1add = GroupNormalMask.nodes.new(type='ShaderNodeMath')
        node_g1_1add.operation = 'ADD'
        node_g1_1add.inputs[1].default_value = 1.0
        node_g1_1add.location = 0, 200

        # create subtract
        node_g1_2subtract = GroupNormalMask.nodes.new(type='ShaderNodeMath')
        node_g1_2subtract.operation = 'SUBTRACT'
        node_g1_2subtract.inputs[0].default_value = 1.0
        node_g1_2subtract.location = 0, 200
        node_g1_2subtract.use_clamp = True

        #create links
        GroupNormalMask.links.new(node_g1_geometry.outputs[1], node_g1_SeparateXYZ.inputs[0])
        GroupNormalMask.links.new(node_g1_geometry.outputs[6], node_g1_1multiply.inputs[0])
        GroupNormalMask.links.new(node_g1_1multiply.outputs[0], node_g1_1subtract.inputs[0])
        GroupNormalMask.links.new(node_g1_1subtract.outputs[0], node_g1_combine.inputs[2])
        GroupNormalMask.links.new(node_g1_SeparateXYZ.outputs[2], node_g1_VectorMath.inputs[0])
        GroupNormalMask.links.new(node_g1_combine.outputs[0], node_g1_VectorMath.inputs[1])
        GroupNormalMask.links.new(node_g1_VectorMath.outputs['Value'], node_g1_1add.inputs[0])
        GroupNormalMask.links.new(node_g1_1add.outputs[0], node_g1_2subtract.inputs[1])
        GroupNormalMask.links.new(node_g1_2subtract.outputs[0], node_g1_output.inputs[0])

        return GroupNormalMask

def angle(v1, v2):
  return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

def SetUVsToStorePivotOffset(ob):
    ob.data.uv_layers.new(name="PivotOffset")
    #ob.data.uv_layers['PivotOffset'].active = True
    for face in ob.data.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    ob.data.uv_layers['PivotOffset'].data[loop_idx].uv = ( ob.data.vertices[vert_idx].co[0] * 0.1, ob.data.vertices[vert_idx].co[1] * 0.1)
                    #ob.data.uv_layers['PivotOffset'].data[loop_idx].uv = ( face.vertices[vert_idx].co[0] * 0.1, face.vertices[vert_idx].co[2] * 0.1)
    return ob

def SetUVsToStorePivotOffset2D(ob):
    ob.data.uv_layers.new(name="PivotOffset0")
    for face in ob.data.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    vert_distance = pow(pow(ob.data.vertices[vert_idx].co[0], 2) + pow(ob.data.vertices[vert_idx].co[1], 2), 0.5)
                    if ob.data.uv_layers['PivotOffset'].data[loop_idx].uv[0] < 0:
                        vert_distance = vert_distance * -1
                    ob.data.uv_layers['PivotOffset0'].data[loop_idx].uv = ( vert_distance * 0.1, ob.data.vertices[vert_idx].co[2] * 0.1)
    return ob

def SetUVsToStorePivotOffset3D(ob):
    ob.data.uv_layers.new(name="PivotOffset1")
    ob.data.uv_layers.new(name="PivotOffset2")
    for face in ob.data.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    ob.data.uv_layers['PivotOffset1'].data[loop_idx].uv = ( ob.data.vertices[vert_idx].co[0] * 0.1, ob.data.vertices[vert_idx].co[1] * 0.1)
                    ob.data.uv_layers['PivotOffset2'].data[loop_idx].uv = ( ob.data.vertices[vert_idx].co[2] * 0.1, 0)
                    
    return ob

def SetVertexColors(ob):
    #Set vertex colors to store pivot offset
    if not ob.data.vertex_colors:
        ob.data.vertex_colors.new()
    
    color_layer = ob.data.vertex_colors["Col"]
    i = 0
    for poly in ob.data.polygons:
        for v_ix, l_ix in zip(poly.vertices, poly.loop_indices):
            PositionColor = ob.data.vertices[v_ix].co
            color_layer.data[l_ix].color = mathutils.Vector(((PositionColor[0] + 10) / 20, (PositionColor[1] + 10) / 20, (PositionColor[2] + 10) / 20, 0))
            i += 1
    return ob

#Recursivly transverse layer_collection for a particular name
def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found

def totalUnlink(unlinkObject):
    for thisCollection in unlinkObject.users_collection:
        thisCollection.objects.unlink(unlinkObject)
    return 1

def create_margin_for_image(image, fileName, originalObject, saveFilePath):
    W,H = image.size

    #px0 = image.pixels[:]
    px0 = [min(max(v, 0), 1) for v in image.pixels] ## <!> clamp
    pixels = numpy.array([float(v) for v in px0])
    #print(pixels[0])
    pixels.resize(W, H, 4)

    output_image = numpy.copy(pixels)
    list_with_new_pixels = []
    for thisY in range(0, H-1):
        for thisX in range(0, W-1):
            if pixels[thisX][thisY][3] > 0.09:
                if pixels[thisX][thisY][3] < 1:
                    output_image[thisX][thisY] = (pixels[thisX][thisY][0],pixels[thisX][thisY][1],pixels[thisX][thisY][2],1)
                if thisX-1 >= 0 and thisX+1 < int(originalObject["Impostor Resolution"]) and thisY-1 >= 0 and thisY+1 < int(originalObject["Impostor Resolution"]):
                    checkSurroundingPixels(thisX, thisY, pixels, output_image, list_with_new_pixels)
    
    iterateList = list_with_new_pixels.copy()
    list_with_new_pixels = []
    pixels = numpy.copy(output_image)
    for checkNext in iterateList:
        if checkNext[0]-1 >= 0 and checkNext[0]+1 < int(originalObject["Impostor Resolution"]) and checkNext[1]-1 >= 0 and checkNext[1]+1 < int(originalObject["Impostor Resolution"]):
            checkSurroundingPixels(checkNext[0], checkNext[1], output_image, pixels, list_with_new_pixels)

    iterateList = list_with_new_pixels.copy()
    list_with_new_pixels = []
    output_image = numpy.copy(pixels)
    for checkNext in iterateList:
        if checkNext[0]-1 >= 0 and checkNext[0]+1 < int(originalObject["Impostor Resolution"]) and checkNext[1]-1 >= 0 and checkNext[1]+1 < int(originalObject["Impostor Resolution"]):
            checkSurroundingPixels(checkNext[0], checkNext[1], pixels, output_image, list_with_new_pixels)

    iterateList = list_with_new_pixels.copy()
    list_with_new_pixels = []
    pixels = numpy.copy(output_image)
    for checkNext in iterateList:
        if checkNext[0]-1 >= 0 and checkNext[0]+1 < int(originalObject["Impostor Resolution"]) and checkNext[1]-1 >= 0 and checkNext[1]+1 < int(originalObject["Impostor Resolution"]):
            checkSurroundingPixels(checkNext[0], checkNext[1], output_image, pixels, list_with_new_pixels)


    marginImage = bpy.data.images.new(originalObject.name + "_" + fileName + ".png", alpha=False, width=originalObject["Impostor Resolution"], height=originalObject["Impostor Resolution"])
    marginImage.filepath = saveFilePath + originalObject.name + "_" + fileName + ".png"
    marginImage.file_format = 'PNG'
    marginImage.pixels = pixels.ravel()  #flatten the array to 1 dimension and write it to testImg pixels
    marginImage.save()
    return True

class SetPinOperator(bpy.types.Operator):
    bl_idname = "object.setpin"
    bl_label = "SetPin"
    bl_description = ""
    bl_options = {"REGISTER"}

    def execute(self, context):

        for vert in context.object.data.vertices:
            vert.select = vert.index % 2 == 0
        
        bpy.ops.object.editmode_toggle()
        for loop in context.object.data.loops :
            uv_coords = context.object.data.uv_layers.active.data[loop.index].uv
            print(uv_coords)

        return {'FINISHED'}

class BakeAndCreateImpostorOperator(bpy.types.Operator):
    bl_idname = "object.bakeandcreateimpostor"
    bl_label = "Bake And Create Impostor"
    bl_description = ""
    bl_options = {"REGISTER"}

    def execute(self, context):

        class rotation:
            def __init__(self,maxX = 0,minX = 0):
                self.maxX = maxX
                self.minX = minX
        
            rotation = 0
            direction = (0, 0, 0)

        class collectionVisibility:
            def __init__(self,collection,visible = False):
                self.collection = collection
                self.visible = visible
                self.name = collection.name

        originalObject = context.object
        if bpy.context.object.data.users == 1:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        if originalObject.type != "MESH":
            self.report({'ERROR_INVALID_INPUT'}, 'You need to select an object of type Mesh')
            return {'CANCELLED'}

        #---------------preferences---------------#
        p_bake_normal = context.preferences.addons[__package__].preferences.bake_normal_map
        p_bake_OBN_map = context.preferences.addons[get_name()].preferences.bake_OBN_map
        p_bake_TBN_map = context.preferences.addons[__package__].preferences.bake_TBN_map
        p_bake_depth_map = context.preferences.addons[__package__].preferences.bake_depth_map
        p_bake_mask_map = context.preferences.addons[__package__].preferences.bake_mask_map

        p_suffix_margin = context.preferences.addons[__package__].preferences.suffix_margin
        p_margin_base_color_map = context.preferences.addons[__package__].preferences.margin_base_color_map
        p_margin_OBN_map = context.preferences.addons[__package__].preferences.margin_OBN_map
        p_margin_TBN_map = context.preferences.addons[__package__].preferences.margin_TBN_map
        p_margin_depth_map = context.preferences.addons[__package__].preferences.margin_depth_map

        p_suffix_Base_color = context.preferences.addons[__package__].preferences.suffix_Base_color
        p_suffix_normal = context.preferences.addons[__package__].preferences.suffix_normal
        p_suffix_OBN = context.preferences.addons[__package__].preferences.suffix_OBN
        p_suffix_TBN = context.preferences.addons[__package__].preferences.suffix_TBN
        p_suffix_mask = context.preferences.addons[__package__].preferences.suffix_mask
        p_suffix_depth = context.preferences.addons[__package__].preferences.suffix_depth

        saveFilePath = context.preferences.addons[__package__].preferences.filepath

        if not os.path.exists(saveFilePath):
            print("File path does not exists: " + saveFilePath)
            saveFilePath = ""

        originalObjectCollection = None
        for collection in bpy.data.collections:
            for obj in collection.all_objects:
                if obj.name == originalObject.name:
                    originalObjectCollection = collection
        
        if originalObjectCollection is None:
            originalObjectCollection = bpy.data.collections.new(originalObject.name)
            context.scene.collection.children.link(originalObjectCollection)
        
        layer_collection = context.view_layer.layer_collection
        originalObjectMaxHeight = originalObject.data.vertices[0].co[2]
        originalObjectMinHeight = originalObject.data.vertices[0].co[2]
        originalObjectMaxWidth = math.sqrt(originalObject.data.vertices[0].co[0] ** 2 + originalObject.data.vertices[0].co[1] ** 2)
        bakeObjectScale = 1
        defaultSpp = context.scene.cycles.samples
        defaultCamera = context.scene.camera
        defaultResolution = (context.scene.render.resolution_x, context.scene.render.resolution_y)
        dist = 0.0
        bake_spheres = []
        bake_objects = []
        # if the original object dosn't have a material create one
        if len(originalObject.material_slots) ==  0 or originalObject.material_slots[0].material == None:
            default_mat = bpy.data.materials.new(name="NoMaterial") #set new material to variable
            default_mat.use_nodes = True
            originalObject.data.materials.append(default_mat) #add the material to the object
        for idx, thisMaterialSlot in enumerate(originalObject.material_slots):
            if thisMaterialSlot.material == None:
                originalObject.active_material_index = idx
                bpy.ops.object.material_slot_remove()

        originalObject_material_conections = []
        for this_matslot in originalObject.material_slots:
            originalObject_material_conections.append(this_matslot.material.node_tree.nodes["Material Output"].inputs[0].links[0].from_socket)
        #defaultRotation = copy.deepcopy(originalObject.rotation_euler)
        originalObject.rotation_euler = (0.0, 0.0, 0.0)
        
        #if bpy.data.is_saved == False:
        #    self.report({'ERROR_INVALID_INPUT'}, 'You need to Save the file')
        #    return {'CANCELLED'}

        if not bpy.data.filepath:
            if saveFilePath == "//" or saveFilePath == "":
                self.report({'ERROR_INVALID_INPUT'}, 'You need to Save the file or set the output directory to a global path via the addon settings panel')
                return {'CANCELLED'}
        elif saveFilePath == "":
            #saveFilePath = bpy.data.filepath
            saveFilePath = bpy.path.abspath("//")
            print(saveFilePath)
            #self.report({'ERROR_INVALID_INPUT'}, 'You need to set an output directory in the addon settings panel')
            #return {'CANCELLED'}




        #save Collection Visibility
        collectionsVisibility = []
        for thisCollection in context.view_layer.layer_collection.children:
            collectionsVisibility.append(collectionVisibility(thisCollection, thisCollection.exclude))

        if originalObject.get("Impostor UV Margin") is None:
            originalObject["Impostor UV Margin"] = 0.01

        if originalObject.get("Impostor Mesh Margin") is None:
            originalObject["Impostor Mesh Margin"] = 4

        if originalObject.get("Impostor Rotations") is None:
            originalObject["Impostor Rotations"] = 27

        if originalObject.get("Impostor Samples") is None:
            originalObject["Impostor Samples"] = 16

        if originalObject.get("Impostor Resolution") is None:
            originalObject["Impostor Resolution"] = 256

        Impostor_uv_margin = float(originalObject["Impostor UV Margin"])
        ImpostorMargin = int(originalObject["Impostor Mesh Margin"])
        RotateSteps = int(originalObject["Impostor Rotations"])
        rotations = [rotation(0,0)]

        print("Start")

        #Set originalObjectMaxHeight and originalObjectMinHeight
        for vert in originalObject.data.vertices:              
                if vert.co[2] > originalObjectMaxHeight:
                    originalObjectMaxHeight = vert.co[2]
                if vert.co[2] < originalObjectMinHeight:
                    originalObjectMinHeight = vert.co[2]
                if math.sqrt(vert.co[0] ** 2 + vert.co[1] ** 2) > originalObjectMaxWidth:
                    originalObjectMaxWidth = math.sqrt(vert.co[0] ** 2 + vert.co[1] ** 2)
        #print("originalObjectMaxHeight = " + str(originalObjectMaxHeight))
        #print("originalObjectMaxWidth = " + str(originalObjectMaxWidth))

        #create convexer node group
        Convexer = bpy.data.node_groups.new("Convexer", "GeometryNodeTree")
        Convexer.nodes.new("NodeGroupInput")
        Convexer.nodes.new("NodeGroupOutput")
        Convexer.nodes.new("GeometryNodeConvexHull")
        Convexer.links.new(Convexer.nodes['Convex Hull'].inputs[0], Convexer.nodes['Group Input'].outputs[0])
        Convexer.links.new(Convexer.nodes['Group Output'].inputs[0], Convexer.nodes['Convex Hull'].outputs[0])

        #create convex mesh
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
        convex_mesh = bpy.context.active_object
        convex_mesh.modifiers.new("Convex", "NODES")
        convex_mesh.modifiers['Convex'].node_group = Convexer
        bpy.ops.object.modifier_apply(modifier="Convex")

        # Fill "rotations" Array
        for x in range(0, RotateSteps):

            #flipedNumber = False

            #print(len(rotations))
            if len(rotations) <= x:
                rotations.append(rotation(0,0))

            #overPi = False
            radiantRotation = math.radians((x * (360 / RotateSteps)) * (-1))
            if radiantRotation >= math.pi:
                radiantRotation = math.radians(x * (360 / RotateSteps)) - 2 * math.pi
                #overPi = True

            for vert in convex_mesh.data.vertices:
                rotations[x].rotation = x * (360 / RotateSteps)
                rotations[x].direction = (math.cos(radiantRotation), math.sin(radiantRotation), 0.0)
                dist = numpy.dot(rotations[x].direction, (numpy.subtract((vert.co), (0, 0, 0))))
                if rotations[x].maxX < dist:
                    rotations[x].maxX = dist
                      
                if rotations[x].minX > dist:
                    rotations[x].minX = dist
            print("Rotation = " + str(x) + "  MaxX = " + str(rotations[x].maxX) + "  MinX = " + str(rotations[x].minX) + "  Rotation = " + str(rotations[x].rotation))
        #delete Convex hull
        bpy.ops.object.delete()

        #unhide Collection
        for thisCol in bpy.data.collections:
            if thisCol.name == originalObject.name + "_BakeCollection":
                recurLayerCollection(layer_collection, thisCol.name).exclude = False

        #delete old objects
        bpy.ops.object.select_all(action='DESELECT')
        for ob in context.scene.objects:
            if ob.type == 'MESH' and ob.name.startswith(originalObject.name + '_Impostor_'):
                for thisCollection in context.view_layer.layer_collection.children:
                    for this_ob in thisCollection.collection.objects:
                        if this_ob == ob:
                            thisCollection.exclude = False
                ob.select_set(state=True)

            if ob.type == 'MESH' and ob.name.startswith(originalObject.name + '_BakeObject_'):
                ob.select_set(state=True)
                
            if ob.name == originalObject.name + '_Camera':
                ob.select_set(state=True)
                if ob == defaultCamera:
                    defaultCamera = None
                
            bpy.ops.object.delete(use_global=False, confirm=False)

        #Create Cards
        for index in range(len(rotations)):
            bpy.ops.mesh.primitive_plane_add(calc_uvs=True, location=(originalObject.location.x - ((rotations[0].maxX - rotations[0].minX) * 2), originalObject.location.y, originalObject.location.z))

            #Set new object name
            context.object.name = originalObject.name + '_Impostor_' + str(index + 1)

            #Set X rotation
            context.object.rotation_euler.x = math.radians(90)

            #Set Z Rotation
            context.object.rotation_euler.z = (math.radians((index * (360 / RotateSteps)) * (-1)))
    
            #set Verts position
            margin_multiplicator = (100 + ImpostorMargin) / 100
            context.object.data.vertices[0].co = (rotations[index].minX * margin_multiplicator, originalObjectMinHeight * margin_multiplicator, 0)
            context.object.data.vertices[1].co = (rotations[index].maxX * margin_multiplicator, originalObjectMinHeight * margin_multiplicator, 0)
            context.object.data.vertices[2].co = (rotations[index].minX * margin_multiplicator, originalObjectMaxHeight * margin_multiplicator, 0)
            context.object.data.vertices[3].co = (rotations[index].maxX * margin_multiplicator, originalObjectMaxHeight * margin_multiplicator, 0)
     
            context.object.select_set(state=True)
            bpy.ops.object.editmode_toggle()
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
            bpy.ops.object.editmode_toggle()
            SetUVsToStorePivotOffset(context.object)



            #Create VertexColors
            # create a new euler with default axis rotation order
            eul = mathutils.Euler((context.object.rotation_euler[0], context.object.rotation_euler[1], context.object.rotation_euler[2]), 'XYZ')
        
            vec = mathutils.Vector((0.0, 0.0, 1.0))
            vec.rotate(eul)
        
            if not context.object.data.vertex_colors:
               context.object.data.vertex_colors.new()
            else:
                for this_vertex_color in context.object.data.vertex_colors:
                    context.object.data.vertex_colors.remove(this_vertex_color)
                context.object.data.vertex_colors.new()
        
            color_layer = context.object.data.vertex_colors["Col"]

            VcolAlpha = random.random()
            i = 0
            for poly in context.object.data.polygons:
                for idx in poly.loop_indices:
                    RotationColor = (vec + mathutils.Vector((1.0, 1.0, 1.0))) / 2.0
                    color_layer.data[i].color = mathutils.Vector((RotationColor[0], RotationColor[1], RotationColor[2], VcolAlpha))
                    i += 1





        #--------------Pack-UVs--------------#
        #for every Object in the scene select impostor planes
        bpy.ops.object.select_all(action='DESELECT')
        for ob in context.scene.objects:
            if ob.type == 'MESH' and originalObject.name + '_Impostor_' in ob.name:
                ob.select_set(state=True)
        
        bpy.ops.object.join()
        
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.select_all(action='SELECT')
        #bpy.ops.uv.average_islands_scale()
        
        bpy.ops.mesh.select_all(action='SELECT')
        #bpy.ops.uv.reset()


        #select all even vertices for UV pinning
        for vert in context.object.data.vertices:
            vert.select = vert.index % 2 == 0
        
        me = bpy.context.object.data
        
        bm = bmesh.new()   # create an empty BMesh
        bm.from_mesh(me)   # fill it in from a Mesh
        uv_layer = bm.loops.layers.uv[0]

        for face in bm.faces:
            for loop in face.loops:
                #print(loop[uv_layer].uv)
                if loop.index % 4 == 0:
                    loop[uv_layer].uv = mathutils.Vector((0.0, 0.0))
                    loop[uv_layer].pin_uv = True
                    #print("Pin")
                elif loop.index % 4 == 1:
                    loop[uv_layer].uv = mathutils.Vector((1.0, 0.0))
                    loop[uv_layer].pin_uv = True
                    #print("Pin")
                    
                
                #if loop[uv_layer].uv.x <= 0.01:   
                #    loop[uv_layer].pin_uv = True
                #    print("Pin")
        bpy.ops.object.editmode_toggle()
        bm.to_mesh(me)
        bm.free()

        bpy.context.active_object.data.uv_layers[0].active = True
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.uv.pack_islands(rotate=False, margin=Impostor_uv_margin)
        #bpy.ops.object.editmode_toggle()
        
        
        
        #bpy.ops.object.editmode_toggle()
        # area1 = getUvArea(me)
    
        # bpy.ops.mesh.uv_texture_add()
        #bpy.ops.object.editmode_toggle()
        bpy.ops.uv.select_all(action='SELECT')
        bpy.ops.uv.average_islands_scale()
        bpy.ops.uv.pack_islands(rotate=False, margin=Impostor_uv_margin)
        bpy.ops.uv.pack_islands(rotate=False, margin=Impostor_uv_margin)
        bpy.ops.uv.pack_islands(rotate=False, margin=Impostor_uv_margin)
        bpy.ops.object.editmode_toggle()
        # area2 = getUvArea(me)
        
        # print(str(area1) + str(area2))
        # if area1 < area2:
        #     context.object.data.uv_layers.remove(context.object.data.uv_layers[1])
        # else:
        #     context.object.data.uv_layers.remove(context.object.data.uv_layers[0])
        #     context.object.data.uv_layers[0].name = "UVMap"


        # area1 = getUvArea(me)
    
        # bpy.ops.mesh.uv_texture_add()
        # bpy.ops.object.editmode_toggle()
        # bpy.ops.uv.select_all(action='SELECT')
        # bpy.ops.uv.average_islands_scale()
        # bpy.ops.uv.pack_islands(rotate=False, margin=0.01)
        # bpy.ops.object.editmode_toggle()
        # area2 = getUvArea(me)
        
        # print(str(area1) + str(area2))
        # if area1 < area2:
        #     context.object.data.uv_layers.remove(context.object.data.uv_layers[1])
        # else:
        #     context.object.data.uv_layers.remove(context.object.data.uv_layers[0])
        #     context.object.data.uv_layers[0].name = "UVMap"
        
        impostor = context.object

        #---------_create new collection_---------#
        for thisCollection in context.scene.collection.children:
            if thisCollection.name == originalObject.name + '_BakeCollection':
                #check if originalobject is in the Collection
                for thisObject in thisCollection.objects:
                    if thisObject.name == originalObject.name:
                        originalObjectCollection = bpy.data.collections[0]
                        #if originalObject not in bpy.data.collections[0].objects:
                        if not(elem.name == originalObject.name for elem in bpy.data.collections[0].objects):
                            bpy.data.collections[0].objects.link(originalObject)
                        thisCollection.objects.unlink(originalObject)                     
                context.scene.collection.children.unlink(thisCollection)
                bpy.data.collections.remove(thisCollection)
        
        bakeCollection = bpy.data.collections.new(originalObject.name + '_BakeCollection')
        context.scene.collection.children.link(bakeCollection)
        totalUnlink(originalObject)
        bakeCollection.objects.link(originalObject)
         
        #move impostor to the bake collection
        totalUnlink(impostor)
        bakeCollection.objects.link(impostor)
        
        #Hide all other Collections
        for thisCol in bpy.data.collections:
            if thisCol.name == originalObject.name + "_BakeCollection":
                recurLayerCollection(layer_collection, thisCol.name).exclude = False
            else:
                recurLayerCollection(layer_collection, thisCol.name).exclude = True
    
        
        #---------_Add Camera_---------#
        leftCameraPoint = originalObject.location.x + ((rotations[0].maxX + 0.2) * 1.5)
        rightCameraPoint = leftCameraPoint + 10
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.camera_add(location=((rightCameraPoint - leftCameraPoint) / 2 + leftCameraPoint, -10, originalObject.location.z), rotation=(math.radians(90), 0, math.radians(0)))
        BakeCamera = context.object
        bpy.ops.object.rotation_clear(clear_delta=False)
        BakeCamera.rotation_euler = (math.radians(90), 0, 0)
        
        totalUnlink(BakeCamera)
        bakeCollection.objects.link(BakeCamera)
        BakeCamera.scale = (1, 1, 1)
        BakeCamera.data.type = 'ORTHO'
        BakeCamera.data.ortho_scale = 10
        BakeCamera.name = originalObject.name + "_Camera"
        context.scene.render.resolution_y = int(originalObject["Impostor Resolution"])
        context.scene.render.resolution_x = int(originalObject["Impostor Resolution"])
        context.scene.camera = BakeCamera
        BakeCamera.select_set(state=False)
        bpy.ops.object.select_all(action='DESELECT')


        #---------_create Bake objects_---------#
        originalObject.select_set(state=True)
        for index in range(len(rotations)):
            newObject = originalObject.copy()
            bakeCollection.objects.link(newObject)         
            
            try:
                vert0 = (impostor.data.uv_layers.active.data[index * 4 + 4].uv.x * 10 + leftCameraPoint, impostor.data.uv_layers.active.data[index * 4 + 4].uv.y * 10)
                vert2 = (impostor.data.uv_layers.active.data[index * 4 + 2 + 4].uv.x * 10 + leftCameraPoint, impostor.data.uv_layers.active.data[index * 4 + 2 + 4].uv.y * 10)
            except:
                vert0 = (impostor.data.uv_layers.active.data[0].uv.x * 10 + leftCameraPoint, impostor.data.uv_layers.active.data[0].uv.y * 10)
                vert2 = (impostor.data.uv_layers.active.data[2].uv.x * 10 + leftCameraPoint, impostor.data.uv_layers.active.data[2].uv.y * 10)

            margin_scale_multiplicator = (100 + (ImpostorMargin * 1)) / 100
            vert02Distance = (vert2[1] - vert0[1]) * (1 / margin_scale_multiplicator)

            scale = (vert2[1] - vert0[1]) / (originalObjectMaxHeight - originalObjectMinHeight)
            scale2 = vert02Distance / (originalObjectMaxHeight - originalObjectMinHeight)
            bakeObjectScale = scale
            
            newObject.location.x = vert0[0] + (rotations[index].minX * -1) * scale
            newObject.location.z = ((vert0[1]) - 5) - (originalObjectMinHeight * scale) + originalObject.location.z
            newObject.location.y = rotations[index].rotation
            newObject.name = originalObject.name + "_BakeObject_" + str(index)
            newObject.scale[0] = scale2
            newObject.scale[1] = scale2
            newObject.scale[2] = scale2
    
            newObject.rotation_euler[2] = math.radians(rotations[index].rotation)  
            bake_objects.append(newObject)

            #---------_create bent normal sphere_---------#
            movementX = ((rotations[0].minX - rotations[0].maxX) / 2) * scale
            thisNewScale = pow(pow(originalObject.dimensions.x, 2) + pow(originalObject.dimensions.y, 2) + pow(originalObject.dimensions.z, 2), 0.5) * scale
            shere_scale = (360 / RotateSteps) #360 is the maximum distance the spheres have on the Y axis
            # bake_sphere = create_spere(bakeCollection, newObject.location.x, newObject.location.y, newObject.location.z, (360 / RotateSteps) * 0.5 - 0.5)
            bake_sphere = create_spere(bakeCollection, newObject.location.x, newObject.location.y, newObject.location.z + (((originalObjectMaxHeight - originalObjectMinHeight) * scale) / 2), shere_scale)
            bake_sphere.display_type = 'BOUNDS'
            bake_sphere.display_bounds_type = 'SPHERE'

            bake_sphere.visible_camera = False
            # bake_sphere.cycles_visibility.camera = False
            bake_sphere.hide_render = True
            bake_spheres.append(bake_sphere)

            if bpy.data.materials.find("BakeBentNormal") == -1:
                BakeBentNormal_mat = bpy.data.materials.new("BakeBentNormal")
                bake_sphere.data.materials.append(BakeBentNormal_mat)
                BakeBentNormal_mat.use_nodes = True
                BakeBentNormal_mat.node_tree.nodes.clear()

                # create output node
                node_output = BakeBentNormal_mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')   
                node_output.location = 600,0

                # create Geometry node
                node_Geometry = BakeBentNormal_mat.node_tree.nodes.new(type='ShaderNodeNewGeometry')   
                node_Geometry.location = -800,0

                # create VectorMultiply node
                node_VectorMultiply01 = BakeBentNormal_mat.node_tree.nodes.new(type='ShaderNodeVectorMath')   
                node_VectorMultiply01.location = -600,0
                node_VectorMultiply01.operation = 'MULTIPLY'
                node_VectorMultiply01.inputs[1].default_value = (-1, 1, -1)

                # create VectorRotate node
                node_VectorRotate01 = BakeBentNormal_mat.node_tree.nodes.new(type='ShaderNodeVectorRotate')   
                node_VectorRotate01.location = -400,0
                node_VectorRotate01.rotation_type = 'Z_AXIS'
                node_VectorRotate01.label = "VectorRotate01"

                # create Emission node
                node_Emission = BakeBentNormal_mat.node_tree.nodes.new(type='ShaderNodeEmission')   
                node_Emission.location = 400,0
                node_Emission.label = "Emission"

                # create object info node
                node_ObjectInfo = BakeBentNormal_mat.node_tree.nodes.new(type='ShaderNodeObjectInfo')   
                node_ObjectInfo.location = -1000,-300

                # creat SeparateXYZ node
                node_SeparateXYZ = BakeBentNormal_mat.node_tree.nodes.new(type='ShaderNodeSeparateXYZ')   
                node_SeparateXYZ.location = -800,-300

                # creat ToRadians node
                node_ToRadians = BakeBentNormal_mat.node_tree.nodes.new(type='ShaderNodeMath')
                node_ToRadians.location = -600,-300
                node_ToRadians.operation = 'RADIANS'

                # create VectorMultiply node
                node_VectorMultiply03 = BakeBentNormal_mat.node_tree.nodes.new(type='ShaderNodeVectorMath')   
                node_VectorMultiply03.location = -600,-600
                node_VectorMultiply03.operation = 'MULTIPLY'
                node_VectorMultiply03.inputs[1].default_value = (-1, -1, 1)

                # create VectorRotate node
                node_VectorRotate02 = BakeBentNormal_mat.node_tree.nodes.new(type='ShaderNodeVectorRotate')   
                node_VectorRotate02.location = -400,-600
                node_VectorRotate02.rotation_type = 'EULER_XYZ'
                node_VectorRotate02.inputs[4].default_value = (1.5708, 3.14159, 3.14159)
                node_VectorRotate02.label = "VectorRotate02"


                BakeBentNormal_mat.node_tree.links.new(node_Emission.outputs[0], node_output.inputs[0])
                BakeBentNormal_mat.node_tree.links.new(node_VectorRotate01.outputs[0], node_Emission.inputs[0])
                BakeBentNormal_mat.node_tree.links.new(node_VectorMultiply01.outputs[0], node_VectorRotate01.inputs[0])
                BakeBentNormal_mat.node_tree.links.new(node_Geometry.outputs["Incoming"], node_VectorMultiply01.inputs[0])
                BakeBentNormal_mat.node_tree.links.new(node_ObjectInfo.outputs[0], node_SeparateXYZ.inputs[0])
                BakeBentNormal_mat.node_tree.links.new(node_SeparateXYZ.outputs[1], node_ToRadians.inputs[0])
                BakeBentNormal_mat.node_tree.links.new(node_ToRadians.outputs[0], node_VectorRotate01.inputs["Angle"])
                BakeBentNormal_mat.node_tree.links.new(node_Geometry.outputs["Incoming"], node_VectorMultiply03.inputs[0])
                BakeBentNormal_mat.node_tree.links.new(node_VectorMultiply03.outputs[0], node_VectorRotate02.inputs[0])
            else:
                BakeBentNormal_mat = bpy.data.materials[bpy.data.materials.find("BakeBentNormal")]
                bake_sphere.data.materials.append(BakeBentNormal_mat)

        if originalObject.material_slots.items() == []:
            defaultMaterial = bpy.data.materials.new(name="DefaultMaterial")
            originalObject.data.materials.append(defaultMaterial)
            originalObject.active_material.use_nodes = True
        context.scene.cycles.film_transparent = True
        context.scene.render.film_transparent = True
        context.scene.cycles.use_square_samples = False
        # context.scene.render.tile_y = 64
        # context.scene.render.tile_x = 64
        context.scene.cycles.samples = int(originalObject["Impostor Samples"])
        if str(saveFilePath).startswith('<_PropertyDeferred'):
            saveFilePath = bpy.data.filepath.removesuffix(bpy.path.basename(bpy.context.blend_data.filepath))
            print(saveFilePath)

        context.scene.render.filepath = str(saveFilePath) + str(originalObject.name) + "_" + p_suffix_Base_color + ".png"
        bpy.ops.render.render(write_still=True)
        
        
        #---------_Material_---------# 
        # impostor
        mat = bpy.data.materials.new(name="MaterialName") #set new material to variable
        impostor.data.materials.append(mat) #add the material to the object
        mat.use_backface_culling = True
        impostor.active_material.use_nodes = True
        mat.blend_method = 'BLEND'
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 0, 0, 1) #change color


        # clear all nodes to start clean
        for node in mat.node_tree.nodes:
            mat.node_tree.nodes.remove(node)

        # create output node
        node_output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')   
        node_output.location = 200,0

        # create Texture node
        node_texture = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        node_texture.location = -300,0

        img_D = bpy.data.images.load(filepath=saveFilePath + originalObject.name + "_" + p_suffix_Base_color + ".png")
        node_texture.image = img_D

        # create Normal Texture node
        node_textureNormal = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        node_textureNormal.location = -900,-300

        node_sep = mat.node_tree.nodes.new(type='ShaderNodeSeparateRGB')
        node_sep.location = -600,-300

        node_sub = mat.node_tree.nodes.new(type='ShaderNodeMath')
        node_sub.location = -400,-500
        node_sub.operation = 'SUBTRACT'
        node_sub.inputs[0].default_value = 1

        node_comb = mat.node_tree.nodes.new(type='ShaderNodeCombineRGB')
        node_comb.location = -200,-300
        
        # create ShaderNodeNormalMap
        node_ShaderNodeNormalMap = mat.node_tree.nodes.new(type='ShaderNodeNormalMap')   
        node_ShaderNodeNormalMap.location = 0,-200
        if p_bake_OBN_map:
            node_ShaderNodeNormalMap.space = 'OBJECT'
        else:
            node_ShaderNodeNormalMap.space = 'TANGENT'

        #---------_Create Node Group MeshNormal if non exists_---------##----------_Create Node Group Impostor_----------#
        groupMeshNormalExists = False
        groupExists = False
        for currentGroup in bpy.data.node_groups:
            if currentGroup.name == "MeshNormal":
                groupMeshNormal = currentGroup
                groupMeshNormalExists = True
            if currentGroup.name == "ImpostorGroup":
                group = currentGroup
                groupExists = True
        if groupMeshNormalExists == False:
            groupMeshNormal = CreateNodeGroupMeshNormal()
        if groupExists == False:
            group = CreateNodeGroupImpostor()

        node_group = mat.node_tree.nodes.new("ShaderNodeGroup")
        node_group.node_tree = group

        defaultNumber = RotateSteps
        node_group.inputs[2].default_value = defaultNumber

        mat.node_tree.links.new(node_texture.outputs[0], node_group.inputs[0])
        mat.node_tree.links.new(node_texture.outputs[1], node_group.inputs[1])
        mat.node_tree.links.new(node_textureNormal.outputs[0], node_sep.inputs[0])
        mat.node_tree.links.new(node_sep.outputs[0], node_comb.inputs[0])
        if p_bake_OBN_map:
            mat.node_tree.links.new(node_sep.outputs[1], node_sub.inputs[1])
            mat.node_tree.links.new(node_sub.outputs[0], node_comb.inputs[1])
        else:
            mat.node_tree.links.new(node_sep.outputs[1], node_comb.inputs[1])
        mat.node_tree.links.new(node_sep.outputs[2], node_comb.inputs[2])     
        mat.node_tree.links.new(node_comb.outputs[0], node_ShaderNodeNormalMap.inputs[1])
        if p_bake_OBN_map or p_bake_TBN_map or p_bake_normal:
            mat.node_tree.links.new(node_ShaderNodeNormalMap.outputs[0], node_group.inputs[3])
        mat.node_tree.links.new(node_group.outputs[0], node_output.inputs[0])

        #Apply the groupMeshNormal node to all materials from the originalObject with transparency
        previouslyConnectedNodeSocketFrom = []
        previouslyConnectedNodeSocketTo = []
        for thisMaterial in originalObject.data.materials:
            thisMaterial.use_nodes = True
            node_groupNormal = thisMaterial.node_tree.nodes.new(type='ShaderNodeGroup')
            node_groupNormal.node_tree = groupMeshNormal
            node_groupNormal.location = 0,500
            node_groupNormal.label = "Test"

            for thisNode in thisMaterial.node_tree.nodes:
                if thisNode.type == "OUTPUT_MATERIAL":
                    thisPreviousNode = thisNode.inputs['Surface'].links[0].from_node
                    if thisPreviousNode.type == "MIX_SHADER":
                        thisUseMix = False
                        thisOldConectedNode = thisPreviousNode
                        connectedSocket = thisNode.inputs['Surface']
                        if thisPreviousNode.inputs[1].links[0].from_node.type == "BSDF_TRANSPARENT":
                            thisOldConectedNode = thisPreviousNode.inputs[2].links[0].from_node
                            thisUseMix = True
                            connectedSocket = thisPreviousNode.inputs[2]
                            previouslyConnectedNodeSocketTo.append(thisPreviousNode.inputs[2])
                            previouslyConnectedNodeSocketFrom.append(thisPreviousNode.inputs[2].links[0].from_socket)
                            thisMaterial.node_tree.links.remove(thisPreviousNode.inputs[2].links[0])
                        elif thisPreviousNode.inputs[2].links[0].from_node.type == "BSDF_TRANSPARENT":
                            thisOldConectedNode = thisPreviousNode.inputs[1].links[0].from_node
                            thisUseMix = True
                            connectedSocket = thisPreviousNode.inputs[1]
                            previouslyConnectedNodeSocketTo.append(thisPreviousNode.inputs[1])
                            previouslyConnectedNodeSocketFrom.append(thisPreviousNode.inputs[1].links[0].from_socket)
                            thisMaterial.node_tree.links.remove(thisPreviousNode.inputs[1].links[0])
                        if thisUseMix == False:
                            previouslyConnectedNodeSocketTo.append(thisNode.inputs['Surface'])
                            previouslyConnectedNodeSocketFrom.append(thisNode.inputs['Surface'].links[0].from_socket)
                            thisMaterial.node_tree.links.remove(thisNode.inputs['Surface'].links[0])
                        # links
                        thisMaterial.node_tree.links.new(node_groupNormal.outputs[0], connectedSocket)
                    else:
                        previouslyConnectedNodeSocketTo.append(thisNode.inputs['Surface'])
                        previouslyConnectedNodeSocketFrom.append(thisNode.inputs['Surface'].links[0].from_socket)
                        thisMaterial.node_tree.links.new(node_groupNormal.outputs[0], thisNode.inputs['Surface'])

        #----------------------_Normal_----------------------#
        use_denoising = bpy.context.scene.cycles.use_denoising
        bpy.context.scene.cycles.use_denoising = False
        context.scene.display_settings.display_device = 'None'
        context.scene.cycles.film_transparent = False
        context.scene.cycles.samples = 64
        context.scene.render.film_transparent = False
        needsUnlink = False
        
        #CreateBackgroundPlane
        if bpy.data.objects.find(originalObject.name + "Background") == -1:
            bpy.ops.mesh.primitive_plane_add(size=11, enter_editmode=False, location=(BakeCamera.location.x, BakeCamera.location.y + 15, BakeCamera.location.z))
            bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
            bpy.context.object.location[1] = 370

            backgroundPlane = context.object
            bakeCollection.objects.link(backgroundPlane)
            bpy.context.collection.objects.unlink(backgroundPlane)
            backgroundPlane.name = originalObject.name + "Background"
            backgroundPlaneMat = bpy.data.materials.new(name="NormalMaterial") #set new material to variable
            backgroundPlane.data.materials.append(backgroundPlaneMat) #add the material to the object
            backgroundPlane.active_material.use_nodes = True
            for thisNode in backgroundPlaneMat.node_tree.nodes:
                if thisNode.type != "OUTPUT_MATERIAL":
                    backgroundPlaneMat.node_tree.nodes.remove(thisNode)
                else:
                    background_Node_Output = thisNode
            node_group_Normal = backgroundPlaneMat.node_tree.nodes.new("ShaderNodeGroup")
            node_group_Normal.node_tree = groupMeshNormal
            node_group_Normal.location = -300,-300
            backgroundPlaneMat.node_tree.links.new(node_group_Normal.outputs[0], background_Node_Output.inputs[0])
        else:
            backgroundPlane = bpy.data.objects[originalObject.name + "Background"]
            backgroundPlane.hide_render = False
            if bpy.context.collection != bakeCollection:
                bpy.context.collection.objects.link(backgroundPlane)
                needsUnlink = True
            backgroundPlaneMat = backgroundPlane.material_slots[0].material
            for thisNode in backgroundPlaneMat.node_tree.nodes:
                if thisNode.type != "OUTPUT_MATERIAL":
                    backgroundPlaneMat.node_tree.nodes.remove(thisNode)
                else:
                    background_Node_Output = thisNode
            node_group_Normal = backgroundPlaneMat.node_tree.nodes.new("ShaderNodeGroup")
            node_group_Normal.node_tree = groupMeshNormal
            node_group_Normal.location = -300,-300
            backgroundPlaneMat.node_tree.links.new(node_group_Normal.outputs[0], background_Node_Output.inputs[0])


        context.scene.render.filepath = saveFilePath + originalObject.name + "_" + p_suffix_normal + ".png"
        if p_bake_normal:
            bpy.ops.render.render(write_still=True)
        context.scene.render.film_transparent = True

        backgroundPlane.hide_render = True
        if needsUnlink:
            bpy.context.collection.objects.unlink(backgroundPlane)
        #bpy.ops.object.delete(use_global=False, confirm=False)


        #----------------------Render Depth----------------------
        #socket_conect = []
        groupMeshDepth = CreateNodeGroupDepth(originalObjectMaxWidth, bakeObjectScale, originalObject.location.y)
        for thisMaterial in originalObject.data.materials:
            for thisNode in thisMaterial.node_tree.nodes:
                if thisNode.type == "GROUP" and thisNode.label == "Test":
                    thisNode.node_tree = groupMeshDepth
                    #thisNode.inputs[0].default_value = (originalObjectMaxWidth * bakeObjectScale) - originalObject.location.y
                    thisNode.inputs[0].default_value = (originalObjectMaxWidth * bakeObjectScale)
                    thisNode.inputs[1].default_value = 1 / ((originalObjectMaxWidth * bakeObjectScale) * 2)
                    # for loopNode in thisMaterial.node_tree.nodes:
                    #     if loopNode.type == "OUTPUT_MATERIAL":
                    #         outp = loopNode
                    # thisMaterial.node_tree.links.new(thisNode.outputs[0], outp.inputs[0])
                    #socket_conect.append(get_transparent_material_output_inputSocket(thisMaterial).links[0].from_socket)
                    thisMaterial.node_tree.links.new(thisNode.outputs[0], get_transparent_material_output_inputSocket(thisMaterial))
                    
        context.scene.render.filepath = saveFilePath + originalObject.name + "_" + p_suffix_depth + ".png"
        if p_bake_depth_map:
            bpy.ops.render.render(write_still=True)
        
        # for index, every_old_socket in enumerate(socket_conect):
        #     this_material = originalObject.data.materials[index]
        #     node_outut = this_material.node_tree.nodes["Material Output"]
        #     thisMaterial.node_tree.links.new(every_old_socket, node_outut.inputs[0])


        #----------------------Compositor----------------------
        bpy.context.scene.cycles.filter_width = 0.01
        bpy.context.scene.use_nodes = True
        compositor_tree = bpy.context.scene.node_tree
        compositor_tree.nodes.clear()

        #CompositorNodeRLayers and CompositorNodeComposite cant be saved as a variable
        compositor_tree.nodes.new(type="CompositorNodeRLayers")
        compositor_tree.nodes["Render Layers"].location = -300,0
        compositor_tree.nodes.new(type="CompositorNodeComposite")
        compositor_tree.nodes["Composite"].location = 400,0
      
        c_node_MixRGB = compositor_tree.nodes.new(type='CompositorNodeMixRGB')
        c_node_MixRGB.inputs[0].default_value = 0.5
        c_node_MixRGB.location = 200,0

        c_group_normalize = compositor_tree.nodes.new("CompositorNodeGroup")
        c_group_normalize.node_tree = get_group_normalize()
        c_group_normalize.location = 0,0

        compositor_tree.links.new(c_node_MixRGB.outputs['Image'], compositor_tree.nodes['Composite'].inputs['Image'])
        compositor_tree.links.new(compositor_tree.nodes["Render Layers"].outputs[0], c_group_normalize.inputs[0])
        compositor_tree.links.new(c_group_normalize.outputs[0], c_node_MixRGB.inputs[1])
        

        #----------------------Bake bent normal----------------------

        # Find Nodes
        for thisMaterialNode in BakeBentNormal_mat.node_tree.nodes:
            if thisMaterialNode.label == "VectorRotate01":
                node_VectorRotate01 = thisMaterialNode
            if thisMaterialNode.label == "VectorRotate02":
                node_VectorRotate02 = thisMaterialNode
            if thisMaterialNode.label == "Emission":
                node_Emission = thisMaterialNode
        
        BakeBentNormal_mat.node_tree.links.new(node_VectorRotate01.outputs[0], node_Emission.inputs[0])

        for this_sphere in bake_spheres:
            this_sphere.hide_render = False
        
        for this_material in bake_objects[0].data.materials:
            node_outut_id = get_transparent_material_output_inputSocket(this_material)
            node_previous = node_outut_id.links[0].from_node

            # create diffuse node
            node_diffuse = this_material.node_tree.nodes.new(type='ShaderNodeBsdfDiffuse')   
            node_diffuse.location = 0,500
            node_diffuse.inputs[0].default_value = (1, 1, 1, 1)
            node_diffuse.label = "killMeAtTheEnd"

            this_material.node_tree.links.new(node_diffuse.outputs[0], node_outut_id)

        bpy.context.scene.cycles.samples = int(originalObject["Impostor Samples"])
        context.scene.render.filepath = saveFilePath + originalObject.name + "_" + p_suffix_OBN + ".png"
        if p_bake_OBN_map:
            bpy.ops.render.render(write_still=True)

        # Bake Tangent Space BentNormals
        
        # BakeBentNormal_mat.node_tree.links.remove(node_VectorRotate01.outputs['Vector'].links[0])
        BakeBentNormal_mat.node_tree.links.new(node_VectorRotate02.outputs[0], node_Emission.inputs[0])
        
        context.scene.render.filepath = saveFilePath + originalObject.name + "_" + p_suffix_TBN + ".png"
        if p_bake_TBN_map:
            bpy.ops.render.render(write_still=True)


        bpy.context.scene.use_nodes = False
        bpy.context.scene.cycles.filter_width = 1.5

        #----------------------Bake the Mask----------------------
        CreateNodeGroupNormalMask()
        bpy.context.scene.render.film_transparent = False

        #Set Background Plane Material
        backgroundPlane.hide_render = False
        needsUnlink = False
        if bpy.context.collection != bakeCollection:
                bpy.context.collection.objects.link(backgroundPlane)
                needsUnlink = True
        for thisNode in backgroundPlaneMat.node_tree.nodes:
            if thisNode.type != "OUTPUT_MATERIAL":
                backgroundPlaneMat.node_tree.nodes.remove(thisNode)
            else:
                background_Node_Output = thisNode
        node_group_emission = backgroundPlaneMat.node_tree.nodes.new("ShaderNodeEmission")
        node_group_emission.inputs[0].default_value = (0, 0, 1, 1)
        node_group_emission.location = -300,-300
        backgroundPlaneMat.node_tree.links.new(node_group_emission.outputs[0], background_Node_Output.inputs[0])

        for ThisMaterialIndex, this_material in enumerate(bake_objects[0].data.materials):
            #find node with label Mask
            node_mask_id = -1
            for index, this_node in enumerate(this_material.node_tree.nodes):
                if this_node.label == "Mask":
                    node_mask_id = index
                    break
            if node_mask_id != -1:
                #node_outut_id = this_material.node_tree.nodes.find("Material Output")
                node_outut_id = previouslyConnectedNodeSocketTo[ThisMaterialIndex]
                #conect the nodes
                #this_material.node_tree.links.new(this_material.node_tree.nodes[node_mask_id].outputs[0], this_material.node_tree.nodes[node_outut_id].inputs[0])
                this_material.node_tree.links.new(this_material.node_tree.nodes[node_mask_id].outputs[0], node_outut_id)
            else:
                #node_outut_id = this_material.node_tree.nodes.find("Material Output")
                node_outut_id = previouslyConnectedNodeSocketTo[ThisMaterialIndex]
                node_emmisive = this_material.node_tree.nodes.new("ShaderNodeEmission")
                node_emmisive.inputs[0].default_value = (0, 0, 0, 1)
                node_emmisive.location = 0,-400
                node_emmisive.label = "Mask"
                #this_material.node_tree.links.new(node_emmisive.outputs[0], this_material.node_tree.nodes[node_outut_id].inputs[0])
                this_material.node_tree.links.new(node_emmisive.outputs[0], node_outut_id)

        #Render the mask
        render_samples = bpy.context.scene.cycles.samples
        render_color_mode = bpy.context.scene.render.image_settings.color_mode
        bpy.context.scene.render.image_settings.color_mode = 'RGB'

        bpy.context.scene.cycles.samples = 16
        context.scene.render.filepath = saveFilePath + originalObject.name + "_" + p_suffix_mask + ".png"
        if p_bake_mask_map:
            bpy.ops.render.render(write_still=True)

        #load OBN_NormalMap
        if p_bake_OBN_map:
            texturNormal = bpy.data.images.load(filepath=saveFilePath + originalObject.name + "_" + p_suffix_OBN + ".png")
        elif p_bake_TBN_map:
            texturNormal = bpy.data.images.load(filepath=saveFilePath + originalObject.name + "_" + p_suffix_TBN + ".png")
        elif p_bake_normal:
            texturNormal = bpy.data.images.load(filepath=saveFilePath + originalObject.name + "_" + p_suffix_normal + ".png")
        else:
            if bpy.data.images.find("NoNormal") == -1:
                texturNormal = bpy.data.images.new("NoNormal", 32,32,)
            else:
                texturNormal = bpy.data.images['NoNormal']

        node_textureNormal.image = texturNormal
        texturNormal.colorspace_settings.name = 'Non-Color'

        #show the mainCollection again
        for thisCol in bpy.data.collections:
            recurLayerCollection(layer_collection, thisCol.name).exclude = False

        #reset values
        bpy.context.scene.render.image_settings.color_mode = render_color_mode
        bpy.context.scene.cycles.samples = render_samples
        backgroundPlane.hide_render = True
        if needsUnlink:
            bpy.context.collection.objects.unlink(backgroundPlane)

        #Change the normal material back
        for thisMaterial in originalObject.data.materials:
            thisMaterial.node_tree.links.new(previouslyConnectedNodeSocketFrom[0], previouslyConnectedNodeSocketTo[0])
            del previouslyConnectedNodeSocketFrom[0]
            del previouslyConnectedNodeSocketTo[0]
            for thisNode in thisMaterial.node_tree.nodes:
                if thisNode.type == "GROUP" and thisNode.label == "Test":
                    thisMaterial.node_tree.nodes.remove(thisNode)

        #connect the materials back
        for idx, this_matslot in enumerate(originalObject.material_slots):
            this_matslot.material.node_tree.links.new(originalObject_material_conections[idx], this_matslot.material.node_tree.nodes["Material Output"].inputs[0])
            for thisMaterialNode in this_matslot.material.node_tree.nodes:
                if thisMaterialNode.label == "killMeAtTheEnd":
                    this_matslot.material.node_tree.nodes.remove( thisMaterialNode )

        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[impostor.name].select_set(True)
        context.view_layer.objects.active = bpy.data.objects[impostor.name]
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        
        totalUnlink(originalObject)
        originalObjectCollection.objects.link(originalObject)
        #move impostor
        totalUnlink(impostor)
        originalObjectCollection.objects.link(impostor)

        context.scene.cycles.samples = defaultSpp
        if defaultCamera is not None:
            context.scene.camera = defaultCamera
        
        context.scene.render.resolution_x = defaultResolution[0]
        context.scene.render.resolution_y = defaultResolution[1]

        #Set vertex colors to store pivot offset
        #SetVertexColors(impostor)
        #SetUVsToStorePivotOffset(impostor)
        #originalObject.rotation_euler = defaultRotation
        #impostor.rotation_euler = defaultRotation
        impostor.scale = originalObject.scale

        context.scene.display_settings.display_device = 'sRGB'
        bpy.context.scene.cycles.use_denoising = use_denoising

        for thisCol in bpy.data.collections:
            if thisCol.name == originalObject.name + "_BakeCollection":
                recurLayerCollection(layer_collection, thisCol.name).exclude = True
      
        for thisCollection in context.view_layer.layer_collection.children:
            for thisSavedCollection in collectionsVisibility:
                try:
                    if thisSavedCollection.name == thisCollection.name:
                        thisCollection.exclude = thisSavedCollection.visible
                except:
                    print("Test01")
        
        #----------------------Fill Images----------------------

        if (p_margin_base_color_map):
            create_margin_for_image(img_D, p_suffix_margin + "_" + p_suffix_Base_color, originalObject, saveFilePath)
        if (p_margin_OBN_map and p_bake_OBN_map):
            img_OBN = bpy.data.images.load(filepath=saveFilePath + originalObject.name + "_" + p_suffix_OBN + ".png")
            create_margin_for_image(img_OBN, p_suffix_margin + "_" + p_suffix_OBN, originalObject, saveFilePath)
        if (p_margin_TBN_map and p_bake_TBN_map):
            img_TBN = bpy.data.images.load(filepath=saveFilePath + originalObject.name + "_" + p_suffix_TBN + ".png")
            create_margin_for_image(img_TBN, p_suffix_margin + "_" + p_suffix_TBN, originalObject, saveFilePath)
        if (p_margin_depth_map and p_bake_depth_map):
            img_depth = bpy.data.images.load(filepath=saveFilePath + originalObject.name + "_" + p_suffix_depth + ".png")
            create_margin_for_image(img_depth, p_suffix_margin + "_" + p_suffix_depth, originalObject, saveFilePath)

        print("originalObjectMaxWidth = " + str(originalObjectMaxWidth))

        #SetUVsToStorePivotOffset2D(impostor)
        #SetUVsToStorePivotOffset3D(impostor)

        #----------------------ExportFBX----------------------
        bpy.ops.object.select_all(action='DESELECT')
        impostor.select_set(True)
        bpy.context.view_layer.objects.active = impostor
        originalLocation = impostor.location[0]
        impostor.location = (0,0,0)
        bpy.ops.export_scene.fbx(filepath=saveFilePath + originalObject.name + "_Impostor.fbx", check_existing=False, filter_glob='*.fbx', use_selection=True, use_active_collection=False, global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', use_space_transform=True, bake_space_transform=False, object_types={'MESH'}, use_mesh_modifiers=True, use_mesh_modifiers_render=True, mesh_smooth_type='EDGE', use_subsurf=False, use_mesh_edges=False, use_tspace=False,    use_custom_props=False, add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=False, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True, axis_forward='-Z', axis_up='Y')
        impostor.location[0] = originalLocation
        impostor.location[1] = originalObject.location.y
        impostor.location[2] = originalObject.location.z
        
        impostor["PlaneCulling"] = math.cos(math.radians(180 / RotateSteps))
        print("PlaneCulling: ")
        print(math.cos(math.radians(180 / RotateSteps)))

        return {'FINISHED'}