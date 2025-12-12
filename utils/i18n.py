import json
import os
from typing import Dict

from utils.config import config, resource_path

_LOCALES_CACHE: Dict[str, Dict[str, str]] = {}
_CURRENT_LANG = None
_TRANSLATIONS: Dict[str, str] = {}


def _load_locale(lang: str) -> Dict[str, str]:
    global _LOCALES_CACHE
    if lang in _LOCALES_CACHE:
        return _LOCALES_CACHE[lang]

    locales_dir = resource_path(os.path.join("locales"))
    file_path = os.path.join(locales_dir, f"{lang}.json")

    if not os.path.exists(file_path):
        fallback_path = os.path.join(locales_dir, "zh_CN.json")
        file_path = fallback_path

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}

    _LOCALES_CACHE[lang] = data
    return data


def set_language(lang: str):
    global _CURRENT_LANG, _TRANSLATIONS
    _CURRENT_LANG = lang
    _TRANSLATIONS = _load_locale(lang)


def get_language() -> str:
    global _CURRENT_LANG
    if _CURRENT_LANG is None:
        set_language(config.language)
    return _CURRENT_LANG


def t(key: str, default: str | None = None) -> str:
    global _TRANSLATIONS
    if not _TRANSLATIONS:
        set_language(config.language)

    if key in _TRANSLATIONS:
        return _TRANSLATIONS[key]

    if default is not None:
        return default

    return key
