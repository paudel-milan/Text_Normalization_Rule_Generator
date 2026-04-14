"""
SSML Generator — Config-driven SSML template builder.

Generates SSML markup from category configuration. All templates
and attributes come from the language config, not hardcoded.
"""
from typing import Any

from app.languages.adapter import LanguageAdapter


class SsmlGenerator:
    """
    Builds SSML templates from category config.

    Each category config contains an `ssml` block with:
      - interpret_as: the SSML interpret-as type
      - attributes: extra XML attributes (e.g., format, currency)
      - template: the SSML template string with {placeholders}
    """

    def __init__(self, adapter: LanguageAdapter):
        self.adapter = adapter

    def generate(self, category: str) -> dict[str, Any]:
        """
        Generate SSML template for the given category.

        Returns:
          {
            "template": "<say-as interpret-as=\"currency\">{value}</say-as>",
            "interpret_as": "currency",
            "attributes": {"currency": "INR"},
            "example": "<say-as interpret-as=\"currency\">500</say-as>"
          }
        """
        cat_config = self.adapter.get_category_config(category)
        ssml_config = cat_config.get("ssml", {})

        interpret_as = ssml_config.get("interpret_as", category)
        attributes = ssml_config.get("attributes", {})
        template = ssml_config.get("template", self._default_template(interpret_as))

        # Build the attribute string for the tag
        attr_parts = []
        for key, value in attributes.items():
            attr_parts.append(f'{key}="{value}"')
        attr_string = " " + " ".join(attr_parts) if attr_parts else ""

        # Build the full SSML template
        full_template = f'<say-as interpret-as="{interpret_as}"{attr_string}>{{value}}</say-as>'

        return {
            "template": template,
            "full_template": full_template,
            "interpret_as": interpret_as,
            "attributes": attributes,
            "example": full_template.replace("{value}", "500"),
        }

    def render(self, category: str, value: str) -> str:
        """
        Render an SSML tag with an actual value.

        Example:
          render("currency", "500") →
          '<say-as interpret-as="currency" currency="INR">500</say-as>'
        """
        ssml_info = self.generate(category)
        return ssml_info["full_template"].replace("{value}", value)

    def generate_full_ssml_document(
        self, category: str, text: str, lang: str | None = None
    ) -> str:
        """
        Generate a complete SSML document wrapping the normalized text.
        """
        lang_attr = lang or self.adapter.locale.replace("_", "-")
        ssml = self.render(category, text)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{lang_attr}">\n'
            f"  {ssml}\n"
            f"</speak>"
        )

    @staticmethod
    def _default_template(interpret_as: str) -> str:
        return f'<say-as interpret-as="{interpret_as}">{{value}}</say-as>'
