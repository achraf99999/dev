from django.shortcuts import render
from PIL import Image
import random
import io
from django.http import HttpResponse
import base64
import json  

NOISY_IMAGE_PATH = 'path/to/save/noisy_image.png'  # Change cela vers le bon chemin

def resize_image(image, size=(400, 400)):
    return image.resize(size)


# Vue pour sauvegarder l'image dessinée
def save_drawing_view(request):
    if request.method == 'POST':
        # Obtenir les données de dessin de la requête
        draw_data = request.POST.get('draw_data')
        if draw_data:
            # Convertir les données de dessin en image
            # Suppose que draw_data est en base64
            draw_data = draw_data.split(',')[1]  # Enlever le préfixe "data:image/png;base64,"
            drawn_image_data = base64.b64decode(draw_data)

            # Sauvegarder l'image dessinée dans la session ou comme fichier
            request.session['drawn_image'] = base64.b64encode(drawn_image_data).decode('utf-8')
            return HttpResponse(json.dumps({'status': 'success'}), content_type="application/json")

    return HttpResponse(json.dumps({'status': 'fail'}), content_type="application/json")

def add_strong_noise_to_image(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')  # Convertir en RGB si nécessaire
    pixels = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if random.random() < 0.3:  # 30% de probabilité d'ajouter du bruit
                r, g, b = pixels[i, j]
                noise = random.randint(-40, 40)  # Intensifier le bruit
                pixels[i, j] = (max(0, min(255, r + noise)),
                                max(0, min(255, g + noise)),
                                max(0, min(255, b + noise)))
    return image

def image_noise_view(request):
    original_image_base64 = None
    noisy_image_base64 = None

    if request.method == 'POST':
        action = request.POST.get('action')
        uploaded_image = request.FILES.get('image')

        if uploaded_image:
            image = Image.open(uploaded_image)
            image = resize_image(image)  # Redimensionner l'image

            # Convertir l'image d'origine en base64 pour l'afficher
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            original_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            if action == 'add_noise':
                noisy_image = add_strong_noise_to_image(image.copy())  # Appliquer le bruit sur une copie de l'image

                # Convertir l'image bruitée en base64 pour l'afficher et la stocker dans la session
                buffered_noisy = io.BytesIO()
                noisy_image.save(buffered_noisy, format="PNG")
                noisy_image_base64 = base64.b64encode(buffered_noisy.getvalue()).decode('utf-8')

                # Stocker l'image bruitée dans la session
                request.session['noisy_image'] = noisy_image_base64  # Stocker en base64

            elif action == 'download_with_noise':
                # Récupérer l'image bruitée de la session
                noisy_image_base64 = request.session.get('noisy_image')
                if noisy_image_base64:
                    noisy_image_data = base64.b64decode(noisy_image_base64)

                    # Générer une réponse pour télécharger l'image avec bruit
                    response = HttpResponse(content_type='image/png')
                    response.write(noisy_image_data)
                    response['Content-Disposition'] = 'attachment; filename="noisy_image.png"'
                    return response

    return render(request, 'image_noise.html', {
        'original_image_base64': original_image_base64,
        'noisy_image_base64': noisy_image_base64,
    })