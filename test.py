import os
import shutil

def delete_images():
    # Pot do mape s slikami
    base_folder = 'uploads'

    # Preberemo vse datoteke v mapah (jakita, jakisa, itd.)
    for user_folder in os.listdir(base_folder):
        user_folder_path = os.path.join(base_folder, user_folder)
        if os.path.isdir(user_folder_path):
            for category_folder in os.listdir(user_folder_path):
                category_folder_path = os.path.join(user_folder_path, category_folder)
                if os.path.isdir(category_folder_path):
                    for image_file in os.listdir(category_folder_path):
                        image_path = os.path.join(category_folder_path, image_file)
                        if os.path.isfile(image_path):
                            os.remove(image_path)  # Izbriše posamezno sliko
                            print(f"Image {image_path} deleted.")
                    shutil.rmtree(category_folder_path)  # Odstrani prazno mapo kategorije

delete_images()