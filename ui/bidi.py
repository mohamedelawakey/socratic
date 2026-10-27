class BidiHelper:
    """Helper to detect text direction for Socratic views."""

    @staticmethod
    def is_rtl_text(text: str) -> bool:
        """Determines whether text is predominantly Arabic / RTL."""
        if not text:
            return False
        for char in text:
            code = ord(char)
            # Arabic unicode ranges
            if 0x0600 <= code <= 0x06FF or 0x0750 <= code <= 0x077F or 0x08A0 <= code <= 0x08FF:
                return True
        return False

    @staticmethod
    def format_text(text: str) -> str:
        """
        Modern Linux terminal emulators (GNOME Terminal, VTE, Kitty) have native
        HarfBuzz shaping and BiDi engines. Passing raw Unicode preserves perfect
        ligatures and prevents double-reversing artifacts.
        """
        return text
