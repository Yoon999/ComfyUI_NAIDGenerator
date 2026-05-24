# ComfyUI_NAIDGenerator

<<<<<<< HEAD
A [ComfyUI](https://github.com/comfyanonymous/ComfyUI) extension for generating image via NovelAI API.
=======
A [ComfyUI](https://github.com/comfyanonymous/ComfyUI) extension for generating images via the NovelAI API.
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07

## Installation

- `git clone https://github.com/bedovyy/ComfyUI_NAIDGenerator` into the `custom_nodes` directory.
- or 'Install via Git URL' from [Comfyui Manager](https://github.com/ltdrdata/ComfyUI-Manager)

## Setting up NAI account

<<<<<<< HEAD
Before using the nodes, you should set NAI_ACCESS_TOKEN on `ComfyUI/.env` file.

```
NAI_ACCESS_TOKEN=<ACCESS_TOKEN>
```

You can get persistent API token by **User Settings > Account > Get Persistent API Token** on NovelAI webpage.

Otherwise, you can get access token which is valid for 30 days using [novelai-api](https://github.com/Aedial/novelai-api).

## Usage

The nodes are located at `NovelAI` category.
=======
Before using the nodes, you should set `NAI_ACCESS_TOKEN` in a `.env` file located in your main `ComfyUI` directory.

`ComfyUI/.env`
```
NAI_ACCESS_TOKEN=<YOUR_ACCESS_TOKEN>
```

You can get a persistent API token by navigating to **User Settings > Account > Get Persistent API Token** on the NovelAI website.

Otherwise, you can get an access token which is valid for 30 days using [novelai-api](https://github.com/Aedial/novelai-api).

## Usage

The nodes are located in the `NovelAI` category.
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07

![image](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/8ab1ecc0-2ba8-4e38-8810-727e50a20923)

### Txt2img

<<<<<<< HEAD
Simply connect `GenerateNAID` node and `SaveImage` node.

![generate](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/1328896d-7d4b-4d47-8ec2-d1c4e8e2561c)

Note that all generated images via `GeneratedNAID` node are saved as `output/NAI_autosave_12345_.png` for keeping original metadata.

### Img2img

Connect `Img2ImgOptionNAID` node to `GenerateNAID` node and put original image.

![image](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/15ff8961-4f6b-4f23-86bf-34b86ace45c0)

Note that width and height of the source image will be resized to generation size.

### Inpainting

Connect `InpaintingOptionNAID` node to `GenerateNAID` node and put original image and mask image.

![image](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/5ed1ad77-b90e-46be-8c37-9a5ee0935a3d)

Note that both source image and mask will be resized fit to generation size.

(You don't need `MaskImageToNAID` node to convert mask image to NAID mask image.)

### Vibe Transfer

Connect `VibeTransferOptionNAID` node to `GenerateNAID` node and put reference image.

![Comfy_workflow](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/8c6c1c2e-f29d-42a1-b615-439155cb3164)

You can also relay Img2ImgOption on it.

![image](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/acf0496c-8c7c-48f4-9530-18e6a23669d5)

Note that width and height of the source images will be resized to generation size. **This will change aspect ratio of source images.**

#### Multiple Vibe Transfer

Just connect multiple `VibeTransferOptionNAID` nodes to `GenerateNAID` node.

![preview_vibe_2](https://github.com/user-attachments/assets/2d56c0f7-bcd5-48ff-b436-012ea43604fe)

### ModelOption

The default model of `GenerateNAID` node is `nai-diffusion-3`(NAI Diffusion Anime V3).

If you want to change model, put `ModelOptionNAID` node to `GenerateNAID` node.
=======
Simply connect the `GenerateNAID` node to a `SaveImage` node.

![generate](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/1328896d-7d4b-4d47-8ec2-d1c4e8e2561c)

**Note:** All generated images via the `GenerateNAID` node are automatically saved to `output/NAI_autosave/NAI_autosave_#####_.png` to preserve their original metadata.

### Img2img

Connect an `Img2ImgOptionNAID` node to the `option` input of the `GenerateNAID` node and provide a source image.

![image](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/15ff8961-4f6b-4f23-86bf-34b86ace45c0)

**Note:** The width and height of the source image will be resized to the generation size.

### Inpainting

Connect an `InpaintingOptionNAID` node to the `GenerateNAID` node and provide a source image and a mask.

![image](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/5ed1ad77-b90e-46be-8c37-9a5ee0935a3d)

**Note:** Both the source image and mask will be automatically resized to fit the generation size.

### Vibe Transfer

Connect a `VibeTransferOptionNAID` node to the `GenerateNAID` node and provide a reference image to transfer its style and feel.

![Comfy_workflow](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/8c6c1c2e-f29d-42a1-b615-439155cb3164)

You can also chain it with other options, like Img2Img.

![image](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/acf0496c-8c7c-48f4-9530-18e6a23669d5)

#### Multiple Vibe Transfer

Connect multiple `VibeTransferOptionNAID` nodes to combine their influences.

![preview_vibe_2](https://github.com/user-attachments/assets/2d56c0f7-bcd5-48ff-b436-012ea43604fe)

### Character Reference

Use the `CharacterReferenceOptionNAID` node to guide the generation using a single reference image for character identity and/or style.

![image](https://github.com/user-attachments/assets/9f21eff1-163e-49f4-9e4a-85ea25b29988)

-   **style_aware:** If enabled, it attempts to copy both the character's features and the artistic style.
-   **fidelity:** Controls how strictly the generation should adhere to the reference image. The developers state that `primary_strength` is always kept at `1.0`, while `secondary_strength` is calculated as $1.0 - \text{fidelity}$.

**Note:** The reference image will be automatically letterboxed to an accepted NAI canvas size to preserve its aspect ratio.

### ModelOption

The default model of the `GenerateNAID` node is `nai-diffusion-4-5-full`. To change the model, connect a `ModelOptionNAID` node.

Available V4+ models include:
- `nai-diffusion-4-curated-preview`
- `nai-diffusion-4-full`
- `nai-diffusion-4-5-curated`
- `nai-diffusion-4-5-full`
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07

![ModelOption](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/0b484edb-bcb5-428a-b2af-1372a9d7a34f)

### NetworkOption

<<<<<<< HEAD
You can set timeout or retry option from `NetworkOption` node.
Moreover, you can ignore error by `ignore_errors`. In that case, the result will be 1x1 size grayscale image.
Without this node, the request never retry and wait response forever, and stop the queue when error occurs

![preview_network](https://github.com/user-attachments/assets/d82b0ff2-c57c-4870-9024-8d78261a8fea)

**Note that if you set timeout too short, you may not get image but spend Anlas.**

### PromptToNAID

ComfyUI use `()` or `(word:weight)` for emphasis, but NovelAI use `{}` and `[]`. This node convert ComfyUI's prompt to NovelAI's.

Optionally, you can choose weight per brace. If you set `weight_per_brace` to 0.10, `(word:1.1)` will convert to `{word}` instead of `{{word}}`.
=======
You can set timeout and retry options using the `NetworkOption` node. You can also set `ignore_errors` to prevent the queue from stopping on an API error; if an error occurs, a blank 1x1 image will be output.

![preview_network](https://github.com/user-attachments/assets/d82b0ff2-c57c-4870-9024-8d78261a8fea)

**Note:** If you set the timeout too short, you may not receive an image but could still be charged Anlas.

### Anlas Tracker

This extension now includes Anlas tracking to monitor your usage.

**1. Console Output (Automatic)**
All generation and director tool nodes will automatically print your Anlas balance before and after the operation in the console where you launched ComfyUI.
```
[NovelAI] Anlas (pre-gen): 10000
[NovelAI] Generation cost: 20 Anlas
[NovelAI] Anlas (post-gen): 9980
```

**2. Visual Node**
A new node, **`Anlas Tracker ✒️🅝🅐🅘`**, is available in the `NovelAI/utils` category. You can use it to display your current Anlas balance directly in your workflow.

Connect its `anlas_string` output to a display node (e.g., "Show Text" from the [WAS Node Suite](https://github.com/WASasquatch/was-node-suite-comfyui)) to see the value. Use the `trigger` input to control when the balance is checked.

![image](https://github.com/user-attachments/assets/387799cd-36bd-4b5d-9746-bfd74db09f74) <!-- Placeholder for actual image -->

### PromptToNAID

ComfyUI uses `()` or `(word:weight)` for emphasis, while NovelAI uses `{}` and `[]`. This node, found in `NovelAI/utils`, converts ComfyUI's prompt syntax to NovelAI's.
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07

![image](https://github.com/bedovyy/ComfyUI_NAIDGenerator/assets/137917911/25c48350-7268-4d6f-81fe-9eb080fc6e5a)

### Director Tools

![image](https://github.com/user-attachments/assets/e205a51e-59dc-4d5a-94c8-29715ed98739)

<<<<<<< HEAD
You can find director tools like `LineArtNAID` or `EmotionNAID` on NovelAI > director_tools.

![augment_example](https://github.com/user-attachments/assets/5833e9fb-f92e-4d53-9069-58ca8503a3e7)

### V4 Support (Preview)

The node now supports NAI's V4 architecture through the nai-diffusion-4-curated-preview model. This is a preview release of V4 with some limitations:

- **Important Notes:**
  - This is a preview version of V4 and some features are limited
  - Inpainting will automatically use V3 model (but works with V4-generated images)
  - Vibe transfer is not yet supported with V4 preview (will be available with full V4 release)
  - Full V4 feature support will come with the official V4 release


### V4.5 Support (Curated Preview)

Support has been added for **NAI Diffusion 4.5 Curated Preview**, an updated version of V4 with further improvements in detail, contrast, and prompt responsiveness.

- **Model Name:**  
  ```python
  model = "nai-diffusion-4-5-curated-preview"
  ```

- **Availability:**  
  Selectable through `ModelOptionNAID` node under the name **NAI Diffusion 4.5 Curated Preview**.

- **Compatibility Notes:**
  - Works the same as V4 preview, with the same limitations:
    - Inpainting will still default to V4 backend
    - Vibe transfer is not yet supported
  - Prompt formatting remains the same as for V4 (`V4BasePrompt` and `V4NegativePrompt` nodes are compatible)


#### New Model Option

NAI Diffusion V4 Curated Preview is now available in the ModelOptionNAID node:

```python
model = "nai-diffusion-4-curated-preview"
```

#### V4 Prompt Handling

Two new nodes have been added for V4 prompt handling:

##### V4BasePrompt

A node for handling V4 positive prompts:

```
V4BasePrompt -----> positive
               GenerateNAID
```

##### V4NegativePrompt

A node for handling V4 negative prompts:

```
V4NegativePrompt -> negative
                 GenerateNAID
```

#### Example V4 Workflow

Here's a basic V4 setup:

```
V4BasePrompt -----> positive
V4NegativePrompt -> negative  GenerateNAID
ModelOption ------> option
```

#### Work In Progress Features

The following V4 features are currently in development:

```python
"""
- V4PromptConfig: Advanced prompt configuration
  - Coordinate-based prompting
  - Order-based prompting
- V4CharacterCaption: Character-specific prompting with positioning
"""
```

Note: Basic img2img functionality works with V4 preview. For inpainting, the node will automatically use V3 model but can still work on V4-generated images. Vibe transfer will be supported once V4 fully releases.
=======
You can find director tools like `LineArtNAID`, `EmotionNAID`, and `RemoveBGNAID` in the `NovelAI/director_tools` category.

![augment_example](https://github.com/user-attachments/assets/5833e9fb-f92e-4d53-9069-58ca8503a3e7)

### V4 / V4.5 Support

The nodes fully support NAI's V4 and V4.5 model architecture.

#### V4 Prompt Handling

Two new nodes have been added in `NovelAI/v4` for V4/V4.5 prompt handling:

- **`V4BasePrompt`**: Handles the positive prompt.
- **`V4NegativePrompt`**: Handles the negative prompt.

#### Example V4 / V4.5 Workflow

Here's a basic setup for a V4/V4.5 model:

```
V4BasePrompt -----> positive
                           GenerateNAID
V4NegativePrompt -> negative
```

**Note:** Basic `img2img`, `vibe transfer` and `inpainting` functionality works with V4/V4.5.
>>>>>>> 55d886809bf96057da4983fd40d79350e1aeae07
