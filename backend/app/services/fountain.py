import re
from dataclasses import dataclass, field
from enum import Enum


class SceneHeadingType(Enum):
    INT = "INT"
    EXT = "EXT"
    INT_EXT = "INT/EXT"
    UNKNOWN = "UNKNOWN"


@dataclass
class Character:
    name: str
    dialogue: list[str] = field(default_factory=list)
    parentheticals: list[str] = field(default_factory=list)


@dataclass
class Scene:
    number: int
    heading: str
    heading_type: SceneHeadingType
    location: str
    time_of_day: str | None
    action: list[str] = field(default_factory=list)
    characters: list[Character] = field(default_factory=list)
    dialogue_blocks: list[dict] = field(default_factory=list)
    transitions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def get_full_text(self) -> str:
        parts = [self.heading]
        parts.extend(self.action)
        for block in self.dialogue_blocks:
            parts.append(block["character"])
            if block.get("parenthetical"):
                parts.append(f"({block['parenthetical']})")
            parts.extend(block["dialogue"])
        return "\n".join(parts)


@dataclass
class FountainScript:
    title: str | None = None
    author: str | None = None
    draft_date: str | None = None
    contact: str | None = None
    notes: list[str] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "author": self.author,
            "draft_date": self.draft_date,
            "contact": self.contact,
            "notes": self.notes,
            "scenes": [
                {
                    "number": s.number,
                    "heading": s.heading,
                    "heading_type": s.heading_type.value,
                    "location": s.location,
                    "time_of_day": s.time_of_day,
                    "action": s.action,
                    "characters": [
                        {"name": c.name, "dialogue": c.dialogue, "parentheticals": c.parentheticals}
                        for c in s.characters
                    ],
                    "dialogue_blocks": s.dialogue_blocks,
                    "transitions": s.transitions,
                    "notes": s.notes,
                }
                for s in self.scenes
            ],
        }


class FountainParser:
    SCENE_HEADING_PATTERN = re.compile(
        r"^\s*(?P<type>INT\.?|EXT\.?|INT\.?/EXT\.?|I\.?/E\.?)\s+(?P<location>.+?)\s*-\s*(?P<time>DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|LATER|CONTINUOUS|SAME|MOMENTS LATER)?\.?\s*$",
        re.IGNORECASE,
    )
    CHARACTER_PATTERN = re.compile(r"^\s{0,2}(?P<name>[A-Z][A-Z0-9\s\.'-]{1,})\s*$")
    PARENTHETICAL_PATTERN = re.compile(r"^\s*\((?P<text>.+)\)\s*$")
    DIALOGUE_PATTERN = re.compile(r"^\s*(?P<text>.+)\s*$")
    TRANSITION_PATTERN = re.compile(r"^\s*(?P<transition>CUT TO:|DISSOLVE TO:|FADE TO:|FADE OUT\.|FADE IN:|SMASH CUT TO:|MATCH CUT TO:|JUMP CUT TO:)\s*$", re.IGNORECASE)
    TITLE_PAGE_PATTERN = re.compile(r"^\s*(?P<key>Title|Author|Draft Date|Contact|Notes?):\s*(?P<value>.+)\s*$", re.IGNORECASE)

    def parse(self, text: str) -> FountainScript:
        lines = text.split("\n")
        script = FountainScript()
        current_scene: Scene | None = None
        current_character: Character | None = None
        in_dialogue = False
        scene_number = 0

        for line in lines:
            line = line.rstrip()

            if not line.strip():
                continue

            title_match = self.TITLE_PAGE_PATTERN.match(line)
            if title_match and not script.scenes:
                key = title_match.group("key").lower()
                value = title_match.group("value").strip()
                if key == "title":
                    script.title = value
                elif key == "author":
                    script.author = value
                elif key == "draft date":
                    script.draft_date = value
                elif key == "contact":
                    script.contact = value
                elif key in ("note", "notes"):
                    script.notes.append(value)
                continue

            scene_match = self.SCENE_HEADING_PATTERN.match(line)
            if scene_match:
                if current_scene:
                    script.scenes.append(current_scene)
                scene_number += 1
                heading_type_str = scene_match.group("type").upper().replace(".", "")
                heading_type = SceneHeadingType(heading_type_str) if heading_type_str in [e.value for e in SceneHeadingType] else SceneHeadingType.UNKNOWN
                location = scene_match.group("location").strip()
                time_of_day = scene_match.group("time")
                current_scene = Scene(
                    number=scene_number,
                    heading=line.strip(),
                    heading_type=heading_type,
                    location=location,
                    time_of_day=time_of_day,
                )
                current_character = None
                in_dialogue = False
                continue

            transition_match = self.TRANSITION_PATTERN.match(line)
            if transition_match and current_scene:
                current_scene.transitions.append(transition_match.group("transition").strip())
                in_dialogue = False
                current_character = None
                continue

            char_match = self.CHARACTER_PATTERN.match(line)
            if char_match and current_scene:
                char_name = char_match.group("name").strip()
                existing = next((c for c in current_scene.characters if c.name == char_name), None)
                if existing:
                    current_character = existing
                else:
                    current_character = Character(name=char_name)
                    current_scene.characters.append(current_character)
                in_dialogue = True
                continue

            paren_match = self.PARENTHETICAL_PATTERN.match(line)
            if paren_match and current_character and in_dialogue:
                current_character.parentheticals.append(paren_match.group("text").strip())
                continue

            if in_dialogue and current_character:
                stripped = line.strip()
                if stripped:
                    action_starters = {"she ", "he ", "they ", "it ", "we ", "the ", "a ", "an ", "as ", "then ", "suddenly ", "quickly ", "slowly "}
                    if any(stripped.lower().startswith(s) for s in action_starters) and current_scene:
                        current_scene.action.append(stripped)
                        in_dialogue = False
                        current_character = None
                        continue
                    current_character.dialogue.append(stripped)
                    if current_scene:
                        current_scene.dialogue_blocks.append({
                            "character": current_character.name,
                            "parenthetical": current_character.parentheticals[-1] if current_character.parentheticals else None,
                            "dialogue": [stripped],
                        })
                continue

            if current_scene:
                current_scene.action.append(line.strip())
                in_dialogue = False
                current_character = None

        if current_scene:
            script.scenes.append(current_scene)

        return script


def parse_fountain(text: str) -> FountainScript:
    parser = FountainParser()
    return parser.parse(text)
