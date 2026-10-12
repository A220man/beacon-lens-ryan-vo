from app.services.fountain import SceneHeadingType, parse_fountain


def test_parse_simple_scene():
    fountain = """INT. COFFEE SHOP - DAY

John enters the shop.

JOHN
I'll have a coffee.

He waits."""
    script = parse_fountain(fountain)
    assert len(script.scenes) == 1
    scene = script.scenes[0]
    assert scene.number == 1
    assert scene.heading_type == SceneHeadingType.INT
    assert "COFFEE SHOP" in scene.location
    assert scene.time_of_day == "DAY"
    assert len(scene.action) == 2
    assert len(scene.characters) == 1
    assert scene.characters[0].name == "JOHN"
    assert "I'll have a coffee." in scene.characters[0].dialogue


def test_parse_multiple_scenes():
    fountain = """INT. OFFICE - DAY

Sarah works at her desk.

SARAH
Almost done.

EXT. PARK - NIGHT

Sarah walks home.

SARAH
(whispering)
Finally free."""
    script = parse_fountain(fountain)
    assert len(script.scenes) == 2
    assert script.scenes[0].heading_type == SceneHeadingType.INT
    assert script.scenes[1].heading_type == SceneHeadingType.EXT
    assert script.scenes[0].time_of_day == "DAY"
    assert script.scenes[1].time_of_day == "NIGHT"
    assert len(script.scenes[0].characters) == 1
    assert len(script.scenes[1].characters) == 1
    assert script.scenes[1].characters[0].parentheticals == ["whispering"]


def test_parse_title_page():
    fountain = """Title: My Screenplay
Author: Jane Writer
Draft Date: 2024-01-15
Contact: jane@example.com

INT. HOUSE - DAY

Action here."""
    script = parse_fountain(fountain)
    assert script.title == "My Screenplay"
    assert script.author == "Jane Writer"
    assert script.draft_date == "2024-01-15"
    assert script.contact == "jane@example.com"


def test_parse_transitions():
    fountain = """INT. ROOM - DAY

Action.

CUT TO:

EXT. STREET - DAY

More action."""
    script = parse_fountain(fountain)
    assert len(script.scenes) == 2
    assert "CUT TO:" in script.scenes[0].transitions


def test_parse_dialogue_blocks():
    fountain = """INT. KITCHEN - MORNING

Mary cooks breakfast.

MARY
Good morning!

She serves eggs.

MARY
(cheerful)
Eat up!"""
    script = parse_fountain(fountain)
    scene = script.scenes[0]
    assert len(scene.dialogue_blocks) == 2
    assert scene.dialogue_blocks[0]["character"] == "MARY"
    assert scene.dialogue_blocks[0]["parenthetical"] is None
    assert scene.dialogue_blocks[1]["parenthetical"] == "cheerful"


def test_parse_complex_fountain():
    fountain = """Title: Test Script
Author: Test Author

FADE IN:

INT. LAB - NIGHT

DR. SMITH (50s, brilliant but tired) works furiously.

DR. SMITH
It's almost ready.

A beep sounds.

DR. SMITH
(excited)
Success!

CUT TO:

EXT. CITY ROOFTOP - DAWN

Dr. Smith looks over the city.

DR. SMITH
A new day."""
    script = parse_fountain(fountain)
    assert script.title == "Test Script"
    assert len(script.scenes) == 2
    assert script.scenes[0].heading_type == SceneHeadingType.INT
    assert script.scenes[1].heading_type == SceneHeadingType.EXT
    assert len(script.scenes[0].characters) == 1
    assert script.scenes[0].characters[0].name == "DR. SMITH"
    assert "excited" in script.scenes[0].characters[0].parentheticals
