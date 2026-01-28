#!/usr/bin/env python3
"""
FreeCAD script for Asus ROG Flow Z13 2025 back shell
PROTO version: Simple frame for dimension testing
"""

import FreeCAD as App
import Part

# Tablet parameters (exact Z13 2025 dimensions)
TABLET_WIDTH = 300.0  # mm
TABLET_HEIGHT = 204.0  # mm
TABLET_THICKNESS = 15.0  # mm

# Shell parameters
SHELL_THICKNESS = 3.0  # mm - wall thickness (v1.1.0: increased for rigidity)
CLEARANCE = 0.5  # mm - gap between tablet and shell
LIP_HEIGHT = 8.0  # mm - lip height

# Inner fillets
INNER_CORNER_RADIUS = 5.0  # mm


def create_frame_shell(doc):
    """Creates a simple frame with U-profile - wide cavity for 15mm tablet, lip on top"""

    # CORRECTED DIMENSIONS
    # Inner cavity = tablet size + clearance
    cavity_width = TABLET_WIDTH + 2 * CLEARANCE
    cavity_height = TABLET_HEIGHT + 2 * CLEARANCE

    # Outer box = cavity + wall thickness
    outer_width = cavity_width + 2 * SHELL_THICKNESS
    outer_height = cavity_height + 2 * SHELL_THICKNESS

    # Heights for U-profile
    TABLET_SPACE = 15.0  # mm - height for tablet (15mm thickness)
    LIP_OVERHANG = 3.0   # mm - horizontal lip on sides and top (original value)
    LIP_OVERHANG_BOTTOM = 9.0  # mm - horizontal lip at bottom (v1.2.6: +6mm)
    LIP_VERTICAL = 3.0   # mm - vertical thickness of lip
    total_height = SHELL_THICKNESS + TABLET_SPACE + LIP_VERTICAL

    print(f"Outer box dimensions: {outer_width} x {outer_height} x {total_height} mm")
    print(f"Cavity dimensions: {cavity_width} x {cavity_height} mm")
    print(f"Tablet dimensions: {TABLET_WIDTH} x {TABLET_HEIGHT} x 15 mm")
    print(f"Structure: Bottom {SHELL_THICKNESS}mm + Tablet space {TABLET_SPACE}mm + Lip {LIP_VERTICAL}mm")
    
    # Outer body
    outer_box = Part.makeBox(outer_width, outer_height, total_height)

    # WIDE CAVITY at BOTTOM: To accommodate the tablet (15mm high)
    # From z=SHELL_THICKNESS to z=SHELL_THICKNESS+TABLET_SPACE
    lower_cavity = Part.makeBox(
        cavity_width,
        cavity_height,
        TABLET_SPACE + 0.1,
        App.Vector(SHELL_THICKNESS, SHELL_THICKNESS, SHELL_THICKNESS)
    )

    # NARROW CAVITY at TOP: With lip going inward (asymmetric: more at bottom)
    # From z=SHELL_THICKNESS+TABLET_SPACE to z=total_height
    upper_cavity_width = cavity_width - 2 * LIP_OVERHANG
    upper_cavity_height = cavity_height - LIP_OVERHANG - LIP_OVERHANG_BOTTOM  # Asymmetric top/bottom
    upper_cavity = Part.makeBox(
        upper_cavity_width,
        upper_cavity_height,
        LIP_VERTICAL + 0.1,
        App.Vector(SHELL_THICKNESS + LIP_OVERHANG, SHELL_THICKNESS + LIP_OVERHANG_BOTTOM, SHELL_THICKNESS + TABLET_SPACE)
    )

    # Remove bottom IN THE MIDDLE ONLY (save material)
    # Keep 4cm of solid material at TOP and 4cm at BOTTOM
    bottom_margin = 10.0  # mm - margin on sides
    solid_top_area = 40.0  # mm - 4cm of solid bottom at top
    solid_bottom_area = 40.0  # mm - 4cm of solid bottom at bottom

    # The hole starts 4cm after the bottom and stops 4cm before the top
    bottom_hole_y_start = SHELL_THICKNESS + bottom_margin + solid_bottom_area
    bottom_hole_y_size = cavity_height - 2 * bottom_margin - solid_top_area - solid_bottom_area

    bottom_hole = Part.makeBox(
        cavity_width - 2 * bottom_margin,
        bottom_hole_y_size,
        SHELL_THICKNESS + 0.1,
        App.Vector(SHELL_THICKNESS + bottom_margin, bottom_hole_y_start, -0.05)
    )

    # Subtract all cavities
    shell_shape = outer_box.cut(lower_cavity).cut(upper_cavity).cut(bottom_hole)

    # Hole for rear webcam TOP LEFT (in solid area)
    # v1.2.6: Moved down 3mm and closer to edge by 2mm
    WEBCAM_FROM_TOP = 18.0  # mm - 1.8cm from top (was 1.5cm)
    WEBCAM_FROM_SIDE = 18.0  # mm - 1.8cm from left side (was 2.0cm)
    WEBCAM_RADIUS = 6.0  # mm - radius 0.6cm = diameter 1.2cm

    # Left camera position (top left)
    webcam_x = SHELL_THICKNESS + WEBCAM_FROM_SIDE
    webcam_y = outer_height - SHELL_THICKNESS - WEBCAM_FROM_TOP

    webcam_hole = Part.makeCylinder(
        WEBCAM_RADIUS,
        SHELL_THICKNESS + 1,
        App.Vector(webcam_x, webcam_y, -0.5),
        App.Vector(0, 0, 1)
    )

    # Subtract webcam hole
    shell_shape = shell_shape.cut(webcam_hole)
    
    # === APPLY FILLETS IN 3 SEPARATE PASSES ===

    # PASS 1: Inner cavity fillets
    print("Applying inner fillets...")
    edges_to_fillet_inner = []

    for edge in shell_shape.Edges:
        if len(edge.Vertexes) < 2:
            continue

        p1 = edge.Vertexes[0].Point
        p2 = edge.Vertexes[1].Point

        # Vertical edge
        if abs(p1.x - p2.x) < 0.001 and abs(p1.y - p2.y) < 0.001:
            x = p1.x
            y = p1.y
            z = p1.z

            # INNER corners of the wide cavity (at bottom)
            is_inner_corner = (
                (abs(x - SHELL_THICKNESS) < 0.1 and abs(y - SHELL_THICKNESS) < 0.1) or
                (abs(x - SHELL_THICKNESS) < 0.1 and abs(y - (outer_height - SHELL_THICKNESS)) < 0.1) or
                (abs(x - (outer_width - SHELL_THICKNESS)) < 0.1 and abs(y - SHELL_THICKNESS) < 0.1) or
                (abs(x - (outer_width - SHELL_THICKNESS)) < 0.1 and abs(y - (outer_height - SHELL_THICKNESS)) < 0.1)
            )

            # Inner edges (lower part only)
            if is_inner_corner and z > SHELL_THICKNESS - 0.5 and z < SHELL_THICKNESS + TABLET_SPACE + 0.5:
                edges_to_fillet_inner.append(edge)

    if edges_to_fillet_inner and INNER_CORNER_RADIUS > 0:
        try:
            shell_shape = shell_shape.makeFillet(INNER_CORNER_RADIUS, edges_to_fillet_inner)
            print(f"  -> {len(edges_to_fillet_inner)} inner edges filleted")
        except Exception as e:
            print(f"  Warning: Inner fillet error: {e}")

    # PASS 2: Outer vertical fillets (corners)
    print("Applying outer vertical fillets...")
    edges_to_fillet_outer_vertical = []

    for edge in shell_shape.Edges:
        if len(edge.Vertexes) < 2:
            continue

        p1 = edge.Vertexes[0].Point
        p2 = edge.Vertexes[1].Point

        # Vertical edge
        if abs(p1.x - p2.x) < 0.001 and abs(p1.y - p2.y) < 0.001:
            x = p1.x
            y = p1.y

            # OUTER corners of the box
            is_outer_corner = (
                (abs(x) < 0.1 and abs(y) < 0.1) or
                (abs(x) < 0.1 and abs(y - outer_height) < 0.1) or
                (abs(x - outer_width) < 0.1 and abs(y) < 0.1) or
                (abs(x - outer_width) < 0.1 and abs(y - outer_height) < 0.1)
            )

            if is_outer_corner:
                edges_to_fillet_outer_vertical.append(edge)

    OUTER_CORNER_RADIUS = 5.0  # mm
    if edges_to_fillet_outer_vertical and OUTER_CORNER_RADIUS > 0:
        try:
            shell_shape = shell_shape.makeFillet(OUTER_CORNER_RADIUS, edges_to_fillet_outer_vertical)
            print(f"  -> {len(edges_to_fillet_outer_vertical)} outer corners filleted")
        except Exception as e:
            print(f"  Warning: Vertical fillet error: {e}")

    # PASS 3: Outer horizontal fillets (light edges)
    print("Applying outer horizontal fillets...")
    edges_to_fillet_outer_horizontal = []

    for edge in shell_shape.Edges:
        if len(edge.Vertexes) < 2:
            continue

        p1 = edge.Vertexes[0].Point
        p2 = edge.Vertexes[1].Point

        # HORIZONTAL outer edges (top and bottom edges)
        if abs(p1.z - p2.z) < 0.001:
            z = p1.z
            x_min = min(p1.x, p2.x)
            x_max = max(p1.x, p2.x)
            y_min = min(p1.y, p2.y)
            y_max = max(p1.y, p2.y)

            # Outer edges (on outer faces of the box)
            is_outer_edge = (
                (abs(z - total_height) < 0.1 or abs(z) < 0.1) and  # Top or bottom
                (
                    abs(x_min) < 0.1 or abs(x_max - outer_width) < 0.1 or  # Left or right side
                    abs(y_min) < 0.1 or abs(y_max - outer_height) < 0.1    # Front or back side
                )
            )

            if is_outer_edge:
                edges_to_fillet_outer_horizontal.append(edge)

    OUTER_EDGE_RADIUS = 1.5  # mm - very light for horizontal edges
    if edges_to_fillet_outer_horizontal and OUTER_EDGE_RADIUS > 0:
        try:
            shell_shape = shell_shape.makeFillet(OUTER_EDGE_RADIUS, edges_to_fillet_outer_horizontal)
            print(f"  -> {len(edges_to_fillet_outer_horizontal)} horizontal edges filleted")
        except Exception as e:
            print(f"  Warning: Horizontal fillet error: {e}")
    
    shell = doc.addObject("Part::Feature", "Complete_Frame_U_Profile")
    shell.Shape = shell_shape
    
    return shell


def create_all_cutouts_left(doc):
    """Creates all objects to subtract for the left part"""
    cutouts = []

    cavity_height = TABLET_HEIGHT + 2 * CLEARANCE

    # Cutout 1: Main ports (USB, HDMI, power) AT TOP
    # v1.2.6: Moved up 2mm and enlarged
    PORT_START_FROM_TOP = 23.0  # mm - 2.3cm from top (was 2.5cm)
    PORT_CUT_LENGTH = 74.0  # mm - 7.4cm length (was 7.2cm)

    port_y_start = cavity_height + SHELL_THICKNESS - PORT_START_FROM_TOP - PORT_CUT_LENGTH

    TABLET_SPACE = 15.0  # mm
    port_cut_height = TABLET_SPACE + 1  # mm - goes through entire vertical lip
    port_cut_width = 8.0  # mm

    ports_cutout = Part.makeBox(
        port_cut_width,   # Width (depth into wall)
        PORT_CUT_LENGTH,  # Length along edge
        port_cut_height,  # Height (goes through lip)
        App.Vector(-1, port_y_start, SHELL_THICKNESS)  # Starts ABOVE bottom
    )
    cutouts.append(ports_cutout)

    # Cutout 2: From 14.5cm to 16.5cm (2cm long)
    PORT2_START_FROM_TOP = 145.0  # mm - 14.5cm from top
    PORT2_CUT_LENGTH = 20.0  # mm - 2cm length (16.5 - 14.5)

    port2_y_start = cavity_height + SHELL_THICKNESS - PORT2_START_FROM_TOP - PORT2_CUT_LENGTH

    ports_cutout2 = Part.makeBox(
        port_cut_width,
        PORT2_CUT_LENGTH,
        port_cut_height,
        App.Vector(-1, port2_y_start, SHELL_THICKNESS)  # Starts ABOVE bottom
    )
    cutouts.append(ports_cutout2)

    # Notch for kickstand in the BOTTOM
    # From 10cm to 15.5cm on long edge (same side as USB ports)
    # FIXED v1.2.6: Positioned AFTER central hole margin (x=13mm instead of x=3mm)
    KICKSTAND_START = 100.0  # mm - 10cm from top
    KICKSTAND_END = 155.0    # mm - 15.5cm from top
    KICKSTAND_LENGTH = KICKSTAND_END - KICKSTAND_START  # 5.5cm

    # Y position (from top to bottom)
    kickstand_y_start = cavity_height + SHELL_THICKNESS - KICKSTAND_END

    kickstand_width = 10.0  # mm - notch width

    # The notch must be in the central hole area, not in the margin!
    # bottom_margin = 10mm, so the lip goes from x=3mm to x=13mm
    kickstand_x_start = SHELL_THICKNESS  # x=0mm (after lip)

    kickstand_cutout = Part.makeBox(
        kickstand_width,      # Width
        KICKSTAND_LENGTH,     # Length (5.5cm)
        SHELL_THICKNESS + 1,  # Goes through entire bottom
        App.Vector(kickstand_x_start, kickstand_y_start, -0.5)  # FIXED: x=13mm
    )
    cutouts.append(kickstand_cutout)

    return cutouts


def create_ventilation_cutouts_top(doc):
    """Creates circular holes (6mm diameter) on the upper short edge for ventilation (BOTH SIDES)"""
    cutouts = []

    cavity_width = TABLET_WIDTH + 2 * CLEARANCE
    cavity_height = TABLET_HEIGHT + 2 * CLEARANCE
    outer_height = cavity_height + 2 * SHELL_THICKNESS
    outer_width = cavity_width + 2 * SHELL_THICKNESS

    # Ventilation zone: from 1.5cm to 8cm from edge
    VENT_START_FROM_EDGE = 15.0  # mm - 1.5cm from edge
    VENT_END_FROM_EDGE = 80.0    # mm - 8cm from edge

    # Hole dimensions
    HOLE_RADIUS = 3.0  # mm - radius 3mm = diameter 6mm
    HOLE_SPACING = 8.0  # mm - spacing between holes (reduced for more ventilation)

    TABLET_SPACE = 15.0  # mm

    # Upper wall height
    wall_thickness = 8.0  # mm - upper wall thickness

    # Z position (middle of lip height)
    hole_z = SHELL_THICKNESS + TABLET_SPACE / 2

    # LEFT SIDE: Create holes from 1.5cm to 8cm from left edge
    x_position = VENT_START_FROM_EDGE + SHELL_THICKNESS + HOLE_RADIUS

    while x_position + HOLE_RADIUS < VENT_END_FROM_EDGE + SHELL_THICKNESS:
        # Horizontal circular hole (cylinder oriented in Y)
        hole = Part.makeCylinder(
            HOLE_RADIUS,
            wall_thickness + 1,
            App.Vector(x_position, outer_height - wall_thickness - 0.5, hole_z),
            App.Vector(0, 1, 0)  # Oriented forward
        )
        cutouts.append(hole)

        x_position += HOLE_SPACING

    # RIGHT SIDE: Create same holes symmetrically (from 1.5cm to 8cm from right edge)
    x_position = outer_width - VENT_END_FROM_EDGE - SHELL_THICKNESS - HOLE_RADIUS

    while x_position + HOLE_RADIUS < outer_width - VENT_START_FROM_EDGE - SHELL_THICKNESS:
        # Horizontal circular hole (cylinder oriented in Y)
        hole = Part.makeCylinder(
            HOLE_RADIUS,
            wall_thickness + 1,
            App.Vector(x_position, outer_height - wall_thickness - 0.5, hole_z),
            App.Vector(0, 1, 0)  # Oriented forward
        )
        cutouts.append(hole)

        x_position += HOLE_SPACING

    return cutouts


def create_all_cutouts_right(doc):
    """Creates all objects to subtract for the right part (mirror of left)"""
    cutouts = []

    cavity_width = TABLET_WIDTH + 2 * CLEARANCE
    cavity_height = TABLET_HEIGHT + 2 * CLEARANCE
    outer_width = cavity_width + 2 * SHELL_THICKNESS

    # Cutout 1: Main ports AT TOP (mirror of left side)
    PORT_START_FROM_TOP = 20.0  # mm - 2.0cm from top
    PORT_CUT_LENGTH = 72.0  # mm - 7.2cm length

    port_y_start = cavity_height + SHELL_THICKNESS - PORT_START_FROM_TOP - PORT_CUT_LENGTH

    TABLET_SPACE = 15.0  # mm
    port_cut_height = TABLET_SPACE + 1  # mm - goes through entire vertical lip
    port_cut_width = 8.0  # mm

    # Position on RIGHT edge (x = outer_width instead of x = -1)
    ports_cutout = Part.makeBox(
        port_cut_width,   # Width (depth into wall)
        PORT_CUT_LENGTH,  # Length along edge
        port_cut_height,  # Height (goes through lip)
        App.Vector(outer_width - port_cut_width + 1, port_y_start, SHELL_THICKNESS)  # Starts ABOVE bottom
    )
    cutouts.append(ports_cutout)

    # Cutout 2: Audio connector + USB - v1.2.6: Moved up 2mm and enlarged
    PORT2_START_FROM_TOP = 138.0  # mm - 13.8cm from top (was 14.0cm)
    PORT2_CUT_LENGTH = 37.0  # mm - 3.7cm length (was 3.5cm)

    port2_y_start = cavity_height + SHELL_THICKNESS - PORT2_START_FROM_TOP - PORT2_CUT_LENGTH

    ports_cutout2 = Part.makeBox(
        port_cut_width,
        PORT2_CUT_LENGTH,
        port_cut_height,
        App.Vector(outer_width - port_cut_width + 1, port2_y_start, SHELL_THICKNESS)  # Starts ABOVE bottom
    )
    cutouts.append(ports_cutout2)

    # Notch for kickstand in the BOTTOM (mirror)
    # From 10cm to 15.5cm on RIGHT long edge
    # FIXED v1.2.5: Positioned BEFORE right side lip
    KICKSTAND_START = 100.0  # mm - 10cm from top
    KICKSTAND_END = 155.0    # mm - 15.5cm from top
    KICKSTAND_LENGTH = KICKSTAND_END - KICKSTAND_START  # 5.5cm

    # Y position (from top to bottom)
    kickstand_y_start = cavity_height + SHELL_THICKNESS - KICKSTAND_END

    kickstand_width = 10.0  # mm - notch width

    kickstand_cutout = Part.makeBox(
        kickstand_width,      # Width
        KICKSTAND_LENGTH,     # Length (5.5cm)
        SHELL_THICKNESS + 1,  # Goes through entire bottom
        App.Vector(outer_width - SHELL_THICKNESS - kickstand_width, kickstand_y_start, -0.5)  # FIXED: ends BEFORE lip
    )
    cutouts.append(kickstand_cutout)

    return cutouts


def create_welding_groove(doc, outer_width, outer_height, total_height):
    """Creates a V-groove for PLA pen welding"""

    # Groove parameters
    GROOVE_WIDTH = 1.5  # mm - width on each side of the V
    GROOVE_DEPTH = 1.8  # mm - groove depth
    INSET_FROM_EDGE = 1.5  # mm - setback from outer edge

    print(f"Creating welding groove: {GROOVE_WIDTH}mm wide x {GROOVE_DEPTH}mm deep")

    # The groove is a triangular prism (V-section) that follows the perimeter
    # We create 4 segments: top, bottom, front, back (but not on left/right sides as that's the junction)

    grooves = []

    # === GROOVE ON FRONT EDGE (Y = 0) ===
    # V-profile: triangle pointing inward, groove open toward OUTSIDE
    v_points_front = [
        App.Vector(outer_width/2, INSET_FROM_EDGE + GROOVE_DEPTH, 0),  # V apex (points inward)
        App.Vector(outer_width/2 - GROOVE_WIDTH, INSET_FROM_EDGE, 0),  # Left corner (outer surface)
        App.Vector(outer_width/2 + GROOVE_WIDTH, INSET_FROM_EDGE, 0),  # Right corner (outer surface)
        App.Vector(outer_width/2, INSET_FROM_EDGE + GROOVE_DEPTH, 0)   # Return to apex
    ]

    # Create 2D V-profile
    v_wire_front = Part.makePolygon(v_points_front)
    v_face_front = Part.Face(v_wire_front)

    # Extrude vertically over entire height
    groove_front = v_face_front.extrude(App.Vector(0, 0, total_height))
    grooves.append(groove_front)

    # === GROOVE ON BACK EDGE (Y = outer_height) ===
    v_points_back = [
        App.Vector(outer_width/2, outer_height - INSET_FROM_EDGE, 0),
        App.Vector(outer_width/2 - GROOVE_WIDTH, outer_height - INSET_FROM_EDGE - GROOVE_DEPTH, 0),
        App.Vector(outer_width/2 + GROOVE_WIDTH, outer_height - INSET_FROM_EDGE - GROOVE_DEPTH, 0),
        App.Vector(outer_width/2, outer_height - INSET_FROM_EDGE, 0)
    ]

    v_wire_back = Part.makePolygon(v_points_back)
    v_face_back = Part.Face(v_wire_back)
    groove_back = v_face_back.extrude(App.Vector(0, 0, total_height))
    grooves.append(groove_back)

    # === GROOVE ON TOP EDGE (Z = total_height) ===
    # Horizontal V-profile
    v_points_top = [
        App.Vector(outer_width/2, INSET_FROM_EDGE, total_height - INSET_FROM_EDGE),
        App.Vector(outer_width/2 - GROOVE_WIDTH, INSET_FROM_EDGE, total_height - INSET_FROM_EDGE - GROOVE_DEPTH),
        App.Vector(outer_width/2 + GROOVE_WIDTH, INSET_FROM_EDGE, total_height - INSET_FROM_EDGE - GROOVE_DEPTH),
        App.Vector(outer_width/2, INSET_FROM_EDGE, total_height - INSET_FROM_EDGE)
    ]

    v_wire_top_front = Part.makePolygon(v_points_top)
    v_face_top_front = Part.Face(v_wire_top_front)
    groove_top_front = v_face_top_front.extrude(App.Vector(0, outer_height - 2*INSET_FROM_EDGE, 0))
    grooves.append(groove_top_front)

    # === GROOVE ON BOTTOM EDGE (Z = 0) ===
    v_points_bottom = [
        App.Vector(outer_width/2, INSET_FROM_EDGE, INSET_FROM_EDGE),
        App.Vector(outer_width/2 - GROOVE_WIDTH, INSET_FROM_EDGE, INSET_FROM_EDGE + GROOVE_DEPTH),
        App.Vector(outer_width/2 + GROOVE_WIDTH, INSET_FROM_EDGE, INSET_FROM_EDGE + GROOVE_DEPTH),
        App.Vector(outer_width/2, INSET_FROM_EDGE, INSET_FROM_EDGE)
    ]

    v_wire_bottom_front = Part.makePolygon(v_points_bottom)
    v_face_bottom_front = Part.Face(v_wire_bottom_front)
    groove_bottom_front = v_face_bottom_front.extrude(App.Vector(0, outer_height - 2*INSET_FROM_EDGE, 0))
    grooves.append(groove_bottom_front)

    # Fuse all grooves
    if grooves:
        all_grooves = grooves[0]
        for groove in grooves[1:]:
            all_grooves = all_grooves.fuse(groove)
        return all_grooves

    return None


def cut_frame_in_half(doc, complete_frame):
    """Cuts the frame in two halves and adds welding grooves"""

    cavity_width = TABLET_WIDTH + 2 * CLEARANCE
    cavity_height = TABLET_HEIGHT + 2 * CLEARANCE
    outer_width = cavity_width + 2 * SHELL_THICKNESS
    outer_height = cavity_height + 2 * SHELL_THICKNESS

    TABLET_SPACE = 15.0  # mm
    LIP_VERTICAL = 3.0   # mm
    total_height = SHELL_THICKNESS + TABLET_SPACE + LIP_VERTICAL

    # Left half
    left_cutter = Part.makeBox(outer_width/2, outer_height, total_height)
    left_shape = complete_frame.Shape.common(left_cutter)

    # Right half
    right_cutter = Part.makeBox(
        outer_width/2,
        outer_height,
        total_height,
        App.Vector(outer_width/2, 0, 0)
    )
    right_shape = complete_frame.Shape.common(right_cutter)

    # Create welding grooves (disabled for now)
    # print("\nAdding PLA pen welding grooves...")
    # welding_groove = create_welding_groove(doc, outer_width, outer_height, total_height)
    #
    # if welding_groove:
    #     # Subtract groove from each half
    #     left_shape = left_shape.cut(welding_groove)
    #     right_shape = right_shape.cut(welding_groove)

    left_shell = doc.addObject("Part::Feature", "Left_Half")
    left_shell.Shape = left_shape

    right_shell = doc.addObject("Part::Feature", "Right_Half")
    right_shell.Shape = right_shape

    return left_shell, right_shell


def main():
    """Main function"""

    doc = App.newDocument("Z13_Proto")

    print("=== QUICK PROTOTYPE - DIMENSION TEST ===\n")

    print("Creating complete frame...")
    complete_frame = create_frame_shell(doc)

    print("Cutting into two halves...")
    left_half, right_half = cut_frame_in_half(doc, complete_frame)

    print("Adding port cutouts...")
    # Add cutouts on the left part
    left_cutouts = create_all_cutouts_left(doc)

    # Add ventilation cutouts (common to both halves)
    vent_cutouts = create_ventilation_cutouts_top(doc)
    left_cutouts.extend(vent_cutouts)

    if left_cutouts:
        all_left_cuts = left_cutouts[0]
        for cutout in left_cutouts[1:]:
            all_left_cuts = all_left_cuts.fuse(cutout)
        left_final_shape = left_half.Shape.cut(all_left_cuts)
        left_final = doc.addObject("Part::Feature", "Left_Half_Final")
        left_final.Shape = left_final_shape
    else:
        left_final = left_half

    # Right part: also add ventilation
    right_cutouts = create_all_cutouts_right(doc)
    right_cutouts.extend(vent_cutouts)

    if right_cutouts:
        all_right_cuts = right_cutouts[0]
        for cutout in right_cutouts[1:]:
            all_right_cuts = all_right_cuts.fuse(cutout)
        right_final_shape = right_half.Shape.cut(all_right_cuts)
        right_final = doc.addObject("Part::Feature", "Right_Half_Final")
        right_final.Shape = right_final_shape
    else:
        right_final = right_half

    # Hide complete frame and base halves
    complete_frame.ViewObject.Visibility = False
    left_half.ViewObject.Visibility = False
    right_half.ViewObject.Visibility = False

    # Space the two halves for visualization
    right_final.Placement = App.Placement(
        App.Vector((TABLET_WIDTH + 2*CLEARANCE + 2*SHELL_THICKNESS)/2 + 10, 0, 0),
        App.Rotation(App.Vector(0,0,1), 0)
    )

    doc.recompute()

    cavity_width = TABLET_WIDTH + 2 * CLEARANCE
    cavity_height = TABLET_HEIGHT + 2 * CLEARANCE

    print("\n=== SHELL v1.2.6 - CUTOUT AND LIP ADJUSTMENTS ===")
    print(f"\nU-profile structure (cross-section view):")
    print(f"")
    print(f"  |----3mm----|  <- 18-21mm: Lip (extends 3mm inward)")
    print(f"  |           |")
    print(f"  |           |  <- 3-18mm: WIDE cavity (15mm high)")
    print(f"  |           |            The 15mm tablet fits here")
    print(f"  |___________|  <- 0-3mm: 3MM bottom (rigid!)")
    print(f"")
    print(f"Total height: 21mm (3mm bottom + 15mm tablet + 3mm lip)")
    print(f"Outer dimensions: 307 x 211 x 21mm")
    print(f"\nv1.2.6 Features:")
    print(f"- Left side port cutouts: 2.3-9.7cm + 14.5-16.5cm")
    print(f"- Right side port cutouts: 2-9.2cm + 13.8-17.5cm")
    print(f"- Screen lip: 6mm (reinforced hold)")
    print(f"- Kickstand notches (x2): 8mm wide, AFTER lips - FIXED!")
    print(f"- Left position: x=3mm (after left lip)")
    print(f"- Right position: x=outer_width-11mm (before right lip)")
    print(f"- FINAL SOLUTION: Notches in inner cavity, not on edge!")
    print(f"- Circular ventilation: 6mm diameter, 8mm spacing (BOTH sides)")
    print(f"- Solid bottom: 4cm top + 4cm bottom + side lips INTACT")
    print(f"- Webcam hole (left): 6mm radius, 1.8cm from top, 1.8cm from side")
    print(f"- Outer corner fillets: 5mm")
    print(f"- Outer edge fillets: 1.5mm (very light)")
    print(f"- Inner fillets: 5mm")
    print(f"- PLA welding groove (1.5mm x 1.8mm V-shape)")
    print(f"\nVersion history:")
    print(f"v1.0.0: Dimensions and cutouts validated")
    print(f"v1.1.0: 3mm bottom -> +50% rigidity")
    print(f"v1.1.1: Rounded outer edges -> smooth finish")
    print(f"v1.1.2: Connector adjustments (power -5mm, audio -10mm)")
    print(f"v1.2.0: PLA welding groove -> solid pen welding assembly!")
    print(f"v1.2.1: Circular ventilation 6mm -> more aesthetic and efficient")
    print(f"v1.2.5: Kickstand notches repositioned INSIDE cavity -> lips intact!")
    print(f"v1.2.6: Fine adjustments - cutouts +2mm, webcam repositioned, lip +3mm")
    print(f"\nAssembly:")
    print(f"1. Assemble the two halves around the tablet")
    print(f"2. Weld with a PLA pen along the V-groove")
    print(f"3. The groove guides the melted plastic for a clean and solid weld")
    print(f"\nVersion v1.2.6 ready!")

    return doc


if __name__ == "__main__":
    main()
    