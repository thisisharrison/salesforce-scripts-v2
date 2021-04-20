from lib.bot import SFBot


def openSecrets():
    f = open('secrets.txt', 'r')
    secret = [x.strip() for x in f.read().splitlines()]
    f.close
    return secret


def run():
    secret = openSecrets()
    email, password = secret 
    prompt = "Enter your site preference:\nHK: Hong Kong\nJP: Japan\nUK: EMEA\nAU: AU/NZ"
    print(prompt)
    site = input("Enter Site > ").strip()
    my_bot = SFBot(email, password, site)
    mapping = my_bot.getCategories()
    my_bot.navProducts()
    my_bot.setCategories(mapping[0], mapping[1])
    prompt = "Finished!!! 😃"
    print(prompt)
    
    
if __name__ == "__main__":    
    run()

