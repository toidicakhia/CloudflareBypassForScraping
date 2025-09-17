import time
from DrissionPage import ChromiumPage

class CloudflareBypasser:
    def __init__(self, driver: ChromiumPage, max_retries=-1, log=True):
        self.driver = driver
        self.max_retries = max_retries
        self.log = log

    def search_recursively_shadow_root_with_iframe(self, ele):
        if ele.shadow_root:
            if ele.shadow_root.child().tag == "iframe":
                return ele.shadow_root.child()
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_iframe(child)
                if result:
                    return result
        return None

    def search_recursively_shadow_root_with_cf_input(self, ele):
        if ele.shadow_root:
            if ele.shadow_root.ele("tag:input"):
                return ele.shadow_root.ele("tag:input")
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_cf_input(child)
                if result:
                    return result
        return None
    
    def locate_cf_button(self):
        button = None
        eles = self.driver.eles("tag:input")
        captcha_ele = None
        for ele in eles:
            if "name" in ele.attrs.keys() and "type" in ele.attrs.keys():
                if "turnstile" in ele.attrs["name"] and ele.attrs["type"] == "hidden":
                    captcha_ele = ele
                    button = ele.parent().shadow_root.child()("tag:body").shadow_root("tag:input")
                    break
            
        return captcha_ele, button

    def log_message(self, message):
        if self.log:
            print(message)

    def is_bypassed(self, button):
        try:
            print(button)
            return button != None and "value" in button.attrs.keys()
        except Exception as e:
            self.log_message(f"Error checking page title: {e}")
            return False

    def bypass(self):
        button = None
        captcha_ele = None
        try_count = 0
        
        while not button:
            captcha_ele, button = self.locate_cf_button()
            time.sleep(1)
            
        if button:
            button.click()
                
            while not self.is_bypassed(captcha_ele):
                if 0 < self.max_retries + 1 <= try_count:
                    self.log_message("Exceeded maximum retries. Bypass failed.")
                    break
                
                try_count += 1
                time.sleep(2)
                
        if self.is_bypassed(captcha_ele):
            self.log_message("Bypass successful.")                
        else:
            self.log_message("Bypass failed.")
                
        return captcha_ele
