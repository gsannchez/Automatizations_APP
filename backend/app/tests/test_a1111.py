from app.services.image_generator import generate_images_for_scenes

scenes = [
    {
        "text": "Un perro feliz",
        "duration": 3,
        "image_prompt": "a cute dog running in a park"
    }
]

paths = generate_images_for_scenes(scenes)
print("Rutas generadas:", paths)
