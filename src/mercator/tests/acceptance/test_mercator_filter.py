from webtest import TestApp
from pytest import fixture
import time

from mercator.tests.fixtures.fixturesMercatorProposals1 import create_proposals
from adhocracy_frontend.tests.acceptance.shared import login_god
from adhocracy_frontend.tests.acceptance.shared import wait


@fixture(scope='module')
def proposals():
    return create_proposals()


class TestMercatorFilter(object):

    @fixture(scope='class')
    def sidebar(self, browser):
        return browser.find_by_css(".moving-column-sidebar").first.find_by_tag("ul")

    @fixture(scope='class')
    def locations(self, browser, sidebar):
        return [l.find_by_tag("a").first for l in sidebar[1].find_by_tag("li")]

    @fixture(scope='class')
    def budgets(self, browser, sidebar):
        return [l.find_by_tag("a").first for l in sidebar[2].find_by_tag("li")]

    @fixture(scope='class')
    def browser(self, browser, app):
        TestApp(app)
        browser.visit(browser.app_url + 'r/mercator/')
        assert wait(lambda: browser.find_link_by_text("filters"))

        browser.find_link_by_text("filters").first.click()
        assert wait(lambda: browser.find_by_css(".moving-column-sidebar").visible)

        return browser

    def test_filter_location(self, browser, locations, proposals):
        for location in locations:
            location.click()
            assert wait(lambda: is_filtered(browser, proposals, location=location.text))

    def test_unfilter_location(self, browser, locations, proposals):
        locations[-1].click()
        assert wait(lambda: is_filtered(browser, proposals))

    def test_filter_budget(self, browser, budgets, proposals):
        for budget in budgets:
            budget.click()
            assert wait(lambda: is_filtered(browser, proposals, budget=budget.text))

    def test_unfilter_budget(self, browser, budgets, proposals):
        budgets[-1].click()
        assert wait(lambda: is_filtered(browser, proposals))

    def test_filter_combinations(self, browser, locations, budgets, proposals):
        for location in locations:
            location.click()
            for budget in budgets:
                budget.click()
                assert wait(lambda: is_filtered(browser, proposals, location=location.text, budget=budget.text))



def is_filtered(browser, proposals, location=None, budget=None):
    introduction_sheet = "adhocracy_mercator.sheets.mercator.IIntroduction"
    title = lambda p: p[18]["body"]["data"][introduction_sheet]["title"]
    expected_titles = [title(p) for p in proposals if _verify_location(location, p) and _verify_budget(budget, p)]

    proposal_list = browser.find_by_css(".moving-column-body").first.find_by_tag("ol").first
    actual_titles = [a.text for a in proposal_list.find_by_css("h3 a")]

    return set(expected_titles) == set(actual_titles)


def _verify_location(location, proposal):
    """Return whether the passed proposal is of given location."""
    data = proposal[16]["body"]["data"]
    details = data["adhocracy_mercator.sheets.mercator.IDetails"]

    if location == "Specific":
        return details["location_is_specific"]

    elif location == "Online":
        return details["location_is_online"]

    elif location == "Linked to the Ruhr area":
        return details["location_is_linked_to_ruhr"]

    elif location is None:
        return True

    return False


def _verify_budget(budget, proposal):
    """Return whether the passed proposal is of given budget."""
    data = proposal[4]["body"]["data"]
    finance = data["adhocracy_mercator.sheets.mercator.IFinance"]

    if budget == "0 - 5000 €":
        return 0 <= finance["budget"] <= 5000

    elif budget == "5000 - 10000 €":
        return 5000 <= finance["budget"] <= 10000

    elif budget == "10000 - 20000 €":
        return 10000 <= finance["budget"] <= 20000

    elif budget == "20000 - 50000 €":
        return 20000 <= finance["budget"] <= 50000

    elif budget is None:
        return True

    return False
