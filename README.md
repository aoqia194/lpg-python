## Purpose
This script is for LethalCompany mods on [Thunderstore](https://thunderstore.io/c/lethal-company/) using [LethalPaintings](https://thunderstore.io/c/lethal-company/p/femboytv/LethalPaintings/) and or [LethalPosters](https://github.com/femboytv/LC_LethalPosters). This generates the formatted images that are used by LethalPaintings and LethalPosters for the game. This is a fork of the original lpg Rust script because I for one do not know Rust enough to maintain the script that is there so I cannot make modifications to it if I wanted, and two because Python is more versatile and the speed is much better.

I'd really like to use JPG instead of PNG but the game doesn't like JPG since it's RGB not RGBA.

## Speed Testing
I cannot provide any speed testing for the Rust script as of current, but here is some quick speed testing from my Python script.
- PNG - Normal - 130 images @ 234MB - 130 in 1:33.6 (1.38/s) - Output size of 214MB
- PNG - 6 Compression & Optimised - 130 images @ 234MB - 130 in 4:39.2 (0.46/s) - Output size of 211MB
- PNG - 7 Compression - 130 images @ 234MB - 130 in ~2:10.0 () - Output size of 211MB
- JPG - Normal - 130 images @ 234MB - 130 in 43.4s (2.98/s) - Output size of 27.8MB
- JPG - 1 compression level - 130 images @ 234MB - 130 in 43.0s (3.01/s) - Output size of 2.99MB
- JPG - 95 compression level - 130 images @ 234MB - 130 in 46.9s (2.76/s) - Output size of 53.2MB
