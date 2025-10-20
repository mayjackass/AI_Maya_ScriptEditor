import maya.cmds as cmds

# Function to create a sphere and assign a material
def create_sphere_with_material():
    # Create a sphere
    sphere_name = cmds.polySphere(name='mySphere', radius=2)[0]  # The first element is the sphere's transform node

    # Create a new shader
    shader_name = cmds.shadingNode('lambert', asShader=True, name='myShader')
    
    # Set the shader color
    cmds.setAttr(f"{shader_name}.color", 0.2, 0.5, 0.8, type="double3")  # RGB values

    # Create a shading group
    shading_group = cmds.sets(shader_name, edit=True, force=True, 
                               name=f"{shader_name}SG")
    
    # Assign the shader to the sphere
    cmds.select(sphere_name)
    cmds.hyperShade(assign=shader_name)

    print(f"Created sphere '{sphere_name}' with shader '{shader_name}'.")

# Execute the function
create_sphere_with_material()