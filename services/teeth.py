"""
Tooth chart utilities for the oral life game.
Creates staged (child/adult) tooth metadata, applies board effects,
and exposes helpers for labels & selection.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Optional, Sequence
import random

TOOTH_CHART_VERSION = 3


@dataclass(frozen=True)
class ToothBlueprint:
    id: str
    arch: str  # 'upper' or 'lower'
    side: str  # 'left' or 'right'
    child_rank: Optional[int]
    adult_rank: Optional[int]
    kind_child: Optional[str]
    kind_adult: Optional[str]

    @property
    def visible_child(self) -> bool:
        return self.child_rank is not None and self.kind_child is not None

    @property
    def visible_adult(self) -> bool:
        return self.adult_rank is not None and (self.kind_adult or self.kind_child)


ADULT_KIND_MAP = {
    1: "central_incisor",
    2: "lateral_incisor",
    3: "canine",
    4: "first_premolar",
    5: "second_premolar",
    6: "first_molar",
    7: "second_molar",
}

CHILD_KIND_MAP = {
    5: "primary_second_molar",
    4: "primary_first_molar",
    3: "primary_canine",
    2: "primary_lateral_incisor",
    1: "primary_central_incisor",
}

ADULT_LABEL_MAP = {
    "central_incisor": "中切歯",
    "lateral_incisor": "側切歯",
    "canine": "犬歯",
    "first_premolar": "第一小臼歯",
    "second_premolar": "第二小臼歯",
    "first_molar": "第一大臼歯",
    "second_molar": "第二大臼歯",
}

CHILD_LABEL_MAP = {
    "primary_central_incisor": "乳中切歯",
    "primary_lateral_incisor": "乳側切歯",
    "primary_canine": "乳犬歯",
    "primary_first_molar": "第一乳臼歯",
    "primary_second_molar": "第二乳臼歯",
}

SHORT_LABEL_MAP = {
    "中切歯": "中切",
    "側切歯": "側切",
    "犬歯": "犬歯",
    "第一小臼歯": "小臼1",
    "第二小臼歯": "小臼2",
    "第一大臼歯": "大臼1",
    "第二大臼歯": "大臼2",
    "乳中切歯": "乳中",
    "乳側切歯": "乳側",
    "乳犬歯": "乳犬",
    "第一乳臼歯": "乳臼1",
    "第二乳臼歯": "乳臼2",
}


def _blueprints() -> List[ToothBlueprint]:
    bp: List[ToothBlueprint] = []

    def add_quadrant(prefix: str, arch: str, side: str) -> None:
        # Child teeth (5 per quadrant)
        child_ids = [f"{prefix}{n}" for n in (5, 4, 3, 2, 1)]
        # Adult teeth (7 per quadrant)
        adult_ids = [f"{prefix}{n}" for n in (7, 6, 5, 4, 3, 2, 1)]

        for idx, tooth_id in enumerate(child_ids):
            number = int(tooth_id[-1])
            bp.append(
                ToothBlueprint(
                    id=tooth_id,
                    arch=arch,
                    side=side,
                    child_rank=idx,
                    adult_rank=adult_ids.index(tooth_id) if tooth_id in adult_ids else None,
                    kind_child=CHILD_KIND_MAP.get(number),
                    kind_adult=ADULT_KIND_MAP.get(number),
                )
            )

        # Adult-only molars (second + first molar already added above if same id),
        # ensure UL6/UL7 etc exist even if not in child list.
        for idx, tooth_id in enumerate(adult_ids[:2]):  # 7,6
            if tooth_id in child_ids:
                continue
            number = int(tooth_id[-1])
            bp.append(
                ToothBlueprint(
                    id=tooth_id,
                    arch=arch,
                    side=side,
                    child_rank=None,
                    adult_rank=idx,
                    kind_child=None,
                    kind_adult=ADULT_KIND_MAP.get(number),
                )
            )

    add_quadrant("UL", "upper", "left")
    add_quadrant("UR", "upper", "right")
    add_quadrant("LL", "lower", "left")
    add_quadrant("LR", "lower", "right")
    return bp


BLUEPRINTS: Dict[str, ToothBlueprint] = {bp.id: bp for bp in _blueprints()}


def _make_tooth_entry(bp: ToothBlueprint, stage: str) -> Dict:
    if stage == "adult":
        visible = bp.visible_adult
        kind = bp.kind_adult or bp.kind_child or "central_incisor"
        order = bp.adult_rank
    else:
        visible = bp.visible_child
        kind = bp.kind_child or "primary_central_incisor"
        order = bp.child_rank

    return {
        "id": bp.id,
        "arch": bp.arch,
        "side": bp.side,
        "status": "healthy" if visible else "hidden",
        "visible": visible,
        "permanent_loss": False,
        "kind": kind,
        "order_child": bp.child_rank,
        "order_adult": bp.adult_rank,
    }


def create_tooth_chart(stage: str = "child") -> List[Dict]:
    return [_make_tooth_entry(bp, stage) for bp in BLUEPRINTS.values()]


def ensure_tooth_state(game_state: Dict) -> None:
    stage = game_state.get("tooth_stage", "child")
    if stage not in {"child", "adult"}:
        stage = "child"
    chart = game_state.get("tooth_chart")
    if (
        not chart
        or game_state.get("tooth_chart_version") != TOOTH_CHART_VERSION
        or any("order_child" not in tooth for tooth in chart)
    ):
        game_state["tooth_chart"] = create_tooth_chart(stage)
        game_state["tooth_chart_version"] = TOOTH_CHART_VERSION
    sync_teeth_count(game_state)


def sync_teeth_count(game_state: Dict) -> None:
    chart = game_state.get("tooth_chart", [])
    visible = [tooth for tooth in chart if tooth.get("visible", True)]
    missing = sum(1 for tooth in visible if tooth.get("status") in {"lost_permanent", "lost_temp"})
    present = sum(1 for tooth in visible if tooth.get("status") not in {"lost_permanent", "lost_temp"})
    max_teeth = 20 if game_state.get("tooth_stage", "child") == "child" else 28
    game_state["teeth_count"] = present
    game_state["teeth_missing"] = missing
    game_state["teeth_max"] = max_teeth


def upgrade_to_adult(game_state: Dict) -> bool:
    if game_state.get("tooth_stage") == "adult":
        return False
    new_chart: List[Dict] = []
    for bp in BLUEPRINTS.values():
        entry = _make_tooth_entry(bp, "adult")
        existing = _find_tooth(game_state, bp.id)
        if existing:
            status = existing.get("status", "healthy")
            if status == "lost_temp":
                status = "healthy"
            entry["status"] = status
            entry["permanent_loss"] = existing.get("permanent_loss", False)
        new_chart.append(entry)
    game_state["tooth_chart"] = new_chart
    game_state["tooth_stage"] = "adult"
    game_state["tooth_chart_version"] = TOOTH_CHART_VERSION
    sync_teeth_count(game_state)
    return True


def _find_tooth(game_state: Dict, tooth_id: str) -> Optional[Dict]:
    chart = game_state.get("tooth_chart", [])
    for tooth in chart:
        if tooth.get("id") == tooth_id:
            return tooth
    return None


def _iter_teeth(game_state: Dict, *, kinds: Optional[Sequence[str]] = None,
                statuses: Optional[Sequence[str]] = None,
                visible_only: bool = True) -> List[Dict]:
    chart = game_state.get("tooth_chart", [])
    result: List[Dict] = []
    for tooth in chart:
        if visible_only and not tooth.get("visible", True):
            continue
        if kinds and tooth.get("kind") not in kinds:
            continue
        if statuses and tooth.get("status") not in statuses:
            continue
        result.append(tooth)
    return result


def lose_primary_tooth(game_state: Dict, count: int = 1) -> List[str]:
    stage = game_state.get("tooth_stage", "child")
    if stage != "child":
        return lose_random_teeth(game_state, count=count, permanent=False, kinds=(
            "central_incisor",
            "lateral_incisor",
            "canine",
        ))
    preferred_order = [
        "UL1", "UR1", "LL1", "LR1",
        "UL2", "UR2", "LL2", "LR2",
        "UL3", "UR3", "LL3", "LR3",
        "UL4", "UR4", "LL4", "LR4",
        "UL5", "UR5", "LL5", "LR5",
    ]

    candidates = {
        tooth["id"]: tooth
        for tooth in _iter_teeth(game_state, kinds=(
            "primary_central_incisor",
            "primary_lateral_incisor",
            "primary_canine",
            "primary_first_molar",
            "primary_second_molar",
        ))
        if tooth.get("status") == "healthy"
    }

    ordered_ids = preferred_order + [tid for tid in candidates if tid not in preferred_order]

    lost_ids: List[str] = []
    for tooth_id in ordered_ids:
        if count <= 0:
            break
        tooth = candidates.get(tooth_id)
        if not tooth:
            continue
        tooth["status"] = "lost_temp"
        tooth["permanent_loss"] = False
        lost_ids.append(tooth_id)
        count -= 1

    sync_teeth_count(game_state)
    return lost_ids


def damage_random_tooth(game_state: Dict, kinds: Optional[Sequence[str]] = None) -> Optional[str]:
    if kinds is None:
        kinds = (
            "central_incisor",
            "lateral_incisor",
            "canine",
            "first_premolar",
            "second_premolar",
            "first_molar",
            "second_molar",
            "primary_first_molar",
            "primary_second_molar",
        )
    candidates = _iter_teeth(game_state, kinds=kinds, statuses=("healthy", "stained"))
    if not candidates:
        return None
    target = random.choice(candidates)
    target["status"] = "damaged"
    target["permanent_loss"] = False
    sync_teeth_count(game_state)
    return target["id"]


def stain_teeth(game_state: Dict, count: int = 4) -> List[str]:
    candidates = _iter_teeth(game_state, kinds=(
        "first_premolar",
        "second_premolar",
        "first_molar",
        "second_molar",
        "primary_first_molar",
        "primary_second_molar",
    ), statuses=("healthy",))
    if not candidates:
        return []
    samples = random.sample(candidates, k=min(count, len(candidates)))
    result: List[str] = []
    for tooth in samples:
        tooth["status"] = "stained"
        tooth["permanent_loss"] = False
        result.append(tooth["id"])
    sync_teeth_count(game_state)
    return result


def whiten_teeth(game_state: Dict) -> int:
    altered = 0
    for tooth in _iter_teeth(game_state, visible_only=False):
        if tooth.get("status") in {"stained", "damaged"} and not tooth.get("permanent_loss"):
            tooth["status"] = "healthy"
            altered += 1
    sync_teeth_count(game_state)
    return altered


def lose_specific_teeth(game_state: Dict, tooth_ids: Iterable[str], *,
                        permanent: bool = True) -> List[str]:
    affected: List[str] = []
    for tooth_id in tooth_ids:
        tooth = _find_tooth(game_state, tooth_id)
        if tooth and tooth.get("visible", True):
            tooth["status"] = "lost_permanent" if permanent else "lost_temp"
            tooth["permanent_loss"] = permanent
            affected.append(tooth_id)
    sync_teeth_count(game_state)
    return affected


def lose_random_teeth(game_state: Dict, count: int = 1, *, permanent: bool = True,
                      kinds: Optional[Sequence[str]] = None) -> List[str]:
    if kinds is None:
        kinds = (
            "central_incisor",
            "lateral_incisor",
            "canine",
            "first_premolar",
            "second_premolar",
            "first_molar",
            "second_molar",
            "primary_central_incisor",
            "primary_lateral_incisor",
            "primary_canine",
            "primary_first_molar",
            "primary_second_molar",
        )
    candidates = _iter_teeth(
        game_state,
        kinds=kinds,
        statuses=("healthy", "stained", "damaged", "prosthetic"),
    )
    if not candidates:
        return []
    chosen = random.sample(candidates, k=min(count, len(candidates)))
    return lose_specific_teeth(game_state, [tooth["id"] for tooth in chosen], permanent=permanent)


def add_prosthetics(game_state: Dict, count: int = 2) -> List[str]:
    missing = _iter_teeth(game_state, statuses=("lost_permanent",), visible_only=False)
    if not missing:
        return []
    result: List[str] = []
    for tooth in missing[:count]:
        tooth["status"] = "prosthetic"
        tooth["permanent_loss"] = True
        result.append(tooth["id"])
    sync_teeth_count(game_state)
    return result


def repair_damaged_teeth(game_state: Dict) -> int:
    repaired = 0
    for tooth in _iter_teeth(game_state, statuses=("damaged",), visible_only=False):
        tooth["status"] = "healthy"
        tooth["permanent_loss"] = False
        repaired += 1
    sync_teeth_count(game_state)
    return repaired


def describe_teeth(ids: Sequence[str]) -> str:
    if not ids:
        return ""
    if len(ids) == 1:
        return ids[0]
    return "、".join(ids)


def get_tooth_label(stage: str, tooth_id: str) -> str:
    tooth = BLUEPRINTS.get(tooth_id)
    if not tooth:
        return tooth_id
    if stage == "adult":
        kind = tooth.kind_adult or tooth.kind_child
        return ADULT_LABEL_MAP.get(kind, tooth_id)
    kind = tooth.kind_child or tooth.kind_adult
    return CHILD_LABEL_MAP.get(kind, tooth_id)


def get_tooth_short_label(stage: str, tooth_id: str) -> str:
    label = get_tooth_label(stage, tooth_id)
    return SHORT_LABEL_MAP.get(label, label)
