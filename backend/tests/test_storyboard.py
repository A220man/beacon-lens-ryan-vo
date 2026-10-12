from unittest.mock import AsyncMock, patch

import pytest
from app.services.storyboard import StoryboardService


@pytest.mark.asyncio
async def test_storyboard_service_parse_script():
    fountain = """INT. ROOM - DAY

Action here.

CHARACTER
Dialogue."""
    service = StoryboardService()
    script = service.parse_script(fountain)
    assert len(script.scenes) == 1
    assert script.scenes[0].heading_type.value == "INT"


@pytest.mark.asyncio
async def test_storyboard_service_generate_prompts():
    fountain = """INT. COFFEE SHOP - DAY

John orders coffee.

JOHN
One coffee please.

EXT. PARK - NIGHT

John walks.

JOHN
Nice night."""
    service = StoryboardService()
    script = service.parse_script(fountain)
    frames = service.generate_prompts_from_script(script)
    assert len(frames) == 2
    assert frames[0].scene_number == 1
    assert frames[1].scene_number == 2
    assert "COFFEE SHOP" in frames[0].prompt
    assert "PARK" in frames[1].prompt


@pytest.mark.asyncio
async def test_storyboard_service_generate_storyboard_mock():
    fountain = """INT. ROOM - DAY

Test."""
    service = StoryboardService()
    script = service.parse_script(fountain)

    with patch.object(service.comfyui, "generate_image", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = [b"image-data"]
        storyboard = await service.generate_storyboard(script)

        assert len(storyboard.frames) == 1
        assert storyboard.frames[0].image_data == b"image-data"
        assert storyboard.frames[0].metadata.get("generated") is True


@pytest.mark.asyncio
async def test_storyboard_service_export_json():
    fountain = """INT. ROOM - DAY

Test."""
    service = StoryboardService()
    script = service.parse_script(fountain)

    with patch.object(service.comfyui, "generate_image", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = [b"image-data"]
        storyboard = await service.generate_storyboard(script)
        storyboard.id = 1
        storyboard.project_id = 1

        json_output = service.export_json(storyboard)
        import json
        data = json.loads(json_output)
        assert data["id"] == 1
        assert data["project_id"] == 1
        assert len(data["frames"]) == 1


@pytest.mark.asyncio
async def test_storyboard_service_export_markdown():
    fountain = """INT. ROOM - DAY

Test."""
    service = StoryboardService()
    script = service.parse_script(fountain)

    with patch.object(service.comfyui, "generate_image", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = [b"image-data"]
        storyboard = await service.generate_storyboard(script)
        storyboard.title = "Test Board"

        md = service.export_markdown(storyboard)
        assert "Test Board" in md
        assert "Scene 1" in md
