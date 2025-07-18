"""
Reusable VMobject that models a roller chain constrained on a single spur gear.

Usage
-----
>>> class ChainDemo(Scene):
>>>     def construct(self):
>>>         gear = Gear(10, stroke_opacity=0, fill_color=WHITE,
>>>                     fill_opacity=1, module=0.5, alpha=20)
>>>         chain = GearChain(gear,
>>>                       roll_radius=None,          # default uses module
>>>                       roll_color=GRAY_A,
>>>                       roll_fill_color=GRAY_C,
>>>                       alternate_link_colors=(GRAY_C, GRAY_B),
>>>                       link_width=35,
>>>                       pin_color=GRAY_D,
>>>                       pin_radius=0.1)
>>>         self.add(gear, chain)
>>>         # Animate links in two passes to get the alternating effect
>>>         even_links = chain.get_links()[0::2]
>>>         odd_links  = chain.get_links()[1::2]
>>>         self.play(*[Create(l) for l in even_links])
>>>         self.play(*[Create(l) for l in odd_links])
>>>         self.wait()
>>>         self.play(Rotate(gear, gear.pitch_angle * 2))
>>>         self.wait()

All heavy-lifting (geometric construction + updaters) is encapsulated in
:class:`GearChain`, so scenes stay tidy and easily reusable.
"""

from typing import Tuple, Optional
import numpy as np
from manim import (
    VGroup,
    Circle,
    Dot,
    Line,
    PI,
    GRAY_A,
    GRAY_B,
    GRAY_C,
    GRAY_D,
    CapStyleType,
    Circle,
)

# ``Gear`` comes from manim_gearbox (pip install manim_gearbox) or any custom gear class
from manim_gearbox import Gear


class GearChain(VGroup):
    """A roller-chain wrapped around a :class:`~manim_gear.Gear`.

    Parameters
    ----------
    gear
        The driving gear instance the chain should sit on.  The chain attaches
        to the *pitch circle* (radius ``gear.rp``) and auto-updates when the
        gear rotates or moves.
    roll_radius
        Radius of each roller.  ``None`` (default) uses :math:`m\pi/4` where
        *m* is the module of the gear, matching standard chain sizing tables.
    roll_color, roll_fill_color, roll_fill_opacity
        Styling for the rollers.
    alternate_link_colors
        Tuple ``(even_color, odd_color)`` for the alternating connecting links.
    link_width
        Stroke width of each link (visual thickness).
    pin_color, pin_radius
        Styling for the pins drawn at each roller centre (purely decorative).

    Notes
    -----
    *Rollers*, *links* and *pins* are stored internally as three separate
    :class:`~manim.mobject.types.vectorized_mobject.VGroup` instances that can
    be retrieved via :py:meth:`get_rolls`, :py:meth:`get_links` and
    :py:meth:`get_pins`.
    """

    def __init__(
        self,
        gear: "Gear",
        *,
        roll_radius: Optional[float] = None,
        roll_color=GRAY_A,
        roll_fill_color=GRAY_C,
        roll_fill_opacity: float = 0.5,
        alternate_link_colors: Tuple = (GRAY_C, GRAY_B),
        link_width: float = 35,
        pin_color=GRAY_D,
        pin_radius: float = 0.1,
        add_subobjects: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.gear = gear

        self.roll_radius = roll_radius or gear.m * PI / 4.0
        self.roll_color = roll_color
        self.roll_fill_color = roll_fill_color
        self.roll_fill_opacity = roll_fill_opacity
        self.link_width = link_width
        self.link_colors = alternate_link_colors
        self.pin_color = pin_color
        self.pin_radius = pin_radius

        # Internal groups
        self._rolls = VGroup()
        self._links = VGroup()
        self._pins = VGroup()

        self._build_geometry()


        if add_subobjects:
            # Ensure the chain (self) contains all parts
            self.add_subobjects()

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def get_rolls(self) -> VGroup:
        """Return the rollers (circles)."""
        return self._rolls

    def get_links(self) -> VGroup:
        """Return the link lines connecting the rollers."""
        return self._links

    def get_pins(self) -> VGroup:
        """Return the (decorative) centre pins."""
        return self._pins
    
    def add_subobjects(self) -> None:
        """Add all subobjects (rollers, links, pins) to the chain."""
        self.add(self._rolls, self._links, self._pins)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _build_geometry(self) -> None:
        """Construct rollers, connecting links and pins with updaters."""
        gear = self.gear
        z = gear.z  # number of teeth / rollers

        def chain_pos(nth: int) -> np.ndarray:
            """Cartesian position of *nth* roller (0 <= nth < z)."""
            if nth < 0 or nth >= z:
                raise ValueError("nth_tooth must be between 0 and z-1")

            pitch_angle = gear.pitch_angle
            offset = gear.get_angle() + 0.5 * pitch_angle  # centre roller on tooth gap
            x = gear.rp * np.cos(nth * pitch_angle + offset)
            y = gear.rp * np.sin(nth * pitch_angle + offset)
            center = gear.get_center()
            return np.array([center[0] + x, center[1] + y, center[2]])

        # ------------------------------------------------------------------
        # Rollers
        # ------------------------------------------------------------------
        rolls: list[Circle] = []
        for n in range(z):
            roller = (
                Circle(
                    radius=self.roll_radius,
                    color=self.roll_color,
                    fill_color=self.roll_fill_color,
                )
                .set_fill(opacity=self.roll_fill_opacity)
                .move_to(chain_pos(n))
            )
            roller.add_updater(lambda m, nth=n: m.move_to(chain_pos(nth)))
            rolls.append(roller)
        self._rolls.add(*rolls)

        # ------------------------------------------------------------------
        # Links (alternating colour)
        # ------------------------------------------------------------------
        links: list[Line] = []
        for i in range(z):
            a, b = rolls[i], rolls[(i + 1) % z]
            color = self.link_colors[i % 2]
            link = Line(a.get_center(), b.get_center(), color=color)
            link.set_stroke(width=self.link_width)
            link.set_cap_style(CapStyleType.ROUND)

            link.add_updater(
                lambda m, ra=a, rb=b: m.put_start_and_end_on(
                    start=ra.get_center(), end=rb.get_center()
                )
            )
            # Safety check – ensure straight link is shorter than theoretical pitch
            assert link.get_length() < gear.pitch, (
                f"Link length {link.get_length()} exceeds pitch {gear.pitch}"
            )
            links.append(link)
        self._links.add(*links)

        # ------------------------------------------------------------------
        # Pins (decorative dots at roller centres)
        # ------------------------------------------------------------------
        pins: list[Dot] = []
        for roll in rolls:
            pin = Dot(roll.get_center(), color=self.pin_color, radius=self.pin_radius)
            pin.add_updater(lambda m, r=roll: m.move_to(r.get_center()))
            pins.append(pin)
        self._pins.add(*pins)

