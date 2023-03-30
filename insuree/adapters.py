import requests
from dataclasses import dataclass
from typing import Any
from django.conf import settings
from datetime import datetime, timedelta
import threading
from graphql.error import GraphQLError
import json
from insuree.models import Insuree, HeraUtilities


class APIAdapter:

    def get_data(self) -> Any: 
        raise NotImplementedError




@dataclass
class HeraAdapter(APIAdapter):
    
    operation: str
    nin: str = None
    uin: str = None
    uuid: str = None
    lock = threading.Lock()


    def get_data(self):
        methods = {
            "access_token": self.__access_token,
            "get_one_person_info": self.__get_one_person,
            "get_bulk_info": self.__get_bulk_info,
            "verify": self.__verify,
            "match": self.__match,
            "document": self.__document,
            "get_subscriptions": self.__get_subscriptions,
            "subscribe_to_life_event": self.__subscribe_to_life_event,
            "confirm_subscription": self.__confirm_subscription,
            "unsubscribe_from_topic": self.__unsubscribe_from_topic,
            "create_topic": self.__create_topic,
            "get_topics": self.__get_topics,
            "delete_topic": self.__delete_topic,
            "publish_topic": self.__publish_topic,
        }
        
        return methods[self.operation]()
        

    def __utilities(self, name):
        instance, _ = HeraUtilities.objects.get_or_create(name=name)
        return instance
    
    def __access_token(self):
        # make it thread safe
        with self.lock:
            try:
                NOW = datetime.now()
                instance = self.__utilities('hera-token')

                # check if token is valid
                if (instance.expiry_time and instance.expiry_time > NOW):
                    TOKEN = instance.access_token
                else:
                    url = settings.HERA_TOKEN_URL
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                    data = {'client_id': 'hera-m2m','client_secret': settings.HERA_CLIENT_SECRET, 'grant_type': 'client_credentials'}
                    response = requests.post(url, headers=headers, data=data)
                    if response.status_code != 200:
                        raise GraphQLError(f"Error: {response.status_code}")
                    
                    _JSON = response.json()
                    TOKEN = _JSON['access_token']

                    instance.access_token = _JSON['access_token']
                    instance.expiry_time = NOW + timedelta(seconds=_JSON['expires_in'] - 60) # 60 seconds expiry buffer
                    instance.save()
                    
                return {"Authorization": f"Bearer {TOKEN}"}
            except Exception as e:
                import traceback
                traceback.print_exc()
                return e


    def __get_one_person(self):
        if headers := self.__access_token():
            url = f"{settings.HERA_GENERAL_URL}/persons/{self.nin}"
            response = requests.get(url, headers=headers, params=settings.HERE_QUERY_STR)
            self.__confirm_subscription()
            return response.json()
        return None

    

    def __get_bulk_info(self):
        if headers := self.__access_token():
            url = f"{settings.HERA_GENERAL_URL}/persons/"
            response = requests.get(url, headers=headers, params=settings.HERE_QUERY_STR)
            return response.json()
        return None

    def __verify(self):
        if headers := self.__access_token():
            url = f"{settings.HERA_GENERAL_URL}/persons/{self.uin}/verify"
            response = requests.post(url, headers=headers)
            return response.json()
        return None


    def __match(self):
        if headers := self.__access_token():
            url = f"{settings.HERA_GENERAL_URL}/persons/{self.uin}/match"
            response = requests.post(url, headers=headers)
            return response.json()
        return None


    def __document(self):
        if headers := self.__access_token():
            url = f"{settings.HERA_GENERAL_URL}/persons/{self.uin}/document"
            response = requests.get(url, headers=headers)
            return response.json()
        return None


    def __subscribe_to_life_event(self):
        subs = self.__get_subscriptions()
        headers = self.__access_token()
        if not subs and headers:
            url = settings.HERA_SUBSCRIBE_URL
            response = requests.post(url, headers=headers)
            response = response.json()
            instance = self.__utilities('LifeEventTopic')
            instance.subscription_uuid = response['uuid']
            instance.save()
            return response
        return None


    def __get_subscriptions(self):
        if headers := self.__access_token():
            url = f"{settings.HERA_GENERAL_URL}/subscriptions"
            response = requests.get(url, headers=headers)
            # rs = next((d for d in response.json() if 'gambia' in d['address']), None)
            return response.json()
        return None
    

    def __confirm_subscription(self):
        print("confirming subscription")
        if headers := self.__access_token():
            url = f"{settings.HERA_GENERAL_URL}/subscriptions/confirm"
            response = requests.get(url, headers=headers)
            print(response.json())
            return response.json()
        return None


    def __unsubscribe_from_topic(self):
        try:
            uuid = self.__utilities('LifeEventTopic').subscription_uuid
            if headers := self.__access_token():
                url = f"{settings.HERA_GENERAL_URL}/subscriptions/{uuid}"
                response = requests.delete(url, headers=headers)  
                return response.json()
            return None
        except Exception as e:
            import traceback
            traceback.print_exc()
            return e
 


    def __create_topic(self):
        if headers := self.__access_token():
            url = f"{settings.HERA_GENERAL_URL}/topics"
            response = requests.post(url, headers=headers)
            return response.json()
        return None
    

    def __get_topics(self):
        if headers := self.__access_token():
            url = f"{settings.HERA_GENERAL_URL}/topics"
            return requests.get(url, headers=headers)
        return None
    

    def __delete_topic(self):
        if headers := self.__access_token():
            url = f"{settings.HERA_GENERAL_URL}/topics/{self.uuid}"
            response = requests.delete(url, headers=headers)
            return response.json()
        return None
    

    def __publish_topic(self):
        if headers := self.__access_token():
            url = f"{settings.HERA_GENERAL_URL}/topics/{self.uuid}/publish"
            response = requests.post(url, headers=headers)
            return response.json()
        return None
    


class AnotherAdapter(APIAdapter):
    def get_data(self):
        "Code to get data from Another API"




class WebhookEventManager:
    
    def create_or_update_insuree(self, **kwargs):
        from insuree.models import Family, InsureePolicy
        from policy.models import Policy
        from product.models import Product
        from contribution.models import Premium
        try:
            insuree = Insuree.objects.filter(nin=kwargs['nin']).first()
            if not insuree:
                insuree =  Insuree.objects.create(
                    nin=kwargs['nin'], 
                    audit_user_id=1,
                    card_issued=False,
                    gender_id='M',
                    chf_id=kwargs['nin'],
                    other_names=kwargs.get(kwargs['first_name'], 'None'),
                    last_name=kwargs.get(kwargs['last_name'], 'None'),
                    uin=kwargs.get('uin', None),
                    place_of_birth=kwargs.get(',place_of_birth', None),
                    certificate_number=kwargs.get('certificate_number', None),
                    height=kwargs.get('height', None),
                    weight=kwargs.get('weight', None),
                    residential_alley=kwargs.get('residential_alley', None),
                    is_local=kwargs.get('is_local', None),
                    occupation=kwargs.get('occupation', None),
                    father_name=kwargs.get('father_name', None),
                    mother_name=kwargs.get('mother_name', None),
                    residential_village=kwargs.get('residential_village', None),
                    residential_district=kwargs.get('residential_district', None),
                    residential_province=kwargs.get('residential_province', None),
                    residential_house_number=kwargs.get('residential_house_number', None),
                    dob=kwargs.get('dob', None),
                    head=True,
                    marital=kwargs.get('marital', None),
                    passport=kwargs.get('passport', None),
                    phone=kwargs.get('phone', None),
                    email=kwargs.get('email', None),
                    current_address=kwargs.get('current_address', None),
                    geolocation=kwargs.get('geolocation', None),
                    current_village=kwargs.get('current_village', None),
                )
                family = Family.objects.create(head_insuree=insuree, audit_user_id=1)
                now = datetime.now()
                policy = Policy.objects.create(
                    family=family, 
                    audit_user_id=1,
                    enroll_date=now,
                    start_date=now,
                    product=Product.objects.all().first()
                )
                InsureePolicy.objects.create(
                    insuree=insuree, 
                    audit_user_id=1,
                    policy=policy,
                )
                prem = Premium.objects.create(
                    policy=policy,
                    audit_user_id=1,
                    receipt='Receipt',
                    amount=0,
                    pay_date=now,
                    pay_type='C',
                    # created_date=now,
                )
            else:
                fields = [field.name for field in Insuree._meta.get_fields()]
                cannot_be_none = ['last_name', 'first_name',]
                for key, value in kwargs.items():
                    if key in cannot_be_none and value is None:
                        value = 'None'
                    if key in fields:
                        setattr(insuree, key, value)
                insuree.save()
            return insuree
        except Exception as e:
            import traceback
            traceback.print_exc()
            return e

    def delete_insuree(self, nin):
        return Insuree.objects.filter(nin=nin).delete()


    def get_insuree(self, nin):
        return Insuree.objects.get(nin=nin)
    
