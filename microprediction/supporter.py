# Things you can run to help support the overall effort
import requests, random
from pprint import pprint
from microprediction import new_key
import multiprocessing as mp

def donate(difficulty=None, password=None, donor='anonymous'):
    try:
        donaten(difficulty,password,donor)
    except:
        print("multithreading is not happy",flush=True)
        donate1(difficulty,password,donor)

def donaten(difficulty=None, password=None, donor='anonymous'):
    num_procs = mp.cpu_count()
    pool = mp.Pool(4*num_procs)
    result = [ pool.apply(func=donate1,args=(difficulty,password,donor)) for _ in range(4*num_procs) ]
    pool.close()


def donate1(difficulty=None, password=None, donor='anonymous'):
    if password is None:
        try:
            from microprediction.config_private import DONATION_PASSWORD, DONOR_NAME
        except:
            raise Exception("Ask Peter for the donation password ")
    write_key = new_key(difficulty=8)
    res = requests.post('https://www.microprediction.com/donations/' + write_key,data={'password': password, 'donor': donor})
    if res.status_code==200:
        if 'password' in res.json()['message']:
            return {"error":res.json()}
        else:
            if difficulty is None:
                difficulty = random.choice([12,13])
            while True:
                print("Mining and donating the MUIDs with password "+password+" and donor name "+donor+". Thanks. Difficulty set to "+str(difficulty))
                write_key = new_key(difficulty=12)
                print(write_key,flush=True)
                res = requests.post('https://www.microprediction.com/donations/' + write_key, data={'password': DONATION_PASSWORD,'donor':DONOR_NAME})
                pprint(res.json())
    else:
        return res


if __name__=="__main__":
    donate(difficulty=8,password='5581cee8a281f4fd8cbe404143017046',donor='test')