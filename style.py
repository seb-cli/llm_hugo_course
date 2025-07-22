# style.py
from reflex.constants.colors import ColorType

STYLESHEETS = [
    "https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&family=Poppins:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&family=Inter:wght@400;500;600;700&family=Roboto:ital,wght@0,400;0,500;0,700;1,400;1,500;1,700&family=Open+Sans:ital,wght@0,400;0,600;0,700;1,400;1,600;1,700&family=Lato:ital,wght@0,400;0,700;1,400;1,700&display=swap"
]


# Default Radix Colors
def create_colors_dict() -> dict:
    colors_dict = {}
    for color in ColorType.__args__:
        if color not in ["black", "white"]:
            colors_dict[color] = {
                shade: f"var(--{color}-{shade})" for shade in range(1, 13)
            }
            # Append the alpha colors
            colors_dict[f"{color}A"] = {
                shade: f"var(--{color}-a{shade})" for shade in range(1, 13)
            }

    # Add accent palette
    colors_dict["accent"] = {shade: f"var(--accent-{shade})" for shade in range(1, 13)}
    colors_dict["accentA"] = {
        shade: f"var(--accent-a{shade})" for shade in range(1, 13)
    }

    return colors_dict
