# Camera.py
# Gerencia a câmera 3D usando yaw (rotação horizontal) e pitch (rotação vertical)
#
# IMPORTANTE:
#
# Existem diferentes convenções para câmeras 3D.
#
# Neste projeto utilizamos o padrão clássico
# do OpenGL moderno:
#
# - frente = eixo Z negativo (-Z)
# - yaw inicial = -90°
#
# Isso faz a câmera iniciar olhando
# para frente no eixo Z negativo.
#
# Em outras aulas ou motores gráficos,
# pode-se utilizar:
#
# - frente = eixo Z positivo (+Z)
# - yaw inicial = 0°
#
# Ambas as abordagens estão corretas,
# desde que toda a câmera utilize
# a mesma convenção.
#
# Atributos principais:
#   camera_pos         : Vector3 – posição da câmera no mundo
#   camera_front       : Vector3 – direção que a câmera está apontando
#   camera_up          : Vector3 – vetor “para cima” da câmera
#   camera_right       : Vector3 – vetor “para a direita” da câmera
#   yaw                : float   – ângulo de rotação horizontal em graus
#   pitch              : float   – ângulo de rotação vertical em graus
#   mouse_sensitivity  : float   – sensibilidade do mouse
#
# Métodos:
#
#   get_view_matrix()
#       → Retorna a matriz look-at com base em camera_pos,
#         camera_front e camera_up.
#
#   process_mouse_movement()
#       → Atualiza yaw e pitch conforme movimento do mouse.
#
#   process_keyboard()
#       → Move a câmera usando teclado.
#
#   update_camera_vectors()
#       → Converte yaw/pitch em vetores direção 3D.

from pyrr import Vector3, vector, vector3, matrix44
from math import sin, cos, radians


class Camera:

    def __init__(self):

        # ==================================================
        # POSIÇÃO DA CÂMERA
        # ==================================================
        #
        # X = esquerda/direita
        # Y = cima/baixo
        # Z = profundidade
        #
        # câmera inicia afastada no eixo Z+
        # ==================================================

        self.camera_pos = Vector3([0.0, 4.0, 30.0])


        # ==================================================
        # DIREÇÃO INICIAL
        # ==================================================
        #
        # câmera olhando inicialmente
        # para o eixo Z negativo (-Z)
        # ==================================================

        self.camera_front = Vector3([0.0, 0.0, -1.0])


        # ==================================================
        # VETOR "PARA CIMA"
        # ==================================================

        self.camera_up = Vector3([0.0, 1.0, 0.0])


        # ==================================================
        # VETOR "PARA DIREITA"
        # ==================================================

        self.camera_right = Vector3([1.0, 0.0, 0.0])


        # ==================================================
        # SENSIBILIDADE DO MOUSE
        # ==================================================

        self.mouse_sensitivity = 0.01


        # ==================================================
        # YAW E PITCH
        # ==================================================
        #
        # yaw = -90°
        #
        # Faz a câmera olhar inicialmente
        # para frente no eixo Z negativo.
        #
        # Isso ocorre devido às fórmulas
        # trigonométricas utilizadas no cálculo
        # do vetor direção.
        # ==================================================

        self.yaw = -90.0

        self.pitch = 0.0


    # ======================================================
    # MATRIZ VIEW
    # ======================================================
    #
    # Cria a matriz look-at da câmera.
    #
    # camera_pos:
    # posição câmera
    #
    # camera_pos + camera_front:
    # ponto para onde câmera olha
    #
    # camera_up:
    # orientação vertical
    # ======================================================

    def get_view_matrix(self):

        return matrix44.create_look_at(self.camera_pos,
                                       self.camera_pos + self.camera_front,
                                       self.camera_up)


    # ======================================================
    # MOVIMENTO MOUSE
    # ======================================================
    #
    # xoffset:
    # movimento horizontal mouse
    #
    # yoffset:
    # movimento vertical mouse
    #
    # Atualiza:
    #
    # - yaw
    # - pitch
    # - direção câmera
    # ======================================================

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):

        # aplica sensibilidade
        xoffset *= self.mouse_sensitivity

        yoffset *= self.mouse_sensitivity


        # atualiza ângulos
        self.yaw += xoffset

        self.pitch += yoffset


        # ==================================================
        # LIMITA PITCH
        # ==================================================
        #
        # evita câmera virar completamente
        # Limita o pitch para evitar que
        # a câmera vire completamente
        # para cima ou para baixo.
        #
        # Sem esse limite, a câmera poderia
        # ficar de ponta cabeça, causando
        # movimentos estranhos e perda
        # de orientação da cena.
        # ==================================================

        if constrain_pitch:

            max_angle = 45.0

            if self.pitch > max_angle:

                self.pitch = max_angle

            if self.pitch < -max_angle:

                self.pitch = -max_angle


        # atualiza vetores câmera
        self.update_camera_vectors()


    # ======================================================
    # MOVIMENTO TECLADO
    # ======================================================
    #
    # FORWARD  = frente
    # BACKWARD = trás
    # LEFT     = esquerda
    # RIGHT    = direita
    #
    # velocity:
    # velocidade baseada em delta time
    # ======================================================

    def process_keyboard(self, direction, velocity):

        # frente
        if direction == "FORWARD":

            self.camera_pos += self.camera_front * velocity


        # trás
        elif direction == "BACKWARD":

            self.camera_pos -= self.camera_front * velocity


        # esquerda
        elif direction == "LEFT":

            self.camera_pos -= self.camera_right * velocity


        # direita
        elif direction == "RIGHT":

            self.camera_pos += self.camera_right * velocity


    # ======================================================
    # ATUALIZA VETORES DA CÂMERA
    # ======================================================
    #
    # Converte yaw/pitch em vetor direção 3D.
    #
    # Fórmulas utilizadas:
    #
    # dir_x = cos(yaw) * cos(pitch)
    # dir_y = sin(pitch)
    # dir_z = sin(yaw) * cos(pitch)
    #
    # Estas fórmulas seguem o padrão clássico
    # do OpenGL moderno, onde:
    #
    # - frente = eixo Z negativo
    # ======================================================

    def update_camera_vectors(self):

        # vetor direção
        front = Vector3([0.0, 0.0, 0.0])


        # ==================================================
        # EIXO X
        # ==================================================

        front.x = cos(radians(self.yaw)) * cos(radians(self.pitch))


        # ==================================================
        # EIXO Y
        # ==================================================

        front.y = sin(radians(self.pitch))


        # ==================================================
        # EIXO Z
        # ==================================================

        front.z = sin(radians(self.yaw)) * cos(radians(self.pitch))


        # ==================================================
        # NORMALIZA VETOR
        # ==================================================
        #
        # mantém tamanho do vetor igual a 1
        # ==================================================

        self.camera_front = vector.normalise(front)


        # ==================================================
        # WORLD UP
        # ==================================================

        world_up = Vector3([0.0, 1.0, 0.0])


        # O produto vetorial (cross product)
        # é utilizado para calcular vetores
        # perpendiculares entre si.
        #
        # Isso permite descobrir:
        #
        # - direção direita da câmera
        # - direção cima da câmera
        #
        # com base na direção frontal atual.

        # ==================================================
        # VETOR DIREITA
        # ==================================================
        #
        # produto vetorial:
        #
        # frente x cima
        # ==================================================

        self.camera_right = vector.normalise(vector3.cross(self.camera_front, world_up))


        # ==================================================
        # VETOR CIMA
        # ==================================================
        #
        # produto vetorial:
        #
        # direita x frente
        # ==================================================

        self.camera_up = vector.normalise(vector3.cross(self.camera_right, self.camera_front))