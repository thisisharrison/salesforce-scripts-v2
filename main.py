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
    
def run():
    secret = openSecrets()
    twoAuth, email, password = secret 
    twoAuth = bool(distutils.util.strtobool(twoAuth))
    prompt = "Enter your site preference:\nHK: Hong Kong\nJP: Japan\nUK: EMEA\nAU: AU/NZ\nKR: Korea\n"
    print(prompt)
    site = input("Enter Site > ").strip()
    
    # ask user to choose action
    actions = {
        "A": ["Primary and/or Secondary Categorize", "my_bot.assign_primary_secondary_categories()"], # TEST: 
        "B": ["Edit Product Data", "my_bot.edit_product_data()"], # TEST: OK
        "C": ["Fill Missing Image", "my_bot.fill_missing_image()"], # TEST: OK
        "D": ["Change Front Facing Color", "my_bot.update_front_color()"], # TEST: OK
        "E": ["Update Category Position", "my_bot.update_category_position(url)"], # TEST: OK
        # TODO
        # "E": "Search Products",
        # "G": "Update Product Attributes",
        # "H": "Create Variation PID",
        # "I": "Delete Sale Price Book",
        # "J": ""
        }
    display_options(actions)
    option = input("Choose an option > ")
    url = None
    if option == "E":
        url = input("Enter category url > ")
    
    # create Bot
    my_bot = SFBot(email, password, twoAuth, site)
    
    # while True: 
        # if action picked and bot is alive 
            # take action by doing:
            # eval(option + "()")
        # prompt new action
      
    # mapping = my_bot.getCategories()
    # my_bot.navProducts()
    # my_bot.setCategories(mapping[0], mapping[1])
    
    if option != "E":
        eval(actions[option][1])
    else:
        eval(actions[option][1], {"my_bot": my_bot}, {"url": url})

    
    prompt = "Finished!!! 😃"
    print(prompt)
    
if __name__ == "__main__":
    run()
