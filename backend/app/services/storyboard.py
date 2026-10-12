import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from app.services.comfyui import ComfyUIService
from app.services.fountain import FountainScript, Scene, parse_fountain


@dataclass
class StoryboardFrame:
    scene_number: int
    scene_heading: str
    prompt: str
    image_data: bytes | None = None
    image_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Storyboard:
    id: int
    project_id: int
    title: str
    fountain_source: str
    script: FountainScript
    frames: list[StoryboardFrame] = field(default_factory=list)
    export_formats: list[str] = field(default_factory=list)


class StoryboardService:
    def __init__(self, comfyui_service: ComfyUIService | None = None):
        self.comfyui = comfyui_service or ComfyUIService()

    def parse_script(self, fountain_text: str) -> FountainScript:
        return parse_fountain(fountain_text)

    def generate_prompts_from_script(self, script: FountainScript, style_template: str | None = None) -> list[StoryboardFrame]:
        frames = []
        default_style = style_template or "cinematic storyboard frame, detailed, professional film concept art, {scene_description}"

        for scene in script.scenes:
            scene_desc = self._scene_to_description(scene)
            prompt = default_style.format(scene_description=scene_desc)
            frames.append(StoryboardFrame(
                scene_number=scene.number,
                scene_heading=scene.heading,
                prompt=prompt,
                metadata={
                    "location": scene.location,
                    "time_of_day": scene.time_of_day,
                    "heading_type": scene.heading_type.value,
                },
            ))
        return frames

    async def generate_storyboard(
        self,
        script: FountainScript,
        style_template: str | None = None,
        progress_callback: Callable[[int, int, str], Any] | None = None,
    ) -> Storyboard:
        frames = self.generate_prompts_from_script(script, style_template)

        for i, frame in enumerate(frames):
            if progress_callback:
                await progress_callback(i + 1, len(frames), frame.scene_heading)

            try:
                images = await self.comfyui.generate_image(frame.prompt)
                if images:
                    frame.image_data = images[0]
                    frame.metadata["generated"] = True
                else:
                    frame.metadata["generated"] = False
                    frame.metadata["error"] = "No images returned"
            except Exception as e:
                frame.metadata["generated"] = False
                frame.metadata["error"] = str(e)

        return Storyboard(
            id=0,
            project_id=0,
            title=script.title or "Untitled Storyboard",
            fountain_source="",
            script=script,
            frames=frames,
        )

    def _scene_to_description(self, scene: Scene) -> str:
        parts = []
        if scene.location:
            parts.append(f"{scene.location}")
        if scene.time_of_day:
            parts.append(f"{scene.time_of_day.lower()}")
        if scene.action:
            action_summary = " ".join(scene.action[:3])
            parts.append(action_summary)
        if scene.characters:
            char_names = ", ".join([c.name for c in scene.characters[:3]])
            parts.append(f"characters: {char_names}")
        return ", ".join(parts)

    def export_json(self, storyboard: Storyboard) -> str:
        return json.dumps({
            "id": storyboard.id,
            "project_id": storyboard.project_id,
            "title": storyboard.title,
            "frames": [
                {
                    "scene_number": f.scene_number,
                    "scene_heading": f.scene_heading,
                    "prompt": f.prompt,
                    "has_image": f.image_data is not None,
                    "metadata": f.metadata,
                }
                for f in storyboard.frames
            ],
            "script": storyboard.script.to_dict(),
        }, indent=2)

    def export_markdown(self, storyboard: Storyboard) -> str:
        lines = [f"# {storyboard.title}\n"]
        if storyboard.script.title:
            lines.append(f"**Original Script:** {storyboard.script.title}")
        if storyboard.script.author:
            lines.append(f"**Author:** {storyboard.script.author}")
        lines.append("")

        for frame in storyboard.frames:
            lines.append(f"## Scene {frame.scene_number}: {frame.scene_heading}")
            lines.append(f"**Prompt:** {frame.prompt}")
            if frame.image_data:
                lines.append("*[Image generated]*")
            else:
                lines.append(f"*Status: {frame.metadata.get('error', 'Not generated')}*")
            lines.append("")
        return "\n".join(lines)
