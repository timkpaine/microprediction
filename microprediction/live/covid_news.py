# You will need a RavenPack account to use this
from microprediction.config_private import COVID_API, COVID_UUID
import logging
import random
import time
from datetime import datetime, timedelta
from pprint import pprint

from microprediction import MicroWriter

from ravenpackapi import RPApi, ApiConnectionError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# initialize the API (here we use the RP_API_KEY in os.environ)
api = RPApi(api_key=COVID_API)

# query the realtime feed
ds = api.get_dataset(dataset_id=COVID_UUID)


def wait_between_attempts():
    """ Incremental backoff between connection attempts """
    wait_time = 19.3  # time is in seconds
    while True:
        yield wait_time
        wait_time = min(wait_time * 1.5, 30)
        wait_time *= (100 + random.randint(0, 50)) / 100

wait_time = wait_between_attempts()


def get_live_data_keyword_count(keywords):
    """ Return number of articles (entities) containing a keyword """
    count = 0
    end_time = datetime.now() + timedelta(minutes = 20)
    prev_headline = ""
    # bool for if any keyword is found in any entity for a single article
    found = False
    while True:
        try:
            for record in ds.request_realtime():
                if datetime.now() > end_time:
                    return count
                hl = record.headline
                entity = record.entity_name

                # make sure to only count each article once
                if prev_headline != hl:
                    prev_headline = hl
                    found = False
                if not found:
                    for keyword in keywords:
                        if keyword.lower() in entity.lower().strip():
                            count += 1
                            found = True
        except (KeyboardInterrupt, SystemExit):
            break
        except ApiConnectionError as e:
            logger.error("Connection error %s: reconnecting..." % e)
            time.sleep(next(wait_time))
    return count

def number_of_articles_that_mention_facebook_or_twitter():
    return get_live_data_keyword_count(["Facebook", "Twitter"])

def number_of_articles_that_mention_cuomo_or_nyc():
    return get_live_data_keyword_count(["Cuomo", "New York City"])


BASE_NAME = 'covid_number_of_articles_mentioning_'

def run():
    try:
        from microprediction.config_private import TRAFFIC_WRITE_KEY
        mw = MicroWriter(write_key=TRAFFIC_WRITE_KEY)
    except:
        raise Exception("You need to set the write key for this example to work")
    while True:
        value = number_of_articles_that_mention_facebook_or_twitter()
        res = mw.set(name=BASE_NAME+"facebook_or_twitter.json",value=float(value))
        pprint({'count':value,"res":res})
        print('',flush=True)
        # print(value)

# run()


def pretty_print():
    prev_headline = ""
    while True:
        try:
            for record in ds.request_realtime():
                hl = record.headline
                ts = record.timestamp_utc
                if prev_headline != hl:
                    print("-"*100)
                    print("{} // {}".format(ts, hl))
                    prev_headline = hl
                print("[{}] {}".format(record.event_relevance, record.entity_name))
        except (KeyboardInterrupt, SystemExit):
            break
        except ApiConnectionError as e:
            logger.error("Connection error %s: reconnecting..." % e)
            time.sleep(next(wait_time))
