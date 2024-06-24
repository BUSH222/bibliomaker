en = {
    'app': {
        'welcome': 'Welcome to bibliomaker!\nRight now it is',
        'wiki_info': 'Wikipedia information found:\n',
        'date_of_birth': 'Date of Birth: ',
        'date_of_death': 'Date of death: ',
        'place_of_birth': 'Place of Birth: ',
        'place_of_death': 'Place of Death: ',
        'description': 'Description: ',
        'exists_in_higeo': 'Person exists in the higeo database: ',
        'bibliographical_info': 'Bibliographical info:\n\n',
        'rsl_data': 'RSL Data:\n',
        'geokniga_data': 'Geokniga Data:\n',
        'rgo_data': 'RGO Data:\n',
        'nnr_data': 'NNR Data:\n',
        'spb_data': 'SPB Data:\n',
        'rnb_card_images': 'RNB Card Images:\n',
        'start': 'Start',
        'surname': 'Surname',
        'name': 'Name',
        'patronymic': 'Patronymic',
        'keywords': 'Keywords',
    },

    'handlers': {
        'error': 'Something went wrong, try again:\nFull exception:\n',
    },

    'scrapers': {
        'geoknigasearch': {
            'start': 'Starting the geokniga search...',
            'looking': 'Looking for the total number of pages',
            'pages': 'Performing requests to get the data, pages found: ',
            'books': 'Filtering the data, books found: ',
            'done': 'Done!',
        },
        'higeosearch': {
            'start': 'Starting the search on the higeo.ginras.ru website',
            'done': 'Done!',
        },
        'nnrsearch': {
            'start': 'Checking if a person exists in nnr. ..',
            'description': 'Obtaining a description from the cards',
            'done': 'Done!',
        },
        'rgosearch': {
            'start': 'Checking if a person exists in rgo...',
            'not_responding': 'RGO cannot be accessed',
            'description': 'Obtaining a description from the cards',
            'done': 'Done!',
            'not_found': 'Not found, exiting',
        },
        'rnbsearch': {
            'start': 'Checking if a person exists in rnb...',
            'description': 'Obtaining a description from the cards',
            'done': 'Done!',
            'not_found': 'Not found'

        },
        'rslsearch': {
            'non_parr_start': 'Non-parallel search specified, starting...',
            'number_of_pages': 'Found, number of pages: ',
            'number_of_hits': 'number of hits: ',
            'fetching_pages': 'Fetching pages',
            'gathering_bib': 'Gathering bibliographical info...',
            'done': 'Done!',
            'start': 'Starting the RSL search...',
            'too_large': 'Too large for parallel search, starting the non-parallel search',
            'found_pages': 'Found pages: ',
            'sleeping': 'Sleeping to prevent rate limits'
        },
        'spbsearch': {
            'start': 'Checking if a person exists in spb...',
            'description': 'Obtaining a description from the cards',
            'done': 'Done!',
            'not_found': 'Not found',
        },
        'wikisearch': {
            'start': 'Checking if a person exists in wikipedia...',
            'not_found': 'Not found, exiting',
            'found': 'Found',
            'wikimedia_id_start': 'Obtaining the wikimedia unique id',
            'error_wikimedia': 'Error getting wikimedia id, no further information can be accessed.',
            'dates_start': 'Fetching dates and places.',
            'error_no_claims': 'No claims for wikimedia id found, no further info can be obtained',
            'error_dob_pob': 'Error fetching date of birth or place of birth id',
            'error_dod_pod': 'Error fetching date of death or place of death id',
            'error_pob': 'Error fetching place of birth',
            'error_pod': 'Error fetching place of death',
            'done': 'Done!',

        },
    }
}
