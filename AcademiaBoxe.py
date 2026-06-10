# ==========================================================
# AcademiaBoxe.py
# ==========================================================
#
# TRABALHO FINAL - COMPUTACAO GRAFICA
# Tema do cenario: ACADEMIA DE BOXE (ambiente fechado / indoor)
#
# Desenvolvido em OpenGL Moderno (Python) reutilizando a
# estrutura dos codigos vistos em aula:
#
#   - Camera.py          -> camera com yaw/pitch (WASD + mouse)
#   - TextureLoader.py   -> carregamento de texturas (Pillow + OpenGL)
#   - ObjLoaderSimple.py -> loader .obj simples (da base do professor)
#   - ObjLoaderMTL.py    -> loader .obj que TAMBEM le o .mtl (cores/texturas
#                           por material) -> usado para os objetos da cena
#
# Recursos implementados (requisitos do trabalho):
#   - OpenGL Moderno (VAO / VBO / shaders #version 400)
#   - Shaders com iluminacao Phong (luz direcional + point lights)
#   - Camera com movimentacao livre (teclado + mouse)
#   - Objetos 3D: 11 modelos .obj importados (ringue, sacos, speedbag,
#     halteres, kettlebell, luva, aparelho, TV, relogio, banco)
#   - Texturas: piso de borracha, paredes de tijolo e texturas proprias
#     dos modelos (relogio, halter)
#   - Cenario completo e organizado, com comentarios explicativos
#
# A sala (piso, paredes, teto) e os espelhos sao geometria procedural;
# todos os demais OBJETOS sao modelos .obj carregados de arquivo.
#
# CONTROLES:
#   W / A / S / D  -> mover a camera
#   Mouse          -> olhar ao redor
#   ESC            -> sair
# ==========================================================

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import pyrr
from pyrr import Vector3
import ctypes
import math

from TextureLoader import load_texture
from Camera import Camera
from ObjLoaderMTL import load_obj_grouped, normalizar_grupos

# ==========================================================
# CONSTANTES DE JANELA
# ==========================================================
WIDTH = 1000
HEIGHT = 700

# ==========================================================
# TEXTURAS DO AMBIENTE
# ==========================================================
TEX_PISO = "texturas/piso/rubber_color.jpg"      # piso de borracha
TEX_PAREDE = "texturas/parede/brick_color.jpg"   # paredes e teto de tijolo

# ==========================================================
# DIMENSOES DO GINASIO (em "metros" do mundo)
# ==========================================================
SALA_W = 44.0   # largura  (eixo X)
SALA_D = 44.0   # comprimento (eixo Z)
SALA_H = 8.0    # altura   (eixo Y) - pe-direito de academia

# ==========================================================
# VARIAVEIS GLOBAIS
# ==========================================================
Window = None
Shader_programm = None
cam = Camera()

first_mouse = True
lastX = WIDTH / 2
lastY = HEIGHT / 2


# ==========================================================
# CALLBACKS DE JANELA / ENTRADA
# ==========================================================
def redimensiona_callback(window, w, h):
    global WIDTH, HEIGHT
    WIDTH = max(w, 1)
    HEIGHT = max(h, 1)
    glViewport(0, 0, WIDTH, HEIGHT)


def teclado_callback(window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)


def mouse_callback(window, xpos, ypos):
    global first_mouse, lastX, lastY
    if first_mouse:
        lastX, lastY = xpos, ypos
        first_mouse = False
    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX, lastY = xpos, ypos
    cam.process_mouse_movement(xoffset, yoffset)


# ==========================================================
# INICIALIZACAO DO OPENGL / JANELA
# ==========================================================
def inicializa_opengl():
    global Window
    if not glfw.init():
        raise RuntimeError("Erro ao inicializar o GLFW")

    Window = glfw.create_window(WIDTH, HEIGHT, "Academia de Boxe - OpenGL Moderno", None, None)
    if not Window:
        glfw.terminate()
        raise RuntimeError("Erro ao criar a janela")

    glfw.make_context_current(Window)
    glfw.set_window_size_callback(Window, redimensiona_callback)
    glfw.set_key_callback(Window, teclado_callback)
    glfw.set_cursor_pos_callback(Window, mouse_callback)
    glfw.set_input_mode(Window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)
    print("OpenGL:", glGetString(GL_VERSION).decode())


# ==========================================================
# HELPER: ENVIA UM BUFFER DE VERTICES PARA A GPU
# ==========================================================
# Cada vertice tem 8 floats: pos(x,y,z) | uv(u,v) | normal(nx,ny,nz)
# ==========================================================
def _enviar_para_gpu(buffer):
    buffer = np.asarray(buffer, dtype=np.float32)
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, buffer.nbytes, buffer, GL_STATIC_DRAW)
    stride = buffer.itemsize * 8
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(buffer.itemsize * 3))
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(buffer.itemsize * 5))
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    return vao, buffer.size // 8


# ==========================================================
# CARREGA UM MODELO .OBJ COM SEUS MATERIAIS (cores + texturas)
# ==========================================================
# Retorna uma lista de "grupos" (vao, num_vertices, textura, cor),
# um por material do modelo. Assim o ringue, por exemplo, mantem
# postes vermelhos, cordas brancas e lona azul.
#
# tamanho : redimensiona o modelo inteiro para esse tamanho
# apoiar  : se True, apoia a base do modelo no chao (y=0)
# ==========================================================
def carregar_modelo(caminho_obj, tamanho, apoiar=True):
    print(f"Carregando {caminho_obj}...")
    grupos = load_obj_grouped(caminho_obj)
    grupos = normalizar_grupos(grupos, tamanho, apoiar)
    saida = []
    for g in grupos:
        vao, num = _enviar_para_gpu(g["buffer"])
        tex_id = None
        if g["tex"]:
            tex_id = glGenTextures(1)
            load_texture(g["tex"], tex_id)
        saida.append((vao, num, tex_id, g["color"]))
    return saida


# ==========================================================
# GEOMETRIA PROCEDURAL DO AMBIENTE (piso, sala e espelhos)
# ==========================================================
def criar_plano(width=50.0, depth=50.0, repeats_u=10.0, repeats_v=10.0):
    """Plano horizontal no eixo XZ, normal para +Y.
       Usado no piso e nos espelhos (com rotacao)."""
    w, d = width / 2.0, depth / 2.0
    buffer = np.array([
        -w, 0.0, -d,  0.0, repeats_v,        0.0, 1.0, 0.0,
         w, 0.0, -d,  repeats_u, repeats_v,  0.0, 1.0, 0.0,
         w, 0.0,  d,  repeats_u, 0.0,        0.0, 1.0, 0.0,
         w, 0.0,  d,  repeats_u, 0.0,        0.0, 1.0, 0.0,
        -w, 0.0,  d,  0.0, 0.0,              0.0, 1.0, 0.0,
        -w, 0.0, -d,  0.0, repeats_v,        0.0, 1.0, 0.0,
    ], dtype=np.float32)
    return _enviar_para_gpu(buffer)


def criar_sala(w, d, h, repeat=6.0):
    """Sala fechada: 4 paredes + teto, com normais apontando para DENTRO
       (a iluminacao vem de dentro do ginasio). Piso desenhado a parte."""
    hx, hz = w / 2.0, d / 2.0
    paredes = [
        ([(-hx, 0, -hz), ( hx, 0, -hz), ( hx, h, -hz), (-hx, h, -hz)], (0, 0, 1)),   # fundo -Z
        ([( hx, 0,  hz), (-hx, 0,  hz), (-hx, h,  hz), ( hx, h,  hz)], (0, 0, -1)),  # frente +Z
        ([(-hx, 0,  hz), (-hx, 0, -hz), (-hx, h, -hz), (-hx, h,  hz)], (1, 0, 0)),   # esquerda -X
        ([( hx, 0, -hz), ( hx, 0,  hz), ( hx, h,  hz), ( hx, h, -hz)], (-1, 0, 0)),  # direita +X
        ([(-hx, h, -hz), ( hx, h, -hz), ( hx, h,  hz), (-hx, h,  hz)], (0, -1, 0)),  # teto +Y
    ]
    uv = [(0.0, 0.0), (repeat, 0.0), (repeat, repeat), (0.0, repeat)]
    ordem = [0, 1, 2, 0, 2, 3]
    buffer = []
    for cantos, n in paredes:
        for i in ordem:
            x, y, z = cantos[i]
            u, v = uv[i]
            buffer += [x, y, z, u, v, n[0], n[1], n[2]]
    return _enviar_para_gpu(buffer)


# ==========================================================
# SHADERS (OpenGL Moderno - GLSL #version 400)
# ==========================================================
def inicializa_shaders():
    global Shader_programm

    vertex_src = """
        #version 400
        layout(location = 0) in vec3 in_pos;
        layout(location = 1) in vec2 in_uv;
        layout(location = 2) in vec3 in_normal;
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        out vec2 frag_uv;
        out vec3 frag_normal;
        out vec3 frag_pos;
        void main()
        {
            frag_uv = in_uv;
            frag_normal = mat3(transpose(inverse(model))) * in_normal;
            frag_pos = vec3(model * vec4(in_pos, 1.0));
            gl_Position = projection * view * vec4(frag_pos, 1.0);
        }
    """

    fragment_src = """
        #version 400
        in vec2 frag_uv;
        in vec3 frag_normal;
        in vec3 frag_pos;

        uniform sampler2D texture1;
        uniform bool use_texture;
        uniform vec3 object_color;
        uniform vec3 view_pos;

        uniform vec3 dir_light_dir;
        uniform vec3 dir_light_color;

        #define MAX_POINT_LIGHTS 8
        uniform vec3 point_light_pos[MAX_POINT_LIGHTS];
        uniform vec3 point_light_color[MAX_POINT_LIGHTS];
        uniform float point_light_intensity;

        out vec4 FragColor;

        void main()
        {
            vec4 texColor = use_texture ? texture(texture1, frag_uv) : vec4(object_color, 1.0);
            vec3 base_color = texColor.rgb;

            vec3 norm = normalize(frag_normal);
            vec3 view_dir = normalize(view_pos - frag_pos);

            // ginasio fechado e iluminado -> ambiente alto
            vec3 ambient = 0.30 * base_color;

            // luz direcional
            vec3 light_dir = normalize(-dir_light_dir);
            float diff = max(dot(norm, light_dir), 0.0);
            vec3 diffuse = diff * dir_light_color * base_color;
            vec3 reflect_dir = reflect(-light_dir, norm);
            float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);
            vec3 specular = 0.12 * spec * dir_light_color;

            vec3 result = ambient + diffuse + specular;

            // luminarias do teto (point lights) com atenuacao
            for (int i = 0; i < MAX_POINT_LIGHTS; i++) {
                vec3 pl_dir = normalize(point_light_pos[i] - frag_pos);
                float distance = length(point_light_pos[i] - frag_pos);
                float attenuation = 1.0 / (1.0 + 0.07 * distance + 0.004 * distance * distance);
                float pl_diff = max(dot(norm, pl_dir), 0.0);
                vec3 pl_diffuse = point_light_intensity * pl_diff * point_light_color[i] * base_color;
                vec3 pl_reflect = reflect(-pl_dir, norm);
                float pl_spec = pow(max(dot(view_dir, pl_reflect), 0.0), 32.0);
                vec3 pl_specular = point_light_intensity * 0.35 * pl_spec * point_light_color[i];
                result += (pl_diffuse + pl_specular) * attenuation;
            }
            FragColor = vec4(result, texColor.a);
        }
    """

    vs = OpenGL.GL.shaders.compileShader(vertex_src, GL_VERTEX_SHADER)
    fs = OpenGL.GL.shaders.compileShader(fragment_src, GL_FRAGMENT_SHADER)
    Shader_programm = OpenGL.GL.shaders.compileProgram(vs, fs)


# ==========================================================
# MATRIZ DE TRANSFORMACAO (posicao + rotacao Y + escala extra)
# ==========================================================
# Mesma convencao da base: (Escala * Rotacao) * Translacao
# ==========================================================
def transform(pos, rot_y=0.0, escala=1.0):
    m = pyrr.matrix44.create_from_scale(Vector3([escala, escala, escala]))
    if rot_y != 0.0:
        m = pyrr.matrix44.multiply(m, pyrr.matrix44.create_from_y_rotation(np.radians(rot_y)))
    m = pyrr.matrix44.multiply(m, pyrr.matrix44.create_from_translation(Vector3(pos)))
    return m


# matriz de um plano vertical (para os espelhos) na parede do fundo (-Z)
def transform_espelho(pos):
    m = pyrr.matrix44.create_from_x_rotation(np.radians(90.0))   # deita o plano para ficar vertical
    m = pyrr.matrix44.multiply(m, pyrr.matrix44.create_from_translation(Vector3(pos)))
    return m


# ==========================================================
# LOOP PRINCIPAL DE RENDERIZACAO
# ==========================================================
def render_loop(amb, modelos, instancias, mirror_geo, mirror_mats):
    last_time = glfw.get_time()
    base_speed = 12.0

    # luminarias do teto (point lights)
    luz_positions = []
    for lx in [-12.0, 0.0, 12.0]:
        for lz in [-10.0, 10.0]:
            luz_positions.append([lx, SALA_H - 0.6, lz])   # 6 luzes no teto

    while not glfw.window_should_close(Window):
        current_time = glfw.get_time()
        delta = current_time - last_time
        last_time = current_time
        vel = base_speed * delta

        if glfw.get_key(Window, glfw.KEY_W) == glfw.PRESS: cam.process_keyboard("FORWARD", vel)
        if glfw.get_key(Window, glfw.KEY_S) == glfw.PRESS: cam.process_keyboard("BACKWARD", vel)
        if glfw.get_key(Window, glfw.KEY_A) == glfw.PRESS: cam.process_keyboard("LEFT", vel)
        if glfw.get_key(Window, glfw.KEY_D) == glfw.PRESS: cam.process_keyboard("RIGHT", vel)

        glClearColor(0.12, 0.12, 0.14, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(Shader_programm)

        view = cam.get_view_matrix()
        projection = pyrr.matrix44.create_perspective_projection_matrix(60.0, WIDTH / HEIGHT, 0.1, 300.0)
        glUniformMatrix4fv(glGetUniformLocation(Shader_programm, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(Shader_programm, "projection"), 1, GL_FALSE, projection)
        glUniform3f(glGetUniformLocation(Shader_programm, "view_pos"),
                    cam.camera_pos.x, cam.camera_pos.y, cam.camera_pos.z)

        glUniform3f(glGetUniformLocation(Shader_programm, "dir_light_dir"), -0.3, -1.0, -0.2)
        glUniform3f(glGetUniformLocation(Shader_programm, "dir_light_color"), 0.40, 0.40, 0.42)
        for i, p in enumerate(luz_positions):
            glUniform3f(glGetUniformLocation(Shader_programm, f"point_light_pos[{i}]"), *p)
            glUniform3f(glGetUniformLocation(Shader_programm, f"point_light_color[{i}]"), 1.0, 0.96, 0.88)
        glUniform1f(glGetUniformLocation(Shader_programm, "point_light_intensity"), 1.3)

        def desenhar(vao, num_v, model, tex_id=None, color=(1, 1, 1)):
            glUniformMatrix4fv(glGetUniformLocation(Shader_programm, "model"), 1, GL_FALSE, model)
            if tex_id is not None:
                glUniform1i(glGetUniformLocation(Shader_programm, "use_texture"), True)
                glBindTexture(GL_TEXTURE_2D, tex_id)
            else:
                glUniform1i(glGetUniformLocation(Shader_programm, "use_texture"), False)
                glUniform3f(glGetUniformLocation(Shader_programm, "object_color"), *color)
            glBindVertexArray(vao)
            glDrawArrays(GL_TRIANGLES, 0, num_v)

        # ---------- AMBIENTE: PISO E SALA ----------
        desenhar(amb["piso"][0], amb["piso"][1], amb["piso_mat"], tex_id=amb["tex_piso"])
        desenhar(amb["sala"][0], amb["sala"][1], amb["sala_mat"], tex_id=amb["tex_parede"])

        # ---------- ESPELHOS (procedurais) ----------
        for m in mirror_mats:
            desenhar(mirror_geo[0], mirror_geo[1], m, color=(0.55, 0.62, 0.75))

        # ---------- OBJETOS .OBJ ----------
        # cada instancia: (nome_modelo, matriz). cada modelo tem varios grupos
        # (um por material), desenhados com sua cor/textura propria.
        for nome, matriz in instancias:
            for (vao, num, tex_id, cor) in modelos[nome]:
                desenhar(vao, num, matriz, tex_id=tex_id, color=cor)

        glfw.swap_buffers(Window)
        glfw.poll_events()

    glfw.terminate()


# ==========================================================
# MAIN
# ==========================================================
def main():
    inicializa_opengl()
    inicializa_shaders()

    # ======================================================
    # AMBIENTE (procedural)
    # ======================================================
    amb = {}
    amb["tex_piso"] = glGenTextures(1); load_texture(TEX_PISO, amb["tex_piso"])
    amb["tex_parede"] = glGenTextures(1); load_texture(TEX_PAREDE, amb["tex_parede"])
    amb["piso"] = criar_plano(SALA_W, SALA_D, repeats_u=12.0, repeats_v=12.0)
    amb["piso_mat"] = pyrr.matrix44.create_identity()
    amb["sala"] = criar_sala(SALA_W, SALA_D, SALA_H, repeat=10.0)
    amb["sala_mat"] = pyrr.matrix44.create_identity()

    # espelhos na parede do fundo (-Z)
    mirror_geo = criar_plano(8.0, 6.0, repeats_u=1.0, repeats_v=1.0)
    mirror_mats = [transform_espelho([-11.0, 3.4, -SALA_D / 2.0 + 0.06]),
                   transform_espelho([ 11.0, 3.4, -SALA_D / 2.0 + 0.06])]

    # ======================================================
    # MODELOS .OBJ  (nome -> grupos)  +  tamanho de cada um
    # ======================================================
    SACO_TAM = 5.5   # altura dos sacos de pancada (usada para pendura-los no teto)
    modelos = {}
    modelos["ringue"]     = carregar_modelo("objetos/ringue/model.obj", 13.0)
    modelos["saco1"]      = carregar_modelo("objetos/saco1/punching bag.obj", SACO_TAM)
    modelos["saco2"]      = carregar_modelo("objetos/saco2/model.obj", SACO_TAM)
    modelos["speedbag"]   = carregar_modelo("objetos/speedbag/speedbag.obj", 3.5)
    modelos["halter"]     = carregar_modelo("objetos/halter/Dumbbell.obj", 2.0)
    modelos["halteres"]   = carregar_modelo("objetos/halteres/model.obj", 2.4)
    modelos["kettlebell"] = carregar_modelo("objetos/kettlebell/Kettlebell.obj", 1.3)
    modelos["luva"]       = carregar_modelo("objetos/luva/BoxingGlove.obj", 1.0)
    modelos["aparelho"]   = carregar_modelo("objetos/aparelho/model.obj", 6.5)
    modelos["tv"]         = carregar_modelo("objetos/tv/model.obj", 6.0, apoiar=False)
    modelos["relogio"]    = carregar_modelo("objetos/relogio/1345 Analog Clock.obj", 3.0, apoiar=False)
    modelos["banco"]      = carregar_modelo("objetos/banco/Obj/Bench_LowRes.obj", 3.8)

    # altura para pendurar os sacos: topo encostando no teto
    saco_y = SALA_H - SACO_TAM

    # ======================================================
    # POSICIONAMENTO DOS OBJETOS NA CENA
    # (nome, matriz). Ajuste posicoes/rotacoes aqui se quiser.
    # ======================================================
    instancias = [
        # ---- RINGUE (centro) ----
        ("ringue", transform([0.0, 0.0, 0.0])),

        # ---- SACOS DE PANCADA pendurados no teto (lado esquerdo) ----
        ("saco1", transform([-14.0, saco_y, -5.0])),
        ("saco2", transform([-14.0, saco_y,  5.0])),
        ("saco1", transform([-14.0, saco_y, 13.0])),
        ("speedbag", transform([-15.0, SALA_H - 3.5, -13.0], rot_y=20.0)),

        # ---- AREA DE PESOS (lado direito) ----
        ("aparelho", transform([15.0, 0.0, -9.0], rot_y=-90.0)),
        ("banco", transform([13.0, 0.0, 3.0], rot_y=90.0)),
        ("halter", transform([15.5, 0.0, 0.0])),
        ("halter", transform([15.5, 0.0, 1.2])),
        ("halteres", transform([15.5, 0.0, 5.0])),
        ("kettlebell", transform([16.0, 0.0, 8.0])),

        # ---- 4 LUVAS (2 pares, perto do ringue) ----
        ("luva", transform([7.0, 0.0, 11.0], rot_y=20.0)),
        ("luva", transform([7.8, 0.0, 11.4], rot_y=200.0)),
        ("luva", transform([10.0, 0.0, 9.0], rot_y=-40.0)),
        ("luva", transform([10.8, 0.0, 9.3], rot_y=140.0)),

        # ---- OBJETOS DE PAREDE ----
        # TV na parede do fundo (-Z)
        ("tv", transform([0.0, 5.5, -SALA_D / 2.0 + 0.3])),
        # Relogio na parede direita (+X) - disco ja fica vertical, sem rotacao
("relogio", transform([SALA_W / 2.0 - 0.4, 5.0, 6.0], rot_y=180)),    ]

    # posicao inicial da camera: dentro do ginasio, olhando para o ringue
    cam.camera_pos = Vector3([0.0, 2.5, 17.0])

    render_loop(amb, modelos, instancias, mirror_geo, mirror_mats)


if __name__ == "__main__":
    main()
