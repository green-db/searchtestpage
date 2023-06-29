from random import random, seed
from typing import Any, Dict, List, Optional, Tuple
from minify_html import minify

# label_map = {label.id: label for label in sustainability_labels}
# js_label_info = json.dumps(
#     {
#         label.id: {
#             k: 0 if v is None else v
#             for k, v in label.dict().items()
#             if k not in {"id", "timestamp"}
#         }
#         for label in sustainability_labels
#     }
# )
# label_metrics = [
#     ("label_cred_credibility", "cred_credibility"),
#     ("label_eco_chemicals", "eco_chemicals"),
#     ("label_eco_lifetime", "eco_lifetime"),
#     ("label_eco_water", "eco_water"),
#     ("label_eco_inputs", "eco_inputs"),
#     ("label_eco_quality", "eco_quality"),
#     ("label_eco_energy", "eco_energy"),
#     ("label_eco_waste_air", "eco_waste_air"),
#     ("label_eco_environmental_management", "eco_environmental_management"),
#     ("label_social_labour_rights", "social_labour_rights"),
#     ("label_social_business_practice", "social_business_practice"),
#     ("label_social_social_rights", "social_social_rights"),
#     ("label_social_company_responsibility", "social_company_responsibility"),
#     ("label_social_conflict_minerals", "social_conflict_minerals"),
# ]

# category_typos = {"PANT": "PANTS", "SHORT": "SHORTS", "JEAN": "JEANS", "SWIMMWEAR": "SWIMWEAR"}


def to_linear(srgb: float) -> float:
	if srgb < 0:
		return 0
	if srgb > 1:
		return 1
	if srgb < 0.04045:
		return srgb / 12.92
	return pow((srgb + 0.055) / 1.055, 2.4)


def to_srgb(linear: float) -> float:
	if linear < 0:
		return 0
	if linear > 1:
		return 1
	if linear < 0.0031308:
		return linear * 12.92
	return pow(linear, 1.0 / 2.4) * 1.055 - 0.055


def kurgel(p: float, q: float) -> float:
	if q == 0:
		return 0
	s = p / q
	return 1 + s - (s * s + 2 * s) ** 0.5


def shadow(bg: float, fg: float, s: float = 0.5, p: float = 0.62) -> float:
	return bg * s / (1.0 - p * bg * fg)


def bevel(bg: float, fg: float, s: float, p: float = 0.62) -> float:
	return fg + shadow(bg, fg, s, p)


def medium(a: float, t: float) -> float:
	return 1 / (t * (1 - a) + 1)


def blend(a: float, b: float, t: float) -> float:
	return (1 - t) ** 2 * a / (1 - t * a * b) + t * b


def temp2color(temp: float) -> List[float]:
	if temp == 0:
		return [0, 0, 0]
	return [f**3 / (exp(f / temp) - 1 + log(10) * 30) / 5 for f in [26, 30, 35]]


def map(func: Any, *iterables: Any, **kwargs: Any) -> Any:
	return (func(*args, **kwargs) for args in zip(*iterables))


def webcolor(color: List[float]) -> str:
	return "#" + "".join(f"{round(to_srgb(c)*255):02x}" for c in color)


def linspace(start: float, end: float, n: int) -> List[float]:
	return [start + (end - start) * i / (n - 1) for i in range(n)]


def animate(curve: list) -> List[Tuple[int, Any]]:
	return [(i * 100 // (len(curve) - 1), c) for i, c in enumerate(curve)]


def rebuild_page(
	page_title: str = "GreenDB",
	description: str = "A Product-by-Product Sustainability Database",
	page_url: str = "https://calgo-lab.github.io/greendb",
	image_url: str = "https://calgo-lab.github.io/greendb/greendb.jpg",
	image_alt_text: str = "GreenDB",
	regenerate_color_scheme: bool = False,
) -> str:
	with open("main.js", "r") as f:
		script = f.read()
	return minify(
		f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<style>

* {{
	box-sizing: border-box;
	animation-timing-function: cubic-bezier(.19,1,.22,1);
}}

#search_field {{
	position:sticky;
	top:0;
	width:100%;
	resize:none;
	overflow:hidden;
}}

#footer {{
	height:90vh;
}}

</style>
<meta name="description" content="{description}">
<meta property="og:title" content="{page_title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{image_url}">
<meta property="og:image:alt" content="{image_alt_text}">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:url" content="{page_url}">
<link rel="canonical" href="{page_url}">
<link rel="icon" href="/favicon.ico">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link href="https://fonts.googleapis.com/css?family=Lato:400,600" rel="stylesheet">
<link href="https://fonts.googleapis.com/css?family=Muli:400,600" rel="stylesheet">
</head>

<body>

<textarea id='search_field' placeholder="hi"></textarea>
<div id='stuff'></div>
<div id='footer'></div>

</body>

</html>

<script type="text/javascript">{script}</script>
""",
		minify_js=True,
		minify_css=True,
	)

if __name__ == "__main__":
	content = rebuild_page()
	with open("index.html", "w", encoding="utf-8") as f:
		f.write(content)
