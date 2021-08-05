from lib.bot import SFBot
import distutils.core


def openSecrets():
    f = open('secrets.txt', 'r')
    secret = [x.strip() for x in f.read().splitlines()]
    f.close
    return secret

def display_options(d): 
    for k, v in d.items():
        print(f"{k}) {v[0]}")

def display_pricebooks():
    pricebooks = {
        '1': '40188-HKD-SALE',
        '2': 'EMP-HKD-PROMO',
        '3': '49188-JPY-SALE',
        '4': 'EMP-JPY-PROMO',
        '5': '59188-AUD-SALE',
        '6': '55188-NZD-SALE',
        '7': '60188-GBP-SALE',
        '8': '64188-EUR-SALE',
        '9': '65188-EUR-SALE',
        '10': '66188-EUR-SALE',
        '11': '66198-CHF-SALE'
    }
    print("Pricebooks: ")
    for k, v in pricebooks.items():
        print(f"{k}) {v}")
    choice = input("Enter PriceBook > ").strip()
    return pricebooks[choice]

def display_actions():
    actions = {
        "A": ["Primary and/or Secondary Categorize", "my_bot.assign_primary_secondary_categories()"], 
        "B": ["Edit Product Data", "my_bot.edit_product_data()"], 
        "C": ["Fill Missing Image", "my_bot.fill_missing_image()"], 
        "D": ["Change Front Facing Color", "my_bot.update_front_color()"], 
        "E": ["Update Category Position", "my_bot.update_category_position(url)"], 
        "F": ["Search Many Products", "my_bot.search_many_products(products)"], # NEW FEATURE!!!
        "G": ["Delete Sale Price Book", "my_bot.delete_price_book(price_book)"] # NEW FEATURE!!!
        "H": ["Create Variation PID", "my_bot.create_variations()"] # NEW FEATURE!!!
        
        # TODO
        # "G": "Update Product Attributes",
        }
    display_options(actions)
    option = input("Choose an option > ")
    return [actions, option]
    
def run():
    secret = openSecrets()
    twoAuth, email, password = secret 
    twoAuth = bool(distutils.util.strtobool(twoAuth))
    prompt = "Enter your site preference:\nHK: Hong Kong\nJP: Japan\nUK: EMEA\nAU: AU/NZ\nKR: Korea\n"
    print(prompt)
    site = input("Enter Site > ").strip()
    
    # ask user to choose action
    actions, option = display_actions()
    
    url = None
    products = None
    price_book = None
    
    if option == "E":
        url = input("Enter category url > ")
    elif option == "F":
        products = [x.strip() for x in input("Enter Products > ").splitlines()]
        products = list(dict.fromkeys(products))
    elif option == "I":
        price_book = display_pricebooks()
        
    # create Bot
    my_bot = SFBot(email, password, twoAuth, site)
    
    if option == "E":
        eval(actions[option][1], {"my_bot": my_bot}, {"url": url})
    elif option == "F":
        eval(actions[option][1], {"my_bot": my_bot}, {"products": products})
    elif option == "G":
        eval(actions[option][1], {"my_bot": my_bot}, {"price_book": price_book})
    else:
        eval(actions[option][1])
    
    prompt = "Finished!!! 😃"
    print(prompt)
    
if __name__ == "__main__":
    run()
