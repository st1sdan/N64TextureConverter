from PIL import Image, ImageEnhance, ImageFilter
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ВАЖНО: Импорт для drag & drop
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
    print("tkinterdnd2 не установлена. Drag & drop недоступен.")

# Настройки форматов N64
N64_FORMATS = {
    '16-bit RGBA (44×44)': {
        'max_size': (44, 44),
        'color_depth': 16,
        'alpha_bits': 1,
        'description': 'Наиболее универсальный формат N64'
    },
    '8-bit Index (64×64)': {
        'max_size': (64, 64), 
        'color_depth': 8,
        'alpha_bits': 0,
        'description': 'Стандартный формат для большинства текстур'
    },
    '32-bit RGBA (32×32)': {
        'max_size': (32, 32),
        'color_depth': 32,
        'alpha_bits': 8,
        'description': 'Только для полупрозрачных текстур'
    },
    '4-bit Index (64×128)': {
        'max_size': (64, 128),
        'color_depth': 4,
        'alpha_bits': 0,
        'description': 'Максимальное разрешение с ограниченной палитрой'
    }
}

def quantize_color_16bit(color):
    """Квантизует цвет до 16-bit N64 формата (5/5/5/1 бит)"""
    r, g, b, a = color
    r = int((r / 255.0) * 31) * 8
    g = int((g / 255.0) * 31) * 8
    b = int((b / 255.0) * 31) * 8
    a = 255 if a > 127 else 0
    return (r, g, b, a)

def quantize_color_8bit(color):
    """Квантизует цвет до 8-bit формата"""
    r, g, b, a = color
    r = int((r / 255.0) * 7) * 36
    g = int((g / 255.0) * 7) * 36  
    b = int((b / 255.0) * 3) * 85
    return (r, g, b, 255)

def quantize_color_4bit(color):
    """Квантизует цвет до 4-bit формата"""
    r, g, b, a = color
    r = int((r / 255.0) * 3) * 85
    g = int((g / 255.0) * 3) * 85
    b = int((b / 255.0) * 3) * 85
    return (r, g, b, 255)

def apply_n64_style_advanced(image, format_name, saturation=0.7, contrast=0.8, 
                           blur_radius=0.5, dithering=True, custom_color_count=None):
    """Применяет продвинутый N64 стиль с учетом технических ограничений"""
    
    format_info = N64_FORMATS[format_name]
    target_size = format_info['max_size']
    color_depth = format_info['color_depth']
    
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    image = image.resize(target_size, Image.LANCZOS)
    
    if saturation != 1.0:
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(saturation)
    
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
    
    if blur_radius > 0:
        image = image.filter(ImageFilter.BoxBlur(blur_radius))
    
    pixels = list(image.getdata())
    quantized_pixels = []
    
    for pixel in pixels:
        if color_depth == 16:
            quantized_pixels.append(quantize_color_16bit(pixel))
        elif color_depth == 8:
            quantized_pixels.append(quantize_color_8bit(pixel))
        elif color_depth == 4:
            quantized_pixels.append(quantize_color_4bit(pixel))
        else:
            quantized_pixels.append(pixel)
    
    quantized_image = Image.new('RGBA', target_size)
    quantized_image.putdata(quantized_pixels)
    
    if dithering:
        if custom_color_count:
            colors = min(custom_color_count, 2**color_depth)
        else:
            colors = 2**color_depth
        
        try:
            rgb_image = quantized_image.convert('RGB')
            quantized_rgb = rgb_image.quantize(
                colors=colors,
                method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.FLOYDSTEINBERG
            )
            quantized_image = quantized_rgb.convert('RGBA')
        except Exception:
            pass
    
    return quantized_image

# ИСПРАВЛЕННЫЙ КЛАСС с рабочим drag & drop
class N64TextureApp(TkinterDnD.Tk if DRAG_DROP_AVAILABLE else tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("N64 Style Texture Converter - Advanced")
        self.geometry("650x700")
        self.resizable(False, False)
        
        self.input_files = []
        self.output_folder = None
        
        self.selected_format = tk.StringVar(value='8-bit Index (64×64)')
        self.saturation = tk.DoubleVar(value=0.7)
        self.contrast = tk.DoubleVar(value=0.8) 
        self.blur_radius = tk.DoubleVar(value=0.5)
        self.enable_dithering = tk.BooleanVar(value=True)
        self.color_count = tk.IntVar(value=256)
        
        self.create_widgets()

    def create_widgets(self):
        # Заголовок
        title_label = ttk.Label(self, text="Nintendo 64 Texture Converter", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Статус drag & drop
        if DRAG_DROP_AVAILABLE:
            subtitle_text = "Перетащите файлы в список ниже или используйте кнопки"
            subtitle_color = "green"
        else:
            subtitle_text = "Drag & Drop недоступен (установите tkinterdnd2)"
            subtitle_color = "red"
            
        subtitle_label = ttk.Label(self, text=subtitle_text, 
                                  font=("Arial", 9), foreground=subtitle_color)
        subtitle_label.pack()

        # Рамка для входных файлов
        drag_text = "📁 Перетащите изображения сюда" if DRAG_DROP_AVAILABLE else "Входные файлы изображений"
        frame_files = ttk.LabelFrame(self, text=drag_text)
        frame_files.pack(fill="both", expand=True, padx=10, pady=5)

        self.file_listbox = tk.Listbox(frame_files, height=6)
        self.file_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scrollbar_files = ttk.Scrollbar(frame_files, orient="vertical", 
                                       command=self.file_listbox.yview)
        scrollbar_files.pack(side="right", fill="y", pady=5)
        self.file_listbox.config(yscrollcommand=scrollbar_files.set)

        # НАСТРОЙКА DRAG & DROP
        if DRAG_DROP_AVAILABLE:
            self.file_listbox.drop_target_register(DND_FILES)
            self.file_listbox.dnd_bind('<<Drop>>', self.on_drop)

        # Кнопки управления файлами
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Добавить изображения", 
                   command=self.add_files).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Очистить список", 
                   command=self.clear_files).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить выбранное", 
                   command=self.remove_selected).pack(side="left", padx=5)

        # Папка для сохранения
        output_frame = ttk.Frame(self)
        output_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(output_frame, text="Папка сохранения:").pack(side="left")
        self.output_folder_label = ttk.Label(output_frame, text="(Не выбрана)", 
                                           foreground="red")
        self.output_folder_label.pack(side="left", padx=5)
        ttk.Button(output_frame, text="Выбрать папку", 
                   command=self.select_output_folder).pack(side="right")

        # Выбор формата N64
        format_frame = ttk.LabelFrame(self, text="Формат текстуры N64")
        format_frame.pack(fill="x", padx=10, pady=5)
        
        format_combo = ttk.Combobox(format_frame, textvariable=self.selected_format, 
                                   values=list(N64_FORMATS.keys()), state="readonly")
        format_combo.pack(fill="x", padx=5, pady=2)
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)
        
        self.format_desc_label = ttk.Label(format_frame, 
                                          text=N64_FORMATS['8-bit Index (64×64)']['description'],
                                          font=("Arial", 8), foreground="gray")
        self.format_desc_label.pack(padx=5, pady=2)

        # Настройка количества цветов
        color_count_frame = ttk.LabelFrame(self, text="Количество цветов в финальном изображении")
        color_count_frame.pack(fill="x", padx=10, pady=5)

        color_count_scale = ttk.Scale(color_count_frame, from_=2, to=256, 
                                     variable=self.color_count, orient="horizontal")
        color_count_scale.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        color_count_scale.config(command=self.update_color_count_label)

        self.color_count_label = ttk.Label(color_count_frame, text="256")
        self.color_count_label.grid(row=0, column=1, padx=5, pady=2)

        # Быстрые настройки цветов
        quick_color_frame = ttk.Frame(color_count_frame)
        quick_color_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        for count in [2, 4, 8, 16, 32, 64, 256]:
            ttk.Button(quick_color_frame, text=str(count), width=4, 
                       command=lambda c=count: self.set_color_count(c)).pack(side="left", padx=2)

        color_count_frame.columnconfigure(0, weight=1)

        # Настройки фильтра
        filter_frame = ttk.LabelFrame(self, text="Настройки обработки")
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Насыщенность
        ttk.Label(filter_frame, text="Насыщенность:").grid(row=0, column=0, 
                                                           sticky="w", padx=5, pady=2)
        saturation_scale = ttk.Scale(filter_frame, from_=0.0, to=1.0, 
                                   variable=self.saturation, orient="horizontal")
        saturation_scale.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.saturation_label = ttk.Label(filter_frame, text="0.70")
        self.saturation_label.grid(row=0, column=2, padx=5, pady=2)

        # Контраст
        ttk.Label(filter_frame, text="Контраст:").grid(row=1, column=0, 
                                                       sticky="w", padx=5, pady=2)
        contrast_scale = ttk.Scale(filter_frame, from_=0.0, to=1.0, 
                                 variable=self.contrast, orient="horizontal")
        contrast_scale.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.contrast_label = ttk.Label(filter_frame, text="0.80")
        self.contrast_label.grid(row=1, column=2, padx=5, pady=2)

        # Размытие
        ttk.Label(filter_frame, text="Размытие:").grid(row=2, column=0, 
                                                       sticky="w", padx=5, pady=2)
        blur_scale = ttk.Scale(filter_frame, from_=0.0, to=2.0, 
                              variable=self.blur_radius, orient="horizontal")
        blur_scale.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.blur_label = ttk.Label(filter_frame, text="0.5")
        self.blur_label.grid(row=2, column=2, padx=5, pady=2)

        filter_frame.columnconfigure(1, weight=1)

        # Привязки для обновления меток
        saturation_scale.config(command=self.update_saturation_label)
        contrast_scale.config(command=self.update_contrast_label)
        blur_scale.config(command=self.update_blur_label)

        # Опции
        options_frame = ttk.Frame(self)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Checkbutton(options_frame, text="Включить дизеринг (улучшает качество)", 
                       variable=self.enable_dithering).pack(side="left")

        # Кнопки управления
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(control_frame, text="Сбросить к N64 умолчаниям", 
                   command=self.reset_to_defaults).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Конвертировать текстуры", 
                   command=self.convert_textures).pack(side="right", padx=5)

        # Прогресс-бар
        self.progress = ttk.Progressbar(self, mode='determinate')
        self.progress.pack(fill="x", padx=10, pady=5)

    # РАБОЧИЙ DRAG & DROP
    def on_drop(self, event):
        """Обработка перетаскивания файлов"""
        # event.data содержит пути к файлам, разделенные пробелами
        files = self.tk.splitlist(event.data)
        
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
        added_count = 0
        
        for file_path in files:
            # Убираем возможные кавычки
            file_path = file_path.strip('{}\"\'')
            
            if (os.path.isfile(file_path) and 
                file_path.lower().endswith(image_extensions) and 
                file_path not in self.input_files):
                
                self.input_files.append(file_path)
                filename_display = os.path.basename(file_path)
                self.file_listbox.insert(tk.END, filename_display)
                added_count += 1
        
        if added_count > 0:
            messagebox.showinfo("Файлы добавлены", f"Добавлено {added_count} изображений")

    def set_color_count(self, count):
        self.color_count.set(count)
        self.update_color_count_label(count)

    def update_color_count_label(self, value):
        self.color_count_label.config(text=f"{int(float(value))}")

    def remove_selected(self):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.file_listbox.delete(index)
            del self.input_files[index]

    def on_format_change(self, event=None):
        format_name = self.selected_format.get()
        description = N64_FORMATS[format_name]['description']
        max_size = N64_FORMATS[format_name]['max_size']
        
        full_desc = f"{description} | Макс. размер: {max_size[0]}×{max_size[1]}"
        self.format_desc_label.config(text=full_desc)

    def update_saturation_label(self, value):
        self.saturation_label.config(text=f"{float(value):.2f}")

    def update_contrast_label(self, value):
        self.contrast_label.config(text=f"{float(value):.2f}")

    def update_blur_label(self, value):
        self.blur_label.config(text=f"{float(value):.1f}")

    def reset_to_defaults(self):
        self.selected_format.set('8-bit Index (64×64)')
        self.saturation.set(0.7)
        self.contrast.set(0.8) 
        self.blur_radius.set(0.5)
        self.enable_dithering.set(True)
        self.color_count.set(16)
        
        self.on_format_change()
        self.update_saturation_label(0.7)
        self.update_contrast_label(0.8)
        self.update_blur_label(0.5)
        self.update_color_count_label(16)

    def add_files(self):
        filenames = filedialog.askopenfilenames(
            title="Выберите файлы изображений", 
            filetypes=[
                ("Все изображения", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp"),
                ("PNG файлы", "*.png"),
                ("JPEG файлы", "*.jpg *.jpeg"), 
                ("BMP файлы", "*.bmp"),
                ("GIF файлы", "*.gif"),
                ("TIFF файлы", "*.tiff"),
                ("WebP файлы", "*.webp"),
                ("Все файлы", "*.*")
            ]
        )
        if filenames:
            for f in filenames:
                if f not in self.input_files:
                    self.input_files.append(f)
                    filename_display = os.path.basename(f)
                    self.file_listbox.insert(tk.END, filename_display)

    def clear_files(self):
        self.input_files.clear()
        self.file_listbox.delete(0, tk.END)

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку для сохранения")
        if folder:
            self.output_folder = folder
            self.output_folder_label.config(text=folder, foreground="green")

    def convert_textures(self):
        if not self.input_files:
            messagebox.showwarning("Нет входных файлов", 
                                 "Добавьте файлы изображений для конвертации.")
            return
        if not self.output_folder:
            messagebox.showwarning("Нет выходной папки", 
                                 "Выберите папку для сохранения.")
            return
        
        self.progress['maximum'] = len(self.input_files)
        self.progress['value'] = 0
        
        converted_count = 0
        failed_files = []
        format_name = self.selected_format.get()
        
        for i, filepath in enumerate(self.input_files):
            try:
                with Image.open(filepath) as img:
                    n64_img = apply_n64_style_advanced(
                        img,
                        format_name,
                        self.saturation.get(),
                        self.contrast.get(), 
                        self.blur_radius.get(),
                        self.enable_dithering.get(),
                        self.color_count.get()
                    )
                    
                    basename = os.path.basename(filepath)
                    name_without_ext = os.path.splitext(basename)[0]
                    format_suffix = format_name.split()[0].lower().replace('-bit', 'bit')
                    color_suffix = f"{self.color_count.get()}colors"
                    new_name = f"{name_without_ext}_n64_{format_suffix}_{color_suffix}.png"
                    output_path = os.path.join(self.output_folder, new_name)
                    
                    n64_img.save(output_path, "PNG")
                    converted_count += 1
                    
            except Exception as e:
                failed_files.append(f"{os.path.basename(filepath)}: {str(e)}")
            
            self.progress['value'] = i + 1
            self.update()
        
        if failed_files:
            error_msg = f"Конвертировано: {converted_count}\nОшибки:\n" + "\n".join(failed_files)
            messagebox.showwarning("Конвертация завершена с ошибками", error_msg)
        else:
            messagebox.showinfo("Готово", 
                               f"Все {converted_count} текстур конвертированы!\n"
                               f"Формат: {format_name}\n"
                               f"Количество цветов: {self.color_count.get()}")
        
        self.progress['value'] = 0

if __name__ == '__main__':
    app = N64TextureApp()
    app.mainloop()
