from app.menus import ActivityChoiceMenu
from core.authenthication import User
from core.menus import ChoiceMenu
from core.sessions import Session

if __name__ == '__main__':
    # =============================================================================================
    # CREATE SESSION
    # =============================================================================================
    while True:
        with Session(user=User('tom', 'tom')) as new_session:
            # =========================================================================================
            # ACTIVITIES MENU
            # =========================================================================================
            actual_menu = ActivityChoiceMenu()
            # =========================================================================================
            # CATEGORIES  PRODUCTS OR FAVORITES MENU
            # =========================================================================================
            while isinstance(actual_menu, ChoiceMenu):
                actual_menu = actual_menu()
            # =========================================================================================
            # PRODUCT AND SUBSTITUTE
            # =========================================================================================
            product = actual_menu()
