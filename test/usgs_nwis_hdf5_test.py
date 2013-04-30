import os
import time

import pytest

import ulmo
import test_util


TEST_FILE_PATH = '/tmp/ulmo_test.h5'


@pytest.fixture
def delete_test_file():
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)


def test_update_site_list(delete_test_file):
    site_files = ['usgs/nwis/RI_daily.xml', 'usgs/nwis/RI_instantaneous.xml']
    for site_file in site_files:
        test_site_file = test_util.get_test_file_path(site_file)
        ulmo.usgs.nwis.hdf5.update_site_list(path=TEST_FILE_PATH,
                input_file=test_site_file)

    sites = ulmo.usgs.nwis.hdf5.get_sites(TEST_FILE_PATH)
    assert len(sites) == 64

    test_sites = {
        '01111410': {
            'agency': 'USGS',
            'code': '01111410',
            'county': '44007',
            'huc': '01090003',
            'location': {
                'latitude': '41.9409318',
                'longitude': '-71.6481214',
                'srs': 'EPSG:4326'
            },
            'name': 'CHEPACHET RIVER WEST OF GAZZA RD AT GAZZAVILLE, RI',
            'state_code': '44',
            'network': 'NWIS',
            'site_type': 'ST',
            'timezone_info': {
                'default_tz': {
                    'abbreviation': 'EST',
                    'offset': '-05:00'
                },
                'dst_tz': {
                    'abbreviation': 'EDT',
                    'offset': '-04:00',
                },
                'uses_dst': False,
            }
        }
    }

    for test_code, test_value in test_sites.iteritems():
        assert sites[test_code] == test_value


def test_get_site(delete_test_file):
    site_code = '08068500'
    site_data_file = 'usgs/nwis/site_%s_daily.xml' % site_code
    ulmo.usgs.nwis.hdf5.get_site(site_code, TEST_FILE_PATH,
            input_file=site_data_file)

    site = ulmo.usgs.nwis.hdf5.get_site(site_code, TEST_FILE_PATH)
    assert len(site) == 10


def test_get_site_raises_lookup(delete_test_file):
    site_code = '98068500'
    site_data_file = 'usgs/nwis/site_%s_daily.xml' % site_code

    ulmo.usgs.nwis.hdf5.get_site(site_code, TEST_FILE_PATH,
            input_file=site_data_file)

    with pytest.raises(LookupError):
        ulmo.usgs.nwis.hdf5.get_site(site_code, TEST_FILE_PATH)


def test_non_usgs_site(delete_test_file):
    site_code = '07335390'
    site_data_file = 'usgs/nwis/site_%s_instantaneous.xml' % site_code
    ulmo.usgs.nwis.hdf5.update_site_data(site_code, period='all',
            path=TEST_FILE_PATH, input_file=site_data_file)

    site_data = ulmo.usgs.nwis.hdf5.get_site_data(site_code, path=TEST_FILE_PATH)
    assert len(site_data['00062:00011']['values']) > 1000


def test_update_site_data(delete_test_file):
    site_code = '01117800'
    site_data_file = 'usgs/nwis/site_%s_daily.xml' % site_code

    ulmo.usgs.nwis.hdf5.update_site_data(site_code, path=TEST_FILE_PATH,
            input_file=site_data_file)
    site_data = ulmo.usgs.nwis.pytables.get_site_data(site_code, path=TEST_FILE_PATH)

    last_value = site_data['00060:00003']['values'][-1]

    assert last_value['value'] == '74'
    assert last_value['last_checked'] == last_value['last_modified']
    original_timestamp = last_value['last_checked']

    # sleep for a second so last_modified changes
    time.sleep(1)

    update_data_file = 'usgs/nwis/site_%s_daily_update.xml' % site_code
    ulmo.usgs.nwis.hdf5.update_site_data(site_code, path=TEST_FILE_PATH,
            input_file=update_data_file)
    site_data = ulmo.usgs.nwis.pytables.get_site_data(site_code, path=TEST_FILE_PATH)

    last_value = site_data['00060:00003']['values'][-1]
    assert last_value['last_checked'] != original_timestamp
    assert last_value['last_checked'] == last_value['last_modified']

    modified_timestamp = last_value['last_checked']

    test_values = [
        dict(datetime="1963-01-23T00:00:00", last_checked=modified_timestamp, last_modified=modified_timestamp, qualifiers="A", value='7'),
        dict(datetime="1964-01-23T00:00:00", last_checked=modified_timestamp, last_modified=modified_timestamp, qualifiers="A", value='1017'),
        dict(datetime="1964-01-24T00:00:00", last_checked=original_timestamp, last_modified=original_timestamp, qualifiers="A", value='191'),
        dict(datetime="1969-05-26T00:00:00", last_checked=modified_timestamp, last_modified=modified_timestamp, qualifiers="A", value='1080'),
        dict(datetime="2012-05-25T00:00:00", last_checked=modified_timestamp, last_modified=original_timestamp, qualifiers="P", value='56'),
        dict(datetime="2012-05-26T00:00:00", last_checked=modified_timestamp, last_modified=original_timestamp, qualifiers="P", value='55'),
        dict(datetime="2012-05-27T00:00:00", last_checked=modified_timestamp, last_modified=modified_timestamp, qualifiers="A", value='52'),
        dict(datetime="2012-05-28T00:00:00", last_checked=modified_timestamp, last_modified=original_timestamp, qualifiers="P", value='48'),
        dict(datetime="2012-05-29T00:00:00", last_checked=modified_timestamp, last_modified=modified_timestamp, qualifiers="P", value='1099'),
        dict(datetime="2012-05-30T00:00:00", last_checked=modified_timestamp, last_modified=modified_timestamp, qualifiers="P", value='1098'),
        dict(datetime="2012-05-31T00:00:00", last_checked=modified_timestamp, last_modified=original_timestamp, qualifiers="P", value='41'),
        dict(datetime="2012-06-01T00:00:00", last_checked=modified_timestamp, last_modified=original_timestamp, qualifiers="P", value='37'),
        dict(datetime="2012-06-02T00:00:00", last_checked=modified_timestamp, last_modified=modified_timestamp, qualifiers="P", value='1097'),
        dict(datetime="2012-06-03T00:00:00", last_checked=modified_timestamp, last_modified=original_timestamp, qualifiers="P", value='69'),
        dict(datetime="2012-06-04T00:00:00", last_checked=modified_timestamp, last_modified=original_timestamp, qualifiers="P", value='81'),
        dict(datetime="2012-06-05T00:00:00", last_checked=modified_timestamp, last_modified=modified_timestamp, qualifiers="P", value='1071'),
        dict(datetime="2012-06-06T00:00:00", last_checked=modified_timestamp, last_modified=modified_timestamp, qualifiers="P", value='2071'),
    ]

    for test_value in test_values:
        assert site_data['00060:00003']['values'].index(test_value) >= 0


def test_last_refresh_gets_updated(delete_test_file):
    site_code = '01117800'
    site_data_file = 'usgs/nwis/site_%s_daily.xml' % site_code
    ulmo.usgs.nwis.hdf5.update_site_data(site_code, path=TEST_FILE_PATH,
            input_file=site_data_file)
    site_data = ulmo.usgs.nwis.pytables.get_site_data(site_code, path=TEST_FILE_PATH)

    # sleep for a second so last_modified changes
    time.sleep(1)

    update_data_file = 'usgs/nwis/site_%s_daily_update.xml' % site_code
    ulmo.usgs.nwis.hdf5.update_site_data(site_code, path=TEST_FILE_PATH,
            input_file=update_data_file)
    site_data = ulmo.usgs.nwis.hdf5.get_site_data(site_code, path=TEST_FILE_PATH)

    last_value = site_data['00060:00003']['values'][-1]
    last_checked = last_value['last_checked']

    site = ulmo.usgs.nwis.hdf5.get_site(site_code, path=TEST_FILE_PATH)
    last_refresh = site['last_refresh']
    assert last_refresh == last_checked