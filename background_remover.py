import os


def remove_background(input_path):
    try:
        from rembg import remove
    except Exception as exc:
        raise ImportError(
            "Background removal requires rembg with a supported backend. "
            "Install it with `pip install \"rembg[cpu]\"` or `pip install \"rembg[gpu]\"`."
        ) from exc

    os.makedirs("backgrounds_removed", exist_ok=True)

    output_path = os.path.join(
        "backgrounds_removed",
        os.path.splitext(os.path.basename(input_path))[0] + ".png"
    )

    with open(input_path, "rb") as inp:
        with open(output_path, "wb") as out:
            out.write(remove(inp.read()))

    return output_path