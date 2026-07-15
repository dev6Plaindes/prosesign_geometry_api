import os
import base64
from datetime import datetime

from google import genai
from google.genai import types

# probar

class GeminiNanoBananaService:

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def generate_architecture_render(
        self,
        images_path: list[str],
        output_folder: str = "renders_ai",
        prompt: str = """
“Create a hyper-realistic architectural render from the attached 3D model of a school building. The provided 3D model/image is a strict and mandatory reference that must be preserved exactly.

IMPORTANT RESTRICTIONS:

Do NOT add any new buildings, structures, rooms, roofs, walls, floors, columns, stairs, furniture, playgrounds, or architectural elements.
Do NOT extend, redesign, reinterpret, or complete missing parts of the project.
Do NOT modify the existing infrastructure in any way.
Do NOT change dimensions, proportions, scale, heights, spacing, or geometry.
Keep the exact same layout, silhouette, and construction visible in the original 3D model/image.
Only improve the visual quality through realistic materials, lighting, textures, shadows, reflections, and environmental rendering.

Project context:

This is a school / educational campus.
All green areas must be rendered as synthetic grass (artificial turf).

Rendering style:

Hyper-realistic architectural visualization.
Realistic daylight and physically accurate lighting.
Professional architectural rendering quality.
Clean and believable environment.
Context elements such as people or vegetation are allowed only if they do NOT cover, alter, or imply additional infrastructure.

The final render must look exactly like the original 3D model structurally, with zero architectural modifications.”
       """
    ):
        # Validación inicial
        if not images_path:
            raise ValueError("La lista 'images_path' no puede estar vacía.")

        os.makedirs(output_folder, exist_ok=True)

        # Leer todas las imágenes dinámicamente
        image_parts = []
        for path in images_path:
            if not os.path.exists(path):
                raise FileNotFoundError(f"No existe la imagen: {path}")
            
            with open(path, "rb") as f:
                image_bytes = f.read()
                # Construimos el objeto Part directamente en el bucle
                image_parts.append(
                    types.Part.from_bytes(data=image_bytes, mime_type="image/png")
                )

        # Enviar todas las imágenes procesadas a Gemini
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[
                *image_parts,
                prompt
            ]
        )

        saved_images = []
        binary_image = None

        # Recorrer respuesta y guardar las imágenes generadas
        for idx, part in enumerate(response.candidates[0].content.parts):
            if getattr(part, "inline_data", None):
                image_data = part.inline_data.data

                filename = (
                    f"nano_render_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                    f"{idx}.png"
                )

                output_path = os.path.join(output_folder, filename)

                with open(output_path, "wb") as f:
                    f.write(image_data)

                saved_images.append(output_path)
                binary_image = image_data

        return {
            "success": True,
            "input_images": images_path,
            "generated_images": saved_images,
            "binary_image": binary_image
        }
        
        