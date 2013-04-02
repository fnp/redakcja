from tests.integration.base import SeleniumTestCase, MainPage, _

class SmokeTest(SeleniumTestCase):

    def test_add_book(self):
        user = self.create_super_user(do_login = True)
        
        page = self.get_main_page()
        page.select_tab(_('All'))
        assert page.tab.visible_books_count == 0
        
        page.select_tab(_('Add'))
        page.tab.put_title('Test title')
        page.tab.put_text('Test text')
        page.tab.submit()
        page.select_tab(_('All'))
        assert page.tab.visible_books_count == 1
        