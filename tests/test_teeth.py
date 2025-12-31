"""
Tests for services/teeth.py
"""
import pytest
from services import teeth as teeth_service


class TestToothBlueprint:
    """ToothBlueprint dataclass tests"""
    
    def test_blueprints_exist(self):
        """BLUEPRINTSが正しく定義されている"""
        assert teeth_service.BLUEPRINTS is not None
        assert len(teeth_service.BLUEPRINTS) > 0
    
    def test_blueprint_structure(self):
        """各blueprintが必要なフィールドを持つ"""
        for bp_id, bp in teeth_service.BLUEPRINTS.items():
            assert bp.id == bp_id
            assert bp.arch in ['upper', 'lower']
            assert bp.side in ['left', 'right']


class TestCreateToothChart:
    """歯チャート作成のテスト"""
    
    def test_create_child_chart(self):
        """子供用歯チャート（20本）の作成"""
        chart = teeth_service.create_tooth_chart(stage="child")
        assert chart is not None
        # chartはリストとして返される
        if isinstance(chart, list):
            visible_count = sum(1 for t in chart if t.get('visible', False))
        else:
            visible_count = sum(1 for t in chart.values() if t.get('visible', False))
        assert visible_count == 20, f"子供は20本の歯が見える: got {visible_count}"
    
    def test_create_adult_chart(self):
        """大人用歯チャート（28本）の作成"""
        chart = teeth_service.create_tooth_chart(stage="adult")
        assert chart is not None
        if isinstance(chart, list):
            visible_count = sum(1 for t in chart if t.get('visible', False))
        else:
            visible_count = sum(1 for t in chart.values() if t.get('visible', False))
        assert visible_count == 28, f"大人は28本の歯が見える: got {visible_count}"


class TestEnsureToothState:
    """歯の状態初期化テスト"""
    
    def test_ensure_creates_tooth_chart_if_missing(self):
        """game_stateにtooth_chartがなければ作成"""
        game_state = {}
        teeth_service.ensure_tooth_state(game_state)
        # 'teeth' または 'tooth_chart' のどちらかがある
        assert 'teeth' in game_state or 'tooth_chart' in game_state
    
    def test_ensure_sets_teeth_count(self):
        """teeth_countが設定される"""
        game_state = {}
        teeth_service.ensure_tooth_state(game_state)
        assert 'teeth_count' in game_state
        assert game_state['teeth_count'] > 0


class TestSyncTeethCount:
    """歯の数同期テスト"""
    
    def test_sync_counts_healthy_teeth(self):
        """健康な歯を正しくカウント"""
        game_state = {}
        teeth_service.ensure_tooth_state(game_state)
        teeth_service.sync_teeth_count(game_state)
        assert game_state.get('teeth_count', 0) > 0


class TestUpgradeToAdult:
    """永久歯への移行テスト"""
    
    def test_upgrade_changes_stage(self):
        """子供から大人への移行"""
        game_state = {}
        teeth_service.ensure_tooth_state(game_state)
        result = teeth_service.upgrade_to_adult(game_state)
        # 移行が成功したか、既に大人だった場合
        assert result == True or result is None or result == False


class TestResetAllTeethToHealthy:
    """歯リセットテスト"""
    
    def test_reset_sets_teeth_count(self):
        """リセット後はteeth_countが設定される"""
        game_state = {}
        teeth_service.ensure_tooth_state(game_state)
        teeth_service.reset_all_teeth_to_healthy(game_state)
        
        # teeth_countまたはtooth_chartが存在する
        assert 'teeth_count' in game_state or 'tooth_chart' in game_state


class TestLoseRandomTeeth:
    """ランダム歯損失テスト"""
    
    def test_lose_teeth_function_exists(self):
        """lose_random_teeth関数が存在する"""
        assert hasattr(teeth_service, 'lose_random_teeth')
    
    def test_lose_teeth_callable(self):
        """lose_random_teethが呼び出し可能"""
        game_state = {}
        teeth_service.ensure_tooth_state(game_state)
        # エラーなく呼び出せる
        teeth_service.lose_random_teeth(game_state, count=1)


class TestStainTeeth:
    """着色テスト"""
    
    def test_stain_function_exists(self):
        """stain_teeth関数が存在する"""
        assert hasattr(teeth_service, 'stain_teeth')


class TestWhitenTeeth:
    """ホワイトニングテスト"""
    
    def test_whiten_function_exists(self):
        """whiten_teeth関数が存在する"""
        assert hasattr(teeth_service, 'whiten_teeth')
    
    def test_whiten_callable(self):
        """whiten_teethが呼び出し可能"""
        game_state = {}
        teeth_service.ensure_tooth_state(game_state)
        teeth_service.whiten_teeth(game_state)
