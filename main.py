from manim import *
from manim_gearbox import *
from PIL import Image
import numpy as np
import requests
from pathlib import Path

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





class gear_transform(Scene):
    def construct(self):

        z = ValueTracker(12)

        gear = Gear(int(z.get_value()), stroke_opacity=0.5, fill_color=WHITE, fill_opacity=0.5)
        

        self.play(Create(gear))
        self.play(Rotate(gear, gear.pitch_angle, rate_func=linear),
                  run_time=4)
        gear.add_updater(lambda m: m.become(Gear(int(z.get_value()), stroke_opacity=0.5, fill_color=WHITE, fill_opacity=0.5)))
        self.play(z.animate.set_value(20), run_time=2, rate_func=linear)
        self.wait(2)


        gear2 = Gear(19, stroke_opacity=0.5, fill_color=WHITE, fill_opacity=0.5)

        self.play(Transform(gear, gear2))

class gear_example(Scene):
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