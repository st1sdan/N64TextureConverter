
## 🎮 N64 Style Texture Converter
<div align="center">




**Convert any image to authentic Nintendo 64 style textures**

*Transform modern images into pixel-perfect N64 textures with accurate color quantization and technical limitations*

[Features](#-features) -  [Installation](#-installation) -  [Usage](#-usage) -  [N64 Formats](#-n64-texture-formats)

</div>

## ✨ Features

- **Authentic N64 Formats**: 16-bit RGBA, 8-bit indexed, 32-bit RGBA, 4-bit indexed
- **Drag \& Drop Support**: Simply drag images from your file explorer
- **Batch Processing**: Convert multiple images at once
- **Real N64 Limitations**: Based on actual TMEM memory constraints (4KB)
- **Color Quantization**: Accurate 5/5/5/1 bit color reduction for 16-bit format
- **Customizable Settings**: Saturation, contrast, blur, and color count controls
- **Dithering Support**: Floyd-Steinberg dithering for better quality


## 🎨 N64 Texture Formats

| Format | Max Resolution | Colors | Best For |
| :-- | :-- | :-- | :-- |
| **16-bit RGBA** | 44×44 px | 32,768 + transparency | General textures with transparency |
| **8-bit Index** | 64×64 px | 256 | Standard N64 textures |
| **32-bit RGBA** | 32×32 px | 16M + full alpha | Semi-transparent effects only |
| **4-bit Index** | 64×128 px | 16 | Large textures with limited palette |

## 🚀 Installation

1. **Install Python 3.7+**
2. **Install dependencies:**
```bash
pip install pillow numpy tkinterdnd2
```

3. **Run the application:**
```bash
python3 -m main.py
```


## 📖 Usage

### Quick Start

1. **Add Images**: Drag \& drop files or click "Add Images"
2. **Choose Format**: Select N64 texture format from dropdown
3. **Select Output**: Choose folder to save converted textures
4. **Convert**: Click "Convert Textures"

### Settings

**N64 Format Options:**

- 16-bit RGBA (44×44) - Most versatile
- 8-bit Index (64×64) - Standard format
- 32-bit RGBA (32×32) - For transparency
- 4-bit Index (64×128) - Maximum resolution

**Image Processing:**

- **Saturation** (0.0-1.0): Color intensity
- **Contrast** (0.0-1.0): Image contrast
- **Blur** (0.0-2.0): N64-style softening
- **Colors** (2-256): Final color count
- **Dithering**: Improves quality at low color counts


## 🎯 Default N64 Settings

```
Format: 8-bit Index (64×64)
Saturation: 0.7
Contrast: 0.8
Blur: 0.5
Colors: 16
Dithering: Enabled
```


## 📁 Supported Formats

**Input:** PNG, JPEG, BMP, GIF, TIFF, WebP
**Output:** PNG (with N64 format suffix)

## 🔧 Building Executable

```bash
pip install pyinstaller
python3 -m pyinstaller
```


## 📋 Requirements

```txt
pillow>=10.0.0
numpy>=1.24.0
tkinterdnd2>=0.3.0
```


***

<div align="center">

**Made with ❤️ for retro gaming enthusiasts**

⭐ Star this repo if you find it useful!

</div>
