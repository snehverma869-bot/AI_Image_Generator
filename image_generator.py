import os
from datetime import datetime
from typing import Optional

import torch
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from PIL import Image

MODEL_ID = "runwayml/stable-diffusion-v1-5"

pipe = None
img2img_pipe = None


def load_model(device: Optional[str] = None):
    """Load and cache the Stable Diffusion pipeline.

    Args:
        device: Optional explicit device string (e.g. 'cuda' or 'cpu').

    Returns:  
        The loaded pipeline.
    """
    global pipe

    if pipe is None:
        device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        torch_dtype = torch.float16 if device == "cuda" else torch.float32

        try:
            if device == "cuda":
                pipe = StableDiffusionPipeline.from_pretrained(
                    MODEL_ID,
                    torch_dtype=torch_dtype,
                    device_map="auto",
                )
            else:
                pipe = StableDiffusionPipeline.from_pretrained(
                    MODEL_ID,
                    torch_dtype=torch_dtype,
                    device_map=None,
                )
        except Exception as exc:
            msg = (
                f"Failed to load model '{MODEL_ID}': {exc}.\n"
                "Common causes: no internet, missing Hugging Face token, or model access not accepted.\n"
                "If the model requires authentication, set the environment variable HUGGINGFACE_HUB_TOKEN,\n"
                "or run `huggingface-cli login` and accept the model terms on huggingface.co."
            )
            raise RuntimeError(msg) from exc

        # Reduce memory usage where supported
        try:
            pipe.enable_attention_slicing()
        except Exception:
            pass

        if device == "cuda":
            try:
                pipe.enable_xformers_memory_efficient_attention()
            except Exception:
                pass

            pipe = pipe.to(device)

    return pipe


def _run_pipeline(
    pipe,
    prompt: str,
    negative_prompt: Optional[str],
    height: int,
    width: int,
    num_inference_steps: int,
    guidance_scale: float,
    generator,
    device: str,
    
):
    if device == "cuda":
        with torch.cuda.amp.autocast():
            return pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
            )
    return pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        height=height,
        width=width,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        generator=generator,
    )


def _create_output_path(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(output_dir, f"{timestamp}.png")


def reset_pipeline():
    global pipe
    pipe = None
    global img2img_pipe
    img2img_pipe = None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Check environment and model availability (no heavy download)")
    args = parser.parse_args()

    if args.check:
        print(f"Torch available: {torch.__version__}; CUDA available: {torch.cuda.is_available()}")
        try:
            _ = load_model()
            print("Model loaded (or cached) successfully.")
        except Exception as e:
            print("Model load failed:")
            print(e)


def generate_image(
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

    # Use autocast on CUDA for faster/fp16 generation
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
    except Exception as e:
        raise RuntimeError(f"Image generation failed: {e}") from e

    image = result.images[0]
    image.save(filename)

    return filename


def generate_image_from_image(
    init_image_path: str,
    prompt: str,
    negative_prompt: Optional[str] = None,
    strength: float = 0.75,
    height: int = 512,
    width: int = 512,
    num_inference_steps: int = 50,
    guidance_scale: float = 7.5,
    seed: Optional[int] = None,
    output_dir: str = "generated_images",
):
    """Run an image-to-image transform using Stable Diffusion Img2Img.

    `strength` controls how strongly the init image is transformed (0.0 - keep, 1.0 - full transform).
    Returns the path to the saved image.
    """
    global img2img_pipe

    device = "cuda" if torch.cuda.is_available() else "cpu"

    if img2img_pipe is None:
        try:
            if device == "cuda":
                img2img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
                    MODEL_ID,
                    torch_dtype=torch.float16,
                    device_map="auto",
                )
            else:
                img2img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
                    MODEL_ID,
                    torch_dtype=torch.float32,
                    device_map=None,
                )
        except Exception as exc:
            raise RuntimeError(f"Failed to load img2img model '{MODEL_ID}': {exc}") from exc

        try:
            img2img_pipe.enable_attention_slicing()
        except Exception:
            pass

        if device == "cuda":
            try:
                img2img_pipe.enable_xformers_memory_efficient_attention()
            except Exception:
                pass

            img2img_pipe = img2img_pipe.to(device)

    generator = None
    if seed is not None:
        generator = torch.Generator(device=device).manual_seed(seed)

    filename = _create_output_path(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    try:
        init_image = Image.open(init_image_path).convert("RGB")
        # resize init image to target size to avoid size mismatch
        init_image = init_image.resize((width, height))

        if device == "cuda":
            with torch.cuda.amp.autocast():
                result = img2img_pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    image=init_image,
                    strength=strength,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator,
                )
        else:
            result = img2img_pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=init_image,
                strength=strength,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
            )
    except Exception as e:
        raise RuntimeError(f"Image-to-image generation failed: {e}") from e

    image = result.images[0]
    image.save(filename)

    return filename