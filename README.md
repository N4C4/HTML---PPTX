# html2pptx

Convierte wireframes **HTML** (o imágenes **PNG/JPG**) en presentaciones **PowerPoint editables**: cada caja, borde, texto y gráfico queda como forma o cuadro de texto real, no como una imagen pegada. Ideal para importar en **Canva** (*Subir archivo → PowerPoint*) y seguir editando allí.

## Características

- **HTML → PPTX editable**: renderiza el HTML en Chrome/Edge y mide la geometría real (posición, bordes por lado, colores, redondeos, tipografía, tamaño, negritas, interlineado, espaciado de letras, texto en mayúsculas).
- **Soporta**: cajas con bordes parciales o discontinuos, esquinas redondeadas, tablas, gráfico de donut (conic-gradient) y líneas SVG (p. ej. código QR).
- **PNG/JPG → PPTX**: cada imagen entra como fondo de una diapositiva.
- **CLI** (`html2pptx`) y **GUI** (`html2pptx-gui`) en español.
- Sin dependencias de navegador externo a Python: usa el Chrome/Edge ya instalado (se puede forzar con la variable de entorno `HTML2PPTX_BROWSER`).
- Multiplataforma: Windows, macOS y Linux (Chrome/Chromium/Edge).

## Requisitos

- Python 3.9 o superior (con `tkinter` para la GUI; viene en el instalador estándar de Windows/macOS).
- Google Chrome, Chromium o Microsoft Edge.
- `python-pptx` (se instala automáticamente con la herramienta).

## Instalación

```bash
cd html2pptx
pip install .
```

En desarrollo (instalación editable):

```bash
pip install -e .
```

## Uso

### Interfaz gráfica

```bash
html2pptx-gui
```

1. Agregue los archivos con **+ HTML…** o **+ Imágenes…** (el orden de la lista define las diapositivas).
2. Ajuste el lienzo (por defecto 1440 × 1024 px) y, si quiere, la ruta de salida.
3. Pulse **Convertir**; el registro muestra cada archivo procesado. **Abrir carpeta** lleva al resultado.

### Línea de comandos

```bash
# Un wireframe HTML
html2pptx mi-wireframe.html -o mi-wireframe.pptx

# Varias láminas en una sola presentación (el orden define las diapositivas)
html2pptx lamina1.html lamina2.html lamina3.html -o laminas.pptx

# Imágenes (una diapositiva por imagen) y mezcla HTML + imágenes
html2pptx pantalla1.png pantalla2.jpg -o pantallas.pptx
html2pptx fondo.png formulario.html -o mixto.pptx

# Lienzo personalizado y versión
html2pptx ejemplo.html --width 1920 --height 1080
html2pptx --version
```

También disponible como módulo: `python -m html2pptx ejemplo.html`.

### Desde Python

```python
from html2pptx import convert

convert(["examples/ejemplo.html"], "salida.pptx")
```

## Ejemplo

```bash
html2pptx examples/ejemplo.html -o ejemplo.pptx
```

`examples/ejemplo.html` es un wireframe de muestra (encabezado, botones, KPIs, donut y tabla) que demuestra lo que la herramienta detecta y reproduce como formas editables.

## Cómo funciona

1. Se inyecta un script de medición al HTML y se abre en modo *headless* con Chrome/Edge (`--dump-dom`).
2. El script recorre el DOM con `getBoundingClientRect` + `getComputedStyle` y devuelve la geometría: rectángulos y sus cuatro bordes por separado, rellenos, radios, textos con su fuente exacta, donut (porcentajes del `conic-gradient`) y líneas SVG.
3. Ese modelo se traduce a formas de PowerPoint (rectángulos, redondeados, óvalos, sectores "pie", conectores) y cuadros de texto con alineación, tamaño y color reales.

**Límites**

- No captura imágenes rasterizadas dentro del HTML (`<img>`, `background-image`), sombras complejas ni animaciones: convierta esas partes a PNG y agréguelas como diapositiva.
- El texto usa las tipografías del sistema (p. ej. Comic Sans MS, Segoe Print). Al importar en Canva, las fuentes que Canva no tenga se sustituirán por equivalentes (el texto sigue siendo editable).
- Es una medición, no un visor: el PPTX queda geométricamente fiel, pero no conserva el HTML original.

## Licencia

MIT — ver [LICENSE](LICENSE).
