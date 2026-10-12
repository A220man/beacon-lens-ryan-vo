import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, cast

import httpx

from app.core.config import get_settings

settings = get_settings()


@dataclass
class ComfyUIWorkflow:
    prompt: dict[str, Any]
    negative_prompt: str | None = None
    seed: int | None = None
    steps: int = 20
    cfg: float = 7.0
    width: int = 1024
    height: int = 1024
    sampler_name: str = "euler"
    scheduler: str = "normal"
    denoise: float = 1.0


class ComfyUIClient:
    def __init__(self, base_url: str | None = None, timeout: int = 300):
        self.base_url = (base_url or settings.comfyui_url).rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def queue_prompt(self, workflow: ComfyUIWorkflow) -> str:
        client = await self._get_client()
        prompt_data = self._build_prompt(workflow)
        response = await client.post(f"{self.base_url}/prompt", json={"prompt": prompt_data})
        response.raise_for_status()
        data = response.json()
        return cast(str, data.get("prompt_id", ""))

    async def get_history(self, prompt_id: str) -> dict[str, Any]:
        client = await self._get_client()
        response = await client.get(f"{self.base_url}/history/{prompt_id}")
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        client = await self._get_client()
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        response = await client.get(f"{self.base_url}/view", params=params)
        response.raise_for_status()
        return response.content

    async def wait_for_completion(self, prompt_id: str, poll_interval: float = 2.0, max_wait: int = 300) -> dict[str, Any]:
        start_time = asyncio.get_event_loop().time()
        while True:
            history = await self.get_history(prompt_id)
            if prompt_id in history:
                prompt_data = history[prompt_id]
                if prompt_data.get("status", {}).get("completed", False):
                    return cast(dict[str, Any], prompt_data)
                if prompt_data.get("status", {}).get("status_str") == "error":
                    raise RuntimeError(f"ComfyUI generation failed: {prompt_data.get('status', {}).get('error', 'Unknown error')}")

            if asyncio.get_event_loop().time() - start_time > max_wait:
                raise TimeoutError(f"Generation timed out after {max_wait}s")

            await asyncio.sleep(poll_interval)
    async def generate(self, workflow: ComfyUIWorkflow) -> list[bytes]:
        prompt_id = await self.queue_prompt(workflow)
        history = await self.wait_for_completion(prompt_id)
        outputs = history.get(prompt_id, {}).get("outputs", {})
        images = []
        for node_output in outputs.values():
            for image_info in node_output.get("images", []):
                img_data = await self.get_image(
                    image_info["filename"],
                    image_info.get("subfolder", ""),
                    image_info.get("type", "output"),
                )
                images.append(img_data)
        return images

    def _build_prompt(self, workflow: ComfyUIWorkflow) -> dict[str, Any]:
        return {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": workflow.seed or int(datetime.now(UTC).timestamp() * 1000) % 2**32,
                    "steps": workflow.steps,
                    "cfg": workflow.cfg,
                    "sampler_name": workflow.sampler_name,
                    "scheduler": workflow.scheduler,
                    "denoise": workflow.denoise,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                },
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "sdxl_base_1.0.safetensors"},
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": workflow.width, "height": workflow.height, "batch_size": 1},
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": workflow.prompt.get("positive", ""), "clip": ["4", 1]},
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": workflow.negative_prompt or "", "clip": ["4", 1]},
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"images": ["8", 0], "filename_prefix": "beacon-lens"},
            },
        }


class ComfyUIService:
    def __init__(self, base_url: str | None = None):
        self.client = ComfyUIClient(base_url)

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str | None = None,
        **kwargs: Any,
    ) -> list[bytes]:
        workflow = ComfyUIWorkflow(
            prompt={"positive": prompt},
            negative_prompt=negative_prompt,
            **kwargs,
        )
        return await self.client.generate(workflow)

    async def health_check(self) -> bool:
        try:
            client = await self.client._get_client()
            response = await client.get(f"{self.client.base_url}/system_stats", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        await self.client.close()


_comfyui_service: ComfyUIService | None = None


def get_comfyui_service(base_url: str | None = None) -> ComfyUIService:
    global _comfyui_service
    if _comfyui_service is None:
        _comfyui_service = ComfyUIService(base_url)
    return _comfyui_service
