from tkinter import Tk, Label, Button, Entry, filedialog, IntVar, StringVar, BooleanVar, Scale, HORIZONTAL, Toplevel, Checkbutton, DoubleVar
from tkinter.ttk import Progressbar
from PIL import Image, ImageEnhance
import numpy as np
import os
import random

def add_grain(image, intensity):
    """Apply grain (noise) effect to the image."""
    if intensity == 0:
        return image

    np_image = np.array(image)
    noise = np.random.normal(0, intensity, np_image.shape[:2])
    noise = noise[:, :, np.newaxis]
    np_image = np_image + noise
    np_image = np.clip(np_image, 0, 255).astype(np.uint8)
    return Image.fromarray(np_image, mode="RGBA")

def start_generation():
    try:
        png_folder = png_folder_path.get()
        background_folder = background_folder_path.get()
        output_folder = output_folder_path.get()
        output_count = int(output_count_var.get())

        # Define scale range
        scale_range = (scale_min.get(), scale_max.get())

        enable_exposure = exposure_var.get()
        enable_contrast = contrast_var.get()
        enable_shadows = shadows_var.get()
        enable_grain = grain_var.get()

        exposure_range = (exposure_min.get(), exposure_max.get())
        contrast_range = (contrast_min.get(), contrast_max.get())
        shadows_range = (shadows_min.get(), shadows_max.get())
        grain_range = (grain_min.get(), grain_max.get())

        os.makedirs(output_folder, exist_ok=True)

        png_files = [f for f in os.listdir(png_folder) if f.endswith('.png')]
        background_files = [f for f in os.listdir(background_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

        if not png_files:
            result_label.config(text="PNG dosyası bulunamadı!", fg="red")
            return
        if not background_files:
            result_label.config(text="Arka plan dosyası bulunamadı!", fg="red")
            return

        progress_window = Toplevel(root)
        progress_window.title("İlerleme Durumu")
        Label(progress_window, text="Cenker Cookluyor...").pack(pady=10)
        progress_bar = Progressbar(progress_window, orient="horizontal", length=300, mode="determinate")
        progress_bar.pack(pady=10)

        total_operations = output_count * len(png_files)
        operation_counter = 0

        for png_file in png_files:
            png_path = os.path.join(png_folder, png_file)
            overlay = Image.open(png_path).convert("RGBA")

            for i in range(output_count):
                bg_file = random.choice(background_files)
                bg_path = os.path.join(background_folder, bg_file)
                background = Image.open(bg_path).convert("RGBA")

                # Intelligent scaling to ensure entire PNG fits in background
                scale_width = background.width / overlay.width
                scale_height = background.height / overlay.height
                scale_factor = random.uniform(
                    min(scale_range[0], min(scale_width, scale_height)),
                    min(scale_range[1], min(scale_width, scale_height))
                )
                
                new_size = (int(overlay.width * scale_factor), int(overlay.height * scale_factor))
                resized_overlay = overlay.resize(new_size)

                # Ensure placement within background
                x = random.randint(0, max(0, background.width - resized_overlay.width))
                y = random.randint(0, max(0, background.height - resized_overlay.height))

                temp_overlay = Image.new('RGBA', background.size, (0, 0, 0, 0))
                temp_overlay.paste(resized_overlay, (x, y), resized_overlay)

                if enable_exposure:
                    factor = random.uniform(*exposure_range)
                    temp_overlay_adjusted = ImageEnhance.Brightness(temp_overlay).enhance(factor)
                else:
                    temp_overlay_adjusted = temp_overlay

                if enable_contrast:
                    factor = random.uniform(*contrast_range)
                    temp_overlay_adjusted = ImageEnhance.Contrast(temp_overlay_adjusted).enhance(factor)

                if enable_shadows:
                    factor = random.uniform(*shadows_range)
                    background = ImageEnhance.Brightness(background).enhance(factor)

                if enable_grain:
                    intensity = random.uniform(*grain_range)
                    temp_overlay_adjusted = add_grain(temp_overlay_adjusted, intensity)

                combined = Image.alpha_composite(background, temp_overlay_adjusted)

                output_file_name = f"{os.path.splitext(png_file)[0]}_{i+1}.png"
                output_path = os.path.join(output_folder, output_file_name)
                combined.save(output_path, format="PNG")

                background.close()
                combined.close()

                operation_counter += 1
                progress_bar["value"] = (operation_counter / total_operations) * 100
                progress_window.update_idletasks()

        progress_window.destroy()
        result_label.config(text=f"{output_count * len(png_files)} görüntü başarıyla oluşturuldu!", fg="green")

    except Exception as e:
        result_label.config(text=f"Hata: {str(e)}", fg="red")

def select_png_folder():
    folder_path = filedialog.askdirectory()
    png_folder_path.set(folder_path)

def select_background_folder():
    folder_path = filedialog.askdirectory()
    background_folder_path.set(folder_path)

def select_output_folder():
    folder_path = filedialog.askdirectory()
    output_folder_path.set(folder_path)

# Ana Ekran baba
root = Tk()
root.title("Cenker Görüntü Üretme Botu")

# PNG Folder Selection
Label(root, text="Cenker Görüntü Üretme Botu", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=10)

Label(root, text="PNG Klasörünü Seçin:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
png_folder_path = StringVar()
Entry(root, textvariable=png_folder_path, width=50).grid(row=1, column=1, padx=10, pady=5)
Button(root, text="Seç", command=select_png_folder).grid(row=1, column=2, padx=10, pady=5)

# Background Folder Selection
Label(root, text="Arka Plan Klasörünü Seçin:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
background_folder_path = StringVar()
Entry(root, textvariable=background_folder_path, width=50).grid(row=2, column=1, padx=10, pady=5)
Button(root, text="Seç", command=select_background_folder).grid(row=2, column=2, padx=10, pady=5)

# Output Folder Selection
Label(root, text="Çıktı Klasörünü Seçin:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
output_folder_path = StringVar()
Entry(root, textvariable=output_folder_path, width=50).grid(row=3, column=1, padx=10, pady=5)
Button(root, text="Seç", command=select_output_folder).grid(row=3, column=2, padx=10, pady=5)

# Output Count
Label(root, text="Her PNG için Üretilecek Görüntü Sayısı:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
output_count_var = IntVar(value=5)
Entry(root, textvariable=output_count_var, width=10).grid(row=4, column=1, padx=10, pady=5, sticky="w")

# Scale Range
Label(root, text="Scale Min:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
scale_min = DoubleVar(value=0.1)
Scale(root, from_=0.1, to=10, resolution=0.1, orient=HORIZONTAL, variable=scale_min).grid(row=5, column=1)

Label(root, text="Scale Max:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
scale_max = DoubleVar(value=1)
Scale(root, from_=0.1, to=10, resolution=0.1, orient=HORIZONTAL, variable=scale_max).grid(row=6, column=1)

# Exposure Range
Label(root, text="Exposure Min-Max:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
exposure_min, exposure_max = DoubleVar(value=1), DoubleVar(value=2)
Scale(root, from_=0.1, to=4, resolution=0.1, orient=HORIZONTAL, variable=exposure_min).grid(row=7, column=1)
Scale(root, from_=0.1, to=4, resolution=0.1, orient=HORIZONTAL, variable=exposure_max).grid(row=7, column=2)

# Contrast Range
Label(root, text="Contrast Min-Max:").grid(row=8, column=0, padx=10, pady=5, sticky="w")
contrast_min, contrast_max = DoubleVar(value=1), DoubleVar(value=2)
Scale(root, from_=0.1, to=4, resolution=0.1, orient=HORIZONTAL, variable=contrast_min).grid(row=8, column=1)
Scale(root, from_=0.1, to=4, resolution=0.1, orient=HORIZONTAL, variable=contrast_max).grid(row=8, column=2)

# Shadows Range
Label(root, text="Shadows Min-Max:").grid(row=9, column=0, padx=10, pady=5, sticky="w")
shadows_min, shadows_max = DoubleVar(value=0.5), DoubleVar(value=2)
Scale(root, from_=0.1, to=4, resolution=0.1, orient=HORIZONTAL, variable=shadows_min).grid(row=9, column=1)
Scale(root, from_=0.1, to=4, resolution=0.1, orient=HORIZONTAL, variable=shadows_max).grid(row=9, column=2)

# Grain Range
Label(root, text="Grain Min-Max:").grid(row=10, column=0, padx=10, pady=5, sticky="w")
grain_min, grain_max = IntVar(value=0), IntVar(value=50)
Scale(root, from_=0, to=100, resolution=1, orient=HORIZONTAL, variable=grain_min).grid(row=10, column=1)
Scale(root, from_=0, to=100, resolution=1, orient=HORIZONTAL, variable=grain_max).grid(row=10, column=2)

# Effect Toggles
exposure_var = BooleanVar(value=True)
contrast_var = BooleanVar(value=True)
shadows_var = BooleanVar(value=True)
grain_var = BooleanVar(value=True)
Checkbutton(root, text="Exposure Etkin", variable=exposure_var).grid(row=11, column=1, sticky="w")
Checkbutton(root, text="Contrast Etkin", variable=contrast_var).grid(row=11, column=2, sticky="w")
Checkbutton(root, text="Shadows Etkin", variable=shadows_var).grid(row=11, column=3, sticky="w")
Checkbutton(root, text="Grain Etkin", variable=grain_var).grid(row=11, column=4, sticky="w")

# Generate Button
Button(root, text="Görselleri Üret", command=start_generation, bg="blue", fg="white").grid(row=12, column=1, pady=10)

# Result Label
result_label = Label(root, text="")
result_label.grid(row=13, column=0, columnspan=4, pady=5)

root.mainloop()
