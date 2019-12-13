from udata_piwik.download_counter import DailyDownloadCounter


def test_detect_by_url_mismatch(app):
    '''Check that everything is fine when detect_by_url does not match'''
    counter = DailyDownloadCounter('2012-12-12')
    counter.detect_by_url({'url': 'nimp'})
    assert counter.resources == []
    assert counter.community_resources == []
