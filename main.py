from lib.bot import SFBot
import distutils.core


def openSecrets():
    f = open('secrets.txt', 'r')
    secret = [x.strip() for x in f.read().splitlines()]
    f.close
    return secret


def run():
    secret = openSecrets()
    twoAuth, email, password = secret 
    twoAuth = bool(distutils.util.strtobool(twoAuth))
    prompt = "Enter your site preference:\nHK: Hong Kong\nJP: Japan\nUK: EMEA\nAU: AU/NZ\nKR: Korea\n"
    print(prompt)
    site = input("Enter Site > ").strip()
    
    # ask user to choose action
    # create Bot
    # while True: 
        # if action picked
            # take action
        # prompt new action
    
    
    my_bot = SFBot(email, password, twoAuth, site)
    mapping = my_bot.getCategories()
    my_bot.navProducts()
    my_bot.setCategories(mapping[0], mapping[1])
    prompt = "Finished!!! 😃"
    print(prompt)
    
    
if __name__ == "__main__":
    run()
