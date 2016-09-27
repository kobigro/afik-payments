from bs4 import BeautifulSoup, NavigableString
import json
import asyncio
import itertools
import datetime
from utils import get_viewstates
from session import AfikSession
import cities

# TODO: refactor to two modules - result pages scraper and schools scraper
BASE_URL = "http://hinuch.education.gov.il/acthorim/"
SEARCH_URL = "http://hinuch.education.gov.il/acthorim/IturMosad.aspx"


SCHOOL_PAGE_COUNT = 964
# Pages 1-10 have viewstate A..etc. this needs to be saved due to the
# async nature of the scraper. if page 11 is requested before page 2 is,
# we can't update the viewstate globally,because page 2 would be requested
# with the invalid viewstate. index -1 is the special case of the first
# request.
page_numbers_viewstates = {}

search_session = AfikSession()
school_session = AfikSession()

# School search params mappings(name -> cbo id). see
# `get_school_search_params`.
SUPERVISION_TO_ID = {
    "ממלכתי": 1,
    "ממלכתי דתי": 2,
    "חרדי": 3
}
SECTOR_TO_ID = {
    "בדואי": 5,
    "דרוזי": 4,
    "יהודי": 1,
    "ערבי": 2,
    "צרקסי": 6,
    "שומרוני": 7
}

PAYMENT_CLAUSE_COLUMN_WIDTH = "235"
PAYMENT_PRICE_COLUMN_WIDTH = "40"
PAYMENT_TYPES = {
    "תשלומי חובה": "חובה",
    "תשלומי רשות": "רשות",
    "תשלומים מרצון": "מרצון",
    "תוכנית לימודים נוספת": "תוכנית לימודים נוספת"
}

OUTPUT_PATH_TEMPLATE = "../data/schools-{}.json"


def set_pages_viewstate_values(html, pagelist_index=-1):
    soup = BeautifulSoup(html, "html.parser")
    viewstates = get_viewstates(soup)
    page_numbers_viewstates[pagelist_index] = viewstates

async def get_schools():
    await search_session.start()
    schools = []
    pages, next_main_page_html = await get_result_pages()
    last_page = False
    schools = []
    page_number = 0
    while not last_page:
        for page in pages:
            soup = BeautifulSoup(page, "html.parser")
            page_number = _get_page_number(soup)
            print("Get page {}".format(page_number))
            if page_number == SCHOOL_PAGE_COUNT:
                last_page = True
            schools.extend(await get_schools_in_page(soup))
        if not last_page:
            pages, next_main_page_html = await get_result_pages(next_main_page_html)

    dump_schools(schools)

async def get_result_pages(main_page_html=None):
    # Returns all subpages and the html of the next main page
    tasks = []
    subpages = []
    if main_page_html is None:
        # This is a special case, can't be async. This is the first page of
        # all, so can't retrieve later lazily
        main_page_html, _ = await get_page_html(-1, "", True)
        subpages = [main_page_html]

    soup = BeautifulSoup(main_page_html, "html.parser")
    page_number = _get_page_number(soup)
    page_links = _get_page_links(soup, page_number)
    # Result pages are paginated with a page size of 10.
    # We use the paglist index with the viewstate, as described above
    pagelist_index = int(page_number) // 10

    for page_event_target, is_main_page in page_links:
        page_html_task = get_page_html(
            pagelist_index, page_event_target, is_main_page)
        tasks.append(page_html_task)

    pages, next_main_page_html = await _fetch_pages(tasks)
    # Subpages might already contain the next main page html due to the
    # special case of the first main page, as described above.
    subpages.extend(pages)
    return subpages, next_main_page_html

async def _fetch_pages(page_tasks):
    # This function gathers the async tasks for fetching
    # the pages. It returns the pages html,
    # and the next main page html.
    all_pages = await asyncio.gather(*page_tasks)
    subpages = []
    next_main_page = ""
    for page, is_main in all_pages:
        if is_main:
            next_main_page = page
        subpages.append(page)
    return subpages, next_main_page


def _get_page_links(parsed_page, page_number):
    # Return a list of tuples, each tuple contain the link target and whether
    # the links points to a main page.
    page_links = parsed_page.find("tr", {'class': 'textNormal'}).find(
        "td", recursive=False).find_all("a")
    links = []
    for link in page_links:
        page_event_target = _link_to_eventtarget(link)
        is_main = link.text == "..."
        # If not link to previous main-page(in that case, no need to download
        # the previous main page).
        # Also, In the last results page, there are links to *previous* pages.
        # which is why we check if the link points to a previous page, to prevent a
        # "loop" bug.
        links_to_previous_main_page = page_event_target == "grdMosdot:_ctl9:_ctl0"
        if not links_to_previous_main_page and not _links_to_previous_page(link, page_number):
            links.append((page_event_target, is_main))
    return links


def _links_to_previous_page(link, current_page_number):
    # Check if a link found in the parsed page points to a previous page.
    try:
        link_page_number = int(link.text)
        return link_page_number < current_page_number
    except ValueError:
        # This is a main page, we shouldn't care about a ValueError.
        pass


def _link_to_eventtarget(link):
    return link.get("href", "").replace(
        "javascript:__doPostBack('", "").replace("','')", "").replace("$", ":")

async def get_page_html(pagelist_index, page_event_target="", is_main=False):
    params = {
        "__EVENTTARGET": page_event_target
    }
    if pagelist_index != -1:
        # If not first page
        search_session.remove_param("cmdItur")
        viewstate_values = page_numbers_viewstates[pagelist_index]
        params.update(viewstate_values)

    page_html = await search_session.post(SEARCH_URL, params)
    if is_main:
        print(pagelist_index)
        set_pages_viewstate_values(page_html, pagelist_index + 1)
    return page_html, is_main


def _get_page_number(parsed_page):
    if len(parsed_page.select("#lblDaf")) > 0:
        return int(parsed_page.select("#lblDaf")[0].text)


async def get_schools_in_page(parsed_page):
    rows = parsed_page.find_all(
        True, {'class': ['TableFirstRow', 'TableSecondRow']})
    schools = []
    school = {}
    school_tasks = [get_school(row) for row in rows]
    # Return all schools in page coroutine without awaiting to it's result.
    # That's because there will be another aggregation in the
    # get_all_schools_function, so if we await in every page it won't be
    # truely async
    return await asyncio.gather(*school_tasks)


async def get_school(school_row):
    details = get_school_details(school_row)
    print("Finding a school with id of {id} named {name}".format(**details))
    school_page = await find_school(details)
    payments = await get_school_payments(school_page)
    return dict(details, payments=payments)


def get_school_details(school_row):
    columns = school_row.find_all(["td", "a", "span"], text=True)
    # TODO: move column indexes to constants
    details = {
        "id": columns[0].text,
        "name": columns[1].text.replace('\r', '').replace('\t', '').replace('\n', ''),
        "city": columns[2].text,
        "level": columns[3].text,
        "sector": columns[4].text,
        "supervision": columns[5].text,
        "is_approved": columns[7].text == "מאושר"
    }
    return details


def get_school_search_params(school_details):
    # Convert from detail strings to cbo ids, from afik selects.
    name = school_details["name"]
    city_id = cities.get_city_id(school_details["city"])
    supervision_id = SUPERVISION_TO_ID.get(school_details["supervision"], 0)
    sector_id = SECTOR_TO_ID.get(school_details["sector"], 0)
    return {
        "txtShemMosad": name,
        "cboYeshuv": city_id,
        "cboSugPikuach": supervision_id,
        "cboMigzar": sector_id,
        "cmdItur": "איתור"
    }

async def find_school(school_details):
    params = get_school_search_params(school_details)
    content = await school_session.post(SEARCH_URL, params)
    return content


def get_payment_type(payment_clause_column):
    print("Get payment type! yesss!")
    # Get payment type by searching in the column js click
    clause_click_js = payment_clause_column.find(
        "a", recursive=False).attrs["href"]
    payment_type = ""
    for afik_type_name, actual_type_name in PAYMENT_TYPES.items():
        if afik_type_name in clause_click_js:
            payment_type = actual_type_name
    return payment_type

async def get_school_payments(school_page):
    parsed_school_page = BeautifulSoup(school_page, "html.parser")
    classes = parsed_school_page.find_all(
        "td", {"class": "TableHeader", "width": "40"}, text=True)
    payments = parsed_school_page.find_all(
        "td", {"class": ["TableFirstRowDynamic", "TableSecondRowDynamic"]})
    payment_rows = itertools.groupby(payments, lambda payment: payment.parent)

    all_payments = []
    for payment_columns, payments_row in payment_rows:
        clause_class_payments = {}
        clause_name, class_payments = get_clause_payments(
            payment_columns, classes)
        clause_class_payments[clause_name] = class_payments
        all_payments.append(clause_class_payments)
    return all_payments


def get_clause_payments(payment_columns, classes):
    clause_name = ""
    payment_type = ""
    class_payments = []
    for idx, column in enumerate(payment_columns):
        if not isinstance(column, NavigableString):
            is_payment_price = column.get(
                "width", 0) == PAYMENT_PRICE_COLUMN_WIDTH
            is_payment_clause = column.get(
                "width", 0) == PAYMENT_CLAUSE_COLUMN_WIDTH
            if is_payment_price:
                # Payment value columns obviously match directly to classes(99
                # to א, 210 to ב, etc) so we can match class to payment
                # directly using list index. We substract 2 because of the 2
                # extra columns(chozer mankal and clause name)
                class_name = classes[idx - 2].text
                price = 0
                try:
                    price = float(column.text)
                except ValueError:
                    pass
                class_payment = {
                    "class": class_name,
                    "price": price,
                    "type": payment_type
                }
                class_payments.append(class_payment)
            elif is_payment_clause:
                clause_name = column.text
                payment_type = get_payment_type(column)
    return clause_name, class_payments


def dump_schools(schools):
    json_path = get_json_path()
    with open(json_path, "w") as json_file:
        json.dump(schools, json_file)


def get_json_path():
    today = datetime.date.today()
    month = today.month
    year = today.year
    # Between january and july, schoolyear new year part
    if 1 <= month <= 7:
        # Payment data year is the year when the
        # schoolyear started, which starts in september,
        # i.e one year less from now
        year -= 1
    return OUTPUT_PATH_TEMPLATE.format(year)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_schools())
