from pytest import fixture
from pytest import raises
from pytest import mark
from webtest import TestApp

from adhocracy_frontend.tests.acceptance.shared import login_god
from mercator.tests.fixtures.fixturesMercatorProposals1 import create_proposals

class TestMercatorForm:

    @fixture(scope='class')
    def browser(self, browser):
        login_god(browser)
        browser.visit(browser.app_url + 'r/mercator/@create_proposal')
        return browser

    def test_fill_all_fields(self, browser):
        fill_all(browser)
        assert is_valid(browser)

    @mark.skipif(True, reason="pending")
    # FIXME: this should work, but: (1) it may alter state and confuse
    # subsequent tests; and (2) i'm not sure if it does even work
    # itself.
    def test_submitting_creates_a_new_proposal(self, browser, app):
        browser.find_by_css('input[type="submit"]').first.click()
        #FIXME make this test shorter and more acceptance test like
        import time
        time.sleep(1)
        app = TestApp(app)
        rest_url = 'http://localhost'
        post_pool = '/adhocracy'

        resp = app.get(rest_url + post_pool)
        assert resp.status_code == 200
        elements = resp.json['data']['adhocracy_core.sheets.pool.IPool']['elements']
        assert len(elements) == 1

    def test_field_extra_exprerience_is_optional(self, browser):
        browser.find_by_name('experience').first.fill('')
        assert is_valid(browser)

    def test_field_status_text_is_not_shown_if_non_custom_status(self, browser):
        browser.find_by_name('organization-info-status-enum').first.check()
        status_text = 'organization-info-status-other'
        assert browser.is_element_not_present_by_name(status_text)
        assert is_valid(browser)

    def test_field_status_text_is_required_if_custom_status(self, browser):
        browser.find_by_name('organization-info-status-enum').last.check()
        status_text = 'organization-info-status-other'
        assert browser.is_element_present_by_name(status_text)
        assert not is_valid(browser)
        browser.find_by_name(status_text).first.fill('statustext')
        assert is_valid(browser)

    def test_location_is_required(self, browser):
        browser.uncheck('location-location-is-specific')
        browser.uncheck('location-location-is-online')
        browser.uncheck('location-location-is-linked-to-ruhr')
        assert not is_valid(browser)
        browser.check('location-location-is-online')
        assert is_valid(browser)

    def test_field_name_is_required(self, browser):
        browser.find_by_name('user-info-first-name').first.fill('')
        assert not is_valid(browser)

    def test_login_is_required(self, browser):
        with raises(AssertionError):
            create_proposals(user_token="", n=1)

def is_valid(browser):
    form = browser.find_by_css('.mercator-proposal-form').first
    return not form.has_class('ng-invalid')


def fill_all(browser):
    browser.find_by_name('user-info-first-name').first.fill('name')
    browser.find_by_name('user-info-last-name').first.fill('lastname')

    # NOTE: Due to angular magic used in ng-options, the value which is
    # stored in the respective ng-model (e.g. 'DE') isn't reflected in the
    # DOM, and an index is used instead.
    browser.select('user-info-country', '1')

    browser.find_by_name('organization-info-status-enum').first.check()
    browser.find_by_name('organization-info-name').first.fill(
        'organisation name')
    browser.find_by_name('organization-info-country').first.select('2')
    browser.find_by_name('organization-info-website').first.fill(
        'http://example.com')

    browser.find_by_name('introduction-title').first.fill('title')
    browser.find_by_name('introduction-teaser').first.fill('teaser')

    browser.find_by_name('description-description').first.fill('description')
    browser.find_by_name('location-location-is-specific').first.check()
    browser.find_by_name('location-location-specific-1').first.fill('Bonn')
    browser.find_by_name('location-location-is-linked-to-ruhr').first.check()
    browser.find_by_name('story').first.fill('story')

    browser.find_by_name('outcome').first.fill('success')
    browser.find_by_name('steps').first.fill('plan')
    browser.find_by_name('value').first.fill('relevance')
    browser.find_by_name('partners').first.fill('partners')

    browser.find_by_name('finance-budget').first.fill(1000)
    browser.find_by_name('finance-requested-funding').first.fill(1000)
    browser.find_by_name('finance-granted').first.check()

    browser.find_by_name('experience').first.fill('experience')
    browser.find_by_name('heard-from-colleague').first.check()

    browser.find_by_name('accept-disclaimer').first.check()
