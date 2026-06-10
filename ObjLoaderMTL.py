# ==========================================================
# ObjLoaderMTL.py
# ==========================================================
#
# Loader de .obj que TAMBEM le o arquivo .mtl, respeitando a
# cor (Kd) e a textura (map_Kd) de CADA material do modelo.
#
# Diferenca para o ObjLoaderSimple (que ignora o .mtl):
#   - aqui o modelo e dividido em "grupos", um por material;
#   - cada grupo carrega sua propria cor e/ou textura.
#
# Isso permite, por exemplo, que o ringue apareca com postes
# vermelhos, cordas brancas e lona azul (em vez de uma cor so).
#
# Retorno de load_obj_grouped():
#   lista de dicionarios, cada um com:
#     "buffer" : np.float32 no formato [pos(3), uv(2), normal(3)]
#     "num"    : numero de vertices
#     "color"  : (r,g,b) -> cor difusa do material (Kd)
#     "tex"    : caminho absoluto da textura, ou None
# ==========================================================

import os
import numpy as np


def _parse_mtl(mtl_path):
    """Le um arquivo .mtl e devolve {nome_material: {'Kd':(r,g,b), 'map':arquivo}}."""
    materiais = {}
    atual = None
    if not os.path.isfile(mtl_path):
        return materiais
    pasta = os.path.dirname(mtl_path)
    with open(mtl_path, "r", errors="ignore") as f:
        for raw in f:
            linha = raw.strip()                 # remove \n e \r (arquivos do Windows)
            if linha.startswith("newmtl "):
                atual = linha[7:].strip()
                materiais[atual] = {"Kd": (0.8, 0.8, 0.8), "map": None}
            elif atual is None:
                continue
            elif linha.startswith("Kd "):
                vals = linha[3:].split()
                materiais[atual]["Kd"] = (float(vals[0]), float(vals[1]), float(vals[2]))
            elif linha.lower().startswith("map_kd "):
                # o nome do arquivo pode conter espacos -> pega o resto da linha
                nome = linha[7:].strip()
                caminho = os.path.join(pasta, nome)
                materiais[atual]["map"] = caminho if os.path.isfile(caminho) else None
    return materiais


def load_obj_grouped(obj_path):
    pasta = os.path.dirname(obj_path)

    vertices, textures, normals = [], [], []
    # faces separadas por material -> {nome_material: [ (vi,ti,ni), ... ]}
    faces_por_mat = {}
    material_atual = "__default__"
    faces_por_mat[material_atual] = []
    mtl_file = None

    with open(obj_path, "r", errors="ignore") as f:
        for raw in f:
            linha = raw.strip()
            if not linha:
                continue
            if linha.startswith("mtllib "):
                mtl_file = linha[7:].strip()
                continue
            if linha.startswith("usemtl "):
                material_atual = linha[7:].strip()
                faces_por_mat.setdefault(material_atual, [])
                continue

            valores = linha.split()
            tag = valores[0]

            if tag == "v":
                vertices.append([float(valores[1]), float(valores[2]), float(valores[3])])
            elif tag == "vt":
                textures.append([float(valores[1]), float(valores[2])])
            elif tag == "vn":
                normals.append([float(valores[1]), float(valores[2]), float(valores[3])])
            elif tag == "f":
                face = []
                for v in valores[1:]:
                    p = v.split("/")
                    vi = int(p[0]) - 1
                    ti = int(p[1]) - 1 if len(p) > 1 and p[1] else -1
                    ni = int(p[2]) - 1 if len(p) > 2 and p[2] else -1
                    face.append((vi, ti, ni))
                # triangula a face (leque de triangulos)
                for i in range(1, len(face) - 1):
                    faces_por_mat[material_atual].append(face[0])
                    faces_por_mat[material_atual].append(face[i])
                    faces_por_mat[material_atual].append(face[i + 1])

    # le os materiais do .mtl (se existir)
    materiais = {}
    if mtl_file:
        materiais = _parse_mtl(os.path.join(pasta, mtl_file))

    # monta um buffer por material (ignora grupos vazios)
    grupos = []
    for nome, faces in faces_por_mat.items():
        if not faces:
            continue
        buffer = []
        for (vi, ti, ni) in faces:
            buffer.extend(vertices[vi])
            if 0 <= ti < len(textures):
                buffer.extend(textures[ti])
            else:
                buffer.extend([0.0, 0.0])
            if 0 <= ni < len(normals):
                buffer.extend(normals[ni])
            else:
                buffer.extend([0.0, 1.0, 0.0])
        info = materiais.get(nome, {"Kd": (0.8, 0.8, 0.8), "map": None})
        grupos.append({
            "buffer": np.array(buffer, dtype=np.float32),
            "num": len(buffer) // 8,
            "color": info["Kd"],
            "tex": info["map"],
        })

    # normaliza a posicao usando TODOS os grupos juntos (escala/centro globais)
    return grupos


def normalizar_grupos(grupos, tamanho, apoiar_no_chao=True):
    """Redimensiona o modelo inteiro (todos os grupos) para caber num cubo
       de 'tamanho' unidades, centraliza em X/Z e (opcional) apoia em y=0."""
    if not grupos:
        return grupos
    todos = np.concatenate([g["buffer"].reshape(-1, 8)[:, 0:3] for g in grupos], axis=0)
    mn, mx = todos.min(axis=0), todos.max(axis=0)
    extent = (mx - mn).max()
    if extent <= 0:
        return grupos
    escala = tamanho / extent
    # apos escalar, recentraliza em X/Z e apoia no chao
    centro_x = (mn[0] + mx[0]) / 2.0 * escala
    centro_z = (mn[2] + mx[2]) / 2.0 * escala
    base_y = mn[1] * escala
    for g in grupos:
        b = g["buffer"]
        b[0::8] = b[0::8] * escala - centro_x
        b[1::8] = b[1::8] * escala - (base_y if apoiar_no_chao else 0.0)
        b[2::8] = b[2::8] * escala - centro_z
    return grupos
