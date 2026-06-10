# ==========================================================
# TextureLoader.py
# ==========================================================
#
# Responsável por:
#
# - carregar imagem
# - criar textura OpenGL
# - configurar textura
# - enviar textura para GPU
#
# Bibliotecas utilizadas:
#
# OpenGL.GL
# → funções OpenGL
#
# PIL (Pillow)
# → leitura de imagens
#
# ==========================================================

from OpenGL.GL import *

from PIL import Image


# ==========================================================
# FUNÇÃO LOAD_TEXTURE
# ==========================================================
#
# path:
# caminho da imagem
#
# texture:
# ID da textura criada no OpenGL
#
# ==========================================================

def load_texture(path, texture):


    # ======================================================
    # ATIVA TEXTURA
    # ======================================================
    #
    # Faz a textura atual do OpenGL
    # apontar para o ID recebido.
    #
    # Todas configurações feitas depois
    # serão aplicadas nessa textura.
    # ======================================================

    glBindTexture(GL_TEXTURE_2D, texture)


    # ======================================================
    # CONFIGURAÇÕES TEXTURA
    # ======================================================
    #
    # GL_TEXTURE_WRAP_S
    # eixo horizontal (U)
    #
    # GL_TEXTURE_WRAP_T
    # eixo vertical (V)
    #
    # GL_REPEAT:
    # repete textura caso UV ultrapasse:
    #
    # 0 → 1
    #
    # ======================================================

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)


    # ======================================================
    # FILTROS DA TEXTURA
    # ======================================================
    #
    # MIN_FILTER:
    # usado quando textura fica pequena
    #
    # MAG_FILTER:
    # usado quando textura aumenta
    #
    # GL_LINEAR:
    # suaviza pixels da textura
    #
    # evita aparência muito "quadrada"
    # ======================================================

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


    # ======================================================
    # CARREGA IMAGEM
    # ======================================================
    #
    # Pillow abre imagem do disco.
    # ======================================================

    image = Image.open(path)


    # ======================================================
    # INVERTE IMAGEM
    # ======================================================
    #
    # OpenGL considera:
    #
    # origem UV no canto inferior esquerdo
    #
    # Imagens normalmente usam:
    #
    # origem no canto superior esquerdo
    #
    # então precisamos inverter verticalmente.
    # ======================================================

    image = image.transpose(Image.FLIP_TOP_BOTTOM)


    # ======================================================
    # CONVERTE PARA RGBA
    # ======================================================
    #
    # R = red
    # G = green
    # B = blue
    # A = alpha (transparência)
    #
    # tobytes():
    # converte imagem em bytes
    # para envio à GPU
    # ======================================================

    image_data = image.convert("RGBA").tobytes()


    # ======================================================
    # LARGURA E ALTURA
    # ======================================================

    width, height = image.size


    # ======================================================
    # ENVIA TEXTURA PARA GPU
    # ======================================================
    #
    # glTexImage2D():
    #
    # cria textura dentro da GPU.
    #
    # Parâmetros principais:
    #
    # GL_TEXTURE_2D
    # tipo textura
    #
    # GL_RGBA
    # formato da textura
    #
    # width, height
    # tamanho imagem
    #
    # image_data
    # pixels da imagem
    # ======================================================

    glTexImage2D(
        GL_TEXTURE_2D,     # tipo textura
        0,                 # nível mipmap
        GL_RGBA,           # formato interno GPU
        width,             # largura imagem
        height,            # altura imagem
        0,                 # borda (não utilizado)
        GL_RGBA,           # formato imagem
        GL_UNSIGNED_BYTE,  # tipo dados
        image_data         # pixels imagem
    )


    # ======================================================
    # GERA MIPMAPS
    # ======================================================
    #
    # Mipmaps são versões menores
    # da textura.
    #
    # OpenGL utiliza automaticamente
    # quando objeto está distante.
    #
    # Isso melhora:
    #
    # - desempenho
    # - qualidade visual
    # - suavização
    # ======================================================

    glGenerateMipmap(GL_TEXTURE_2D)