# ASUS ROG Flow Z13 2025 - Back Shell

Some information about the Asus ROG Flow Z13 2025.

Let's start with a 3D-printable protective back shell for the ASUS ROG Flow Z13 2025 tablet.

## Project Description

This project provides a FreeCAD macro to generate a custom back shell/case for the ASUS ROG Flow Z13 2025 gaming tablet. The shell is designed to be 3D printed in two halves that can be assembled around the tablet and welded together using a PLA pen or gaffer or whatever you want.

### Features

- **U-profile design**: 3mm solid bottom + 15mm tablet cavity + 3mm retaining lip
- **Port cutouts**: Openings for USB, HDMI, power, and audio connectors on both sides
- **Kickstand notches**: Cutouts to allow the built-in kickstand to deploy
- **Ventilation holes**: Circular holes (6mm diameter) on the top edge for airflow
- **Webcam hole**: Opening for the rear camera
- **Rounded edges**: 5mm fillets on corners, 1.5mm on edges for comfortable handling
- **PLA welding groove**: V-shaped groove (1.5mm x 1.8mm) for pen welding assembly (removed right now, you can active it in the macro)

### Dimensions

- Tablet: 300 x 204 x 15 mm
- Shell outer dimensions: 307 x 211 x 21 mm
- Wall thickness: 3 mm
- Clearance: 0.5 mm

## FreeCAD Macro

### File

`3Dmodels/Asus_FreeCad_macro.py`

### Requirements

- FreeCAD (tested with FreeCAD 0.21+)

### Usage

1. Open FreeCAD
2. Go to **Macro > Macros...**
3. Navigate to and select `Asus_FreeCad_macro.py`
4. Click **Execute**
5. The macro generates two parts: `Left_Half_Final` and `Right_Half_Final`
6. Export each part to 3MF format: **File > Export...** and select `.3mf`
7. Import the 3MF files into your slicer (PrusaSlicer, Cura, etc.)

### Assembly

1. Print both halves
2. Place the tablet in one half
3. Fit the second half around the tablet
4. Use a 3D printing pen with PLA filament to weld along the V-groove where the two halves meet


## Comments

I got the tablet one month ago:
- OS is Ubuntu
- I don't play games, but I use it for local inference with Ollama (in a container)
- I use it for coding and development
- I am a big fan of this tablet, everything is so fast!
- It's perfect for my use cases



## License

Apache License 2.0
