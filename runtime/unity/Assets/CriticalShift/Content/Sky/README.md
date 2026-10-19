# Night sky

**Responsibility:** the outdoor night sky. It shows the real star field and Milky Way turning about the celestial pole, and a lit Moon that crosses the sky with its phase. A directional moonlight follows the Moon, dimming and reddening as it sinks.

**Not its responsibility:** daytime, sunrise or sunset, clouds, weather, fog, interior lighting, tonemapping or exposure, and any game rule. Nothing in the game reads the sky clock.

**Pieces:**
- `NightSky.shader` (`CriticalShift/NightSky`): one URP skybox pass.
- `Presentation/NightSky.cs`: the driver component.
- `Content/Editor/NightSkySetup.cs`:
  - the texture import settings;
  - the menu `Critical Shift > Environment > Set Up Night Sky`, which creates `NightSky.mat`, a "Night Sky" object holding the moonlight and the component, and sets the scene's skybox.
- `Textures/`: four PNGs built by `runtime/tools/build_sky_textures.py` from NASA sources (below). They are Git LFS files: run `git lfs pull --include "runtime/unity/Assets/CriticalShift/Content/Sky/Textures/*"`.

**Owner and lifetime:** while enabled, `NightSky` is the scene's only writer of:
- `RenderSettings.skybox` and `RenderSettings.sun`;
- the moonlight's rotation, colour and intensity;
- the shader globals `_CS_SkyFromWorld`, `_CS_MoonDir`, `_CS_MoonNorth`, `_CS_SunDir` and `_CS_SkyTime`.

It sets the skybox and sun in `OnEnable`, the globals and moonlight every frame, and clears the globals in `OnDisable`; the shader then shows a fixed sky.

**Clock:** sky time = `startHour` + play time × `timeScale`. The clock is local and cosmetic, so in multiplayer each machine runs its own. If the sky must match between players, a host-owned session clock would set it; that isn't built.

## Defaults and what they give

| Setting | Default | Effect |
|---|---|---|
| `timeScale` | 20 | A 30-minute shift runs from 20:00 to 06:00 sky time. The stars turn 5° per real minute. |
| `latitude` | 52° | The celestial pole stands 52° above the northern horizon. |
| `moonIllumination` | 0.97, waxing | A near-full Moon, up all night: 39° high in the south-east at the start, highest (53°) about 22:40, 8° in the west at 05:40. |
| `moonDeclination` | 15° | How high the Moon's arc runs. |
| `_MoonDiameter` | 1.0° | About twice the real 0.52°, for readability. Set 0.52 for the true size. |

The phase also sets when the Moon is up: a half Moon (0.5) sets around midnight, and the Milky Way comes out after it. North is world +Z unless `northHeading` says otherwise.

## How it works

- **Stars and Milky Way:**
  - Two equirectangular maps in celestial coordinates (pole at the top), imported as cubemaps, so there is no seam or pole pinch.
  - The script passes a rotation from world to sky, `FromToRotation(pole, up) * AngleAxis(-siderealAngle, pole)`.
  - `_StarContrast` thins out the faintest stars.
  - Twinkle is a 3D value noise in sky coordinates, so it stays on the stars as they turn. It grows towards the horizon.
- **Atmosphere:**
  - Starlight and moonlight pass through `exp(-_Extinction × airmass)`, using the Kasten and Young airmass. Stars fade and redden near the horizon, and the moonlight does the same through the script.
  - The sky is a dark blue that brightens towards the horizon, plus a blue moonlit scatter around the Moon.
  - The Moon also washes out the Milky Way (`_MoonWashout`).
- **Moon:**
  - A sphere drawn as a disc. Its near side faces the camera, and its north follows the sky's, so it tilts as it crosses.
  - It is coloured by the LROC mosaic and shaded with Lommel-Seeliger, the law behind the flat-looking full Moon.
  - It uses the LOLA relief normals, ×3 exaggerated and faded at the limb.
  - It has earthshine on the dark side and a small halo.
  - The Sun follows the clock (highest at 12:00) and is never drawn. The Moon sits its elongation east of the Sun when waxing.
  - The moonlight's intensity follows the phase (Allen's lunar phase law), its altitude and the extinction.

## Cost (estimated, not measured)

- **Pass:** one full-screen skybox pass.
  - About 4 texture reads per pixel (2 cubemaps, 2 moon maps).
  - Two value noises of 8 hashes each.
  - A few dozen arithmetic operations.
- **Memory:** about 45 MB of video memory with BC7 and mipmaps:
  - stars: cubemap, 2048 per face;
  - Milky Way: cubemap, 1024 per face;
  - Moon: 2048 × 1024 colour and 1440 × 720 normals.
- **Moonlight shadows:** URP renders the main light's shadow map every frame anyway, so moving the light adds no work. If slowly moving shadow edges shimmer, raise `lightUpdateInterval`.

None of this has been profiled.

## Evidence and limits

- **Compiled:**
  - `NightSky.cs` and `NightSkySetup.cs` compile against the pinned 6000.4.3f1 editor's UnityEngine and UnityEditor DLLs (.NET 8 SDK, the same reference set as `runtime/tools/api_compile.py`): 0 errors.
  - The only warnings are CS0649 on the serialized fields, which Unity assigns. A deliberate bad API call failed as expected.
- **Preview:** the shader and script maths were ported line for line to numpy, to set the default exposure and check the geometry. That covers the Moon's arc over the night, the phase direction, the twinkle and extinction. It is not a Unity render: no tonemapping, and the equirectangular map was sampled directly.
- **Not run:** Unity's shader compiler, the import (cubemap conversion, compression), the set-up menu, any frame in Unity and any profiling.
  - The shader is hand-written HLSL against URP 17.4's `Core.hlsl`, and has never been compiled.
  - Expect to tune the brightness settings once tonemapping and exposure are chosen.
- **Unverified:** whether Unity's latitude-longitude conversion shows the star map unmirrored. Photographic panoramas show correctly, and NASA's map is drawn the same way, as seen from inside, but this has not been checked.

## Sources and credits

Downloaded on 2026-10-19:
- **Stars and Milky Way:** *Deep Star Maps 2020*, `hiptyc_2020_8k.exr` and `milkyway_2020_4k.exr`, https://svs.gsfc.nasa.gov/4851/. Credit, as the page asks: "NASA/Goddard Space Flight Center Scientific Visualization Studio. Gaia DR2: ESA/Gaia/DPAC."
- **Moon:** *CGI Moon Kit*, `lroc_color_poles_2k.tif` and `ldem_4.tif`, https://svs.gsfc.nasa.gov/4720/. Credit: "NASA's Scientific Visualization Studio."

NASA's media are generally free to use, including commercially, with credit. The star maps also rest on ESA Gaia data, which ESA asks to be credited as above. Commercial use of the Gaia-derived map should be confirmed by the project owner before release; this is not legal advice.
