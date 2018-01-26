from app.app_classes import ActivityChoiceMenu
from app.core import User, Session

if __name__ == '__main__':
    # =============================================================================================
    # CREATE SESSION
    # =============================================================================================

    new_session = Session(User('tom', 'tom'))

    # =============================================================================================
    # ACTIVITY MENU
    # =============================================================================================
# TODO: find another system to automaticaly save previous menu in Session instance . maybe with
    # a decorator on call methods or a context manager
    activity_choice = ActivityChoiceMenu()
    category_choice_menu = activity_choice()
    product_choice_menu = category_choice_menu()
    Session.previous_menu = category_choice_menu
    product = product_choice_menu()
    Session.previous_menu = product_choice_menu
    print(product)
    Session.previous_menu = product
    print(product.get_best_substitutes())



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
