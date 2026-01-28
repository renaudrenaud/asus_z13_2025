# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

3D-printable protective back shell for the ASUS ROG Flow Z13 2025 tablet. The shell is generated using a FreeCAD macro and designed to be printed in two halves, then assembled around the tablet.

## Structure

- `3Dmodels/Asus_FreeCad_macro.py` - FreeCAD macro that generates the shell geometry

## Key Parameters (in macro)

- `TABLET_WIDTH/HEIGHT/THICKNESS` - Z13 2025 dimensions (300x204x15mm)
- `SHELL_THICKNESS` - Wall thickness (3mm)
- `CLEARANCE` - Gap between tablet and shell (0.5mm)

## Design

The macro creates a U-profile shell split into left and right halves:
1. `create_frame_shell()` - Main shell body with cavities and fillets
2. `cut_frame_in_half()` - Splits into left/right parts
3. `create_all_cutouts_left/right()` - Port and kickstand cutouts
4. `create_ventilation_cutouts_top()` - Circular ventilation holes

## License

Apache License 2.0
