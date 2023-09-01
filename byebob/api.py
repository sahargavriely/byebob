import requests
from bs4 import BeautifulSoup


class API(requests.Session):
    def __init__(self) -> None:
        self._headers = dict()
        self._base_url = 'https://app.hibob.com/api'
        super().__init__()

    def get_user_info(self) -> dict:
        if not self._headers:
            raise RuntimeError('dude what are you trying do to, login first')
        url = f'{self._base_url}/user'
        return self.get(url, headers=self._headers)

    def login(self, email: str) -> None:
        email = email.replace('@', '%40')
        url = f'{self._base_url}/saml/login?email={email}'
        response = self.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        f = 'login.html'
        with open(f, 'w') as ff:
            ff.write(soup.prettify())
        self._login_first_phase(response)

    def _login_first_phase(self, response: requests.Response):
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        url = form['action']
        data = dict()
        for _input in form.find_all('input'):
            attr = _input.attrs
            if 'name' not in attr or 'value' not in attr:
                continue
            # if attr['name'] == 'RelayState':
            #     input_url = attr['value']
            print(attr['name'])
            print(attr['name'])
            print(attr['name'])
            data[attr['name']] = attr['value']
        print(url)
        response = self.post(url, data=data)
        soup = BeautifulSoup(response.content, 'html.parser')
        print(soup.prettify())
        f = 'tmp.html'
        with open(f, 'w') as ff:
            ff.write(soup.prettify())

        # print(url_2)
        # response = self.post(url_2, data=data)
        # print(response.status_code)
        # print(response.headers)
        # print(response.headers.get('location', 'no locooooooooooooooooooo'))
        # print(response.cookies)
        # soup = BeautifulSoup(response.content, 'html.parser')
        # print(soup.prettify())
        # f = 'tmp.html'
        # with open(f, 'w') as ff:
        #     ff.write(soup.prettify())
        # print(self.cookies)
        # client_name = 'saml503440'
        # url = f'{self._base_url}/saml/callback?client_name={client_name}'
        # response = requests.get(url, data=p)
        # print(response)
        # print(response.status_code)
        # print(response.headers)
        # print(response.cookies)

    def _login_end_of_story(self, response):
        session_id = response.headers['location'].split('=')[-1]
        # session_id = 'ada70031-605a-408e-89fb-e3db615eb9de'
        url = f'{self._base_url}/saml/completeLogin?samlSessionId={session_id}'
        response = requests.get(url)
        self._set_headers(response)

    def _set_headers(self, response: requests.Response) -> None:
        cookie = response.cookies['PLAY_SESSION']
        self._headers['cookie'] = f'hibob={cookie}'


def print_res(response):
    print(response.status_code)
    print(response.headers)
    print(response.cookies)
    print(response.text)
    # print(response.json())
    # print(response.headers.get('location', 'no locooooooooooooooooooo'))
