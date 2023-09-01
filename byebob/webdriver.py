import contextlib
import json
import pathlib
import random

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


attendance_url = 'https://app.hibob.com/attendance/my-attendance'


class WebDriver(webdriver.Chrome):
    cookies_path = pathlib.Path('cookies.json')
    driver_path = '.\\webdrivers\\chromedriver.exe'
    timeout = 10

    def __init__(self, email, password, headless=True, first_try=True) -> None:
        try:
            self.email = email
            self.password = password
            self._initialaize_driver(headless)
            self._set_cookies()
            if self._are_valid_cookies():
                return
            self.quit()
            self._initialaize_driver(False)
            self._create_cookies()
            self.quit()
            self._initialaize_driver(headless)
            self._set_cookies()
            if not self._are_valid_cookies():
                raise RuntimeError('Invalid cookies')
        except:
            if first_try:
                self.__init__(email, password, headless, False)

    def _initialaize_driver(self, headless):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        if headless:
            options.add_argument('--headless')
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--disable-extensions')
        # options.add_argument('--no-sandbox')
        super().__init__(self.driver_path, options=options)

    def quit(self):
        with contextlib.suppress(Exception):
            self.close()
        with contextlib.suppress(Exception):
            super().quit()

    ###########################################################################
    # ATTENDENCE

    def is_working_day(self) -> bool:
        self.get(attendance_url)
        non_working_day_span = '/html/body/app-root/app-master-page/app-layout/div[2]/div/app-attendance/app-page-content-wrapper/div/app-my-attendance/b-ee-layout/section/article/div/app-attendance-time-sheet/div/b-table/ag-grid-angular/div/div[2]/div[2]/div[3]/div[1]/div/div[2]/div/div/div[1]/div[6]/b-simple-cell/b-cell-renderers-wrapper/div/span/div/span'
        with contextlib.suppress(TimeoutException):
            self._get_elem_by_xpath(non_working_day_span)
            return False
        # Faield to get non_working_day_span element, meaning it's a working day
        return True

    def clock_in(self):
        self.get(attendance_url)
        clock_in_bttn = '/html/body/app-root/app-master-page/app-layout/div[2]/div/app-attendance/app-page-content-wrapper/div/app-my-attendance/b-ee-layout/section/header/div/app-attendance-clock/div/div[3]/b-button/button'
        _click_button(self._get_elem_by_xpath(clock_in_bttn))

    def clock_out(self):
        self.get(attendance_url)
        clock_out_bttn = '/html/body/app-root/app-master-page/app-layout/div[2]/div/app-attendance/app-page-content-wrapper/div/app-my-attendance/b-ee-layout/section/header/div/app-attendance-clock/div/div[3]/b-button/button'
        _click_button(self._get_elem_by_xpath(clock_out_bttn))
        self._set_location()

    def _set_location(self):
        self.get(attendance_url)
        self.set_window_size(1000, 1800)
        first_row = '/html/body/app-root/app-master-page/app-layout/div[2]/div/app-attendance/app-page-content-wrapper/div/app-my-attendance/b-ee-layout/section/article/div/app-attendance-time-sheet/div/b-table/ag-grid-angular/div/div[2]/div[2]/div[3]/div[1]/div/div[2]/div/div/div[1]/div[1]'
        _click_button(self._get_elem_by_xpath(first_row))
        location_select = '/html/body/div[3]/div[2]/div/mat-dialog-container/app-complete-entry-dialog/b-dialog/div[2]/div/div/div[2]/app-entry-panel/div[1]/form/div/b-single-select/div/div[1]/div'
        _click_button(self._get_elem_by_xpath(location_select))
        selected_choise = f'/html/body/div[3]/div[4]/div/div/b-single-list/div/cdk-virtual-scroll-viewport/div[1]/div/div[{random.randint(2, 4)}]'
        _click_button(self._get_elem_by_xpath(selected_choise))
        save_bttn = '/html/body/div[3]/div[2]/div/mat-dialog-container/app-complete-entry-dialog/b-dialog/div[3]/div/div/b-button[2]/button'
        _click_button(self._get_elem_by_xpath(save_bttn))

    ###########################################################################
    # COOKIES UTILS

    def _create_cookies(self):
        login_url = f'https://app.hibob.com/api/saml/login?email={self.email}'
        self.get(login_url)

        email_input = '/html/body/div/div/div/div/div/form/fieldset/div/input'
        _fill_text_area(self._get_elem_by_xpath(email_input), self.email)

        remember_me_checkbox = '/html/body/div/div/div/div/div/form/div/input'
        _click_button(self._get_elem_by_xpath(remember_me_checkbox))

        continue_bttn = '/html/body/div/div/div/div/div/form/button/span'
        _click_button(self._get_elem_by_xpath(continue_bttn))

        pass_inpit = '/html/body/div/div/div/div/div[2]/form/fieldset/div/input'
        _fill_text_area(self._get_elem_by_xpath(pass_inpit), self.password)

        sso_login_bttn = '/html/body/div/div/div/div/div[2]/form/button'
        _click_button(self._get_elem_by_xpath(sso_login_bttn))

        input('Finish the logging processes and once you are done press ENTER')

        cookies = self.get_cookies()
        with self.cookies_path.open('w') as file:
            json.dump(cookies, file)

    def _set_cookies(self):
        self.get(attendance_url)
        cookies = list()
        with self.cookies_path.open() as file:
            cookies = json.load(file)
        for cookie in cookies:
            self.add_cookie(cookie)
        self.get(attendance_url)

    def _are_valid_cookies(self):
        if not self.cookies_path.exists():
            return False
        self.get(attendance_url)
        login_header = '/html/body/app-root/app-login/app-login-form/app-layout/div[2]/div/div[1]/b-display-1'
        try:
            self._get_elem_by_xpath(login_header)
        except TimeoutException:
            return True
        else:
            return False

    ###########################################################################
    # GET ELEMENT UTILS

    def _get_elem(self, by, path) -> WebElement:
        con = expected_conditions.presence_of_element_located((by, path))
        WebDriverWait(self, self.timeout).until(con)
        return self.find_element(by, path)

    def _get_elem_by_selector(self, selector) -> WebElement:
        return self._get_elem(By.CSS_SELECTOR, selector)

    def _get_elem_by_class_name(self, class_name) -> WebElement:
        return self._get_elem(By.CLASS_NAME, class_name)

    def _get_elem_by_id(self, id) -> WebElement:
        return self._get_elem(By.ID, id)

    def _get_elem_by_link_text(self, link_text) -> WebElement:
        return self._get_elem(By.LINK_TEXT, link_text)

    def _get_elem_by_partial_link_text(self, partial_link_text) -> WebElement:
        return self._get_elem(By.PARTIAL_LINK_TEXT, partial_link_text)

    def _get_elem_by_tag_name(self, tag_name) -> WebElement:
        return self._get_elem(By.TAG_NAME, tag_name)

    def _get_elem_by_name(self, name) -> WebElement:
        return self._get_elem(By.NAME, name)

    def _get_elem_by_xpath(self, xpath) -> WebElement:
        return self._get_elem(By.XPATH, xpath)


###############################################################################
# GENERAL UTILS


def _fill_text_area(web_elem: WebElement, text) -> None:
    web_elem.send_keys(text)


def _click_button(web_elem: WebElement) -> None:
    web_elem.click()
