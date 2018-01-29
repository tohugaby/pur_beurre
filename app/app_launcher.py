from app.app_classes import ActivityChoiceMenu
from app.core import User, Session, ChoiceMenu

if __name__ == '__main__':
    # =============================================================================================
    # CREATE SESSION
    # =============================================================================================

    with Session(user=User('tom', 'tom')) as new_session:
        # =========================================================================================
        # ACTIVITIES MENU
        # =========================================================================================
        actual_menu = ActivityChoiceMenu()
        # =========================================================================================
        # CATEGORIES  PRODUCTS OR FAVORITES MENU
        # =========================================================================================
        while isinstance(actual_menu,ChoiceMenu):
            actual_menu = actual_menu()
        # =========================================================================================
        # PRODUCT AND SUBSTITUTE
        # =========================================================================================
        product = actual_menu()


    # if scenario 1:
    #     categorie
    #     produit
    #     afficher substitut
    #
    # elif scenario 2:
    #     favoris
    #     afficher substitut
    #
    # else:
    #     quitter
