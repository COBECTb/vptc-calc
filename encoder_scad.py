"""Parametric encoder variants for the reducer generator.

No input is read from the manually edited SCAD files in output/.  The generated
modules use the base reducer's dimensions, bearing and actual fastening points.
The PCB is a mechanical layout; a different reducer diameter needs a new PCB.
"""
from dataclasses import dataclass, asdict
import math


@dataclass(frozen=True)
class EncoderDimensions:
    diameter: float
    bearing_inner: float
    bearing_outer: float
    bearing_width: float
    separator_height: float
    flange_extra: float
    bearing_step_z: float
    cap_height: float
    holes: tuple
    magnet_d: float = 5.0
    magnet_clearance: float = 0.2
    rim_wall: float = 0.6
    rim_height: float = 0.4
    magnet_height: float = 1.0
    separator_lift: float = 0.5


def max_even_count(radius, spacing):
    """Largest even count whose adjacent pocket centres have enough material."""
    if radius <= 0 or not 0 < spacing <= 2 * radius:
        return 0
    return 2 * math.floor(math.pi / math.asin(spacing / (2 * radius)) / 2)


def encoder_metrics(d):
    pocket = d.magnet_d + d.magnet_clearance
    rim_d = pocket + 2*d.rim_wall
    outer_r = d.diameter/2 - 2 - rim_d/2 - .3
    inner_r = outer_r - (pocket+d.rim_wall+.2)
    if inner_r-rim_d/2 < d.bearing_inner/2:
        raise ValueError('На торце не помещаются две дорожки магнитов выбранного диаметра')
    outer_n = min(max_even_count(outer_r,pocket+d.rim_wall),
                  max_even_count(inner_r,pocket+d.rim_wall)+2)
    if outer_n < 6:
        raise ValueError('Недостаточно места для двух чётных магнитных дорожек')
    # The original cap seating stop is cap_height-1; preserve its geometry.
    bearing_bottom = d.cap_height-1-d.bearing_width-.5+d.separator_lift
    separator_base = bearing_bottom-d.bearing_step_z
    separator_top = separator_base+d.separator_height+d.flange_extra
    glue_face = d.cap_height+.8+1.45+.2+.4+.4+d.magnet_height
    stem = glue_face+5.9-4-separator_top
    if stem <= 0:
        raise ValueError('Для выбранной осевой сборки длина соединителя неположительна')
    # The sensor sits in a free gap between neighbouring body bolts.
    angles = sorted(math.degrees(math.atan2(y,x))%360 for x,y in d.holes)
    mids = [(a+((b-a)%360)/2)%360 for a,b in zip(angles,angles[1:]+angles[:1])]
    sensor_angle = min(mids,key=lambda a:abs((a-9+180)%360-180))
    if sensor_angle > 180:
        sensor_angle -= 360
    return dict(inner_track_r=inner_r,outer_track_r=outer_r,
                inner_magnet_count=outer_n-2,outer_magnet_count=outer_n,
                separator_base_z=separator_base,bearing_bottom_z=bearing_bottom,
                separator_top_z=separator_top,glue_face_z=glue_face,
                connector_stem_h=stem,sensor_angle=sensor_angle)


def generate_encoder_scad(d):
    """Return independent SCAD modules to append before the assembly selector."""
    metrics=encoder_metrics(d)
    points=', '.join(f'[{x:.9f},{y:.9f}]' for x,y in d.holes)
    header=f'''\n// === Абсолютный off-axis энкодер: два магнитных кольца и одна CAN-плата ===
// Самостоятельные параметрические варианты; ручные output/*.scad не используются.
// Для других габаритов платы нужна отдельная электрическая разводка.
encoder_magnet_d = {d.magnet_d:g};
encoder_magnet_h = {d.magnet_height:g};
encoder_magnet_clearance = {d.magnet_clearance:g};
encoder_rim_wall = {d.rim_wall:g};
encoder_rim_h = {d.rim_height:g};
encoder_separator_lift = {d.separator_lift:g};
encoder_sensor_angle = {metrics['sensor_angle']:.9f};
encoder_body_bolts = [{points}];
encoder_separator_total_h = {d.separator_height+d.flange_extra:.9f};
encoder_separator_bearing_step = {d.bearing_step_z:g};
'''
    return header + ENCODER_MODULES


def encoder_manifest(d):
    m=encoder_metrics(d)
    sensor_a=m['sensor_angle']
    mount_r=m['outer_track_r']+1
    native_compatible=(abs(d.diameter-70)<1e-7 and abs(d.bearing_inner-40)<1e-7
        and abs(d.bearing_outer-52)<1e-7 and abs(sensor_a-9)<1e-7
        and all(abs(math.hypot(x,y)-31.5)<1e-5 for x,y in d.holes))
    return dict(schema_version=1,available=True,dimensions=asdict(d),derived=m,
        native_pcb_compatible=native_compatible,
        pcb=dict(thickness_mm=.8,inner_r_mm=m['inner_track_r']-1.9,
            local_inner_relief_r_mm=m['inner_track_r']-2.2,
            local_relief_angles_deg=[sensor_a-10,sensor_a+10],transition_deg=2,
            outer_r_mm=m['outer_track_r']+3.9,span_deg=160,center_angle_deg=sensor_a,
            bolt_keepout_r_mm=4.5,mount_hole_d_mm=2.2,mount_r_mm=mount_r,
            mount_angles_deg=[sensor_a-68,sensor_a+68],
            front_sensor_hall_radii_mm=[m['inner_track_r'],m['outer_track_r']],
            hall_from_body_radial_tangent_mm=[-.12,-.4],
            rear_pocket_inner_r_mm=d.bearing_outer/2+1,rear_pocket_outer_r_mm=d.diameter/2-1.3,
            rear_pocket_depth_mm=2.3,
            mcu_relief=dict(center_r_mm=m['outer_track_r']-.2,center_angle_deg=sensor_a-14,
                rotation_deg=sensor_a-9,body_size_mm=[5.1,5.1,.6],xy_clearance_mm=.2,
                axial_clearance_mm=.15,bottom_z_mm=d.cap_height-.6-.15)),
        notes=['Mechanical PCB layout only; an altered envelope requires a new electrical PCB.',
               'Separator lift changes roller-window and 688ZZ mating positions; verify the complete gearbox.'])


ENCODER_MODULES = r'''
encoder_clamp_h = 12;
encoder_pocket_d = encoder_magnet_d+encoder_magnet_clearance;
encoder_rim_d = encoder_pocket_d+2*encoder_rim_wall;
encoder_outer_track_r = D_out/2-2-encoder_rim_d/2-0.3;
encoder_track_pitch = encoder_pocket_d+encoder_rim_wall+0.2;
encoder_inner_track_r = encoder_outer_track_r-encoder_track_pitch;
function encoder_max_even(r,s) = 2*floor((180/asin(s/(2*r)))/2);
encoder_outer_count = min(
    encoder_max_even(encoder_outer_track_r,encoder_pocket_d+encoder_rim_wall),
    encoder_max_even(encoder_inner_track_r,encoder_pocket_d+encoder_rim_wall)+2);
encoder_inner_count = encoder_outer_count-2;
encoder_track_radii = [encoder_inner_track_r,encoder_outer_track_r];
encoder_track_counts = [encoder_inner_count,encoder_outer_count];

encoder_pcb_h = 0.8;
encoder_pcb_inner_r = encoder_inner_track_r-1.9;
encoder_pcb_relief_r = encoder_pcb_inner_r-0.3;
encoder_pcb_outer_r = encoder_outer_track_r+3.9;
encoder_pcb_span = 160;
encoder_pcb_mount_r = encoder_outer_track_r+1;
encoder_pcb_mount_angles = [encoder_sensor_angle-68,encoder_sensor_angle+68];
encoder_pcb_clearance = 0.25;
encoder_body_bolt_keepout = 4.5;
encoder_rear_inner_r = bearing_outer/2+1;
encoder_rear_outer_r = D_out/2-1.3;
encoder_rear_depth = 2.3;
encoder_mcu_r = encoder_outer_track_r-0.2;
encoder_mcu_angle = encoder_sensor_angle-14;
encoder_mcu_rotation = encoder_sensor_angle-9;
encoder_mcu_body = [5.1,5.1,0.6];
encoder_mcu_xy_clearance = 0.2;
encoder_mcu_axial_clearance = 0.15;
encoder_sensor_envelope_h = 1.45; // TI DBV Amax1.4 plus0.05 mechanical reserve.
encoder_sensor_max_h = 1.4;
encoder_hall_depth_from_top = 0.73;
encoder_hall_height = encoder_sensor_max_h-encoder_hall_depth_from_top;
encoder_sensor_gap = 0.2;
encoder_window_h = 0.4;
encoder_magnet_air_gap = 0.4;
encoder_roof_extra_h = 0.4;
encoder_pcb_bottom_z = cap_thickness;
encoder_pcb_top_z = encoder_pcb_bottom_z+encoder_pcb_h;
encoder_sensor_front_z = encoder_pcb_top_z+encoder_sensor_envelope_h;
encoder_pocket_ceiling_z = encoder_sensor_front_z+encoder_sensor_gap;
encoder_lid_base_z = encoder_pcb_top_z+0.25;
encoder_lid_top_z = encoder_pocket_ceiling_z+encoder_window_h;
encoder_main_ceiling_z = encoder_pocket_ceiling_z-encoder_roof_extra_h;
encoder_magnet_bottom_z = encoder_lid_top_z+encoder_magnet_air_gap;
encoder_glue_face_z = encoder_magnet_bottom_z+encoder_magnet_h;
encoder_bearing_bottom_z = cap_thickness-1-bearing_width-0.5+encoder_separator_lift;
encoder_separator_base_z = encoder_bearing_bottom_z-encoder_separator_bearing_step;
encoder_separator_top_z = encoder_separator_base_z+encoder_separator_total_h;
encoder_connector_contact_z = encoder_glue_face_z+5.9;
encoder_connector_stem_h = encoder_connector_contact_z-4-encoder_separator_top_z;
encoder_load_connector_h = 15;
encoder_screw_head_h = 1.3;
encoder_screw_ceiling_z = encoder_pcb_top_z+encoder_screw_head_h+0.2;

module encoder_validate() {
    assert(encoder_magnet_d>0 && encoder_magnet_h>0 && encoder_rim_wall>0 && encoder_rim_h>0,
        "Проверьте размеры магнитов и бортиков");
    assert(encoder_inner_track_r-encoder_rim_d/2>=bearing_inner/2,
        "Два кольца магнитов не помещаются на торце зажима");
    assert(encoder_outer_count>=6 && encoder_outer_count%2==0,
        "Нужно чётное число магнитов");
    for(t=[0:1]) assert(2*encoder_track_radii[t]*sin(180/encoder_track_counts[t])
        >=encoder_pocket_d+encoder_rim_wall,"Недостаточна перемычка между магнитами");
    assert(encoder_connector_stem_h>0,"Неположительная длина соединителя");
    assert(encoder_separator_lift<=0.5,"Подшипник поднят выше сохранённого упора крышки");
    assert(encoder_screw_ceiling_z<=encoder_lid_top_z-encoder_window_h,
        "Головка M2 не помещается под крышкой");
    assert(encoder_pcb_bottom_z-encoder_mcu_body[2]-encoder_mcu_axial_clearance>=cap_thickness-1+0.2,
        "Локальный карман MCU затрагивает посадку подшипника");
    children();
}

module encoder_body_bolt_positions() {
    for(p=encoder_body_bolts) translate([p[0],p[1],0]) children();
}
module encoder_mount_positions() {
    for(a=encoder_pcb_mount_angles)
        rotate([0,0,a]) translate([encoder_pcb_mount_r,0,0]) children();
}
module encoder_sensor_positions() {
    for(r=encoder_track_radii) rotate([0,0,encoder_sensor_angle]) translate([r,0,0]) children();
}
module encoder_annulus(ro,ri,h) {
    difference() {
        cylinder(r=ro,h=h);
        translate([0,0,-eps]) cylinder(r=ri,h=h+2*eps);
    }
}
function encoder_board_inner_radius(a) = let(d=abs(a-encoder_sensor_angle))
    d<=10 ? encoder_pcb_relief_r : d>=12 ? encoder_pcb_inner_r :
    encoder_pcb_relief_r+(encoder_pcb_inner_r-encoder_pcb_relief_r)*(d-10)/2;
module encoder_pcb_outline(clearance=0) {
    offset(delta=clearance) difference() {
        polygon(concat(
            [for(i=[0:640]) let(a=encoder_sensor_angle-80+i/4)
                [encoder_pcb_outer_r*cos(a),encoder_pcb_outer_r*sin(a)]],
            [for(i=[640:-1:0]) let(a=encoder_sensor_angle-80+i/4,r=encoder_board_inner_radius(a))
                [r*cos(a),r*sin(a)]]));
        encoder_body_bolt_positions() circle(r=encoder_body_bolt_keepout);
    }
}
module encoder_sensor_outline(clearance=0) {
    // Center of the package is +.12 radial and +.40 tangential from the Hall point.
    translate([0.12,0.4]) offset(delta=clearance) square([2.8,2.9],center=true);
}
module encoder_pcb_bare() {
    difference() {
        linear_extrude(height=encoder_pcb_h) encoder_pcb_outline();
        encoder_mount_positions() translate([0,0,-eps]) cylinder(d=2.2,h=encoder_pcb_h+2*eps);
    }
}
module encoder_pcb_model() {
    color("SeaGreen") translate([0,0,encoder_pcb_bottom_z]) encoder_pcb_bare();
    color("DimGray") encoder_sensor_positions()
        translate([0,0,encoder_pcb_top_z]) linear_extrude(height=encoder_sensor_envelope_h)
            encoder_sensor_outline();
    // Mechanical budget only; the electrical KiCad board is supplied separately.
    rotate([0,0,encoder_mcu_angle])
        translate([encoder_mcu_r,0,encoder_pcb_bottom_z-encoder_mcu_body[2]/2])
            rotate([0,0,encoder_mcu_rotation-encoder_mcu_angle])
                color("DimGray") cube(encoder_mcu_body,center=true);
    for(c=[[encoder_sensor_angle+15,3,3,1.45],[encoder_sensor_angle+49,3,3,1.45]])
        rotate([0,0,c[0]]) translate([encoder_outer_track_r+0.5,0,encoder_pcb_bottom_z-c[3]/2])
            color("DimGray") cube([c[1],c[2],c[3]],center=true);
    color("Silver") encoder_mount_positions() translate([0,0,encoder_pcb_top_z])
        cylinder(d=3.5,h=encoder_screw_head_h);
}

module encoder_track_positions(full_circle=false) {
    for(t=[0:1]) let(n=encoder_track_counts[t],r=encoder_track_radii[t])
        for(j=[0:(full_circle ? n-1 : n/2-1)]) let(a=(j+.5)*360/n)
            translate([r*cos(a),r*sin(a),encoder_clamp_h]) children();
}
module encoder_magnet_rims() {
    intersection() {
        difference() {
            encoder_track_positions(true) translate([0,0,-eps])
                cylinder(d=encoder_rim_d,h=encoder_rim_h+eps);
            encoder_track_positions(true) translate([0,0,-2*eps])
                cylinder(d=encoder_pocket_d,h=encoder_rim_h+3*eps);
        }
        translate([-D_out,0,encoder_clamp_h-2*eps]) cube([2*D_out,D_out,encoder_rim_h+4*eps]);
    }
}
module encoder_magnets(second_half=false) {
    for(t=[0:1]) let(n=encoder_track_counts[t],r=encoder_track_radii[t])
        for(j=[0:n/2-1]) let(a=(j+.5)*360/n,index=j+(second_half ? n/2 : 0))
            color(index%2==0 ? "Firebrick" : "RoyalBlue")
                translate([r*cos(a),r*sin(a),encoder_clamp_h]) cylinder(d=encoder_magnet_d,h=encoder_magnet_h);
}
module connector_clamp_encoder_half() {
    encoder_validate() union() { connector_clamp(); encoder_magnet_rims(); }
}
module connector_clamp_encoder(show_magnets=false) {
    for(half=[0:1]) rotate([0,0,180*half]) {
        connector_clamp_encoder_half();
        // Magnets are always background objects for printable clamp exports.
        if(show_magnets) %encoder_magnets(second_half=half==1);
    }
}
module reducer_connector_encoder() {
    reducer_connector(h1=encoder_connector_stem_h,skirt=false);
}
module load_connector_encoder() {
    reducer_connector(h1=encoder_load_connector_h,skirt=true,holes=[1,0,1,0,1,0,1,0]);
}
module encoder_rear_pocket() {
    difference() {
        intersection() {
            encoder_pcb_outline(encoder_pcb_clearance);
            difference() { circle(r=encoder_rear_outer_r); circle(r=encoder_rear_inner_r); }
        }
        encoder_mount_positions() circle(d=4.4);
    }
}
module encoder_mcu_clearance() {
    rotate([0,0,encoder_mcu_angle])
        translate([encoder_mcu_r,0,encoder_pcb_bottom_z-encoder_mcu_body[2]-encoder_mcu_axial_clearance])
            rotate([0,0,encoder_mcu_rotation-encoder_mcu_angle])
                translate([-encoder_mcu_body[0]/2-encoder_mcu_xy_clearance,
                           -encoder_mcu_body[1]/2-encoder_mcu_xy_clearance,0])
                    cube([encoder_mcu_body[0]+2*encoder_mcu_xy_clearance,
                          encoder_mcu_body[1]+2*encoder_mcu_xy_clearance,
                          encoder_mcu_body[2]+encoder_mcu_axial_clearance+eps]);
}
module cap_encoder(with_bracing=true) {
    encoder_validate() difference() {
        union() {
            if(with_bracing) cap_with_bracing(); else cap();
            translate([0,0,cap_thickness-eps])
                encoder_annulus(D_out/2,bearing_outer/2-2,encoder_lid_base_z-cap_thickness+eps);
        }
        translate([0,0,encoder_pcb_bottom_z])
            linear_extrude(height=encoder_lid_base_z-encoder_pcb_bottom_z+eps)
                encoder_pcb_outline(encoder_pcb_clearance);
        translate([0,0,encoder_pcb_bottom_z-encoder_rear_depth])
            linear_extrude(height=encoder_rear_depth+eps) encoder_rear_pocket();
        encoder_mcu_clearance();
        encoder_mount_positions() translate([0,0,encoder_pcb_bottom_z-2]) cylinder(d=1.6,h=2+eps);
        encoder_body_bolt_positions() translate([0,0,cap_thickness-eps]) cylinder(d=3.2,h=5);
        rotate([0,0,encoder_sensor_angle+59])
            translate([encoder_pcb_outer_r-1.4,-2,encoder_pcb_bottom_z-1.2]) cube([9,4,1.1]);
    }
}
module lid_encoder() {
    encoder_validate() difference() {
        translate([0,0,encoder_lid_base_z])
            encoder_annulus(D_out/2,bearing_inner/2+0.6,encoder_lid_top_z-encoder_lid_base_z);
        translate([0,0,encoder_lid_base_z-eps])
            linear_extrude(height=encoder_main_ceiling_z-encoder_lid_base_z+eps)
                encoder_pcb_outline(encoder_pcb_clearance);
        encoder_sensor_positions() translate([0,0,encoder_lid_base_z-eps])
            linear_extrude(height=encoder_pocket_ceiling_z-encoder_lid_base_z+eps)
                encoder_sensor_outline(encoder_pcb_clearance);
        encoder_mount_positions() translate([0,0,encoder_lid_base_z-eps])
            cylinder(d=4,h=encoder_screw_ceiling_z-encoder_lid_base_z+eps);
        encoder_body_bolt_positions() {
            translate([0,0,encoder_lid_base_z-eps]) cylinder(d=3.2,h=encoder_lid_top_z-encoder_lid_base_z+2*eps);
            // The90degree countersink remains exactly6mm at the real top face.
            translate([0,0,encoder_lid_top_z-1.4]) cylinder(d1=3.2,d2=6+2*eps,h=1.4+eps);
        }
    }
}
module encoder_assembly(exploded=false,section=false,with_bracing=true,show_electronics=true,show_magnets=true) {
    encoder_validate() intersection() {
        union() {
            color("LightGray") cap_encoder(with_bracing);
            color("Gainsboro") translate([0,0,exploded ? 12 : 0]) lid_encoder();
            if(show_electronics) translate([0,0,exploded ? 5 : 0]) encoder_pcb_model();
            color("Silver") translate([0,0,encoder_bearing_bottom_z+(exploded ? -10 : 0)])
                encoder_annulus(bearing_outer/2,bearing_inner/2,bearing_width);
            color("DarkSalmon") translate([0,0,encoder_separator_base_z+(exploded ? -25 : 0)]) separator();
            color("LightSteelBlue") translate([0,0,encoder_connector_contact_z+(exploded ? 20 : 0)])
                mirror([0,0,1]) reducer_connector_encoder();
            color("SteelBlue") translate([0,0,encoder_connector_contact_z+(exploded ? 32 : 0)]) load_connector_encoder();
            translate([0,0,encoder_glue_face_z+encoder_clamp_h+(exploded ? 20 : 0)]) mirror([0,0,1])
                for(half=[0:1]) rotate([0,0,180*half]) {
                    color("SlateGray") connector_clamp_encoder_half();
                    if(show_magnets) encoder_magnets(half==1);
                }
        }
        if(section) rotate([0,0,encoder_sensor_angle]) translate([-D_out,0,-D_out]) cube([2*D_out,D_out,3*D_out]);
        else translate([-D_out,-D_out,-D_out]) cube([2*D_out,2*D_out,3*D_out]);
    }
}
module encoder_selected_part(part) {
    echo("Encoder magnets inner/outer:",encoder_inner_count,encoder_outer_count);
    echo("Encoder output connector stem, mm:",encoder_connector_stem_h);
    if(part=="encoder_assembly") encoder_assembly();
    else if(part=="encoder_exploded") encoder_assembly(exploded=true);
    else if(part=="encoder_section") encoder_assembly(section=true);
    else if(part=="encoder_cap") cap_encoder();
    else if(part=="encoder_lid") translate([0,0,-encoder_lid_base_z]) lid_encoder();
    else if(part=="encoder_print") {
        translate([-D_out/2-4,0,0]) cap_encoder();
        translate([D_out/2+4,0,-encoder_lid_base_z]) lid_encoder();
    }
    else if(part=="encoder_clamp") connector_clamp_encoder(show_magnets=true);
    else if(part=="encoder_clamp_half") connector_clamp_encoder_half();
    else if(part=="encoder_connector") reducer_connector_encoder();
    else if(part=="encoder_load_connector") load_connector_encoder();
    else if(part=="encoder_pcb") encoder_pcb_bare();
    else assert(false,str("Неизвестный вариант: ",part));
}
'''
