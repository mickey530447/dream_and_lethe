#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Data Manager for Discord Bot
Manages user character lists
"""

import json
import os
from pathlib import Path
from typing import List, Optional

class UserDataManager:
    def __init__(self, data_dir: str = "user_data"):
        """Initialize user data manager"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def _get_user_file(self, user_id: int) -> Path:
        """Get file path for specific user"""
        return self.data_dir / f"user_{user_id}.json"
    
    def _load_user_data(self, user_id: int) -> dict:
        """Load user data from file"""
        user_file = self._get_user_file(user_id)
        if user_file.exists():
            try:
                with open(user_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {"characters": [], "created_at": None, "last_updated": None}
    
    def _save_user_data(self, user_id: int, data: dict) -> bool:
        """Save user data to file"""
        try:
            user_file = self._get_user_file(user_id)
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def get_user_characters(self, user_id: int) -> List[str]:
        """Get user's character list"""
        data = self._load_user_data(user_id)
        return data.get("characters", [])
    
    def add_character(self, user_id: int, character: str, valid_characters: List[str]) -> tuple[bool, str]:
        """
        Add character to user's list
        Returns: (success, message)
        """
        # Check if character exists in valid list (case insensitive)
        valid_char = None
        for valid in valid_characters:
            if character.lower() == valid.lower():
                valid_char = valid
                break
        
        if not valid_char:
            return False, f"❌ Character '{character}' không tồn tại!"
        
        # Load user data
        data = self._load_user_data(user_id)
        user_chars = data.get("characters", [])
        
        # Check if already exists
        if valid_char in user_chars:
            return False, f"❌ Character '{valid_char}' đã có trong danh sách!"
        
        # Add character
        user_chars.append(valid_char)
        data["characters"] = user_chars
        data["last_updated"] = str(user_id)  # Simple timestamp
        
        if self._save_user_data(user_id, data):
            return True, f"✅ Đã thêm '{valid_char}' vào danh sách! (Tổng: {len(user_chars)})"
        else:
            return False, "❌ Lỗi khi lưu dữ liệu!"
    
    def remove_character(self, user_id: int, character: str) -> tuple[bool, str]:
        """
        Remove character from user's list
        Returns: (success, message)
        """
        data = self._load_user_data(user_id)
        user_chars = data.get("characters", [])
        
        if not user_chars:
            return False, "❌ Danh sách của bạn đang trống!"
        
        # Find character to remove (case insensitive)
        char_to_remove = None
        for char in user_chars:
            if character.lower() == char.lower():
                char_to_remove = char
                break
        
        if not char_to_remove:
            return False, f"❌ Character '{character}' không có trong danh sách của bạn!"
        
        # Remove character
        user_chars.remove(char_to_remove)
        data["characters"] = user_chars
        data["last_updated"] = str(user_id)
        
        if self._save_user_data(user_id, data):
            return True, f"✅ Đã xóa '{char_to_remove}' khỏi danh sách! (Còn lại: {len(user_chars)})"
        else:
            return False, "❌ Lỗi khi lưu dữ liệu!"
    
    def clear_user_data(self, user_id: int) -> tuple[bool, str]:
        """
        Clear all user data
        Returns: (success, message)
        """
        user_file = self._get_user_file(user_id)
        
        if not user_file.exists():
            return False, "❌ Bạn chưa có dữ liệu nào để xóa!"
        
        try:
            user_file.unlink()  # Delete file
            return True, "✅ Đã xóa toàn bộ dữ liệu của bạn!"
        except Exception:
            return False, "❌ Lỗi khi xóa dữ liệu!"
    
    def generate_rela_command(self, user_id: int) -> tuple[bool, str]:
        """
        Generate /rela command string for user
        Returns: (success, command_string)
        """
        characters = self.get_user_characters(user_id)
        
        if not characters:
            return False, "❌ Danh sách của bạn đang trống! Hãy dùng `/add` để thêm characters."
        
        command_string = "/rela characters: " + ", ".join(characters)
        return True, command_string
    
    def get_user_stats(self, user_id: int) -> str:
        """Get user statistics"""
        characters = self.get_user_characters(user_id)
        
        if not characters:
            return "📋 Danh sách của bạn đang trống."
        
        stats = f"📋 **Danh sách characters của bạn:**\n"
        stats += f"**Tổng số:** {len(characters)}\n\n"
        
        # Show all characters in one line
        stats += f"{', '.join(characters)}\n"
        
        return stats
    
    def reset_all_users(self) -> int:
        """
        Reset all user data (weekly cleanup)
        Returns: Number of users cleared
        """
        reset_count = 0
        
        try:
            # Get all user files in the directory
            for user_file in self.data_dir.glob("user_*.json"):
                try:
                    user_file.unlink()  # Delete file
                    reset_count += 1
                except Exception as e:
                    print(f"Error deleting {user_file}: {e}")
            
            return reset_count
            
        except Exception as e:
            print(f"Error in reset_all_users: {e}")
            return 0
    
    def get_total_users(self) -> int:
        """Get total number of users with data"""
        try:
            return len(list(self.data_dir.glob("user_*.json")))
        except Exception:
            return 0
