"""
Constants for Discord bot
"""

# House capacities for assignment
HOUSE_CAPACITIES = [3, 6, 6]

# Character relationships
RELATIONSHIPS = {
    "Imperial": ["Jingke", "Hanfei", "Han Wu"],
    "Weiqing": ["Qubing", "Han Wu"],
    "Yuhuan": ["Libai", "Longji"],
    "Dufu": ["Libai"],
    "Qubing": ["Weiqing", "Han Wu"],
    "Zhen Ji": ["Zihuan"],
    "Han Wu": ["Weiqing", "Shimin", "Zifu", "Imperial", "Qubing"],
    "Zihuan": ["Zhen Ji", "Zijian"],
    "Jikang": ["Ruanji"],
    "Jingke": ["Imperial", "Jianli"],
    "Jianli": ["Jingke", "Longji"],
    "Wan'er": ["Empress", "Taiping"],
    "Ruanji": ["Jikang"],
    "Zhangliang": ["Liubang"],
    "Zhaojun": ["Mulan"],
    "Empress": ["Wan'er", "Taiping", "Luzhi"],
    "Taiping": ["Empress", "Wan'er"],
    "Longji": ["Yuhuan", "Jianli"],
    "Libai": ["Yuhuan", "Dufu"],
    "Shimin": ["Han Wu", "Xizhi"],
    "Zijian": ["Zihuan"],
    "Xiangyu": ["Consort Yu"],
    "Consort Yu": ["Xiangyu"],
    "Zifu": ["Han Wu"],
    "Xizhi": ["Shimin"],
    "Luzhi": ["Empress", "Liubang"],
    "Liubang": ["Zhangliang", "Luzhi"],
    "Hanfei": ["Imperial"],
    "Mulan": ["Zhaojun"]
}

# Character names for /rela command autocomplete (automatically generated from RELATIONSHIPS)
def _get_all_characters():
    """Extract all unique characters from RELATIONSHIPS"""
    characters = set()
    for main_char, related_chars in RELATIONSHIPS.items():
        characters.add(main_char)
        characters.update(related_chars)
    return sorted(list(characters))

CHARACTERS = _get_all_characters()

# Allowed channels (by name) where bot can respond
ALLOWED_CHANNEL_NAMES = [
    "test-bot",
    # "gacha-gamer",
    # Add more channel names as needed
]
