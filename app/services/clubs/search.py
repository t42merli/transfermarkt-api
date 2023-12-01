from dataclasses import dataclass
from datetime import datetime

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url
from app.utils.xpath import Clubs


@dataclass
class TransfermarktClubSearch(TransfermarktBase):
    """
    A class for searching football clubs on Transfermarkt and retrieving search results.

    Args:
        query (str): The search query for finding football clubs.
        URL (str): The URL template for the search query.
        page_number (int): The page number of search results (default is 1).
    """

    query: str = None
    URL: str = (
        "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={query}&Verein_page={page_number}"
    )
    page_number: int = 1

    def __post_init__(self) -> None:
        """Initialize the TransfermarktClubSearch class."""
        self.URL = self.URL.format(query=self.query, page_number=self.page_number)
        self.page = self.request_url_page()

    def __parse_search_results(self) -> list:
        """
        Parse the search results page and extract information about the found football clubs.

        Returns:
            list: A list of dictionaries, where each dictionary contains information about a
                football club found in the search results, including the club's unique identifier,
                URL, name, country, squad size, and market value.
        """
        clubs_names = self.get_list_by_xpath(Clubs.Search.NAMES)
        clubs_urls = self.get_list_by_xpath(Clubs.Search.URLS)
        clubs_ids = [extract_from_url(url) for url in clubs_urls]
        clubs_countries = self.get_list_by_xpath(Clubs.Search.COUNTRIES)
        clubs_squads = self.get_list_by_xpath(Clubs.Search.SQUADS)
        clubs_market_values = self.get_list_by_xpath(Clubs.Search.MARKET_VALUES)

        clubs_league = self.get_list_by_xpath(Clubs.Search.LEAGUE)
        clubs_league_urls = self.get_list_by_xpath(Clubs.Search.LEAGUE_URLS)
        clubs_league_ids =  [extract_from_url(url) for url in clubs_league_urls]
        clubs_league_ids_formatted = []
        filteredClubs = []

        print(len(clubs_names), '\n\n', len(clubs_league))
        i = 0
        j = 0
        k = 0
        lastMatch = 1
        while i < len(clubs_league):
            if j >= len(clubs_names) or clubs_names[j] == clubs_league[i]:
                i+=1
                j+=1
                if lastMatch == 0:
                    filteredClubs.append("")
                    clubs_league_ids_formatted.append("")
                lastMatch = 0
            else:
                filteredClubs.append(clubs_league[i])
                clubs_league_ids_formatted.append(clubs_league_ids[k])
                i+=1
                k+=1
                lastMatch = 1


        
        return [
            {
                "id": idx,
                "url": url,
                "name": name,
                "country": country,
                "squad": squad,
                "marketValue": market_value,
                "league" : clubs_league,
                "leagueId": clubs_league_ids_formatted
            }
            for idx, url, name, country, squad, market_value, clubs_league, clubs_league_ids_formatted in zip(
                clubs_ids,
                clubs_urls,
                clubs_names,
                clubs_countries,
                clubs_squads,
                clubs_market_values,
                filteredClubs,
                clubs_league_ids_formatted
            )
        ]

    def search_clubs(self) -> dict:
        """
        Perform a search for football clubs on Transfermarkt and retrieve search results.

        Returns:
            dict: A dictionary containing the search query, current page number, last page number,
                search results, and the timestamp of when the search was conducted.
        """
        self.response["query"] = self.query
        self.response["pageNumber"] = self.page_number
        self.response["lastPageNumber"] = self.get_search_last_page_number(Clubs.Search.BASE)
        self.response["results"] = self.__parse_search_results()
        self.response["updatedAt"] = datetime.now()

        return self.response
