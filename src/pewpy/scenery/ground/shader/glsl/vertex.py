"""The vertex program both shaders share."""

VERTEX_SHADER = """
#version 150

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec4 p3d_Color;
in vec4 p3d_MultiTexCoord0;

out vec3 v_position;
out vec3 v_normal;
out vec3 v_model;
out vec4 v_data;
out vec4 v_wall;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    v_position = (p3d_ModelViewMatrix * p3d_Vertex).xyz;
    v_normal = p3d_Normal;
    v_model = p3d_Vertex.xyz;
    v_data = p3d_Color;
    v_wall = p3d_MultiTexCoord0;
}
"""
