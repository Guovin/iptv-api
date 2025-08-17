import os
import re

import utils.constants as constants
from utils.tools import get_real_path, resource_path, format_name


class Alias:
    def __init__(self):
        self.primary_to_aliases: dict[str, set[str]] = {}
        self.alias_to_primary: dict[str, str] = {}
        self.pattern_to_primary: list[tuple[re.Pattern, str]] = []

        real_path = get_real_path(resource_path(constants.alias_path))
        if os.path.exists(real_path):
            with open(real_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() and not line.startswith("#") and "," in line:
                        parts = [p.strip() for p in line.split(",")]
                        primary = parts[0]
                        aliases = set(parts[1:])
                        aliases.add(format_name(primary))
                        self.primary_to_aliases[primary] = aliases
                        for alias in aliases:
                            self.alias_to_primary[alias] = primary
                            if '*' in alias:
                                pattern = '^' + re.escape(alias).replace('\\*', '.*') + '$'
                                self.pattern_to_primary.append((re.compile(pattern), primary))
                        self.alias_to_primary[primary] = primary

    def get(self, name: str):
        """
        Get the alias by name
        """
        return self.primary_to_aliases.get(name, set())

    def get_primary(self, name: str):
        """
        Get the primary name by alias
        """
        primary_name = self.alias_to_primary.get(name, None) or self.get_primary_by_pattern(name)
        if primary_name is None:
            alias_format_name = format_name(name)
            primary_name = self.alias_to_primary.get(alias_format_name, name)
        return primary_name

    def get_primary_by_pattern(self, name: str):
        """
        Get the primary name by pattern match
        """
        for pattern, primary in self.pattern_to_primary:
            if pattern.match(name):
                return primary
        return None

    def set(self, name: str, aliases: set[str]):
        """
        Set the aliases by name
        """
        if name in self.primary_to_aliases:
            for alias in self.primary_to_aliases[name]:
                self.alias_to_primary.pop(alias, None)
        self.primary_to_aliases[name] = set(aliases)
        for alias in aliases:
            self.alias_to_primary[alias] = name
        self.alias_to_primary[name] = name
