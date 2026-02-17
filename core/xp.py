def calculate_xp_for_level(level: int) -> int:
    return level * 750 + (level - 1) * 500

def get_level_from_xp(xp: int) -> int:
    level = 0
    while xp >= calculate_xp_for_level(level + 1):
        xp -= calculate_xp_for_level(level + 1)
        level += 1
    return level