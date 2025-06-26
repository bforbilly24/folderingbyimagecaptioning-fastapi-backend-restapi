import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "folderisasi")

# Prioritas kategori (action-focused first, then people, animals, scenery, atmosphere)
CATEGORY_PRIORITY = ["kegiatan", "manusia", "hewan", "pemandangan", "suasana"]

# Kata kunci untuk kategori
CATEGORY_KEYWORDS = {
    "kegiatan": [
        "walking", "running", "jumping", "riding", "swimming", "cycling",
        "dancing", "playing", "summersault", "activity", "sport", "exercise",
        "working", "cooking", "painting", "singing", "climbing"
    ],
    "manusia": [
        "human", "person", "man", "woman", "people", "child", "boy", "girl",
        "adult", "individual", "group", "crowd", "family", "friend"
    ],
    "hewan": [
        "animal", "dog", "cat", "bird", "fish", "horse", "elephant", "tiger",
        "lion", "puppy", "kitten", "pet", "cow", "sheep", "rabbit"
    ],
    "pemandangan": [
        "view", "mountain", "sea", "sunset", "nature", "landscape", "ocean",
        "scenery", "river", "beach", "shore", "lake", "building", "sign",
        "city", "sky", "horizon", "field", "forest", "hill", "valley",
        "road", "bridge", "village"
    ],
    "suasana": [
        "calm", "quiet", "peaceful", "relax", "serene", "tranquil", "silence",
        "mood", "atmosphere", "vibe", "ambiance"
    ]
}