import requests as r

class barchart_scraper:
    def __init__(self, symbol):
        self.__request_headers = {
            "Accept":"application/json",
            "Accept-Encoding":"gzip, deflate, sdch, br",
            "Accept-Language":"en-US,en;q=0.8",
            "Connection":"keep-alive",
            "Host":"core-api.barchart.com",
            "Origin":"https://www.barchart.com",
            "Referer":"https://www.barchart.com/etfs-funds/quotes/SPY/options",
            "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
            }

        self.__base_url_str = 'https://core-api.barchart.com/v1/options/chain?symbol={}&fields=strikePrice%2ClastPrice%2CpercentFromLast%2CbidPrice%2Cmidpoint%2CaskPrice%2CpriceChange%2CpercentChange%2Cvolatility%2Cvolume%2CopenInterest%2CoptionType%2CdaysToExpiration%2CexpirationDate%2CsymbolCode%2CsymbolType&groupBy=optionType&raw=1&meta=field.shortName%2Cfield.type%2Cfield.description'

        self.__expiry_url_str = "https://core-api.barchart.com/v1/options/chain?symbol={}&fields=strikePrice%2ClastPrice%2CpercentFromLast%2CbidPrice%2Cmidpoint%2CaskPrice%2CpriceChange%2CpercentChange%2Cvolatility%2Cvolume%2CopenInterest%2CoptionType%2CdaysToExpiration%2CexpirationDate%2CsymbolCode%2CsymbolType&groupBy=optionType&expirationDate={}&raw=1&meta=field.shortName%2Cfield.type%2Cfield.description"
        self.symbol = symbol
    # ------------------------------------------------
    def _construct_url(self):
        return self.__base_url_str.format(self.symbol)

    def _construct_expiry_url(self, expiry):
        return self.__expiry_url_str.format(self.symbol, expiry)
    # ------------------------------------------------
    def post_url(self, expiry=None):
        if not expiry:
            return r.post(
                url = self._construct_url(),
                headers = self.__request_headers
                )
        else:
            return r.post(
                url = self._construct_expiry_url(expiry=expiry),
                headers = self.__request_headers
                )
    # ------------------------------------------------
    def get_expirys(self, response):
        return response.json()['meta']['expirations']