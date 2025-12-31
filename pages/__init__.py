"""
ページモジュール
各ページの表示関数を提供
"""
from pages.reception import show_reception_page
from pages.quiz import show_caries_quiz_page, show_perio_quiz_page
from pages.job_experience import show_job_experience_page, auto_complete_job_experience
from pages.checkup import show_checkup_page
from pages.goal import show_goal_page, show_line_coloring_page
from pages.staff import show_staff_management_page
from pages.utils import navigate_to, load_settings, debug_log, load_events_config, save_active_event, get_board_file_for_age

__all__ = [
    'show_reception_page',
    'show_caries_quiz_page',
    'show_perio_quiz_page',
    'show_job_experience_page',
    'auto_complete_job_experience',
    'show_checkup_page',
    'show_goal_page',
    'show_line_coloring_page',
    'show_staff_management_page',
    'navigate_to',
    'load_settings',
    'debug_log',
    'load_events_config',
    'save_active_event',
    'get_board_file_for_age',
]
