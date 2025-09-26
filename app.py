import io
import modal

app = modal.App("sdxl-h100-ui")

# GPU image with PyTorch + diffusers
gpu_image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "torch==2.5.1+cu121",
        "torchvision==0.20.1+cu121",
        "torchaudio==2.5.1+cu121",
        index_url="https://download.pytorch.org/whl/cu121",
    )
    .pip_install(
        "diffusers==0.31.0",
        "transformers~=4.44.0",
        "accelerate==0.33.0",
        "huggingface-hub[hf_transfer]==0.25.2",
        "pillow==10.4.0",
        "safetensors==0.4.3",
        "sentencepiece==0.2.0",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

CACHE_DIR = "/cache"
cache_vol = modal.Volume.from_name("hf-hub-cache", create_if_missing=True)

with gpu_image.imports():
    import torch
    from diffusers import DiffusionPipeline


@app.cls(
    image=gpu_image,
    gpu="H100",
    volumes={CACHE_DIR: cache_vol},
    timeout=600,
)
class Inference:
    @modal.enter()
    def init(self):
        self.pipe = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            cache_dir=CACHE_DIR,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16",
        ).to("cuda")

    @modal.method()
    def run(self, prompt: str, steps: int = 30, guidance_scale: float = 5.0) -> bytes:
        image = self.pipe(
            prompt=prompt,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
        ).images[0]
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()


# Separate lightweight image for the web endpoint
web_image = modal.Image.debian_slim().pip_install("fastapi[standard]")

@app.function(image=web_image)
@modal.fastapi_endpoint()
def generate(
    prompt: str = "A cinematic photo of a fox in moonlight",
    steps: int = 30,
    guidance_scale: float = 5.0,
):
    from fastapi.responses import StreamingResponse
    img_bytes = Inference().run.remote(prompt, steps, guidance_scale)
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")
