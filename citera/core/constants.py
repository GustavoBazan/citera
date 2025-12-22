"""Shared constants for Citera."""

STAGE_DIRS = {
    "playground": "playground",
    "incubator": "incubator",
    "product": "products",
    "tool": "tools",
}

ARCHIVE_DIR = "archives"

CATEGORY_CHOICES = {
    "games": "Games",
    "libraries": "Libraries",
    "clis": "CLIs",
    "cli": "CLIs",
    "web": "Web",
    "ai": "AI",
    "tools": "Tools",
    "tool": "Tools",
    "other": "Other",
}

ADJECTIVES = [
    "Agile",
    "Bright",
    "Calm",
    "Daring",
    "Eager",
    "Fuzzy",
    "Gentle",
    "Happy",
    "Jolly",
    "Lively",
    "Mighty",
    "Nimble",
    "Quick",
    "Radiant",
    "Sunny",
    "Swift",
    "Witty",
]

NOUNS = [
    "Fox",
    "Llama",
    "Otter",
    "Panda",
    "Rocket",
    "River",
    "Comet",
    "Harbor",
    "Maple",
    "Nimbus",
    "Quartz",
    "Signal",
    "Sprout",
    "Summit",
    "Vector",
]

LANG_STARTERS = {
    "python": ("main.py", "print(\"Hello from citera\")\n"),
    "js": ("main.js", "console.log(\"Hello from citera\");\n"),
    "javascript": ("main.js", "console.log(\"Hello from citera\");\n"),
    "rust": ("main.rs", "fn main() {\n    println!(\"Hello from citera\");\n}\n"),
}
