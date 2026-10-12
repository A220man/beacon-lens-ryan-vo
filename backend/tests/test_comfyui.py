from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.comfyui import ComfyUIClient, ComfyUIService, ComfyUIWorkflow


@pytest.mark.asyncio
async def test_comfyui_client_queue_prompt():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"prompt_id": "test-123"},
            raise_for_status=lambda: None,
        )
        client = ComfyUIClient("http://localhost:8188")
        workflow = ComfyUIWorkflow(prompt={"positive": "test"})
        prompt_id = await client.queue_prompt(workflow)
        assert prompt_id == "test-123"


@pytest.mark.asyncio
async def test_comfyui_client_get_history():
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"test-123": {"status": {"completed": True}}},
            raise_for_status=lambda: None,
        )
        client = ComfyUIClient("http://localhost:8188")
        history = await client.get_history("test-123")
        assert "test-123" in history


@pytest.mark.asyncio
async def test_comfyui_workflow_dataclass():
    workflow = ComfyUIWorkflow(
        prompt={"positive": "a beautiful landscape"},
        negative_prompt="ugly",
        steps=30,
        cfg=8.0,
        width=512,
        height=512,
    )
    assert workflow.prompt["positive"] == "a beautiful landscape"
    assert workflow.negative_prompt == "ugly"
    assert workflow.steps == 30
    assert workflow.cfg == 8.0
    assert workflow.width == 512
    assert workflow.height == 512


@pytest.mark.asyncio
async def test_comfyui_service_generate_image():
    with patch("app.services.comfyui.ComfyUIClient.generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = [b"fake-image-data"]
        service = ComfyUIService("http://localhost:8188")
        images = await service.generate_image("test prompt", negative_prompt="bad")
        assert len(images) == 1
        assert images[0] == b"fake-image-data"


@pytest.mark.asyncio
async def test_comfyui_service_health_check():
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        service = ComfyUIService("http://localhost:8188")
        healthy = await service.health_check()
        assert healthy is True
