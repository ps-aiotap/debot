import json
import os
from typing import Dict, List, Any

class PersonaManager:
    def __init__(self, config_path: str = "persona_config.json"):
        self.config_path = config_path
        self.personas = self._load_config()
        self.current_persona = "default"
        self._load_last_used_persona()

    def _load_config(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                
                # Ensure default persona exists
                if "default" not in config:
                    config["default"] = {
                        "collections": ["documents"],
                        "prompt_style": "balanced"
                    }
                return config
            else:
                print(f"Warning: {self.config_path} not found. Using default configuration.")
                return {"default": {"collections": ["documents"], "prompt_style": "balanced"}}
        except Exception as e:
            print(f"Error loading persona config: {e}")
            return {"default": {"collections": ["documents"], "prompt_style": "balanced"}}

    def get_available_personas(self) -> List[str]:
        return list(self.personas.keys())

    def set_persona(self, persona_name: str) -> bool:
        if persona_name in self.personas:
            self.current_persona = persona_name
            self._save_last_used_persona()
            return True
        return False

    def get_collections(self) -> List[str]:
        try:
            return self.personas[self.current_persona]["collections"]
        except (KeyError, TypeError):
            return ["documents"]

    def get_prompt_style(self) -> str:
        try:
            return self.personas[self.current_persona]["prompt_style"]
        except (KeyError, TypeError):
            return "balanced"

    def get_current_persona(self) -> str:
        return self.current_persona
    
    def get_data_dir(self) -> str:
        """Get data directory for the current persona."""
        try:
            return self.personas[self.current_persona]["data_dir"]
        except (KeyError, TypeError):
            return "./data"

    def _save_last_used_persona(self) -> None:
        try:
            with open(".last_persona", "w") as f:
                f.write(self.current_persona)
        except Exception:
            pass  # Silently fail if we can't save

    def _load_last_used_persona(self) -> None:
        try:
            if os.path.exists(".last_persona"):
                with open(".last_persona", "r") as f:
                    persona = f.read().strip()
                    if persona in self.personas:
                        self.current_persona = persona
        except Exception:
            pass  # Silently fail if we can't load