import requests
from utils import async_request, get_viewstates
from bs4 import BeautifulSoup
import asyncio

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1"
}
POST_PARAMS = {
    "__EVENTTARGET": "",
    "__EVENTARGUMENT": "",
    "__VIEWSTATE": "",
    "__VIEWSTATEGENERATOR": "",
    "helpUrl": "http://cms.education.gov.il/EducationCMS/Applications/Afik/MadrichLahorim/",
    "txtShemMosad": "",
    "cboYeshuv": "0",
    "cboShllavChinuch": "0",
    "cboSugPikuach": "0",
    "cboMigzar": "0",
    "cmdItur": "איתור",
    "lblSelectedRow": "-1",
    "lblMisparSchumLeSeif": "",
    "lblSchum": "",
    "lblHodaa": "",
    "cmdItur": "איתור"
}
BASE_URL = "http://hinuch.education.gov.il/acthorim/"
TIMEOUT = 10


class AfikSession:

    def __init__(self, **kwargs):
        self.session = requests.Session()
        self.session.headers.update(kwargs.get("headers", REQUEST_HEADERS))
        self.post_params = kwargs.get("post_params", POST_PARAMS)
        self.timeout = kwargs.get(
            "timeout", TIMEOUT)

    async def start(self):
        initial_response = await async_request(self.session.get, BASE_URL)
        parsed_html = BeautifulSoup(initial_response, "html.parser")
        self.update_params(get_viewstates(parsed_html))

    async def post(self, url, data):
        params = self.post_params.copy()
        params.update(data)
        return await async_request(self.session.post, url, data=params, timeout=self.timeout)

    def update_params(self, params):
        self.post_params.update(params)

    def remove_param(self, param):
        if param in self.post_params:
            del self.post_params[param]
