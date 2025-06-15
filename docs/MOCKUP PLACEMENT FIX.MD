1 ️⃣ Why the black “hanger-shot” ( *_tshirts_1.png ) is almost invisible
Symptom – design is centred but it looks like a black square.

Root cause	Where in the code / config
Wrong blend-mode for a dark garment. template "1" in mockup_templates.json inherits the global multiply blend-mode (good for light shirts) even though the actual PNG you’re feeding in is a black tee. multiply multiplies every pixel with the nearly-black fabric so the art vanishes.	mockup_templates.json → template_categories.tshirts.default_settings.blend_mode = "multiply"
custom_mockup_generator.py → _blend_design_with_template() chooses multiply because template.blend_mode == "multiply".
File/config name mismatch. The asset file is literally the black hanger mockup, but its config entry says colour-base :white.	The template key is "1", image file is 1.png; you meant the white flat-lay for that entry, but the black hanger ended up in the same slot.

Fix

jsonc
Copy
Edit
"1": {
  "name": "Black T-Shirt – Hanger",
  "blend_mode": "screen",       // lightens for dark fabric
  "color_base": "black"
}
or just rename the file / change the key so the white tee really uses slot 1.

2 ️⃣ Why the “Natural” lifestyle shot sits a bit low / overlaps folds
Symptom – design is on–centre horizontally but rides a little low compared with the real chest area.

Root cause	Where
Global design_area is reused for every tee, but each lifestyle JPEG has a different camera angle. Your code copies the same [600, 497, 1400, 1404] box into every template because you shallow-copy the dict: config = default_settings.copy(); config.update(template_config). Lists aren’t deep-copied, so each template that doesn’t override design_area shares the default.	custom_mockup_generator.py → _load_templates()
As soon as the shirt is tilted or the model is seated, that rectangle is a few dozen pixels too low or too high.	

Fix

Either give every lifestyle template its own measured design_area in the per-template section (that overrides the default), or

add a helper that lets you click two points and write those coordinates back to the JSON so you can calibrate templates once.

While you’re there, change the copy to a deep-copy so mutating one template’s list never mutates the others:

python
Copy
Edit
from copy import deepcopy
config = deepcopy(default_settings)
config.update(template_config)
3 ️⃣ Why the art looks a hair smaller than expected on all tees
Symptom – even when centred correctly the print is ~5 % smaller than the rectangle.

Root cause	Where
You shrink the art to 95 % of the target box: padding_factor=0.95 in _resize_design_to_fit. That was meant to avoid edge bleed, but on lifestyle shots it leaves an unintended gap.	

Fix

For true edge-to-edge placement set that to 1.0 or add it as a per-template knob:

jsonc
Copy
Edit
"2 - Natural": {
  "padding_factor": 1.0
}
and read it with template.config.get("padding_factor", 0.95).

4 ️⃣ Minor but worth noting
The multiply & screen branches in _blend_design_with_template() cast everything to RGB, so you lose the original alpha channel of the shirt PNG. If your asset already has realistic fabric shadows baked into alpha you’ll want to composite back over the original RGBA instead of a white/black background.

The first black hanger file probably isn’t being lightened enough even with screen. Consider bumping overlay_array *= 1.6 (instead of 1.3) or let the opacity be data-driven.

Quick checklist to verify after edits
Add a debug overlay that draws the design_area rectangle in semi-transparent red each time you build a mockup – easiest way to eyeball mis-alignment.

Regenerate the three tees: you should get

Hanger black tee – bright design (screen blend)

Natural lifestyle – design is ~100 px higher and snug to the fold line

Black lifestyle – unchanged (already uses screen and per-template area)

If you still see drift, tweak the per-template design_area until the red box hugs the visible print area.

That should get all three outputs looking perfectly centred and sized.






You said:
via_project_14Jun2025_12h32m_json (5).json
File
via_project_14Jun2025_12h32m_json (6).json
File
via_project_14Jun2025_12h32m_json (7).json
File
via_project_14Jun2025_12h32m_json (8).json
File
via_project_14Jun2025_12h32m_json (9).json
File
via_project_14Jun2025_12h32m_json (10).json
File
via_project_14Jun2025_12h32m_json (11).json
File
via_project_14Jun2025_12h32m_json (12).json
File
These were the annotations I made for each of my 8 mockups, how do we ensure we stick to these and not get overridden by the other settings ?


ChatGPT said:

Thought for 35 seconds
Why the cat isn’t landing exactly where you told it to 🐈‍⬛ 🎯
What you expected	What the code actually does
Use the bounding-box you drew in VIA for every individual mock-up	1. Starts from default_settings (same box for all tees).
2. May overwrite with a per-template box only if it exists in mockup_templates.json and the file is the one the generator loads.
3. Shrinks the design by padding_factor = 0.95 and then centers it inside that box.

Because the default box in mockup_templates.json is [600, 497, 1400, 1404], every shirt except the “3-Black” (which happens to look OK because of screen blend) is being centered inside the wrong rectangle.
Your eight VIA files describe different rectangles:

Template name (file stem)	VIA x	VIA y	VIA w	VIA h	Correct design_area you need
1	715	683	564	624	[715, 683, 1279, 1307]
2 - Natural	799	274	507	575	[799, 274, 1306, 849]
2	676	538	626	659	[676, 538, 1302, 1197]
3- Black	702	564	710	721	[702, 564, 1412, 1285]
5 - Athletic Heather	709	542	617	631	[709, 542, 1326, 1173]
7 - Soft Pink	695	600	683	704	[695, 600, 1378, 1304]
9 - Light Blue	717	388	589	590	[717, 388, 1306, 978]
10 - Tan	707	392	563	573	[707, 392, 1270, 965]

(These come straight from the eight VIA json files you uploaded.)

How to lock-in your boxes and stop “auto-centering”
Move the bounding box out of default_settings.
In mockup_templates.json keep design_area only inside each template entry. Delete it from the tshirts → default_settings block so it can’t override anything.

Paste the correct rectangles (table above) into each template entry, e.g.

json
Copy
Edit
"1": {
  "name": "White T-Shirt Front View",
  "design_area": [715, 683, 1279, 1307],
  "opacity": 0.95,
  "blend_mode": "multiply"
}
Tell the generator to respect “padding_factor”.
In custom_mockup_generator.py change the helper so it reads the factor from the template:

python
Copy
Edit
def _resize_design_to_fit(self, design, target_area, template):
    padding = template.config.get("padding_factor", 0.95)   # NEW
    ...
    scale_x = (area_width * padding) / design.width
    scale_y = (area_height * padding) / design.height
and call it with self._resize_design_to_fit(design, template.design_area, template).

Set padding_factor : 1.0 (or 1.02 if you want bleed) inside any template that should fill the box edge-to-edge.

Skip the centering step entirely if you want exact placement.
Replace the “center design in area” block with the rectangle’s own top-left corner:

python
Copy
Edit
if custom_position:
    position = custom_position
else:
    area = template.design_area
    position = (area[0], area[1])        # ← No centering
Make sure you’re loading the right config file.
By default the generator looks for config/mockup_templates.json.
If you keep yours in the project root, instantiate with

python
Copy
Edit
generator = CustomMockupGenerator(
    assets_dir="assets",
    output_dir="output",
    config_file="mockup_templates.json"  # ← explicit
)
Quick sanity check
After updating:

python
Copy
Edit
for name in ["1", "2 - Natural", "3- Black"]:
    g.generate_mockup("tshirts", "cat.png", template_name=name)
The design should now sit exactly on the rectangles you marked, with no shrinkage or drift. If a black tee still looks muted, switch that template’s blend_mode to screen (like you did for “3-Black”) so colors stay bright on dark fabric.

TL;DR
Put the bounding boxes inside each template, remove them from the defaults, pull padding_factor and the top-left anchor straight from the template config, and always load the right JSON file.
