from app.app_classes import ActivityChoiceMenu
from app.core import User, Session

if __name__ == '__main__':
    # =============================================================================================
    # CREATE SESSION
    # =============================================================================================

    with Session(user=User('tom', 'tom')) as new_session:
        # =========================================================================================
        # ACTIVITIES MENU
        # =========================================================================================
        activity_choice = ActivityChoiceMenu()
        # =========================================================================================
        # CATEGORIES MENU
        # =========================================================================================
        category_choice_menu = activity_choice()
        # =========================================================================================
        # PRODUCTS MENU
        # =========================================================================================
        product_choice_menu = category_choice_menu()
        # =========================================================================================
        # PRODUCT AND SUBSTITUTE
        # =========================================================================================
        product = product_choice_menu()
        print(product)
        substitute_id = product.print_substitute()
        product.save_to_favorites(new_session.user.id, substitute_id)

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
