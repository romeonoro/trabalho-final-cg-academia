import numpy as np

class ObjLoaderSimple:
    @staticmethod
    def load_obj(filename):
        vertices = []
        textures = []
        normals = []
        faces = []

        with open(filename, "r") as file:
            for line in file:
                values = line.split()

                if len(values) == 0:
                    continue

                if values[0] == "v":
                    vertex = [float(values[1]), float(values[2]), float(values[3])]
                    vertices.append(vertex)

                elif values[0] == "vt":
                    texcoord = [float(values[1]), float(values[2])]
                    textures.append(texcoord)
                    
                elif values[0] == "vn":
                    normal = [float(values[1]), float(values[2]), float(values[3])]
                    normals.append(normal)

                elif values[0] == "f":
                    face = []
                    for v in values[1:]:
                        vals = v.split('/')
                        v_idx = int(vals[0]) - 1
                        
                        vt_idx = -1
                        if len(vals) > 1 and vals[1]:
                            vt_idx = int(vals[1]) - 1
                            
                        vn_idx = -1
                        if len(vals) > 2 and vals[2]:
                            vn_idx = int(vals[2]) - 1

                        face.append((v_idx, vt_idx, vn_idx))

                    for i in range(1, len(face) - 1):
                        faces.append(face[0])
                        faces.append(face[i])
                        faces.append(face[i + 1])

        buffer = []
        for face in faces:
            v_idx, vt_idx, vn_idx = face

            vertex = vertices[v_idx]
            buffer.extend(vertex)

            if vt_idx >= 0 and vt_idx < len(textures):
                texcoord = textures[vt_idx]
            else:
                texcoord = [0.0, 0.0]
            buffer.extend(texcoord)
            
            if vn_idx >= 0 and vn_idx < len(normals):
                normal = normals[vn_idx]
            else:
                normal = [0.0, 1.0, 0.0]
            buffer.extend(normal)

        buffer = np.array(buffer, dtype=np.float32)
        num_vertices = len(buffer) // 8

        return buffer, num_vertices