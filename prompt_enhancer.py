STYLE_PRESETS = [
    "Realistic",
    "Anime",
    "Cyberpunk",
    "Pixar",
    "Fantasy",
    "3D Render",
    "Oil Painting",
    "Sketch",
]

NEGATIVE_PROMPT_BASE = (
    "blurry, low resolution, deformed anatomy, bad lighting, poor composition, oversaturated,"
    " watermark, text, artifacts, ugly, grainy"
)

QUALITY_MODIFIERS = {
    "Low": "basic quality, simple details",
    "Medium": "good detail, balanced composition",
    "High": "high detail, refined textures",
    "Ultra": "ultra realistic, cinematic quality, professional finish",
}


def normalize_text(text):
    text = text.strip()
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1].strip()
    return text.rstrip(",").strip()


def clean_prompt(prompt, max_chars=220):
    prompt_text = normalize_text(prompt)
    if len(prompt_text) > max_chars:
        prompt_text = prompt_text[:max_chars].rsplit(' ', 1)[0]
    return prompt_text


def enhance_prompt(prompt, style=None, quality="High"):
    prompt_text = clean_prompt(prompt)
    attributes = [
        "Ultra realistic",
        "8k resolution",
        "highly detailed",
        "cinematic lighting",
        "masterpiece",
        "professional photography",
        "sharp focus",
    ]

    if style and style not in ["Text Only"]:
        attributes.insert(0, style)

    quality_text = QUALITY_MODIFIERS.get(quality, "high detail, polished rendering")
    if quality_text:
        attributes.insert(1, quality_text)

    if prompt_text:
        attributes.append(prompt_text)

    return ", ".join([item for item in attributes if item])


def score_prompt(prompt):
    prompt_text = normalize_text(prompt)
    if not prompt_text:
        return 0, ["Start with a specific subject and add context."]

    score = 30
    suggestions = []

    if len(prompt_text) > 80:
        score += 35
    elif len(prompt_text) > 45:
        score += 20
    else:
        suggestions.append("Add more context and details to your prompt.")

    if any(word in prompt_text.lower() for word in ["cinematic", "dramatic", "detailed", "realistic", "highly detailed"]):
        score += 20
    else:
        suggestions.append("Include words like cinematic, realistic, or highly detailed.")

    if any(word in prompt_text.lower() for word in ["8k", "ultra", "photorealistic", "masterpiece"]):
        score += 15
    else:
        suggestions.append("Add quality tags like 8k, ultra, masterpiece, or photorealistic.")

    if any(word in prompt_text.lower() for word in ["sunset", "night", "studio", "dramatic", "soft"]):
        score += 10

    score = min(score, 100)
    return score, list(dict.fromkeys(suggestions))


def generate_negative_prompt(prompt, style=None):
    prompt_text = normalize_text(prompt)
    style_negative = ""
    if style == "Anime":
        style_negative = "poor line work, unnatural shading"
    elif style == "Realistic":
        style_negative = "cartoonish, flat colors"
    elif style == "Cyberpunk":
        style_negative = "dull, dated technology"
    elif style == "Pixar":
        style_negative = "dark, gritty"
    elif style == "Fantasy":
        style_negative = "ordinary, mundane"
    elif style == "Oil Painting":
        style_negative = "pixelated, low detail"
    elif style == "Sketch":
        style_negative = "blurry, smudged"

    negative_parts = [NEGATIVE_PROMPT_BASE]
    if style_negative:
        negative_parts.append(style_negative)

    return ", ".join(negative_parts)


def build_prompt(subject, style, lighting, camera, quality, extra=""):
    pieces = [
        subject,
        style,
        lighting,
        camera,
        QUALITY_MODIFIERS.get(quality, "high detail, polished rendering"),
    ]
    if extra:
        pieces.append(extra.strip())
    return ", ".join([p for p in pieces if p])
