from pathlib import Path
import re

path = Path(__file__).with_name('image_generator.py')
text = path.read_text()
start = text.index('def generate_image(')
end = text.index('\n    return filename\n', start) + len('\n    return filename\n')
old = text[start:end]
new = '''def generate_image(
    prompt: str,
    negative_prompt: Optional[str] = None,
    height: int = 512,
    width: int = 512,
    num_inference_steps: int = 50,
    guidance_scale: float = 7.5,
    seed: Optional[int] = None,
    output_dir: str = "generated_images",
):
    """Generate an image from a text prompt and save it to disk.

    Returns the path to the saved image.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = load_model(device=device)

    generator = None
    if seed is not None:
        generator = torch.Generator(device=device).manual_seed(seed)

    filename = _create_output_path(output_dir)

    for attempt in range(2):
        try:
            if device == "cuda":
                with torch.cuda.amp.autocast():
                    result = pipe(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        height=height,
                        width=width,
                        num_inference_steps=num_inference_steps,
                        guidance_scale=guidance_scale,
                        generator=generator,
                    )
            else:
                result = pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    height=height,
                    width=width,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator,
                )
            break
        except IndexError as e:
            if attempt == 0 and "out of bounds" in str(e):
                reset_pipeline()
                pipe = load_model(device=device)
                continue
            raise RuntimeError(f"Image generation failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Image generation failed: {e}") from e

    image = result.images[0]
    image.save(filename)

    return filename
'''
path.write_text(text[:start] + new + text[end:])
print('patched image_generator.py')
