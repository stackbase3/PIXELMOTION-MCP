// PixelMotion Subtle Depth Vignette & Ambient Light Shader
precision mediump float;

uniform vec2 u_resolution;
uniform float u_time;
uniform float u_vignette_intensity;
uniform sampler2D u_diffuse;

varying vec2 v_uv;

void main() {
    vec4 color = texture2D(u_diffuse, v_uv);
    
    // Normalized distance from center (0.0 at center, 1.0 at corner)
    vec2 uv = (gl_FragCoord.xy / u_resolution.xy) - 0.5;
    float dist = length(uv);
    
    // Smooth cinematic vignette falloff
    float vignette = smoothstep(0.75, 0.25, dist * (0.8 + 0.4 * u_vignette_intensity));
    
    // Subtle ambient color grade: deep navy blacks, warm specular highlights
    vec3 grade = mix(vec3(0.04, 0.06, 0.12), color.rgb, vignette);
    
    gl_FragColor = vec4(grade, color.a);
}
