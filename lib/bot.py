from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import csv 
from bs4 import BeautifulSoup
import requests
import os
from pathlib import Path
import datetime
from lib.price_utils import getSkus, mergeSort, merge, wildCardDict
import pdb


class SFBot:
    def __init__(self, username, password, twoAuth, site):
        # Locate Chrome Driver
        home = str(Path.home())
        try:
            # Windows
            driver_loc = home + '\chromedriver'
            self.driver = webdriver.Chrome(driver_loc)
        except: 
            # Mac
            driver_loc = home + '/chromedriver'
            self.driver = webdriver.Chrome(driver_loc)
            
        # Set implicit wait time
        self.driver.implicitly_wait(5)
        
        # Maximize window
        self.driver.maximize_window()
        
        # Secrets
        self.username = username
        self.password = password
        self.twoAuth = twoAuth
        self.site = site
        
        # CSV File for Category Mapping
        csv_folder = Path("csv/")
        file_to_open = csv_folder / ("categories_" + self.site + ".csv")
        self.category_csv = file_to_open
        
        # Go to login site
        self.driver.get("https://staging-eu01-lululemon.demandware.net/on/demandware.store/Sites-Site/default/ViewLogin-StartAM")
        self.driver.find_element_by_xpath("//button[contains(text(), 'Log In')]")\
            .click()
        self.login()


    def login(self):

        try:
            if self.twoAuth:
                """ User needs two factor auth """
                # Enter username
                self.driver.find_element_by_xpath("//input[@name=\"callback_0\"]")\
                    .send_keys(self.username)
                self.driver.find_element_by_xpath('//input[@type="submit"]')\
                    .click()
                # Enter password
                self.driver.find_element_by_xpath("//input[@name=\"callback_1\"]")\
                    .send_keys(self.password)
                self.driver.find_element_by_xpath('//input[@type="submit"]')\
                    .click()
                message = "You are using Two-Factor Authentication.\nI need some help, could you finish loggin us in?\nOnce logged in, enter 'y'."
                self.helpMeHuman(message)
                
            else:
                # Enter username
                self.driver.find_element_by_xpath("//input[@name=\"callback_0\"]")\
                    .send_keys(self.username)
                self.driver.find_element_by_xpath('//input[@type="submit"]')\
                    .click()
                # Enter password
                self.driver.find_element_by_xpath("//input[@name=\"callback_1\"]")\
                    .send_keys(self.password)
                self.driver.find_element_by_xpath('//input[@type="submit"]')\
                    .click()
        
        except Exception as error:
            print("==========================")
            print(error)
            print("Retry logging in...")
            print("==========================")
            self.login()
        
        # Select Site preference
        select_map = {
            'JP': '1',
            'UK': '8',
            'HK': '5',
            'AU': '7',
            'KR': '10'
            }
        idx = select_map[self.site]
        script = 'arguments[0].selectedIndex = {}; arguments[0].onchange();'.format(idx)
        sites = self.driver.find_element_by_xpath('//select[@id="SelectedSiteID"]')
        self.driver.execute_script(script, sites)
        
        # Confirm you logged in
        print("==========================")
        print("Logged in as: ", self.username)
        print("==========================")

        sleep(3)

    """ Navigate to Product Page """
    def navProducts(self):
        
        self.driver.get("https://staging-eu01-lululemon.demandware.net/on/demandware.store/Sites-Site/default/ViewProductList_52-List?SelectedMenuItem=prod-cat&CurrentMenuItemId=prod-cat&CatalogItemType=Product")
        
        try:
            self.driver.find_element_by_link_text('By ID').click()
        except:
            pass
        
        print("==========================")
        print("Product Page")
        print("==========================")
    
            
    """ Search for Products in Products Tool """
    def searchProducts(self, products):
        # Return if no products
        if len(products) == 0:
            return 

        # The search input textarea
        searchInput = self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")
        # Transform array to string with JS and update searchInput
        self.driver.execute_script("arguments[0].value = {}.toString()".format(products), searchInput) 
        
        print("==========================")
        print("Searching: ", products)
        print("==========================")

        SimSearch = self.driver.find_element_by_xpath('//*[@id="IDListDiv"]/form')
        try:
            self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]').click()
        except Exception as error:
            try: 
                SimSearch.submit()
            except:
                self.helpMeHuman("Help Me Click Enter")

    """ Get Primary and SubCategories Assignment from CSV to pass to #setCategories """
    def getCategories(self):
        
        pCats = {}
        sCats = {}
            
        with open (self.category_csv, newline = '', encoding='UTF-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
    
            for row in reader: 
                master = row['master']
                primary = row['primaryCategory']
                secondary = [cat.strip() for cat in row['subCategories'].split(',')]
                navigation = [nav.strip() for nav in row['navigationId'].split(',')]
                
                # no primary for this product
                if len(primary) < 1:
                    pass
                else:
                    # add to primary list
                    if primary in pCats.keys():
                        for nav in navigation:
                            if nav in pCats[primary].keys():
                                pCats[primary][nav].add(master)
                            else: 
                                pCats[primary][nav] = set([master])
                    else: 
                        pCats[primary] = {}
                        # remove duplicate masters 
                        for nav in navigation:
                            pCats[primary][nav] = set([master])
                            
                for sec in secondary:
                    if len(sec) < 1:
                        continue
                    if sec in sCats.keys():
                        for nav in navigation:
                            if nav in sCats[sec].keys():
                                sCats[sec][nav].add(master)
                            else:
                                sCats[sec][nav] = set([master])
                    else:
                        sCats[sec] = {}
                        for nav in navigation:
                            sCats[sec][nav] = set([master])
                        
        print("==========================")
        print("Primary Categories to merchandise: ",pCats)
        print("==========================")
        print("Sub Categories to merchandise: ",sCats)
        print("==========================")
        
        return [pCats, sCats]

    """ Assign Primary and Subcategories to Products """
    def setCategories(self, primary, secondary):
            
        while primary or secondary: 

            try: 
                category = next(iter(primary))
                isPrimary = True
                job = "Primary Categorized"
            except:
                category = next(iter(secondary))
                isPrimary = False
                job = "Secondary Categorized"
                
            print("==========================")
            print("Merchandising: ", category)
            print("==========================")
                    
            try:
                navigations = primary[category]
            except: 
                navigations = secondary[category]

            for nav in navigations: 
                products = list(navigations[nav])
                
                self.searchProducts(products)
                
                self.editAll_ProductTool()
                
                print("==========================")
                print("Found: ", products)
                print("==========================")
                
                self.driver.find_element_by_xpath("//input[@value='AssignProductToCatalogCategory']").click()
                
                try:
                    self.driver.find_element_by_xpath('//button[@name=\"selectAction\"]').click()
                except:
                    script = """document.querySelector("button[name='selectAction']").click()"""
                    self.driver.execute_script(script)
                
                try:
                    self.driver.find_element_by_xpath('//*[@id="ext-gen77"]').click()
                except:
                    script = """"document.querySelector('.x-btn-text.listview_disabled').click()"""
                    self.driver.execute_script(script)
                
                self.driver.execute_script("document.querySelector('.x-form-trigger.x-form-arrow-trigger').click()")
                
                sleep(2)
                
                select_nav = """
                const navs = Array.from(document.querySelector('.x-layer.x-combo-list').querySelectorAll('.x-combo-list-item'));
                for (let nav of navs) {{
                        if (nav.textContent.toLowerCase().includes('{}'.toLowerCase())) {{
                                nav.click();
                        }}
                }}
                """.format(nav)
                
                self.driver.execute_script(select_nav)
                
                print("==========================")
                print("Select Nav: ", nav)
                print("==========================")
                
                try:
                    search = self.driver.find_element_by_xpath("//input[@name=\"ext-comp-1009\"]").send_keys(category)
                except:
                    sleep(2)
                    search = self.driver.find_element_by_xpath("//input[@name=\"ext-comp-1009\"]").send_keys(category)
                
                print("==========================")
                print("Categorizing: ", products)
                print("==========================")
                
                try:
                    self.driver.find_element(By.ID, "ext-comp-1009").send_keys(Keys.ENTER)
                except:
                    search = self.driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/form/table[1]/tbody/tr[2]/td[2]/div/div/div/div/div[2]/div/div[1]/div/table/tbody/tr/td[2]/div/span/img[1]')
                    search.click()

                sleep(2)

                select_cat = """
                const option = document.querySelector(`[data-automation*="{}"]`);
                if (!option) {{
                        return false;
                }} else {{
                    option.querySelector('input').click();
                }}
                return true;
                """.format(category)
                
                cat_result = self.driver.execute_script(select_cat)

                if not cat_result:
                    message = "Category ID not found. Search ID and select the checkbox then enter 'y'."
                    self.helpMeHuman(message)


                try:
                    self.driver.find_element(By.NAME, "selectAction").click()
                except:
                    try:
                        selectAction = """document._getElementsByXPath('//button[@name="selectAction"]')[0].click();
                        """
                        self.driver.execute_script(selectAction)
                    except:
                        message = "This is embarrassing. Press 'Next' for me please! Then enter 'y'."
                        self.helpMeHuman(message)
                
                if isPrimary:
                    dropdown = self.driver.find_element_by_xpath('//select[@name="PrimaryCategoryUUID"]')
                
                    dropdown.find_element_by_xpath("//option[contains(text(), 'lululemon')]")\
                        .click()
                
                try:
                    self.driver.find_element_by_xpath('//button[@name="assignProductsAndReturn"]')\
                    .click()
                except:
                    try:
                        sleep(2)
                        self.driver.find_element_by_xpath('//button[@name="assignProductsAndReturn"]')\
                        .click()
                    except:
                        assignAction = """document._getElementsByXPath('//button[@name="assignProductsAndReturn"]')[0].click();"""
                        self.driver.execute_script(assignAction)
                
                print("==========================")    
                print("%s: %s > %s" % (job, products, category))
                print("==========================")
    
            try:
                primary.pop(category)
            except:
                secondary.pop(category)

    def helpMeHuman(self, message):
        print("\nHey %s user! I'm in a pickle here...\nCan you help me??" % (self.site))
        print("Message: " + message)
        stuck = True
        
        while stuck:
            user = input("Are we ready? > ")
            if user != 'y':
                continue
            else:
                stuck = False
                break            
        
        return
    
    def editAll_ProductTool(self):
        try:
            self.driver.find_element_by_xpath('//button[@name=\"EditAll\"]')\
                .click()
        except:
            edit_all = """
                button = document._getElementsByXPath('//button[@name=\"EditAll\"]')
                button[0].click()
            """
            self.driver.execute_script(edit_all)
    
    def assign_primary_secondary_categories(self):
        mapping = self.getCategories()
        self.navProducts()
        self.setCategories(mapping[0], mapping[1])
        
    def get_product_data(self):
        filename = "./csv/product_data.csv"
        products = []

        with open (filename, newline = '', encoding='UTF-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                pair = []
                attrs = {}
                
                master = row['master'].strip()
                pair.append(master)
                
                attrs['name'] = row['name'].strip()
                attrs['whyWeMadeThis'] = row['whyWeMadeThis'].replace('\n','').strip()
                attrs['careDescription'] = row['careDescription'].strip()
                attrs['features'] = row['features'].strip()
                attrs['fabric'] = row['fabric'].replace('\n','').strip()
                
                pair.append(attrs)
                products.append(pair)
                
        print("Changing Attributes: ",products)
        return products
    
    def selectLanguage(self, option = None):
        if not option:
            option = self.site
        
        # Select language
        try:
            lang = self.driver.find_element_by_xpath('//select[@name="LocaleID"]')
        except:
            lang = self.driver.find_element_by_xpath('//select[@name="LocaleId"]')
            
        """ SELECT LANGUAGE """
        indices = {
            'JP': '23',
            'HK': '7',
            'UK': '12',
            'DE': '19',
            'DE_DE': '20',
            'DE_LX': '21',
            'DE_SW': '22',
            }
           
        script = 'arguments[0].selectedIndex = {}; arguments[0].onchange();'.format(indices[option])
        
        self.driver.execute_script(script, lang)

        print("Language Selected")
    
    def set_product_data(self, products):
        try: 
            while products:
                pair = products[0]
                print(pair)
                
                product = pair[0]
                attrs = pair[1]
            
                self.searchProducts([product])
                self.driver.find_element_by_link_text(product).click()                    
                self.selectLanguage()
                
                try:
                    self.driver.find_element_by_link_text('Lock').click()
                except:
                    pass
                print("Unlocked")

                if attrs['name']:
                    self.changeName(attrs['name'])
                if attrs['whyWeMadeThis']:
                    self.changeWWMT(attrs['whyWeMadeThis'])
                if attrs['careDescription']:
                    self.changeCareDescription(attrs['careDescription'])
                if attrs['features']:
                    self.changeFeatures(attrs['features'])
                if attrs['fabric']:
                    self.changeFabric(attrs['fabric'])
        
                try:
                    self.driver.find_elements_by_xpath("//button[contains(text(), 'Apply')]")[0].click()
                except:
                    try:
                        self.driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/form[1]/table/tbody/tr[1]/td/table/tbody/tr/td[1]/button').click()
                    except:
                        apply_script = """document._getElementsByXPath('//*[@id="ssaForm"]/table/tbody/tr[1]/td/table/tbody/tr/td[1]/button')[0].click()"""
                        self.driver.execute_script(apply_script)
                
                print("Applied")
                        
                try:
                    self.driver.find_element_by_link_text('Unlock').click()
                except: 
                    self.driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table[2]/tbody/tr/td[1]/table/tbody/tr[3]/td/table/tbody/tr/td[2]/p[1]/a').click()
                
                print("Unlocked")
                
                self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()                
                
                done = products.pop(0)
                
                print(f"Remaining: {len(products)} products: ", products)
                
        except Exception as error:            
            print(error)
            print('Error: Remaining Pairs: ', products)            
            self.navProducts()
            self.set_product_data(products)
    
    def changeName(self, attribute):
        name = self.driver.find_element_by_xpath('//input[@name="Metaf070c9f07840c78a8b2edc1902"]')
        name.clear()                
        name.send_keys(attribute)
        
    def changeWWMT(self, attribute):
        wwmt = self.driver.find_element_by_xpath('//textarea[@id="Meta458a0dcf59c3a300e482bf9054"]')
        wwmt.clear()
        wwmt.send_keys(attribute)
        wwwt2 = self.driver.find_element_by_xpath('//textarea[@id="Meta64da50faa3659f25acdd0d1691"]')
        wwwt2.clear()
        wwwt2.send_keys(attribute)
    
    def changeCareDescription(self, attribute):
        care = self.driver.find_element_by_xpath('//textarea[@name="Metaef8f635ef33efeeecd7ae8c72f"]')
        care.clear()
        care.send_keys(attribute)
        
    def changeFeatures(self, attribute):
        feature = self.driver.find_element_by_xpath('//textarea[@name="Meta482485cfc4b410b57671f7f577"]')
        feature.clear()
        feature.send_keys(attribute)
        
        attr_value = attribute.split('\n')
        script = """
                attr_value = {}
                attr_len = attr_value.length
                for (let i = 0; i < attr_len; i++) {{
                 	container = document.getElementById('Meta525732d56b9c0454ddd1e3aed2_Container')                
                 	inputs = container.getElementsByTagName('input')                
                 	inputs[i].value = attr_value[i]                
                 	add_another = document.getElementById('Meta525732d56b9c0454ddd1e3aed2_lastRow').getElementsByTagName('a')[0]                
                 	add_another.click()                
                }}""".format(attr_value)
        self.driver.execute_script(script)
    
    def changeFabric(self, attribute):
        fabric = self.driver.find_element_by_xpath('//input[@id="Meta01b431b006b7e6bf4082c2bc8f_1"]')
        fabric.clear()
        fabric.send_keys(attribute)
    
    def edit_product_data(self):
        products = self.get_product_data()
        self.navProducts()
        self.set_product_data(products)
        
    """ Get Styles of Missing Images """
    def get_missing_image(self):
        filename = './csv/missing_images.csv'
        pairs = []
        with open (filename, newline = '', encoding='UTF-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                try:
                    """ PERSONAL MAC """
                    master = row['master']
                except:
                    """ OFFICE COMPUTER """
                    master = row['\ufeffmaster']                
                color = row['color']
                style_color = row['style_color']
                pair = [master, color, style_color]                
                pairs.append(pair)                
        print("Adding Images to > ",pairs)
        return pairs

    """ Add Missing Images for Styles"""
    def add_missing_image(self, s, pairs):
        while pairs:    
            pair = pairs[0]

            product = pair[0]
            color = pair[1]
            style_color = pair[2]
            style_color = style_color.replace("-","_")
            
            domain = "https://images.lululemon.com/is/image/lululemon/"
            avail_img = [style_color + '_' + str(i) for i in range(10) if s.get(domain + style_color + '_' + str(i)).status_code == 200]
            print("Available images -",avail_img)
            
            self.searchProducts([product])
            
            self.driver.find_element_by_link_text(product)\
                .click()
            
            try:
                self.driver.find_element_by_link_text('Lock').click()
            except:
                pass
            print("Unlocked")
            
            # Edit Image
            try:
                self.driver.find_element(By.ID, "imageSpecificationButton").click()
            except:
                button = """
                    document.querySelector('#imageSpecificationButton').click()
                """
                self.driver.execute_script(button)
            # Product Master
            try:
                self.driver.find_element_by_xpath("//span[contains(text(),'product master')]").click()
            except:
                productmaster = """
                    document.querySelector('#extdd-27').click()
                """
                self.driver.execute_script(productmaster)
            
            if self.selectColor(color):
                pass
            # Color is hidden and need to add color back
            else:
                self.driver.find_element_by_id('ext-gen98').click()
                sleep(3)
                
                color_options = self.driver.find_elements_by_class_name("x-tree-node-el.x-unselectable.x-tree-node-collapsed.x-tree-node-leaf")
                
                for el in color_options: 
                    if color.lower() in el.get_attribute("innerHTML").lower():
                        el.find_element_by_class_name('x-tree-node-cb').click()
                        popup = self.driver.find_element_by_css_selector('div.x-window-bbar')
                        popup.find_element_by_xpath("//button[contains(text(), 'OK')]").click()
                        self.selectColor(color)
                        break
 
            new_script = """
            let ul = document.querySelector('#ext-gen123')
            let div = ul.childElements()[0]
            let lis = div.childElements()
            return lis
            """
            lis = self.driver.execute_script(new_script)
            rows = [x.get_attribute('innerHTML') for x in lis]

            
            # hi-res to small 
            # add all image if missing
            for row in rows[0:4]:
                soup = BeautifulSoup(row, "html.parser")
                imgs = soup.find_all('img', {'class': 'img-mgr-image-node'})            
                count = 0
                for img in imgs:
                    for avail in avail_img:
                        if avail in img['src']: 
                            count += 1
                if len(avail_img) == count:
                    print("This Row is OK")
                else:
                    # Add image using count, avail img
                    row_id = soup.find('div')['id']
                    sel = self.driver.find_element_by_id(row_id)
                    el = self.driver.execute_script("return arguments[0].nextSibling", sel)
                                     
                    while len(avail_img) != count:
                        soup = BeautifulSoup(el.get_attribute('innerHTML'), "html.parser")
                        new_img = soup.find_all('img')[-2]
                        new_ele = self.driver.find_element_by_id(new_img['id'])
                        new_ele.click()
                        self.driver.find_element_by_id('detail_path').send_keys(avail_img[count])
                        count += 1

            # Check Swatch
            swatch = avail_img[0].split("_")[1]
            if swatch[0:2] == "00":
                pass
            else:
                swatch = swatch[1:]
                                
            swatch_row = rows[-1]
            soup = BeautifulSoup(swatch_row, "html.parser")
            swatch_row_id = soup.find('div')['id']
            sel = self.driver.find_element_by_id(swatch_row_id)
            el = self.driver.execute_script("return arguments[0].nextSibling", sel)
            
            soup = BeautifulSoup(el.get_attribute('innerHTML'), "html.parser")
            swatch_img = soup.find_all('img')
            
            swatch_is_good = False
            for img in swatch_img:
                if swatch in img['src']:
                    swatch_is_good = True
            if not swatch_is_good:
                input_el = swatch_img[-2]
                swatch_ele = self.driver.find_element_by_id(input_el['id'])
                swatch_ele.click()
                self.driver.find_element_by_id('detail_path').send_keys(swatch)
            
            sleep(2)
            
            try:
                save = self.driver.find_elements_by_xpath('//*[@id="ext-gen79"]')
                save.click()
            except:
                self.driver.find_element_by_xpath("//button[contains(text(), 'Save')]")\
                    .click()
            
            done = pairs.pop(0)

            sleep(5)
                
            try: 
                self.driver.find_element_by_link_text('Unlock').click()
            except Exception as e:
                # print(e)
                try:
                    sleep(5)
                    self.driver.find_element_by_xpath('//a[contains(text(), "Unlock")]').click()
                except Exception as e:
                    # print(e)
                    unlock = """
                        a = document._getElementsByXPath('//a[contains(text(), "Unlock")]')
                        a[0].click()
                    """
                    self.driver.execute_script(unlock)
                
            print("Applied")
                
            self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()
                
            print("Complete pair -", pair)
        
    """ Select Color to Add Images to """
    def selectColor(self, color):
        show_colors = self.driver.find_element_by_css_selector('ul.x-tree-node-ct').find_elements_by_class_name('x-tree-node')
        
        color_search = "color = \'{}\'".format(color.lower())
        
        for el in show_colors: 
            if color_search in el.get_attribute("innerHTML").lower():
                soup = BeautifulSoup(el.get_attribute("innerHTML"), "html.parser")
                break
        
        try:
            idx = soup.find('a').find('span').get('id')
            self.driver.find_element_by_id(idx).click()
            return True
        except Exception as e:
            print(e)
            return False
    
    def fill_missing_image(self):
        self.navProducts()
        s = requests.Session()
        pairs = self.get_missing_image()
        self.add_missing_image(s, pairs)
       
    """ Get Front Facing Colors from CSV """
    def get_front_color(self):
        filename = './csv/front_colors.csv'
        variations = []

        with open (filename, newline = '', encoding='UTF-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                
                try:
                    """ PERSONAL MAC """
                    master = row['master']
                except:
                    """ OFFICE COMPUTER """
                    master = row['\ufeffmaster']
                
                colors = [color.strip() for color in row['colors'].split(",")]
                
                pair = [master, colors]
                
                variations.append(pair)
                
        print("Variations: ",variations)
        return variations
    
    """ Update Front Color """
    def set_front_color(self, variations):
        try:
            while variations: 
                # Takes first pair, when finished pop(0)
                pair = variations[0]
                print(pair)
                
                product = pair[0]
                colors = [color.lower() for color in pair[1]]
                first_color = colors[0]
                
                print("Product -", product)
                print("Colors -", colors)
                print("First Color -", first_color)
                
                search = self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")
                search.send_keys(product)
                               
                self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]')\
                    .click()
                
                self.driver.find_element_by_link_text(product)\
                    .click()
                
                self.driver.find_element_by_link_text('Variations').click()
                
                self.driver.find_element_by_link_text('color ⁄ color').click()
                
                try:
                    self.driver.find_element_by_link_text('Lock').click()
                except: 
                    pass
                
                all_button = """
                    button = document._getElementsByXPath('//button[@name="PageSize"]');
                    button[1].click()
                """
                try:
                    self.driver.execute_script(all_button)                
                except: 
                    pass
                
                color_script = """
                            table = document._getElementsByXPath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/form/table[4]');
                            rows = table[0];
                            inputs = rows.querySelectorAll('input');
                            
                            length = inputs.length
                            colors = {}
                            
                            for (let i = 0; i < length; i++) {{
                                name = inputs[i].value.toLowerCase();    
                                if (colors.include(name)) {{
                                        inputs[i-2].click();
                                }}
                            }}
                            button = rows.querySelector('input[name="moveTop"]');
                            button.click();      
                """.format(colors)
                self.driver.execute_script(color_script)             

                self.driver.find_element_by_link_text('Unlock').click()
                print("Applied")
                
                self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()
                
                done = variations.pop(0)
                print("Complete pair -", pair)
        except Exception as error:
            print(error)
            raise
    
    def update_front_color(self):
        variations = self.get_front_color()
        self.navProducts()
        self.set_front_color(variations)
        
    def update_category_position(self, url):
        
        mapping = self.getNewCategoryPosition()
        
        self.driver.get(url)
        self.expandCategoryPosition()
        
        self.categoryPositionClear()
        self.updatePositionsButton()
        self.expandCategoryPosition()
        
        # update new positions
        self.categoryPositionUpdate(mapping)

        self.driver.find_element_by_xpath("//body").send_keys(Keys.END)
        self.updatePositionsButton()
    
    def updatePositionsButton(self):
        button = """document._getElementsByXPath("//button[@id='updatePositions']")[0].click()"""
        self.driver.execute_script(button)

    def expandCategoryPosition(self):
        self.driver.find_element_by_xpath("//body").send_keys(Keys.END)
        sleep(2)
        try:
            self.driver.find_element_by_xpath('//button[text()="All"]').click()
        except:
            pass
        
    def getNewCategoryPosition(self):
        with open('./csv/change_category_position.csv', encoding = 'utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            mapping = {}
            
            for row in reader:
                ID = row['ID']
                position = row['position']
                mapping[position] = ID
            
            return mapping
    
    def categoryPositionClear(self):
        table = self.driver.find_element_by_xpath('//input[@name="ProductFormSubmitted"]/following-sibling::table')
        input_fields = table.find_elements_by_xpath('//*[contains(@name, "NewPosition")]')
        
        for i in input_fields:
            if i.get_attribute("value"):
                print(i.get_attribute("value"))
                try:
                    i.click()
                    i.clear()
                    self.driver.execute_script("arguments[0].removeAttribute('value')", i)
                except:
                    self.driver.execute_script("arguments[0].scrollIntoView();", i)
                    self.driver.execute_script("window.scrollBy(0,-100)")
                    i.click()
                    i.clear()
                    self.driver.execute_script("arguments[0].removeAttribute('value')", i)
            else:
                continue
        return
        
    def categoryPositionUpdate(self, mapping):
        for k, v in mapping.items():
            print("{} => {}".format(v, k))            
            script = """inputs = document._getElementsByXPath('//*[contains(text(),"{}")]')[0].parentNode.parentNode.getElementsByTagName('input');
            if (inputs) {{
            for (let i = 0; i < inputs.length; i++) {{
                    if(!inputs[i].getAttribute('name')) continue
                    if (inputs[i].getAttribute('name').includes('NewPosition_')) {{
                            inputs[i].click();
                            inputs[i].value = {};
                            }}
                    else
                        continue;
                    }}
            }}
            """.format(v,k)
            
            self.driver.execute_script(script)
        return
    
    def copy_product_status(self, products):
        filename = "./search/" + self.site + "_searchResult.txt"
        with open(filename, "w", encoding='utf-8') as file:
            file.write("style\tname\tstatus\n")
            file.close()
            
        isFinished = True 
        while isFinished:
            if len(products) == 0:
                isFinished = False
                break
            if len(products) > 1000:
                print(len(products))
                search = products[0:1000]
                print(len(search))
                del products[0:1000]
                print("====")
                print(len(products))
                
                self.searchProducts(search)
            else: 
                
                self.searchProducts(products)
                del products[0:len(products)]
                                
            all_button = """
                    button = document._getElementsByXPath('//button[@name="PageSize"]');
                    button[button.length -1].click()
                """
            try:
                self.driver.execute_script(all_button)                
            except: 
                pass
            
            table = self.driver.find_element_by_xpath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/form/table/tbody/tr/td/table[1]')
            
            content = table.get_attribute('outerHTML')

            soup = BeautifulSoup(content, "lxml")
            trs = soup.find_all('tr')
            total = len(trs)
            counter = 1
            
            filename = "./search/" + self.site + "_searchResult.txt"
            with open(filename, "a", encoding='utf-8') as file:
                for tr in trs:                 
                    tds = tr.find_all('a',{'class':'table_detail_link'})
                    if not tds:
                        counter += 1
                        continue                
                    style = tds[0].text.strip()
                    name = tds[1].text.strip().replace('\t', ' ')
                    
                    imgs = tr.find_all('img')
                    stat = ''
                    
                    for img in imgs:    
                        try:
                            alt = img['alt']
                            stat += alt
                        except:
                            continue
                    file.write(f"{style}\t{name}\t{stat.strip()}\n")
                    counter += 1
                    print("{}/{}".format(counter, total))
                file.close()
                    
            self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]").clear()
            
    def search_many_products(self, products):
        self.navProducts()
        self.copy_product_status(products)
    
    
    def navigate_pricebook(self, price_book):
        url = 'https://staging-eu01-lululemon.demandware.net/on/demandware.store/Sites-Site/default/ViewPriceBook_52-Edit?PriceBookID='
        url = url + price_book
        self.driver.get(url)
        self.driver.find_element(By.LINK_TEXT, "Price Definitions").click() 
        self.driver.find_element(By.CSS_SELECTOR, "td:nth-child(3) > .perm_not_disabled").click()
        print(f"Entered {price_book} Price Book Page")
    
    def delete_price_wtih_wild_card(self, skuDict):
        search = self.driver.find_element_by_xpath("//input[@name=\"SearchTerm\"]")
        search.clear()
        keys = [*skuDict]
        total = len(keys)
        count = 0
        
        while keys: 
            key = keys[0]
            skus = skuDict[key]            
            search = self.driver.find_element_by_xpath("//input[@name=\"SearchTerm\"]")
            search.clear()            
            searchTerm = str(key) + '*'
            search.send_keys(searchTerm)
            self.driver.find_element_by_xpath('//button[@name=\"simpleSearch\"]').click()
            
            script = """
                let a = {};
                const i = document._getElementsByXPath('//input[@name="sku"]')
                let found = true;
                let clicked = 0
                
                if (i.length === 0) {{ 
                        found = false;
                }} else {{
                    const ar = Array.from(i);
            
                    ar.forEach((el)=> {{
                        if (a.include(el.defaultValue)) {{
                                el.click();
                                clicked += 1;
                        }}
                    }})
                    
                    if (clicked === 0) {{ found = false; }}
                }}
                return found;
            """.format(skus)
            
            event = self.driver.execute_script(script)
            
            if (event):
                deleteButton = self.driver.find_element_by_xpath('//*[@id="deleteButton"]')
                self.driver.execute_script("arguments[0].click();", deleteButton)
                confirmDelete = self.driver.find_element_by_xpath('//button[@name=\"deletePrices\"]')   
                self.driver.execute_script("arguments[0].click();", confirmDelete)
                print("Deleted: ", skus)
            else: 
                print("Sku not found", skus)
            done = keys.pop(0)
            count += 1
            
            print("{} / {}".format(count, total))
        
    def delete_price_book(self, price_book):
        skus = getSkus()
        skuSorted = mergeSort(skus)
        skuDict = wildCardDict(skuSorted)
        self.navigate_pricebook(price_book)
        self.delete_price_wtih_wild_card(skuDict)
        
    """ Get Variation Mapping for Product Variation Groups """
    def getVariations(self):
        variations = []
        filename = './csv/variations.csv'
        with open (filename, newline = '', encoding='UTF-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                try:
                    """ PERSONAL MAC """
                    master = row['master']
                except:
                    """ OFFICE COMPUTER """
                    master = row['\ufeffmaster']                
                styleNumber = row['styleNumber'].strip()                
                colorID = row['colorID'].strip()                
                pair = [master, styleNumber, colorID]                
                variations.append(pair)                
        print("Variations: ",variations)
        return variations
        
    def createVariants(self, variations):
        try:
            while variations: 
                pair = variations[0]
                print(pair)
                
                product, styleNumber, colorID = pair
                
                self.searchProducts([product])
                self.driver.find_element_by_link_text(product).click()
                self.driver.find_element_by_link_text('Variations').click()
                
                try:
                    self.driver.find_element_by_link_text('Lock').click()
                    print("Unlocked")
                except:
                    pass
                
                form = self.driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/form[1]')
                
                self.expand_variations()
                
                try: 
                    exist = self.driver.find_element_by_link_text(styleNumber)
                    if exist:
                        print(f"Variation {styleNumber} was created before")
                        self.apply_color_to_variation(styleNumber, colorID)
                        done = variations.pop(0)
                        self.driver.find_element_by_xpath("//body").send_keys(Keys.HOME)
                        self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()
                        continue
                except:
                    print(f"Creating new variation {styleNumber}")
                    pass
                
                self.driver.find_element_by_xpath('//input[@id="VariationGroupProductSKU"]').send_keys(styleNumber)
                
                try: 
                    # is this the first variation ever? 
                    self.driver.find_element_by_xpath('//button[@name="confirmDisableSlicing"]').click()
                    print("First ever variation!")
                    try:
                        button = self.driver.find_element_by_xpath('//button[@name="createVariationGroup"]')
                        button.click()
                    except:
                        self.driver.execute_script(
                        """
                        document._getElementsByXPath('//button[@name="createVariationGroup"]')[0].click()
                        """
                        )
                except: 
                    try:
                        button = self.driver.find_element_by_xpath('//button[@name="createVariationGroup"]')
                        button.click()
                    except:
                        self.driver.execute_script(
                        """
                        document._getElementsByXPath('//button[@name="createVariationGroup"]')[0].click()
                        """
                        )
                print(f"Add {styleNumber}")
                
                self.expand_variations()
                
                self.apply_color_to_variation(styleNumber, colorID) 
                
                try:
                    self.driver.find_element_by_xpath('//button[@name="applyVariationGroup"]')\
                        .click()
                except:
                    try:
                        apply = """button = document._getElementsByXPath('//button[@name="applyVariationGroup"]');
                        button[0].click();
                        """                
                        self.driver.execute_script(apply)
                    except:
                        raise
                                
                self.driver.find_element_by_link_text('Unlock').click()
                        
                print("Applied")
                
                self.driver.find_element_by_xpath("//body").send_keys(Keys.HOME)           
                self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()
                
                done = variations.pop(0)
                
        except Exception as error:
            print(f"Oops... something went wrong > {error}")
            print("Variations that are not created will be saved in incomplete_variation.txt in csv folder")            
            
            with open('./variations/variation_errors.txt', "a", encoding='utf-8') as file:
                content = product + '\t' + styleNumber + '\t' + colorID + '\t' + datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '\n'
                file.write(content)
                print('Error > ', content)            
            
            try:
                self.driver.find_element_by_xpath("//body").send_keys(Keys.HOME)           
                self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()
            except:
                self.navProducts()
            done = variations.pop(0)
            self.createVariants(variations)
            
    def apply_color_to_variation(self, styleNumber, colorID):
        script = """table = document._getElementsByXPath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/form[1]/table[2]');
        let rows = table[0].rows
        let length = rows.length
        Array.from(rows).forEach(row => {{
            if(row.innerText.include("{}")) {{
                let options = row.getElementsByTagName('option');
                let select = row.querySelector('select')
                Array.from(options).forEach((option, i) => {{
                    if (option.value === "{}".toString()) {{
                        select.selectedIndex = i
                    }}
                }})
            }}
        }})
        """.format(styleNumber, colorID)
        self.driver.execute_script(script) 
        
    def expand_variations(self):
        # Expand all 
        try:
            form = self.driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/form[1]')
            button = form.find_element_by_xpath('//button[@name="PageSize"]')               
            button.click()
            print("Expanded all")
        except:
            print("Do not need to expand all")
            pass
    
    def create_variations(self):
        variations = self.getVariations()
        self.navProducts()
        self.createVariants(variations)
        
    """ Update Refinement Buckets """
    def getBuckets(self):
        filename = './csv/buckets_' + self.site + '.csv'
        with open(filename, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            mapping = {}
            
            for row in reader:
                k = row['bucket']
                v = row['style']
                
                if not k:
                    continue 
                
                if k in mapping.keys():  
                    mapping[k].append(v)
                else:
                    if "," in k:
                        for j in list(map(lambda x: x.strip(), k.split(","))):
                            if j in mapping.keys():    
                                mapping[j].append(v)
                            else:
                                mapping[j] = [v]
                    else:
                        mapping[k] = [v]
        return mapping
    
    """ Rewrite all buckets """
    def bucketRefinementUpdate(self, urls, index):
        mapping = self.getBuckets()
        attr_types = {
            1: 'By Attribute (Style Number)',
            2: 'By Attribute (ID)',
            3: 'By Attribute (Type)',
            4: 'By Attribute (Size)'
            }
        
        for url in urls:
            buckets = list(mapping.keys())             
            self.driver.get(url)
            self.driver.find_element_by_link_text('Search Refinement Definitions').click()            
            attribute = self.driver.find_elements_by_link_text(attr_types[index])[-1]            
            self.driver.execute_script("arguments[0].scrollIntoView()", attribute)            
            attribute.click()            
            self.selectLanguage()            
            self.driver.find_element_by_xpath("//body").send_keys(Keys.END)            
            rows = self.driver.find_elements_by_xpath('//td[@class="table_detail s"]')            
            
            while len(rows) > 1:
                selectAll = self.driver.find_element_by_link_text('Select All')
                self.driver.execute_script("arguments[0].click();",selectAll)
                try:
                    confirmDelete = self.driver.find_element_by_xpath('//button[@name="confirmDelete"]')
                    self.driver.execute_script("arguments[0].click();",confirmDelete)
                except:
                    script = """document._getElementsByXPath('//button[@name="confirmDelete"]')[0].click()"""
                    self.driver.execute_script(script)
                delete = self.driver.find_element_by_xpath('//button[@name="delete"]')
                self.driver.execute_script("arguments[0].click();",delete)                
                rows = self.driver.find_elements_by_xpath('//td[@class="table_detail s"]')
                        
            while buckets:
                bucket_display = buckets[0]                
                bucket_values = mapping[bucket_display]
                bucketInput = self.driver.find_element_by_xpath('//input[@name="NewBucketValues"]')
                self.driver.execute_script("arguments[0].value = {}.toString()".format(bucket_values), bucketInput)
                self.driver.find_element_by_xpath('//input[@name="NewBucketDisplay"]').send_keys(bucket_display)
                
                try:
                    self.driver.find_element_by_xpath('//button[@name="add"]').click()
                except:
                    script = """document._getElementsByXPath('//button[@name="add"]')[0].click()"""
                    self.driver.execute_script(script)
                
                print("Done > {}".format(bucket_display))
                
                done = buckets.pop(0)
