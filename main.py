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

def display_refinements():
    urls = input("Enter Category URL(s) > ").splitlines()
    
    # Select last refinement using the attribute type
    attr_types = {
        1: 'By Attribute (Style Number)',
        2: 'By Attribute (ID)',
        3: 'By Attribute (Type)',
        4: 'By Attribute (Size)'
        }
    for k, v in attr_types.items():
        print(f"{k}) {v}")
    index = int(input("Enter Attribute Type > "))
    
    return [urls, index]

def display_actions():
    actions = {
        "A": ["Primary and/or Secondary Categorize", "my_bot.assign_primary_secondary_categories()"], 
        "B": ["Edit Product Data", "my_bot.edit_product_data()"], 
        "C": ["Fill Missing Image", "my_bot.fill_missing_image()"], 
        "D": ["Change Front Facing Color", "my_bot.update_front_color()"], 
        "E": ["Update Category Position", "my_bot.update_category_position(url)"], 
        "F": ["Search Many Products", "my_bot.search_many_products(products)"],
        "G": ["Delete Sale Price Book", "my_bot.delete_price_book(price_book)"], 
        "H": ["Create Variation PID", "my_bot.create_variations()"], # NEW FEATURE!!!
        "I": ["Rewrite Search Refinement", "my_bot.bucketRefinementUpdate(urls, index)"] 
        
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
    
    if option == "E":
        # Update Category Positions
        url = input("Enter category url > ")
    elif option == "F":
        # Search Many Products
        products = [x.strip() for x in input("Enter Products > ").splitlines()]
        products = list(dict.fromkeys(products))
    elif option == "G":
        # Remove Sale Price
        price_book = display_pricebooks()
    elif option == "I":
        # Search Refinements
        urls, index = display_refinements()
        
    # create Bot
    my_bot = SFBot(email, password, twoAuth, site)
    
    if option == "E":
        eval(actions[option][1], {"my_bot": my_bot}, {"url": url})
    elif option == "F":
        eval(actions[option][1], {"my_bot": my_bot}, {"products": products})
    elif option == "G":
        eval(actions[option][1], {"my_bot": my_bot}, {"price_book": price_book})
    elif option == "I":
        eval(actions[option][1], {"my_bot": my_bot}, {"urls": urls, "index": index})
    else:
        eval(actions[option][1])
    
    prompt = "Finished!!! 😃"
    print(prompt)
    
if __name__ == "__main__":
    run()
