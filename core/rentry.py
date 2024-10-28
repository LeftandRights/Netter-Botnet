from secrets import token_urlsafe
from bs4 import BeautifulSoup
from .enums import RentryContent, RentryResponse, RentryType

import requests
import requests.cookies

class Tools:

    @staticmethod
    def getPayload(_type: RentryType, token: str, **kwargs) -> dict:

        edit_code: str = kwargs.get('edit_code', None)
        defaultPayload: dict[str, str] = {
            'csrfmiddlewaretoken': token
        }

        if (not edit_code and _type != RentryType.CREATE_NEW):
            raise ValueError('Rentry(Edit Code) is not yet to be set.')

        defaultPayload['edit_code'] = edit_code

        if (_type in (RentryType.EDIT_EXISTING, RentryType.CREATE_NEW)):
            if not (_text := kwargs.get('text', None)):
                raise ValueError('Rentry(Text) is not yet to be set.')

            defaultPayload['text'] = _text

        if (_type == RentryType.CREATE_NEW and (kwargs.get('edit_code', None) is None)):
            defaultPayload['edit_code'] = token_urlsafe(16)

        if (_type == RentryType.CREATE_NEW):
            if not(_url := kwargs.get('url_name', None)):
                raise ValueError('Rentry(Url Path) is not yet to be set')

            defaultPayload['url'] = _url

        if (_type == RentryType.DELETE):
            defaultPayload['delete'] = 'delete'

        return defaultPayload

    @staticmethod
    def getCookies() -> requests.cookies.RequestsCookieJar:
        response = requests.head(Rentry.BASE_URL)
        return response.cookies

class Rentry:
    BASE_URL: str = 'https://rentry.org'
    DEFAULT_HEADER: dict = {
        'Host': 'rentry.org',
        'Accpet': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://rentry.org',
        'User-Agent': 'curl/8.8.0'
    }

    # Create New:     /api/new
    # Edit Existing:  /api/edit/name
    # Delete:         /name/edit

    @staticmethod
    def new(urlName: str, text: str, edit_code: None | str = None) -> RentryResponse:
        if (testing := Rentry.get_content(Rentry.BASE_URL + '/' + urlName) is not None):
            raise NameError('Url name has already been taken.')

        print(testing)
        cookies: requests.cookies.RequestsCookieJar = Tools.getCookies()
        payload: dict = Tools.getPayload(
            RentryType.CREATE_NEW, cookies.get_dict()['csrftoken'],
            edit_code = edit_code,
            url_name = urlName,
            text = text
        )

        response: requests.Response = requests.post(Rentry.BASE_URL + '/api/new', data = payload, headers = Rentry.DEFAULT_HEADER, cookies = cookies)

        if not ((_code := response.status_code) == 200):
            raise ConnectionError('Requests to server return the code of ' + str(_code))

        return RentryResponse(
            cookies = cookies,
            requests_response = response,
            url = Rentry.BASE_URL + '/' + urlName,
            edit_code = payload['edit_code'],
            payload = payload,
            text = text
        )

    @staticmethod
    def delete(urlName: str, edit_code: str) -> RentryResponse:
        cookies: requests.cookies.RequestsCookieJar = Tools.getCookies()
        payload: dict = Tools.getPayload(
            RentryType.DELETE, cookies.get_dict()['csrftoken'],
            edit_code = edit_code,
            urlName = urlName
        )

        response: requests.Response = requests.post(Rentry.BASE_URL + f'/{urlName}/edit', data = payload, headers = Rentry.DEFAULT_HEADER, cookies = cookies)

        return RentryResponse(
            cookies = cookies,
            requests_response = response,
            url = Rentry.BASE_URL + '/' + urlName,
            edit_code = payload['edit_code'],
            payload = payload,
            text = ''
        )

    @staticmethod
    def edit(urlName: str, edit_code: str, text: str) -> RentryResponse:
        cookies: requests.cookies.RequestsCookieJar = Tools.getCookies()
        payload: dict = Tools.getPayload(
            RentryType.EDIT_EXISTING, cookies.get_dict()['csrftoken'],
            edit_code = edit_code,
            text = text
        )

        response: requests.Response = requests.post(Rentry.BASE_URL + f'/api/edit/{urlName}', data = payload, headers = Rentry.DEFAULT_HEADER, cookies = cookies)

        return RentryResponse(
            cookies = cookies,
            requests_response = response,
            url = Rentry.BASE_URL + '/' + urlName,
            edit_code = payload['edit_code'],
            payload = payload,
            text = text
        )

    @staticmethod
    def get_content(url: str) -> RentryContent | None:
        response = requests.get(url)

        if (response.status_code == 200):
            soup = BeautifulSoup(response.content, 'html.parser')

            title = soup.title.string if soup.title else "No Title"
            content = soup.find('div', class_ = 'entry-text').find('article').get_text(separator = "\n", strip = True)
            details = soup.find('div', class_ = 'text-muted').find('div', 'float-right').get_text(separator = '\n', strip = True).splitlines()

            if (len(details) > 3):
                publish_date, last_edit, views = details[0][5:], details[2][6:], details[4][7:]
            else:
                publish_date, last_edit, views = details[0][5:], 'No history', details[-1][7:]

            return RentryContent(title, content, publish_date, last_edit, int(views))

        return None
