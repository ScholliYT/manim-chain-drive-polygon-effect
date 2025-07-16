from manim import *
from manim_gearbox import *
import numpy as np


from manim.mobject.geometry.tips import *
from manim_cad_drawing_utils import *
class NonUniformityOfTheChainSpeed(Scene):
    """Plot of cos(180/z) in % over z from 6 to 40"""
    def construct(self):
        # Create the axes
        axes = Axes(
            x_range=[6, 40, 2],
            y_range=[86, 102, 2],
            axis_config={"color": BLUE},
            x_axis_config={"label_direction": DOWN,
                           # include 6-30 and 40
                           "numbers_to_include": np.arange(6, 30, 4).tolist() + [40],
                           },
            y_axis_config={"label_direction": LEFT, 
                           "numbers_to_include": np.arange(86, 102, 2).tolist(),},
        )

        # Create the graph of cos(180/z) in %
        graph = axes.plot(lambda z: np.cos(np.pi / z) * 100, color=YELLOW)
        z = ValueTracker(10)
        graph_label = MathTex(r"\cos\left(\frac{180}{", "z", r"}\right)", color=YELLOW).move_to(axes.i2gp(z.get_value(), graph)).shift(DOWN * 0.8 + RIGHT * 0.8)

        # Add labels to the axes using Tex objects
        axes_labels = axes.get_axis_labels(x_label=MathTex("z"), y_label=MathTex(r"\%"))

        # Create a title for the scene
        title = Title("Non-Uniformity of the Chain Speed", include_underline=False)

        # Add everything to the scene
        self.add(axes, axes_labels, title)
        self.play(Create(graph))
        self.play(Write(graph_label))
        self.wait(2)


        # transform the graph_label to a parameterized variable form starting at z=10. Make the number colored red in the otherwise yellow label
        def compute_graph_label(m: Mobject, make_become=True):
            # Update the label with the current value of z using one decimal place
            z_string = f"{z.get_value():.0f}"  # no decimal places since there can only be a whole number of links
            y_value = np.cos(np.pi / z.get_value()) * 100
            label = MathTex(r"\cos\left(\frac{180}{", z_string, r"}\right) = ", f"{y_value:.1f}", r"\%", color=YELLOW)
            label.set_color_by_tex(z_string, RED)

            
            # add a dot on the graph at the current value of z
            dot = Dot(axes.i2gp(z.get_value(), graph), color=RED)
            
            # move the label to the right of the graph point, then shift a bit down and to the right
            label.next_to(dot, RIGHT, buff=0.1).shift(DOWN * 0.6)
            
            # combine both into one mobject
            group = VGroup(label, dot)

            if make_become:
                m.become(group)
            else:
                return group
        new_label = compute_graph_label(graph_label, make_become=False)
        self.play(Transform(graph_label, new_label))
        graph_label.add_updater(lambda m: compute_graph_label(m))
        self.wait(2)
            
        gear = Gear(int(z.get_value()), stroke_opacity=0, fill_color=RED, fill_opacity=1).shift(RIGHT*2 + DOWN)
        

        self.play(Create(gear))
        self.play(Rotate(gear, gear.pitch_angle, rate_func=linear),
                  run_time=4)
        self.wait(2)
        gear.add_updater(lambda m: m.become(Gear(int(z.get_value()), stroke_opacity=0, fill_color=RED, fill_opacity=1).move_to(gear.get_center()), match_height=True, match_width=True))

        self.play(z.animate.set_value(14), run_time=1, rate_func=linear)
        self.wait(3)
        self.play(z.animate.set_value(20), run_time=1, rate_func=linear)
        self.wait(3)
        self.play(z.animate.set_value(26), run_time=1, rate_func=linear)





class PolygonEffect(Scene):
    """Demonstration of the polygon effect on a gear with 6 teeth and a chain drive."""
    def construct(self):

        gear = Gear(12, stroke_opacity=0, fill_color=WHITE, fill_opacity=1)
        
        self.add(gear)

        gear2 = Gear(13, stroke_opacity=0, fill_color=WHITE, fill_opacity=1)

        self.play(Transform(gear, gear2))

class StandardGear(MovingCameraScene):
    """A standard gear with all the important properties shown next to it"""
    def construct(self):

        self.add(Title("Standard Gear Properties", include_underline=False))

        alpha_vt = ValueTracker(20)

        gear = Gear(12, stroke_opacity=0, fill_color=WHITE, fill_opacity=1, alpha=alpha_vt.get_value())
        self.play(Create(gear))

        # num_of_teeth: number of gear teeth.
        num_of_teeth_label = MathTex(f"z = {gear.z}", color=YELLOW).to_edge(LEFT).shift(UP * 2)
        self.play(Write(num_of_teeth_label))

        # write text with "Number of teeth" next to the label
        num_of_teeth_text = Tex("Number of teeth", color=YELLOW).next_to(num_of_teeth_label, RIGHT).shift(RIGHT * 0.2)
        self.play(Write(num_of_teeth_text))

        # module: standard size scaling parameter. Diameter = module * num_of_teeth.
        module_label = MathTex(f"m = {gear.m}", color=BLUE).next_to(num_of_teeth_label, DOWN)
        self.play(Write(module_label))

        # write text with "Module" next to the label
        module_text = Tex("Module (fixed)", color=BLUE).next_to(module_label, RIGHT).align_to(num_of_teeth_text, LEFT)
        self.play(Write(module_text))

        # show the formula for the pitch radius: rp = m * z / 2
        pitch_radius_label = MathTex(r"r_p = \frac{m \cdot z}{2}", color=GREEN).next_to(module_label, DOWN)
        self.play(Write(pitch_radius_label))



        # draw a dottet circle at the pitch circle using gear.rp
        pitch_circ_base = Circle(radius=gear.rp, color=GREEN, stroke_width=5, stroke_opacity=1)
        pitch_circle = Dashed_line_mobject(pitch_circ_base,num_dashes=int(gear.z*2), dashed_ratio=0.65, dash_offset=0.35/2)
        pitch_circle.set_fill(GREEN, opacity=0.1)
        pitch_circle_label = MathTex(r"r_p \text{ (pitch radius)}", color=GREEN).next_to(pitch_circle, RIGHT)
        self.play(Create(pitch_circle), Write(pitch_circle_label)) 
        self.wait(3)


        # undraw the pitch circle
        self.play(FadeOut(pitch_circle), FadeOut(pitch_circle_label))

        # alpha: pressure angle in degrees, affects tooth curvature. Suggested values between 10-30
        alpha_label = MathTex(r"\alpha = ", f"{gear.alpha:.0f}^\circ", color=PURPLE).next_to(pitch_radius_label, DOWN)
        self.play(Write(alpha_label))

        # write text with "Pressure angle" next to the label
        alpha_text = Tex("Pressure angle", color=PURPLE).next_to(alpha_label, RIGHT).align_to(module_text, LEFT)
        self.play(Write(alpha_text))



        # rack has reverse parameters
        rack = Rack(6,
                     module=gear.m,
                     alpha=alpha_vt.get_value(),
                     h_f=gear.h_a,
                     h_a=gear.h_f,
                     stroke_width=1,
                     color=PURPLE)
        def rack_updater(mob: Rack):
            mob.match_points(Rack(mob.z,
                                  module=gear.m,
                                  alpha=alpha_vt.get_value(),
                                  h_f=gear.h_a,
                                  h_a=gear.h_f,
                                  stroke_width=5
                                  ))
            mob.rotate(PI/2)
            mob.shift(DOWN*gear.rp)
        rack.add_updater(rack_updater)

        self.play(Create(rack))


        # zoom onto the gear
        self.camera.frame.save_state()
        self.play(self.camera.frame.animate.scale(m * 10 / self.camera.frame.width).move_to(gear.rp * DOWN), 
                  alpha_label.animate.next_to(rack, DOWN), 
                  Unwrite(alpha_text))
        # animate alpha_label to move to the bottom of the screen
        alpha_label.save_state()

        self.wait(2)

        gear.add_updater(lambda mob: mob.become(Gear(mob.z, module=mob.m, alpha=alpha_vt.get_value(), stroke_opacity=0, fill_color=WHITE, fill_opacity=1).move_to(gear.get_center()), match_height=True, match_width=True))
        alpha_label.add_updater(lambda m: m.become(MathTex(r"\alpha = ", f"{alpha_vt.get_value():.1f}^\circ", color=PURPLE).next_to(rack, DOWN)))


        self.play(alpha_vt.animate.set_value(14.5), run_time=2, rate_func=smooth)
        self.wait(3)
        self.play(alpha_vt.animate.set_value(25.5), run_time=2, rate_func=smooth)
        self.wait(3)
        self.play(alpha_vt.animate.set_value(20), run_time=2, rate_func=smooth)
        self.wait(2)

        # remove updaters again
        gear.clear_updaters()
        alpha_label.clear_updaters()

        # move everything back 
        self.play(self.camera.frame.animate.restore(), Uncreate(rack), alpha_label.animate.next_to(pitch_radius_label, DOWN))








class GearExample(Scene):
    def construct(self):
        # small gear
        gear1=Gear(15, stroke_opacity=0.5, fill_color=WHITE,fill_opacity=0.5)
        # larger gear
        gear2=Gear(25,  stroke_opacity=0, fill_color=RED, fill_opacity=1)
        # shifting gear1 away from center
        gear1.shift(-gear1.rp * 1.5 * RIGHT)
        # position gear2 next to gear1 so that they mesh together
        gear2.mesh_to(gear1)

        self.add(gear1, gear2)
        self.play(Rotate(gear1, gear1.pitch_angle, rate_func=linear),
                  Rotate(gear2, - gear2.pitch_angle, rate_func=linear),
                  run_time=4)
        


class gear_sum(Scene):
    def construct(self):
        m=1
        ofs = ValueTracker(0)
        Nt = ValueTracker(25)
        gear_1 = Gear(40,module=m, nppc=10, stroke_opacity=0,fill_color=BLUE_B,fill_opacity=1)
        gear_2 = Gear(int(Nt.get_value()//1),module=m, nppc=10,stroke_opacity=0,fill_color=BLUE_C,fill_opacity=1)
        def gear_updater(mob: Gear):
            newgear = Gear(int(Nt.get_value()//1),module=m, nppc=10,stroke_opacity=0,fill_color=BLUE_C,fill_opacity=1)
            mob.become(newgear)
            mob.z=newgear.z
            mob.rp = newgear.rp
            mob.rb = newgear.rb
            mob.ra = newgear.ra
            mob.rf = newgear.rf
            mob.angle_ofs = newgear.angle_ofs
            mob.pitch = newgear.pitch
            mob.pitch_angle = newgear.pitch_angle
            mob.h=newgear.h
            mob.h_a = newgear.h_a
            mob.h_f = newgear.h_f
            mob.X=newgear.X
            mob.shift(UP*mob.rp)
            mob.mesh_to(gear_1,offset=ofs.get_value())

        gear_1.shift(gear_1.rp*DOWN)
        gear_2.shift(gear_2.rp*UP)
        gear_2.mesh_to(gear_1)
        gear_2.add_updater(gear_updater)
        self.add(gear_1,gear_2)

        self.play(Rotate(gear_1,gear_1.pitch_angle*2),run_time=4)
        self.wait()
        self.play(Nt.animate.set_value(12),run_time=5,rate_func=smooth)
        self.wait()
        self.play(Rotate(gear_1, gear_1.pitch_angle * 2), run_time=4)
        self.play(Nt.animate.set_value(60), run_time=5, rate_func=smooth)
        self.wait()
        self.play(Rotate(gear_1, gear_1.pitch_angle * 2), run_time=4)
        self.wait()
        self.play(ofs.animate.set_value(0.5))
        self.wait()
        self.play(Rotate(gear_1, gear_1.pitch_angle * 2), run_time=4)
        # self.wait()


m = 0.5
z = 32
strw=2


class Add_height(MovingCameraScene):
    def construct(self):
        # m = 0.5
        # z = 32
        at = ValueTracker(20)
        xt = ValueTracker(0)
        adden = ValueTracker(1)
        deden = ValueTracker(1.25)
        gear1 = Gear(z,module=m, alpha=at.get_value(), h_a=adden.get_value(), h_f=deden.get_value(), stroke_width=strw)
        gear1.add_updater(lambda mob: mob.match_points(Gear(z,
                                                            module=m,
                                                            alpha=at.get_value(),
                                                            h_a=adden.get_value(),
                                                            h_f=deden.get_value(),
                                                            profile_shift=xt.get_value())))

        # the rack has to have reverse params
        rack1 = Rack(6,
                     module=m,
                     alpha=at.get_value(),
                     h_f=adden.get_value(),
                     h_a=deden.get_value(),
                     stroke_width=1,
                     color=RED)
        def rack_updater(mob: Rack):
            mob.match_points(Rack(6,
                                  module=m,
                                  alpha=at.get_value(),
                                  h_f=adden.get_value(),
                                  h_a=deden.get_value(),
                                  stroke_width=1
                                  ))
            mob.rotate(-PI/2)
            mob.shift(UP*gear1.rp)
            mob.shift(UP*xt.get_value()*m)
        rack1.add_updater(rack_updater)

        def get_max_height(alpha):
            return np.pi*0.5/np.tan(alpha*np.pi/180)/2

        pitch_circ_base = Circle(radius=gear1.rp,stroke_width=1)
        pitch_circ = DashDot_mobject(pitch_circ_base,num_dashes=int(z*2), dashed_ratio=0.65, dash_offset=0.35/2)

        self.camera.frame.save_state()
        # self.camera.frame.scale(m * 15 / 16)
        # self.camera.frame.move_to(gear1.rp*UP)
        self.camera.frame.scale(m * 15 / self.camera.frame.width).move_to(gear1.rp * UP)
        self.add(gear1)
        self.play(Create(rack1))
        self.play(Create(pitch_circ))


        dima = Linear_Dimension((gear1.ra)*UP,gear1.rp*UP,
                                text="1m",
                                outside_arrow=True,
                                offset=m*PI/2 * 1,
                                stroke_width=1,
                                tip_len=0.1,
                                color=RED)
        dimb = Linear_Dimension((gear1.rf) * UP, gear1.rp * UP,
                                text="1.25m",
                                outside_arrow=True,
                                offset=m * PI / 2 * 0.8,
                                stroke_width=1,
                                tip_len=0.1,
                                color=RED)

        self.play(Create(dima))
        self.wait()
        self.play(Create(dimb))
        self.wait()
        self.play(Uncreate(dima), Uncreate(dimb))
        self.wait()
        self.play(adden.animate.set_value(get_max_height(at.get_value())),
                  deden.animate.set_value(get_max_height(at.get_value())), run_time=2)
        self.wait()
        hmax = 1
        dim = Linear_Dimension((gear1.rb+hmax)*UP,gear1.rp*UP,
                               text=f"{(hmax+gear1.rb-gear1.rp)/m:.3}m",
                               outside_arrow=True,
                               offset=m*PI/2,
                               stroke_width=1,
                               tip_len=0.1,
                               color=RED)

        self.play(Create(dim))
        self.wait()
        self.play(Uncreate(dim))

        # dim_a = Angle_Dimension_3point(start=rack1.get_center()+rack1.h_f*UP+UP*0.1,
        #                                end=rack1.get_center()+rack1.h_f*UP+rotate_vector(UP,at.get_value()*DEGREES)*0.1,
        #                                arc_center=rack1.get_center()+rack1.h_f*UP,
        #                                offset=0.3,
        #                                color=RED,
        #                                outside_arrow=True,
        #                                stroke_width=2)

        # dim_a = MathTex(r'\alpha=',f'{at.get_value():.0f}').move_to(rack1.get_center()+rack1.h_f*UP+UP*0.5)
        dim_a = Text(f'α={at.get_value():.0f}°',color=RED).move_to(rack1.get_center() + rack1.h_f * UP + UP * 0.5).scale(0.5)
        dim_a.add_updater( lambda mob: mob.become(Text(f'α={at.get_value():.1f}°',color=RED).move_to(rack1.get_center() + rack1.h_f * UP + UP * 0.5).scale(0.5)))

        self.play(Create(dim_a))
        self.play(at.animate.set_value(14.5),run_time=2)
        self.wait()

        self.play(adden.animate.set_value(get_max_height(14.5)),
                  deden.animate.set_value(get_max_height(14.5)),
                  run_time=2)
        self.wait()
        self.play(FadeOut(dim_a))

        self.play(at.animate.set_value(20),
                  adden.animate.set_value(1),
                  deden.animate.set_value(1.25),
                  run_time=2)

        self.wait()
        self.play(xt.animate.set_value(0.5))
        self.wait()
        self.play(xt.animate.set_value(-0.5))
        self.wait()
        self.play(xt.animate.set_value(0))
        self.wait()

        self.play(Uncreate(rack1))
        self.play(self.camera.frame.animate.move_to(ORIGIN).scale(gear1.ra*2.5/self.camera.frame.height),
                  gear1.animate.set_stroke(width=4,family=True),
                  pitch_circ.animate.set_stroke(width=4,family=True)
                  )

        dimdp = Linear_Dimension(gear1.rp*UP,
                                 gear1.rp*DOWN,
                                 text="zm",
                                 color=RED,
                                 tip_len=0.5,
                                 offset=gear1.rp+2)

        dimda = Linear_Dimension(gear1.ra * UP,
                                 gear1.ra * DOWN,
                                 text="(z+2)m",
                                 color=RED,
                                 tip_len=0.5,
                                 offset=gear1.rp+4)

        self.play(Create(dimdp))
        self.play(Create(dimda))
        self.wait(2)