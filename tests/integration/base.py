import os
import inspect
from urlparse import urlparse

from django.test import LiveServerTestCase
from django.test.client import Client
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.utils.translation import ugettext as _

from selenium import webdriver, selenium
from selenium.webdriver.support.wait import WebDriverWait


class SeleniumTestCase(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        LiveServerTestCase.setUpClass()
        cls.browser = getattr(webdriver, os.environ.get('TEST_BROWSER', 'Firefox'))()
        cls.browser.implicitly_wait(5)
        
    @classmethod
    def tearDownClass(cls):
        LiveServerTestCase.tearDownClass()
        cls.browser.quit()
        
    def setUp(self):
        self.browser.delete_all_cookies()
    
    def create_user(self, username = 'testuser',  passwd = 'passwd', do_login = False):
        user = User.objects.create_user(username, '', passwd)
        user._plain_passwd = passwd
        if do_login:
            self.login_user(user)
        return user
    
    def create_super_user(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        user.is_superuser = True
        user.save()
        return user
        
    def login_user(self, user):
        client = Client()
        client.login(username = user.username, password = user._plain_passwd)

        if not self.browser.current_url.startswith(self.live_server_url):
            self.browser.get(self.live_server_url+'/not_existing_url')
            
        self.browser.find_element_by_tag_name('body') # Make sure the page is actually loaded before setting the cookie
        self.browser.delete_cookie(settings.SESSION_COOKIE_NAME)
        self.browser.add_cookie(dict(name = settings.SESSION_COOKIE_NAME, 
                                     value = client.cookies[settings.SESSION_COOKIE_NAME].value,
                                     path = '/')
                               )
        
    def get_main_page(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_tag_name('body')
        return MainPage(self.browser)

        
class Page(object):
    def __init__(self, browser):
        self.browser = browser
    
    
class MainPage(Page):

    def __init__(self, browser):
        Page.__init__(self, browser)
        self.tab = None
    
    @property
    def element(self):
        return self.browser.find_element_by_tag_name('body')
    
    def select_tab(self, tab_title):
        for a in self.element.find_element_by_id('tabs-nav-left').find_elements_by_tag_name('a'):
            if a.text == tab_title:
                a.click()
                self.tab = find_tab_class(tab_title)(self.browser)
                return
        raise Exception, 'Tab not found'
        
                
def find_tab_class(tab_title):       
    for obj in globals().values():
        if inspect.isclass(obj) and issubclass(obj, MainPageTabBase) and getattr(obj, 'tab_title', None) == tab_title:
            return obj
    raise NotImplementedError
                

class MainPageTabBase(Page):
    def __init__(self, browser):
        Page.__init__(self, browser)
    
    @property
    def element(self):
        return self.browser.find_element_by_id('content')
        

class AddBookPage(MainPageTabBase):
    tab_title = _('Add')
    
    def put_title(self, title):
        self.element.find_element_by_id('id_title').send_keys(title)
        
    def put_text(self, text):
        self.element.find_element_by_id('id_text').send_keys(text)
        
    def submit(self):
        self.browser.find_element_by_css_selector('table.editable button').click()
        return self.browser
        
    
class BooksListPage(MainPageTabBase):
    tab_title = _('All')
    
    @property
    def visible_books_count(self):
        return len(self.element.find_element_by_id('file-list').find_elements_by_tag_name('tr')) - 2
        
        