from linkedin_job_scraper.job_search import JobSearch, BASE_SEARCH_URL


def test_job_search_url_generation():
    params = {
        'keywords': 'Data Engineer',
        'location': 'Germany',
        'distance': 25,
        'work_modes': [1, 2],
        'industries': [3, 4],
        'company_codes': [10, 11],
        'experience_levels': [3, 4],
        'easy_apply': True,
        'posted_ago_max': 10
    }
    mock_driver = None
    job_search = JobSearch(mock_driver, **params)
    url = job_search.get_search_url()
    assert url == BASE_SEARCH_URL + ('/?currentJobId=&keywords=Data%20Engineer&location=Germany'
                                     '&distance=25&f_C=10%2C11&f_WT=1%2C2&f_I=3%2C4&f_E=3%2C4&f_TPR=r10&f_AL=true')