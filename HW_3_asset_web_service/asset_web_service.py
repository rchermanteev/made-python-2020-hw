"""Asset Web Service

"""


from flask import Flask, jsonify, Response, request
from lxml import etree
import requests
from requests.exceptions import ConnectionError

app = Flask(__name__)
URL_CBR_DAILY = "https://www.cbr.ru/eng/currency_base/daily/"
URL_CBR_KEY_INDICATORS = "https://www.cbr.ru/eng/key-indicators/"

app.bank = {}


class Asset:
    """Asset class

    """
    def __init__(self, char_code: str, name: str, capital: float, interest: float):
        self.char_code = char_code
        self.name = name
        self.capital = capital
        self.interest = interest

    def calculate_revenue(self, years: int) -> float:
        """Calculate revenue

        """
        revenue = self.capital * ((1.0 + self.interest) ** years - 1.0)
        return revenue

    def get_content(self) -> list:
        """Get content asset

        Example: ['USD', 'US Dollar', 73.8, 0.1]
        """
        return [self.char_code, self.name, self.capital, self.interest]


def parse_cbr_currency_base_daily(dirty_response_text):
    """Function for parse site cbr page daily

    content have dict with char_code and rate
    """
    root = etree.fromstring(dirty_response_text, etree.HTMLParser())
    collection_raw_data = root.xpath("//table[@class='data']/tbody/tr")
    content = {}
    for data in collection_raw_data[1:]:
        raw_line = data.xpath(".//td")
        char_code = raw_line[1].text
        rate = round(float(raw_line[4].text) / float(raw_line[2].text), 8)
        content[char_code] = rate

    return content


def parse_cbr_key_indicators(dirty_response_text):
    """Function for parse site cbr page key indicators

    content have dict with char_code and rate for currency and valuable metals
    """
    root = etree.fromstring(dirty_response_text, etree.HTMLParser())
    collection_raw_table = root.xpath("//div[@class='table key-indicator_table']/table/tbody")[0: 2]
    content = {}
    for raw_table in collection_raw_table:
        for raw_line in raw_table[1:]:
            char_code = raw_line.xpath(".//td/div/div")[1].text
            rate = float(raw_line.xpath(".//td")[-1].text.replace(',', ''))
            content[char_code] = rate

    return content


@app.route("/cbr/daily")
def json_api_for_cbr_daily():
    """Route which causes function parse_cbr_currency_base_daily


    """
    try:
        response = requests.get(URL_CBR_DAILY)
    except ConnectionError:
        return "CBR service is unavailable", 503

    if not response.ok:
        return "CBR service is unavailable", 503

    parse_response = parse_cbr_currency_base_daily(response.text)
    return jsonify(parse_response)


@app.route("/cbr/key_indicators")
def json_api_for_cbr_key_indicators():
    """Route which causes function parse_cbr_key_indicators

    """
    try:
        response = requests.get(URL_CBR_KEY_INDICATORS)
    except ConnectionError:
        return "CBR service is unavailable", 503

    if not response.ok:
        return "CBR service is unavailable", 503

    parse_response = parse_cbr_key_indicators(response.text)
    return jsonify(parse_response)


@app.errorhandler(404)
def page_not_found(error):
    """Error handling 404

    """
    return "This route is not found", 404


@app.route("/api/asset/add/<string:char_code>/<string:name>/<float:capital>/<float:interest>")
def add_active(char_code: str, name: str, capital: float, interest: float):
    """Add active in our bank


    """
    if name in app.bank:
        return f"Asset '{name}' is already exist", 403

    asset = Asset(char_code, name, capital, interest)
    app.bank[name] = asset

    return f"Asset '{name}' was successfully added", 200


@app.route("/api/asset/list")
def get_list_assets():
    """Get list assets in our bank

    """
    result = []
    for asset in app.bank.values():
        result.append(asset.get_content())

    sort_result = sorted(result, key=lambda x: x[0])

    return jsonify(sort_result)


@app.route("/api/asset/cleanup")
def clean_assets():
    """Clean our bank

    """
    app.bank = {}
    status_code = Response(status=200)

    return status_code


@app.route("/api/asset/get")
def get_assets_from_query():
    """Get content for assets from query

    """
    request_query = request.args.get("query", "")
    result = []
    for asset_name in request_query:
        if asset_name in app.bank:
            result.append(app.bank[asset_name].get_content())

    sort_result = sorted(result, key=lambda x: x[0])

    return jsonify(sort_result)


if __name__ == "__main__":
    app.run(debug=True)
