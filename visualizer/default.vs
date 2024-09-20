#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform float uRow;
uniform float uCol;
uniform float uNumColInOne;

uniform float uZ;
uniform float uSize;
uniform float uSizeData;
uniform float uLocx;
uniform float uLocy;
uniform float uLocMacanx;
uniform float uLocMacany;
uniform float uPlan;

uniform float uisNewWindow;


out vec2 TexCoord;
out float Isdata_in_all;
out float Isplane;
void main()
{
    TexCoord = aTexCoord;
    Isplane = uPlan;
    vec4 result = projection * view * model * vec4(aPos.x, aPos.y, uZ, 1.0);
    if (uisNewWindow >= 0.5){
        // result = vec4(-1.0 + 2.0*aPos.x/(uCol+1.0), -1.0 + 2.0*aPos.y/(uRow+1.0), 0.0, 1.0);
        // float addY = floor(aPos.x / (uCol+1));
        // float newX = aPos.x - addY * (uCol+1);
        // float newY = aPos.y + addY;
        // float addZ = floor(newY / (uRow+1));
        // newY = newY - addZ * (uRow+1);
        
        float addZ = floor((aPos.x - 1.0)/ (uCol));
        float newX = aPos.x - addZ * (uCol);
        float addZ2 = floor((aPos.y - 1.0)/ (uRow));
        float newY = aPos.y - addZ2 * (uRow);
        addZ = addZ + addZ2*uNumColInOne;

        result = projection * view * model * vec4(-1.0 + 2.0*newX/(uCol+1.0), -1.0 + 2.0*newY/(uRow+1.0), -0.3*addZ, 1.0);
        gl_Position = result;
        // gl_PointSize = uSize;
        gl_PointSize = uSize/result.z;
    }
    else{
        result = projection * view * model * vec4(-1.0 + 2.0*aPos.x/(uCol+1.0), -1.0 + 2.0*aPos.y/(uRow+1.0), uZ, 1.0);
        gl_Position = result;
        gl_PointSize = uSize/result.z;

    }

    if (aPos.x==uLocMacanx && aPos.y==uLocMacany){
        Isdata_in_all = 1.0;
        gl_PointSize = 2*uSize/result.z;
    }
    else{
        Isdata_in_all = 0.0;
    
    }
}