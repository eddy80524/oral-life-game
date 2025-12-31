"""
Tests for pages/utils.py
"""
import pytest
import json
import os
import tempfile
from pages.utils import (
    load_settings,
    load_events_config,
    get_board_file_for_age,
)


class TestLoadSettings:
    """設定読み込みテスト"""
    
    def test_returns_dict(self):
        """辞書を返す"""
        result = load_settings()
        assert isinstance(result, dict)
    
    def test_has_staff_pin(self):
        """staff_pinフィールドがある"""
        result = load_settings()
        assert 'staff_pin' in result
    
    def test_has_debug_mode(self):
        """debug_modeフィールドがある"""
        result = load_settings()
        assert 'debug_mode' in result
    
    def test_has_game_config(self):
        """gameフィールドがある（タイマー、報酬設定）"""
        result = load_settings()
        assert 'game' in result
        game = result['game']
        assert 'job_experience_timer_seconds' in game
        assert 'rewards' in game


class TestLoadEventsConfig:
    """イベント設定読み込みテスト"""
    
    def test_returns_dict(self):
        """辞書を返す"""
        result = load_events_config()
        assert isinstance(result, dict)
    
    def test_has_events_list(self):
        """eventsリストがある"""
        result = load_events_config()
        assert 'events' in result
        assert isinstance(result['events'], list)
    
    def test_has_active_event(self):
        """active_eventフィールドがある"""
        result = load_events_config()
        assert 'active_event' in result


class TestGetBoardFileForAge:
    """ボードファイル取得テスト"""
    
    def test_returns_board_file(self):
        """統一ボードファイルを返す"""
        result = get_board_file_for_age(3)
        assert 'board_main' in result
    
    def test_same_for_all_ages(self):
        """年齢に関係なく同じボードファイル"""
        result_3 = get_board_file_for_age(3)
        result_7 = get_board_file_for_age(7)
        assert result_3 == result_7
    
    def test_returns_json_path(self):
        """JSONパスを返す"""
        result = get_board_file_for_age(5)
        assert result.endswith('.json')
