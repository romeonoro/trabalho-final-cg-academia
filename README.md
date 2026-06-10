# Trabalho Final - Computação Gráfica
## Cenário: Academia de Boxe (OpenGL Moderno)

Cenário 3D de uma academia de boxe em **OpenGL Moderno (Python)**, reutilizando
a estrutura dos códigos vistos em aula. Todos os equipamentos são **modelos .obj
importados**; o ambiente (piso, paredes, teto e espelhos) é geometria procedural.

<img width="996" height="696" alt="Captura de tela 2026-06-10 083345" src="https://github.com/user-attachments/assets/e73e9b53-785e-44f5-93c9-3431ad8e9809" />

<img width="995" height="688" alt="Captura de tela 2026-06-10 083511" src="https://github.com/user-attachments/assets/a79a96d8-3d7e-440f-a9a7-9b90da52aa89" />

### Como executar
1. (Recomendado) Crie e ative um ambiente virtual:
   ```
   python -m venv venv
   # Windows (PowerShell):  .\venv\Scripts\Activate.ps1
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   # Windows (cmd):         venv\Scripts\activate.bat
   # Linux/Mac:             source venv/bin/activate
   
   ```
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Rode a partir desta pasta (importante p/ encontrar texturas e modelos):
   ```
   python AcademiaBoxe.py
   ```

### Controles
- **W / A / S / D** — mover a câmera
- **Mouse** — olhar ao redor
- **ESC** — sair

### Objetos da cena (modelos .obj)
- Ringue de boxe (centro)
- 2 sacos de pancada + 1 saco de velocidade (speed bag)
- Aparelho de musculação, banco, halteres, kettlebell
- Luva de boxe
- TV e relógio de parede

### Ambiente (procedural)
- Piso de borracha, paredes/teto de tijolo, 2 espelhos

### Recursos técnicos (requisitos do trabalho)
- OpenGL Moderno: VAO / VBO / shaders (`#version 400`)
- Iluminação Phong: 1 luz direcional + 6 luminárias (point lights)
- Câmera com movimentação livre (teclado + mouse)
- Texturas (piso, paredes e texturas próprias de alguns modelos)
- Código organizado e comentado

### Detalhe importante (vale citar na apresentação)
O projeto tem DOIS loaders de .obj:
- `ObjLoaderSimple.py` — o loader simples da base (lê só o .obj).
- `ObjLoaderMTL.py` — loader que também lê o arquivo **.mtl**, respeitando a
  **cor (Kd) e a textura (map_Kd) de cada material**. Por isso o ringue aparece
  com postes vermelhos, cordas brancas e lona azul, em vez de uma cor só.
  Cada modelo é dividido em "grupos" (um por material) e cada grupo é desenhado
  com sua própria cor/textura.

### Ajustes finos
As posições e rotações dos objetos ficam na lista `instancias`, dentro de
`main()` em `AcademiaBoxe.py`. Se algum objeto de parede (TV ou relógio)
aparecer virado para a parede, troque o valor de `rot_y` dele (ex.: 0 → 180,
ou -90 → 90).

### Estrutura
```
AcademiaBoxe.py      -> cena principal
Camera.py            -> câmera
TextureLoader.py     -> texturas
ObjLoaderSimple.py   -> loader .obj simples (base do professor)
ObjLoaderMTL.py      -> loader .obj com materiais (cores/texturas)
objetos/             -> modelos .obj (+ .mtl e texturas)
texturas/            -> piso (borracha) e parede (tijolo)
```
