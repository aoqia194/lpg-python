import glob
import os
import re
from logging import INFO
from pathlib import Path

import structlog
from about_time import about_time
from alive_progress import alive_it, styles
from PIL import Image, ImageOps, UnidentifiedImageError
from rich import print

# Global Constants
structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(INFO))
LOGGER: structlog.PrintLogger = structlog.get_logger()
POSTERS_DIR = "./output/BepInEx/plugins/LethalPosters/posters"
TIPS_DIR = "./output/BepInEx/plugins/LethalPosters/tips"
PAINTINGS_DIR = "./output/BepInEx/plugins/LethalPaintings/paintings"

POSTER_PIXEL_OFFSETS = [
    [0, 0, 341, 559],
    [346, 0, 284, 559],
    [641, 58, 274, 243],
    [184, 620, 411, 364],
    [632, 320, 372, 672],
]
PAINTING_PIXEL_OFFSET = (264, 19)
TIPS_SIZE = (796, 1024)
PAINTING_SIZE = (243, 324)


# Global Variables
input_images: list[Image.Image] = []
output_format = 0
poster_template: Image.Image | None = None
painting_template: Image.Image | None = None


# Gets the appropriate image `i` from the given input image index.
def get_image(i: int) -> Image.Image:
    try:
        return input_images[i % len(input_images)].copy()
    except IndexError as e:
        LOGGER.critical(f"Raised IndexError in get_image({i})")
        LOGGER.debug(f"input_images size = {len(input_images)}")
        LOGGER.exception(f"{e}")
        LOGGER.info("Exiting to prevent image warfare...")
        exit()


# Generates the painting atlas and inserts the image(s) onto the atlas.
def generate_atlas(i: int) -> Image.Image:
    base = poster_template.copy()
    posters: list[Image.Image] = [get_image(i + j) for j in range(5)]
    for i, o in enumerate(POSTER_PIXEL_OFFSETS):
        poster = ImageOps.contain(posters[i], (o[2], o[3]), Image.Resampling.LANCZOS)
        base.paste(poster, (o[0] + o[2] - poster.width, o[1]))
    return base


# Generates a tip image using the given input image index.
def generate_tips(i: int) -> Image.Image:
    base = Image.new(("RGBA" if output_format < 2 else "RGB"), TIPS_SIZE)
    tip = ImageOps.contain(get_image(i), TIPS_SIZE, Image.Resampling.LANCZOS)
    base.paste(tip, (TIPS_SIZE[0] - tip.width, 0))
    return base


# Generates a painting image using the given input image index.
def generate_painting(i: int) -> Image.Image:
    base = painting_template.copy()
    painting = ImageOps.fit(get_image(i), PAINTING_SIZE, Image.Resampling.LANCZOS)
    base.paste(painting, PAINTING_PIXEL_OFFSET)
    return base


################################
# MAIN EXECUTION
################################
def main():
    global input_images
    global output_format
    global poster_template
    global painting_template

    # Create directories
    if not Path("input").exists() or not Path("output").exists():
        LOGGER.debug("Creating directories...")
        Path("input").mkdir(parents=True, exist_ok=True)
        Path(POSTERS_DIR).mkdir(parents=True, exist_ok=True)
        Path(TIPS_DIR).mkdir(parents=True, exist_ok=True)
        Path(PAINTINGS_DIR).mkdir(parents=True, exist_ok=True)

    # Open templates
    try:
        poster_template = Image.open("./posters_template.png")
        painting_template = Image.open("./painting_template.png")
    except UnidentifiedImageError as e:
        LOGGER.critical("Raised UnidentifiedImageError in main")
        LOGGER.exception(f"{e}")
        LOGGER.info("Missing templates!!!")
        LOGGER.info("Exiting to prevent image warfare...")
        exit()

    # Ask the user for file format and compression
    LOGGER.info("Select the desired output format!")
    LOGGER.info("\t0) PNG")
    LOGGER.info("\t1) PNG (Optimised)")
    LOGGER.info("\t2) JPG")
    LOGGER.info("\t3) JPG (Compressed)")
    output_format = int(input("> "))
    if output_format < 0 or output_format > 3:
        LOGGER.err("Format was invalid.")
        exit()
    format_string = ["png", "png", "jpg", "jpg"][output_format]

    should_optimise = output_format == 1 or output_format == 3
    if output_format == 3:
        LOGGER.info("How much compression do you want?")
        LOGGER.info("\t(1 = Best Compression, 95 = Best Quality)")
        LOGGER.info(
            "\tPlease note that the more compression you apply, the longer it takes to process the image."
        )
        compression = int(input("> "))
        if compression < 1 or output_format > 95:
            LOGGER.err("Compression number was invalid.")
            exit()

    # Loading all input images into a list
    LOGGER.debug("Loading input images...")
    with about_time() as t_total:
        input_images_filenames: list[str] = []
        for _file in glob.iglob("input/*.*"):
            if re.match(
                ".*\.(png|jpg|jpeg|PNG|JPG|JPEG|Png|Jpg|Jpeg)",
                _file,
                flags=re.RegexFlag.IGNORECASE,
            ):
                filename, ext = os.path.splitext(_file)
                input_images.append(Image.open(_file))
                input_images_filenames.append(filename + ext)
    LOGGER.info(f"Successfully loaded images after {t_total.duration_human}!")

    # Do image processing
    LOGGER.debug("Processing images...")
    bar = alive_it(
        enumerate(input_images),
        finalize=lambda bar: bar.text(
            f"Finished processing images after {t_total.duration_human}!"
        ),
        bar=styles.BARS.get("bubbles"),
    )
    with about_time() as t_total:
        for i, _img in bar:
            LOGGER.debug(f"ITER {i} | Generating...")
            with about_time() as t0:
                poster = generate_atlas(i)
                tips = generate_tips(i)
                painting = generate_painting(i)

            LOGGER.info(f"ITER {i} | Generated images after {t0.duration_human}.")
            bar.text(f"Generated images after {t0.duration_human}.")

            if output_format == 2 or output_format == 3:
                with about_time() as t2:
                    poster = poster.convert("RGB")
                    tips = tips.convert("RGB")
                    painting = painting.convert("RGB")

                LOGGER.info(
                    f"ITER {i} | Converted images to RGB after {t2.duration_human}."
                )

            with about_time() as t1:
                if output_format == 3:
                    poster.save(
                        f"{POSTERS_DIR}/{i}.{format_string}",
                        optimize=should_optimise,
                        quality=compression,
                    )
                    tips.save(
                        f"{TIPS_DIR}/{i}.{format_string}",
                        optimize=should_optimise,
                        quality=compression,
                    )
                    painting.save(
                        f"{PAINTINGS_DIR}/{i}.{format_string}",
                        optimize=should_optimise,
                        quality=compression,
                    )
                elif should_optimise:
                    poster.save(
                        f"{POSTERS_DIR}/{i}.{format_string}",
                        optimize=should_optimise,
                    )
                    tips.save(
                        f"{TIPS_DIR}/{i}.{format_string}",
                        optimize=should_optimise,
                    )
                    painting.save(
                        f"{PAINTINGS_DIR}/{i}.{format_string}",
                        optimize=should_optimise,
                    )
                else:
                    poster.save(
                        f"{POSTERS_DIR}/{i}.{format_string}", optimize=should_optimise
                    )
                    tips.save(
                        f"{TIPS_DIR}/{i}.{format_string}", optimize=should_optimise
                    )
                    painting.save(
                        f"{PAINTINGS_DIR}/{i}.{format_string}", optimize=should_optimise
                    )
            LOGGER.info(f"ITER {i} | Saved images after {t1.duration_human}.")
            LOGGER.info("------------")
            bar.text(f"Saved images after {t1.duration_human}.")
    bar.text(f"Completed after {t_total.duration_human}!")

    # Close all manually opened files.
    for _img in input_images:
        _img.close()
    poster_template.close()
    painting_template.close()


if __name__ == "__main__":
    main()