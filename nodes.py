import copy
import io
from pathlib import Path
import folder_paths
import zipfile
<<<<<<< HEAD

from .utils import *

TOOLTIP_LIMIT_OPUS_FREE = "Limit image size and steps for free generation by Opus."

=======
import json as _json
import copy as _copy

from .utils import *
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import torch
import numpy as np
from PIL import Image as PILImage

TOOLTIP_LIMIT_OPUS_FREE = "Limit image size and steps for free generation by Opus."

# ------------------------------------------------------------------
# Helper utilities
# ------------------------------------------------------------------

# Accepted canvas sizes (per CR guidance); we will letterbox/pad to one of these
ACCEPTED_CR_SIZES = [(1024, 1536), (1536, 1024), (1472, 1472)]

def _get_user_data(access_token, timeout=120, retry=3):
    """Fetches user data to check Anlas balance. Now a global helper."""
    USER_API_BASE_URL = "https://api.novelai.net"

    req_mod = requests
    if retry is not None and retry > 1:
        retries = Retry(
            total=retry,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=retries))
        req_mod = session

    response = req_mod.get(
        f"{USER_API_BASE_URL}/user/data",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=timeout
    )

    response.raise_for_status()
    return response.json()

def _choose_cr_canvas(w, h):
    """Select the accepted CR canvas size whose aspect ratio is closest to the source image."""
    aspect = w / h
    best = None
    best_diff = 9e9
    for cw, ch in ACCEPTED_CR_SIZES:
        diff = abs((cw / ch) - aspect)
        if diff < best_diff:
            best_diff = diff
            best = (cw, ch)
    return best

def pad_image_to_canvas(tensor_image, target_size):
    """
    Letterbox the given tensor image [1,H,W,C] into target_size (W,H) with black padding,
    preserving aspect ratio.
    """
    _, H, W, C = tensor_image.shape
    tw, th = target_size
    arr = (tensor_image[0].cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
    mode = "RGBA" if (C == 4) else "RGB"
    pil = PILImage.fromarray(arr)

    scale = min(tw / W, th / H)
    new_w = max(1, int(W * scale))
    new_h = max(1, int(H * scale))
    pil_resized = pil.resize((new_w, new_h), PILImage.LANCZOS)

    if mode == "RGBA":
        canvas = PILImage.new("RGBA", (tw, th), (0, 0, 0, 0))
    else:
        canvas = PILImage.new("RGB", (tw, th), (0, 0, 0))
    offset = ((tw - new_w) // 2, (th - new_h) // 2)
    canvas.paste(pil_resized, offset)

    out = np.array(canvas).astype(np.float32) / 255.0
    return torch.from_numpy(out)[None,]

# -------------------------------------------------
# Core simple prompt conversion / utility nodes
# -------------------------------------------------

>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
class PromptToNAID:
    @classmethod
    def INPUT_TYPES(s):
        return { "required": {
            "text": ("STRING", { "forceInput":True, "multiline": True, "dynamicPrompts": False,}),
            "weight_per_brace": ("FLOAT", { "default": 0.05, "min": 0.05, "max": 0.10, "step": 0.05 }),
            "syntax_mode": (["brace", "numeric"], { "default": "brace" }),
        }}

    RETURN_TYPES = ("STRING",)
    FUNCTION = "convert"
    CATEGORY = "NovelAI/utils"
    def convert(self, text, weight_per_brace, syntax_mode):
        nai_prompt = prompt_to_nai(text, weight_per_brace, syntax_mode)
        return (nai_prompt,)

class ImageToNAIMask:
    @classmethod
    def INPUT_TYPES(s):
        return { "required": { "image": ("IMAGE",) } }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "convert"
    CATEGORY = "NovelAI/utils"
    def convert(self, image):
        s = resize_to_naimask(image)
        return (s,)

class ModelOption:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
<<<<<<< HEAD
                "model": (["nai-diffusion-2", "nai-diffusion-furry-3", "nai-diffusion-3", "nai-diffusion-4-curated-preview", "nai-diffusion-4-full", "nai-diffusion-4-5-curated", "nai-diffusion-4-5-full"], { "default": "nai-diffusion-4-5-full" }),
=======
                "model": ([
                    "nai-diffusion-2",
                    "nai-diffusion-furry-3",
                    "nai-diffusion-3",
                    "nai-diffusion-4-curated-preview",
                    "nai-diffusion-4-full",
                    "nai-diffusion-4-5-curated",
                    "nai-diffusion-4-5-full"
                ], { "default": "nai-diffusion-4-5-full" }),
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
            },
            "optional": { "option": ("NAID_OPTION",) },
        }

    RETURN_TYPES = ("NAID_OPTION",)
    FUNCTION = "set_option"
    CATEGORY = "NovelAI"
    def set_option(self, model, option=None):
        option = copy.deepcopy(option) if option else {}
        option["model"] = model
        return (option,)

class Img2ImgOption:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "strength": ("FLOAT", { "default": 0.70, "min": 0.01, "max": 0.99, "step": 0.01, "display": "number" }),
                "noise": ("FLOAT", { "default": 0.00, "min": 0.00, "max": 0.99, "step": 0.02, "display": "number" }),
            },
        }

    RETURN_TYPES = ("NAID_OPTION",)
    FUNCTION = "set_option"
    CATEGORY = "NovelAI"
    def set_option(self, image, strength, noise):
        option = {}
        option["img2img"] = (image, strength, noise)
        return (option,)

class InpaintingOption:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("IMAGE",),
                "add_original_image": ("BOOLEAN", { "default": True }),
            },
        }

    RETURN_TYPES = ("NAID_OPTION",)
    FUNCTION = "set_option"
    CATEGORY = "NovelAI"
    def set_option(self, image, mask, add_original_image):
        option = {}
        option["infill"] = (image, mask, add_original_image)
        return (option,)

class VibeTransferOption:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "information_extracted": ("FLOAT", { "default": 1.0, "min": 0.01, "max": 1.0, "step": 0.01, "display": "number" }),
                "strength": ("FLOAT", { "default": 0.6, "min": 0.01, "max": 1.0, "step": 0.01, "display": "number" }),
            },
            "optional": { "option": ("NAID_OPTION",) },
        }
    RETURN_TYPES = ("NAID_OPTION",)
    FUNCTION = "set_option"
    CATEGORY = "NovelAI"
    def set_option(self, image, information_extracted, strength, option=None):
        option = copy.deepcopy(option) if option else {}
        if "vibe" not in option:
            option["vibe"] = []
<<<<<<< HEAD

=======
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
        option["vibe"].append((image, information_extracted, strength))
        return (option,)

class NetworkOption:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ignore_errors": ("BOOLEAN", { "default": True }),
                "timeout_sec": ("INT", { "default": 120, "min": 30, "max": 3000, "step": 1, "display": "number" }),
                "retry": ("INT", { "default": 3, "min": 1, "max": 100, "step": 1, "display": "number" }),
            },
            "optional": { "option": ("NAID_OPTION",) },
        }
    RETURN_TYPES = ("NAID_OPTION",)
    FUNCTION = "set_option"
    CATEGORY = "NovelAI"
    def set_option(self, ignore_errors, timeout_sec, retry, option=None):
        option = copy.deepcopy(option) if option else {}
        option["ignore_errors"] = ignore_errors
        option["timeout"] = timeout_sec
        option["retry"] = retry
        return (option,)

<<<<<<< HEAD
=======
# -------------------------------------------------
# Character Reference (Single Image)
# -------------------------------------------------

class CharacterReferenceOption:
    INFO_EXTRACT_DEFAULT = 1.0
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "style_aware": ("BOOLEAN", {"default": True, "tooltip": "Copy style along with identity."}),
                "fidelity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "display": "number", "tooltip": "How strictly to match the character (and style if enabled)."}),
            },
            "optional": {"option": ("NAID_OPTION",),}
        }
    RETURN_TYPES = ("NAID_OPTION",)
    FUNCTION = "set_option"
    CATEGORY = "NovelAI"
    def set_option(self, image, style_aware, fidelity, option=None):
        option = copy.deepcopy(option) if option else {}
        fidelity = max(0.0, min(1.0, fidelity))
        option["character_reference_single"] = {
            "image": image,
            "style_aware": style_aware,
            "fidelity": fidelity,
            "info_extracted": self.INFO_EXTRACT_DEFAULT,
        }
        return (option,)

# -------------------------------------------------
# Generation Node
# -------------------------------------------------
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07

class GenerateNAID:
    def __init__(self):
        self.access_token = get_access_token()
        self.output_dir = folder_paths.get_output_directory()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }),
                "width": ("INT", { "default": 832, "min": 64, "max": 1600, "step": 64, "display": "number" }),
                "height": ("INT", { "default": 1216, "min": 64, "max": 1600, "step": 64, "display": "number" }),
                "positive": ("STRING", { "default": ", best quality, amazing quality, very aesthetic, absurdres", "multiline": True, "dynamicPrompts": False }),
                "negative": ("STRING", { "default": "lowres", "multiline": True, "dynamicPrompts": False }),
                "steps": ("INT", { "default": 28, "min": 0, "max": 50, "step": 1, "display": "number" }),
                "cfg": ("FLOAT", { "default": 5.0, "min": 0.0, "max": 10.0, "step": 0.1, "display": "number" }),
                "variety" : ("BOOLEAN", { "default": False }),
                "decrisper": ("BOOLEAN", { "default": False }),
                "smea": (["none", "SMEA", "SMEA+DYN"], { "default": "none" }),
                "sampler": (["k_euler", "k_euler_ancestral", "k_dpmpp_2s_ancestral", "k_dpmpp_2m_sde", "k_dpmpp_2m", "k_dpmpp_sde", "ddim"], { "default": "k_euler" }),
                "scheduler": (["native", "karras", "exponential", "polyexponential"], { "default": "native" }),
                "seed": ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
                "uncond_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 1.5, "step": 0.05, "display": "number" }),
                "cfg_rescale": ("FLOAT", { "default": 0.0, "min": 0.0, "max": 1.0, "step": 0.02, "display": "number" }),
                "keep_alpha": ("BOOLEAN", { "default": True, "tooltip": "Disable to further process output images locally" }),
            },
            "optional": { "option": ("NAID_OPTION",) },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    CATEGORY = "NovelAI"

<<<<<<< HEAD
    def generate(self, limit_opus_free, width, height, positive, negative, steps, cfg, decrisper, variety, smea, sampler, scheduler, seed, uncond_scale, cfg_rescale, keep_alpha, option=None):
        width, height = calculate_resolution(width*height, (width, height))

        # ref. novelai_api.ImagePreset
        params = {
            "params_version": 1,
            "width": width,
            "height": height,
            "scale": cfg,
            "sampler": sampler,
            "steps": steps,
            "seed": seed,
            "n_samples": 1,
            "ucPreset": 3,
            "qualityToggle": False,
            "sm": (smea == "SMEA" or smea == "SMEA+DYN") and sampler != "ddim",
            "sm_dyn": smea == "SMEA+DYN" and sampler != "ddim",
            "dynamic_thresholding": decrisper,
            "skip_cfg_above_sigma": None,
            "controlnet_strength": 1.0,
            "legacy": False,
            "add_original_image": False,
            "cfg_rescale": cfg_rescale,
            "noise_schedule": scheduler,
            "legacy_v3_extend": False,
            "uncond_scale": uncond_scale,
            "negative_prompt": negative,
            "prompt": positive,
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": [],
            "extra_noise_seed": seed,
            "v4_prompt": {
                "use_coords": False,
                "use_order": False,
                "caption": {
                    "base_caption": positive,
                    "char_captions": []
                }
            },
            "v4_negative_prompt": {
                "use_coords": False,
                "use_order": False,
                "caption": {
                    "base_caption": negative,
                    "char_captions": []
                }
            }
        }
=======
    @staticmethod
    def _post_image(access_token, prompt, model, action, parameters, timeout=None, retry=None):
        data = {"input": prompt, "model": model, "action": action, "parameters": parameters}

        req_mod = requests
        if retry is not None and retry > 1:
            retries = Retry(total=retry, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["POST"])
            session = requests.Session()
            session.mount("https://", HTTPAdapter(max_retries=retries))
            req_mod = session

        response = req_mod.post(f"{BASE_URL}/ai/generate-image", json=data, headers={"Authorization": f"Bearer {access_token}"}, timeout=timeout)

        if response.status_code >= 400:
            print("RAW ERROR STATUS:", response.status_code)
            print("RAW ERROR BODY:", response.text)
            try:
                dbg = _copy.deepcopy(data)
                p = dbg.get("parameters", {})
                if "director_reference_images" in p: p["director_reference_images"] = [i[:60] + "...(trunc)" for i in p["director_reference_images"]]
                if "reference_image_multiple" in p: p["reference_image_multiple"] = [i[:60] + "...(trunc)" for i in p["reference_image_multiple"]]
                dbg["parameters"] = p
                print("OUTGOING PAYLOAD (sanitized):", _json.dumps(dbg)[:2000])
            except Exception as e:
                print("Payload debug failed:", e)

        response.raise_for_status()
        return response.content

    def generate(self, limit_opus_free, width, height, positive, negative,
                 steps, cfg, decrisper, variety, smea, sampler, scheduler,
                 seed, uncond_scale, cfg_rescale, keep_alpha, option=None):

        width, height = calculate_resolution(width * height, (width, height))

        params = {
            "params_version": 1, "width": width, "height": height, "scale": cfg, "sampler": sampler, "steps": steps,
            "seed": seed, "n_samples": 1, "ucPreset": 3, "qualityToggle": False,
            "sm": (smea == "SMEA" or smea == "SMEA+DYN") and sampler != "ddim",
            "sm_dyn": (smea == "SMEA+DYN") and sampler != "ddim",
            "dynamic_thresholding": decrisper, "controlnet_strength": 1.0, "legacy": False, "add_original_image": False,
            "cfg_rescale": cfg_rescale, "noise_schedule": scheduler, "legacy_v3_extend": False,
            "uncond_scale": uncond_scale, "negative_prompt": negative, "prompt": positive,
            "reference_image_multiple": [], "reference_information_extracted_multiple": [], "reference_strength_multiple": [],
            "extra_noise_seed": seed,
            "v4_prompt": {"use_coords": False, "use_order": False, "caption": {"base_caption": positive, "char_captions": []}},
            "v4_negative_prompt": {"use_coords": False, "use_order": False, "caption": {"base_caption": negative, "char_captions": []}}
        }

>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
        model = "nai-diffusion-4-5-full"
        action = "generate"

        if sampler == "k_euler_ancestral" and scheduler != "native":
            params["deliberate_euler_ancestral_bug"] = False
            params["prefer_brownian"] = True

        if option:
            if "img2img" in option:
                action = "img2img"
                image, strength, noise = option["img2img"]
                params["image"] = image_to_base64(resize_image(image, (width, height)))
                params["strength"] = strength
                params["noise"] = noise
            elif "infill" in option:
                action = "infill"
                image, mask, add_original_image = option["infill"]
                params["image"] = image_to_base64(resize_image(image, (width, height)))
                params["mask"] = naimask_to_base64(resize_to_naimask(mask, (width, height), "4" in model))
                params["add_original_image"] = add_original_image

            if "vibe" in option:
                for vibe in option["vibe"]:
<<<<<<< HEAD
                    image, information_extracted, strength = vibe
                    params["reference_image_multiple"].append(image_to_base64(resize_image(image, (width, height))))
                    params["reference_information_extracted_multiple"].append(information_extracted)
                    params["reference_strength_multiple"].append(strength)

            if "model" in option:
                model = option["model"]

            # Handle V4 options
            if "v4_prompt" in option:
                opt_v4 = option["v4_prompt"]
                if "caption" in opt_v4 and "char_captions" in opt_v4["caption"]:
                    params["v4_prompt"]["caption"]["char_captions"].extend(opt_v4["caption"]["char_captions"])
                if "use_coords" in opt_v4:
                    params["v4_prompt"]["use_coords"] = opt_v4["use_coords"]
                if "use_order" in opt_v4:
                    params["v4_prompt"]["use_order"] = opt_v4["use_order"]

            if "v4_negative_prompt" in option:
                opt_neg_v4 = option["v4_negative_prompt"]
                if "caption" in opt_neg_v4 and "char_captions" in opt_neg_v4["caption"]:
                    params["v4_negative_prompt"]["caption"]["char_captions"].extend(
                        opt_neg_v4["caption"]["char_captions"])
                if "use_coords" in opt_neg_v4:
                    params["v4_negative_prompt"]["use_coords"] = opt_neg_v4["use_coords"]
                if "use_order" in opt_neg_v4:
                    params["v4_negative_prompt"]["use_order"] = opt_neg_v4["use_order"]

        timeout = option["timeout"] if option and "timeout" in option else None
        retry = option["retry"] if option and "retry" in option else None

        if limit_opus_free:
            pixel_limit = 1024*1024
            if width * height > pixel_limit:
                max_width, max_height = calculate_resolution(pixel_limit, (width, height))
                params["width"] = max_width
                params["height"] = max_height
            if steps > 28:
                params["steps"] = 28

        if variety:
            params["skip_cfg_above_sigma"] = calculate_skip_cfg_above_sigma(params["width"], params["height"])

        if sampler == "ddim" and model not in ("nai-diffusion-2"):
            params["sampler"] = "ddim_v3"

        if action == "infill" and model not in ("nai-diffusion-2"):
            model = f"{model}-inpainting"

        image = blank_image()
        try:
            zipped_bytes = generate_image(self.access_token, positive, model, action, params, timeout, retry)
            zipped = zipfile.ZipFile(io.BytesIO(zipped_bytes))
            image_bytes = zipped.read(zipped.infolist()[0]) # only support one n_samples

            ## save original png to comfy output dir
            # full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path("NAI_autosave", self.output_dir)
            # file = f"{filename}_{counter:05}_.png"
            # d = Path(full_output_folder)
            # d.mkdir(exist_ok=True)
            # (d / file).write_bytes(image_bytes)

            image = bytes_to_image(image_bytes, keep_alpha)
        except Exception as e:
            if "ignore_errors" in option and option["ignore_errors"]:
                print("ignore error:", e)
            else:
                raise e

        return (image,)


def base_augment(access_token, output_dir, limit_opus_free, ignore_errors, req_type, image, options=None):
    image = image.movedim(-1, 1)
    w, h = (image.shape[3], image.shape[2])
    image = image.movedim(1, -1)

    if limit_opus_free:
        pixel_limit = 1024 * 1024
        if w * h > pixel_limit:
            w, h = calculate_resolution(pixel_limit, (w, h))
    base64_image = image_to_base64(resize_image(image, (w, h)))
    result_image = blank_image()
    try:
        # Build request based on NAI v4 API spec
        request = {
            "image": base64_image,
            "req_type": req_type,
            "width": w,
            "height": h
        }

        # Add optional parameters if provided
        if options:
            if "defry" in options:
                request["defry"] = options["defry"]
            if "prompt" in options:
                request["prompt"] = options["prompt"]

        zipped_bytes = augment_image(access_token, req_type, w, h, base64_image, options=options)
        zipped = zipfile.ZipFile(io.BytesIO(zipped_bytes))
        image_bytes = zipped.read(zipped.infolist()[0]) # only support one n_samples

        ## save original png to comfy output dir
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path("NAI_autosave", output_dir)
=======
                    vimg, information_extracted, strength = vibe
                    params["reference_image_multiple"].append(image_to_base64(resize_image(vimg, (width, height))))
                    params["reference_information_extracted_multiple"].append(information_extracted)
                    params["reference_strength_multiple"].append(strength)

            if "model" in option: model = option["model"]
            if "v4_prompt" in option: params["v4_prompt"].update(option["v4_prompt"])

            if "character_reference_single" in option:
                ref = option["character_reference_single"]
                base_caption = "character&style" if ref["style_aware"] else "character"
                ref_img = ref["image"]
                _, h_raw, w_raw, _ = ref_img.shape
                canvas_w, canvas_h = _choose_cr_canvas(w_raw, h_raw)
                padded = pad_image_to_canvas(ref_img, (canvas_w, canvas_h))
                params["director_reference_images"] = [image_to_base64(padded)]
                params["director_reference_descriptions"] = [{"use_coords": False, "use_order": False, "legacy_uc": False, "caption": {"base_caption": base_caption, "char_captions": []}}]
                params["director_reference_strength_values"] = [1.0]
                params["director_reference_secondary_strength_values"] = [1.0 - ref["fidelity"]]
                params["director_reference_information_extracted"] = [1.0]

        timeout = option.get("timeout", 120) if option else 120
        retry = option.get("retry", 3) if option else 3

        if limit_opus_free:
            pixel_limit = 1024 * 1024
            if width * height > pixel_limit:
                params["width"], params["height"] = calculate_resolution(pixel_limit, (width, height))
            if steps > 28: params["steps"] = 28

        if variety: params["skip_cfg_above_sigma"] = calculate_skip_cfg_above_sigma(params["width"], params["height"])
        if sampler == "ddim" and "nai-diffusion-2" not in model: params["sampler"] = "ddim_v3"
        if action == "infill" and "nai-diffusion-2" not in model: model = f"{model}-inpainting"
        
        start_anlas = None
        try:
            user_data = _get_user_data(self.access_token, timeout, retry)
            start_anlas = user_data.get("subscription", {}).get("trainingStepsLeft")
            if start_anlas is not None: print(f"[NovelAI] Anlas (pre-gen): {start_anlas}")
        except Exception as e: print(f"[NovelAI] Anlas tracking failed (pre-gen): {e}")

        image = blank_image()
        try:
            zipped_bytes = self._post_image(self.access_token, positive, model, action, params, timeout, retry)
            with zipfile.ZipFile(io.BytesIO(zipped_bytes)) as zipped:
                image_bytes = zipped.read(zipped.infolist()[0])

            full_output_folder, filename, counter, _, _ = folder_paths.get_save_image_path("NAI_autosave", self.output_dir)
            file = f"{filename}_{counter:05}_.png"
            d = Path(full_output_folder)
            d.mkdir(exist_ok=True)
            (d / file).write_bytes(image_bytes)
            
            if start_anlas is not None:
                try:
                    user_data_final = _get_user_data(self.access_token, timeout, retry)
                    final_anlas = user_data_final.get("subscription", {}).get("trainingStepsLeft")
                    if final_anlas is not None:
                        print(f"[NovelAI] Generation cost: {start_anlas - final_anlas} Anlas")
                        print(f"[NovelAI] Anlas (post-gen): {final_anlas}")
                except Exception as e: print(f"[NovelAI] Anlas tracking failed (post-gen): {e}")

            image = bytes_to_image(image_bytes, keep_alpha)
        except Exception as e:
            if option and option.get("ignore_errors", False): print("ignore error:", e)
            else: raise e

        return (image,)

# -------------------------------------------------
# Director Tool Augment Nodes
# -------------------------------------------------

def base_augment(access_token, output_dir, limit_opus_free, ignore_errors, req_type, image, options=None):
    w, h = image.shape[2], image.shape[1]
    if limit_opus_free and w * h > 1024 * 1024:
        w, h = calculate_resolution(1024 * 1024, (w, h))
            
    start_anlas = None
    try:
        user_data = _get_user_data(access_token)
        start_anlas = user_data.get("subscription", {}).get("trainingStepsLeft")
        if start_anlas is not None: print(f"[NovelAI] Anlas (pre-augment): {start_anlas}")
    except Exception as e: print(f"[NovelAI] Anlas tracking failed (pre-augment): {e}")
            
    base64_image = image_to_base64(resize_image(image, (w, h)))
    result_image = blank_image()
    try:
        zipped_bytes = augment_image(access_token, req_type, w, h, base64_image, options=options)
        with zipfile.ZipFile(io.BytesIO(zipped_bytes)) as zipped:
            image_bytes = zipped.read(zipped.infolist()[0])

        full_output_folder, filename, counter, _, _ = folder_paths.get_save_image_path("NAI_autosave", output_dir)
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
        file = f"{filename}_{counter:05}_.png"
        d = Path(full_output_folder)
        d.mkdir(exist_ok=True)
        (d / file).write_bytes(image_bytes)

<<<<<<< HEAD
        result_image = bytes_to_image(image_bytes)
    except Exception as e:
        if ignore_errors:
            print("ignore error:", e)
        else:
            raise e
=======
        if start_anlas is not None:
            try:
                user_data_final = _get_user_data(access_token)
                final_anlas = user_data_final.get("subscription", {}).get("trainingStepsLeft")
                if final_anlas is not None:
                    print(f"[NovelAI] Augment cost: {start_anlas - final_anlas} Anlas")
                    print(f"[NovelAI] Anlas (post-augment): {final_anlas}")
            except Exception as e: print(f"[NovelAI] Anlas tracking failed (post-augment): {e}")

        result_image = bytes_to_image(image_bytes)
    except Exception as e:
        if ignore_errors: print("ignore error:", e)
        else: raise e
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07

    return (result_image,)

class RemoveBGAugment:
    def __init__(self):
        self.access_token = get_access_token()
        self.output_dir = folder_paths.get_output_directory()
    @classmethod
    def INPUT_TYPES(s):
<<<<<<< HEAD
        return {
            "required": {
                "image": ("IMAGE",),
                "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }),
                "ignore_errors": ("BOOLEAN", { "default": False }),
            },
        }
=======
        return {"required": {"image": ("IMAGE",), "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }), "ignore_errors": ("BOOLEAN", { "default": False }),}}
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "augment"
    CATEGORY = "NovelAI/director_tools"
    def augment(self, image, limit_opus_free, ignore_errors):
        return base_augment(self.access_token, self.output_dir, limit_opus_free, ignore_errors, "bg-removal", image)

class LineArtAugment:
    def __init__(self):
        self.access_token = get_access_token()
        self.output_dir = folder_paths.get_output_directory()
    @classmethod
    def INPUT_TYPES(s):
<<<<<<< HEAD
        return {
            "required": {
                "image": ("IMAGE",),
                "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }),
                "ignore_errors": ("BOOLEAN", { "default": False }),
            },
        }
=======
        return {"required": {"image": ("IMAGE",), "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }), "ignore_errors": ("BOOLEAN", { "default": False }),}}
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "augment"
    CATEGORY = "NovelAI/director_tools"
    def augment(self, image, limit_opus_free, ignore_errors):
        return base_augment(self.access_token, self.output_dir, limit_opus_free, ignore_errors, "lineart", image)

class SketchAugment:
    def __init__(self):
        self.access_token = get_access_token()
        self.output_dir = folder_paths.get_output_directory()
    @classmethod
    def INPUT_TYPES(s):
<<<<<<< HEAD
        return {
            "required": {
                "image": ("IMAGE",),
                "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }),
                "ignore_errors": ("BOOLEAN", { "default": False }),
            },
        }
=======
        return {"required": {"image": ("IMAGE",), "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }), "ignore_errors": ("BOOLEAN", { "default": False }),}}
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "augment"
    CATEGORY = "NovelAI/director_tools"
    def augment(self, image, limit_opus_free, ignore_errors):
        return base_augment(self.access_token, self.output_dir, limit_opus_free, ignore_errors, "sketch", image)

class ColorizeAugment:
    def __init__(self):
        self.access_token = get_access_token()
        self.output_dir = folder_paths.get_output_directory()
    @classmethod
    def INPUT_TYPES(s):
<<<<<<< HEAD
        return {
            "required": {
                "image": ("IMAGE",),
                "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }),
                "ignore_errors": ("BOOLEAN", { "default": False }),
                "defry": ("INT", { "default": 0, "min": 0, "max": 5, "step": 1, "display": "number" }),
                "prompt": ("STRING", { "default": "", "multiline": True, "dynamicPrompts": False }),
            },
        }
=======
        return {"required": {"image": ("IMAGE",), "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }), "ignore_errors": ("BOOLEAN", { "default": False }), "defry": ("INT", { "default": 0, "min": 0, "max": 5, "step": 1, "display": "number" }), "prompt": ("STRING", { "default": "", "multiline": True, "dynamicPrompts": False }),}}
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "augment"
    CATEGORY = "NovelAI/director_tools"
    def augment(self, image, limit_opus_free, ignore_errors, defry, prompt):
        return base_augment(self.access_token, self.output_dir, limit_opus_free, ignore_errors, "colorize", image, options={ "defry": defry, "prompt": prompt })

class EmotionAugment:
    def __init__(self):
        self.access_token = get_access_token()
        self.output_dir = folder_paths.get_output_directory()
<<<<<<< HEAD

    strength_list = ["normal", "slightly_weak", "weak", "even_weaker", "very_weak", "weakest"]
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }),
                "ignore_errors": ("BOOLEAN", { "default": False }),
                "mood": (["neutral", "happy", "sad", "angry", "scared",
                     "surprised", "tired", "excited", "nervous", "thinking",
                     "confused", "shy", "disgusted", "smug", "bored",
                     "laughing", "irritated", "aroused", "embarrassed", "worried",
                     "love", "determined", "hurt", "playful"], { "default": "neutral" }),
                "strength": (s.strength_list, { "default": "normal" }),
                "prompt": ("STRING", { "default": "", "multiline": True, "dynamicPrompts": False }),
            },
        }
=======
    strength_list = ["normal", "slightly_weak", "weak", "even_weaker", "very_weak", "weakest"]
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"image": ("IMAGE",), "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }), "ignore_errors": ("BOOLEAN", { "default": False }), "mood": (["neutral", "happy", "sad", "angry", "scared", "surprised", "tired", "excited", "nervous", "thinking", "confused", "shy", "disgusted", "smug", "bored", "laughing", "irritated", "aroused", "embarrassed", "worried", "love", "determined", "hurt", "playful"], { "default": "neutral" }), "strength": (s.strength_list, { "default": "normal" }), "prompt": ("STRING", { "default": "", "multiline": True, "dynamicPrompts": False }),}}
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "augment"
    CATEGORY = "NovelAI/director_tools"
    def augment(self, image, limit_opus_free, ignore_errors, mood, strength, prompt):
        prompt = f"{mood};;{prompt}"
        defry = EmotionAugment.strength_list.index(strength)
        return base_augment(self.access_token, self.output_dir, limit_opus_free, ignore_errors, "emotion", image, options={ "defry": defry, "prompt": prompt })

class DeclutterAugment:
    def __init__(self):
        self.access_token = get_access_token()
        self.output_dir = folder_paths.get_output_directory()
    @classmethod
    def INPUT_TYPES(s):
<<<<<<< HEAD
        return {
            "required": {
                "image": ("IMAGE",),
                "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }),
                "ignore_errors": ("BOOLEAN", { "default": False }),
            },
        }
=======
        return {"required": {"image": ("IMAGE",), "limit_opus_free": ("BOOLEAN", { "default": True, "tooltip": TOOLTIP_LIMIT_OPUS_FREE }), "ignore_errors": ("BOOLEAN", { "default": False }),}}
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "augment"
    CATEGORY = "NovelAI/director_tools"
    def augment(self, image, limit_opus_free, ignore_errors):
        return base_augment(self.access_token, self.output_dir, limit_opus_free, ignore_errors, "declutter", image)
<<<<<<< HEAD
class V4BasePrompt:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_caption": ("STRING", { "multiline": True }),
            }
        }

    RETURN_TYPES = ("STRING",)  # Changed from NAID_OPTION to STRING
    FUNCTION = "convert"        # Changed from set_option to convert
    CATEGORY = "NovelAI/v4"
    def convert(self, base_caption):
        return (base_caption,)  # Simply returns the caption as a string

"""class V4PromptConfig:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "use_coords": ("BOOLEAN", { "default": False }),
                "use_order": ("BOOLEAN", { "default": False }),
            },
            "optional": { "option": ("NAID_OPTION",) },
        }

    RETURN_TYPES = ("NAID_OPTION",)
    FUNCTION = "set_option"
    CATEGORY = "NovelAI/v4"
    def set_option(self, use_coords, use_order, option=None):
        option = copy.deepcopy(option) if option else {}
        if "v4_prompt" not in option:
            option["v4_prompt"] = {}
        option["v4_prompt"]["use_coords"] = use_coords
        option["v4_prompt"]["use_order"] = use_order
        return (option,)

class V4CharacterCaption:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "char_caption": ("STRING", { "multiline": True }),
                "x": ("FLOAT", { "default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01 }),
                "y": ("FLOAT", { "default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01 }),
            },
            "optional": { "option": ("NAID_OPTION",) },
        }

    RETURN_TYPES = ("NAID_OPTION",)
    FUNCTION = "set_option"
    CATEGORY = "NovelAI/v4"
    def set_option(self, char_caption, x, y, option=None):
        option = copy.deepcopy(option) if option else {}
        if "v4_prompt" not in option:
            option["v4_prompt"] = {
                "caption": {
                    "base_caption": "",
                    "char_captions": []
                }
            }
        
        char_caption_obj = {
            "char_caption": char_caption,
            "centers": [{"x": x, "y": y}]
        }
        
        option["v4_prompt"]["caption"]["char_captions"].append(char_caption_obj)
        return (option,)
"""
class V4NegativePrompt:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "negative_caption": ("STRING", { "multiline": True }),
            }
        }

=======

# -------------------------------------------------
# Anlas Tracker (Visual Node)
# -------------------------------------------------

class AnlasTrackerNAID:
    def __init__(self):
        self.access_token = get_access_token()
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": { "trigger": ("*",) } # Allows chaining to control execution order
        }

    RETURN_TYPES = ("INT", "STRING",)
    RETURN_NAMES = ("anlas_int", "anlas_string",)
    FUNCTION = "get_anlas"
    CATEGORY = "NovelAI/utils"
    
    def get_anlas(self, trigger=None):
        anlas_count = 0
        try:
            user_data = _get_user_data(self.access_token)
            anlas_count = user_data.get("subscription", {}).get("trainingStepsLeft", 0)
            print(f"[NovelAI] Current Anlas Balance: {anlas_count}")
        except Exception as e:
            print(f"[NovelAI] Failed to fetch Anlas balance: {e}")
            return (0, "Error fetching Anlas")
            
        return (anlas_count, f"{anlas_count} Anlas")

# -------------------------------------------------
# V4 Base / Negative Prompt nodes
# -------------------------------------------------

class V4BasePrompt:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"base_caption": ("STRING", { "multiline": True }),}}
    RETURN_TYPES = ("STRING",)
    FUNCTION = "convert"
    CATEGORY = "NovelAI/v4"
    def convert(self, base_caption):
        return (base_caption,)

class V4NegativePrompt:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"negative_caption": ("STRING", { "multiline": True }),}}
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
    RETURN_TYPES = ("STRING",)
    FUNCTION = "convert"
    CATEGORY = "NovelAI/v4"
    def convert(self, negative_caption):
        return (negative_caption,)

<<<<<<< HEAD

class V4CharacterPromptOption:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "char_caption": ("STRING", {"multiline": True, "tooltip": "해당 캐릭터의 포지티브 프롬프트"}),
                "negative_char_caption": ("STRING",
                                          {"multiline": True, "default": "", "tooltip": "해당 캐릭터의 네거티브 프롬프트 (선택사항)"}),
                "center_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "display": "number"}),
                "center_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "display": "number"}),
            },
            "optional": {"option": ("NAID_OPTION",)},
        }

    RETURN_TYPES = ("NAID_OPTION",)
    FUNCTION = "set_option"
    CATEGORY = "NovelAI/v4"

    def set_option(self, char_caption, negative_char_caption, center_x, center_y, option=None):
        # 기존 옵션 보존을 위해 깊은 복사
        option = copy.deepcopy(option) if option else {}

        # 포지티브 캐릭터 프롬프트가 비어있지 않은 경우 처리
        if char_caption.strip():
            if "v4_prompt" not in option:
                option["v4_prompt"] = {"caption": {"char_captions": []}, "use_coords": True, "use_order": True}

            option["v4_prompt"]["caption"]["char_captions"].append({
                "char_caption": char_caption,
                "centers": [{"x": center_x, "y": center_y}]
            })
            option["v4_prompt"]["use_coords"] = True
            option["v4_prompt"]["use_order"] = True

        # 네거티브 캐릭터 프롬프트가 비어있지 않은 경우 처리
        if negative_char_caption.strip():
            if "v4_negative_prompt" not in option:
                option["v4_negative_prompt"] = {"caption": {"char_captions": []}, "use_coords": True, "use_order": True}

            option["v4_negative_prompt"]["caption"]["char_captions"].append({
                "char_caption": negative_char_caption,
                "centers": [{"x": center_x, "y": center_y}]
            })
            option["v4_negative_prompt"]["use_coords"] = True
            option["v4_negative_prompt"]["use_order"] = True

        return (option,)

=======
# -------------------------------------------------
# Registration
# -------------------------------------------------
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07

NODE_CLASS_MAPPINGS = {
    "GenerateNAID": GenerateNAID,
    "ModelOptionNAID": ModelOption,
    "Img2ImgOptionNAID": Img2ImgOption,
    "InpaintingOptionNAID": InpaintingOption,
    "VibeTransferOptionNAID": VibeTransferOption,
    "NetworkOptionNAID": NetworkOption,
<<<<<<< HEAD
=======
    "CharacterReferenceOptionNAID": CharacterReferenceOption,
    "AnlasTrackerNAID": AnlasTrackerNAID, # New node
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
    "MaskImageToNAID": ImageToNAIMask,
    "PromptToNAID": PromptToNAID,
    "RemoveBGNAID": RemoveBGAugment,
    "LineArtNAID": LineArtAugment,
    "SketchNAID": SketchAugment,
    "ColorizeNAID": ColorizeAugment,
    "EmotionNAID": EmotionAugment,
    "DeclutterNAID": DeclutterAugment,
    "V4BasePrompt": V4BasePrompt,
    "V4NegativePrompt": V4NegativePrompt,
<<<<<<< HEAD
    "V4CharacterPromptOptionNAID": V4CharacterPromptOption,
=======
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GenerateNAID": "Generate ✒️🅝🅐🅘",
    "ModelOptionNAID": "ModelOption ✒️🅝🅐🅘",
    "Img2ImgOptionNAID": "Img2ImgOption ✒️🅝🅐🅘",
    "InpaintingOptionNAID": "InpaintingOption ✒️🅝🅐🅘",
    "VibeTransferOptionNAID": "VibeTransferOption ✒️🅝🅐🅘",
    "NetworkOptionNAID": "NetworkOption ✒️🅝🅐🅘",
<<<<<<< HEAD
=======
    "CharacterReferenceOptionNAID": "Character Reference ✒️🅝🅐🅘",
    "AnlasTrackerNAID": "Anlas Tracker ✒️🅝🅐🅘", # New node
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
    "MaskImageToNAID": "Convert Mask Image ✒️🅝🅐🅘",
    "PromptToNAID": "Convert Prompt ✒️🅝🅐🅘",
    "RemoveBGNAID": "Remove BG ✒️🅝🅐🅘",
    "LineArtNAID": "LineArt ✒️🅝🅐🅘",
    "SketchNAID": "Sketch ✒️🅝🅐🅘",
    "ColorizeNAID": "Colorize ✒️🅝🅐🅘",
    "EmotionNAID": "Emotion ✒️🅝🅐🅘",
    "DeclutterNAID": "Declutter ✒️🅝🅐🅘",
    "V4BasePrompt": "V4 Base Prompt ✒️🅝🅐🅘",
    "V4NegativePrompt": "V4 Negative Prompt ✒️🅝🅐🅘",
<<<<<<< HEAD
    "V4CharacterPromptOptionNAID": "V4 Character Prompt ✒️🅝🅐🅘",
=======
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
}
