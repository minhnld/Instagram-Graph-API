import json
import logging
from fastapi import HTTPException
from typing import Any
from http import HTTPStatus

import requests

from app.models.schemas.instagram import Me


class InstagramGraphApiClient:
    def __init__(self, environment: str) -> None:
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )
        self.environment = environment
        self.is_debug = self.environment != 'production'  # debug mode for api call
        self.graph_domain = 'https://graph.facebook.com/'  # base domain for api calls
        self.graph_version = 'v18.0'  # version of the meta graph api we are hitting
        self.endpoint_base = self.graph_domain + self.graph_version + '/'  # base endpoint with domain and version

    def request_get_endpoint(self, url, endpoint_params):
        data = requests.get(url, endpoint_params)  # make get request
        response = dict()  # hold response info
        response['url'] = url  # url we are hitting
        response['json_data'] = json.loads(data.content)  # response data from the api
        if self.is_debug:  # display out response info
            self.display_api_call_data(response, endpoint_params)  # display response

        return response  # get and return content

    def display_api_call_data(self, response, endpoint_params):
        """ Print out to cli response from api call """
        self.logger.debug("\nURL: ")
        self.logger.debug(response['url'])
        self.logger.debug("\nEndpoint Params: ")
        self.logger.debug(json.dumps(endpoint_params, indent=4))
        self.logger.debug("\nResponse: ")
        self.logger.debug(json.dumps(response['json_data'], indent=4))

    # Use this method to verify token
    def me(
            self,
            token: str,
    ) -> Me:
        try:
            endpoint_params = dict()
            endpoint_params['access_token'] = token
            endpoint_params['fields'] = 'permissions,name'
            url = self.endpoint_base + 'me'  # endpoint url
            payload = self.request_get_endpoint(url, endpoint_params)['json_data']
        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=str(e),
            )
        if 'error' in payload:
            if payload['error']['type'] == 'OAuthException':
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail=str(payload),
                )
            else:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=str(payload),
                )
        user = Me(**payload)
        user.token = token
        return user

    def get_instagram_account(self, access_token: str, page_id: str) -> dict[str, str | Any]:
        endpoint_params = dict()  # parameter to send to the endpoint
        endpoint_params['access_token'] = access_token
        endpoint_params['fields'] = 'about,instagram_business_account,genre,bio,category'
        url = self.endpoint_base + page_id  # endpoint url
        return self.request_get_endpoint(url, endpoint_params)  # make the api call

    def get_instagram_accounts(self, access_token: str) -> dict[str, str | Any]:
        endpoint_params = dict()  # parameter to send to the endpoint
        endpoint_params['access_token'] = access_token
        endpoint_params['fields'] = 'instagram_business_account,about,bio,name'
        url = self.endpoint_base + 'me/accounts'
        return self.request_get_endpoint(url, endpoint_params)  # make the api call

    def get_user_pages(self, access_token: str) -> dict[str, str | Any]:
        endpoint_params = dict()  # parameter to send to the endpoint
        endpoint_params['access_token'] = access_token  # access token
        url = self.endpoint_base + 'me/accounts'  # endpoint url
        return self.request_get_endpoint(url, endpoint_params)  # make the api call

    def create_image_container(self,
                               access_token: str,
                               instagram_business_account_id: str,
                               image_url: str,
                               caption: str) -> dict[str, str | Any]:
        endpoint_params = dict()
        endpoint_params['access_token'] = access_token
        url = self.endpoint_base + f"{instagram_business_account_id}/media?image_url={requests.utils.quote(image_url)}&caption={requests.utils.quote(caption)}"
        data = requests.post(url, endpoint_params)  # make get request
        response = dict()  # hold response info
        response['url'] = url  # url we are hitting
        response['json_data'] = json.loads(data.content)  # response data from the api
        return response

    def publish_image(self,
                      access_token: str,
                      instagram_business_account_id: str,
                      instagram_container_id: str,
                      ) -> dict[str, str | Any]:
        url = self.endpoint_base + f"{instagram_business_account_id}/media_publish?creation_id={instagram_container_id}&access_token={access_token}"
        data = requests.post(url)  # make get request
        response = dict()  # hold response info
        response['url'] = url  # url we are hitting
        response['json_data'] = json.loads(data.content)  # response data from the api
        return response  # make the api call

    def get_image_insights(self,
                           access_token: str,
                           media_id: str,
                           ) -> dict[str, str | Any]:
        endpoint_params = dict()  # parameter to send to the endpoint
        endpoint_params['access_token'] = access_token
        url = self.endpoint_base + media_id + '/insights?metric=likes,comments,reach,impressions'  # endpoint url
        return self.request_get_endpoint(url, endpoint_params)  # make the api call

    def get_all_medias(self,
                       access_token: str,
                       instagram_container_id: str,
                       ) -> dict[str, str | Any]:
        endpoint_params = dict()  # parameter to send to the endpoint
        endpoint_params['access_token'] = access_token
        url = self.endpoint_base + instagram_container_id + '/media?fields=permalink'  # endpoint url
        return self.request_get_endpoint(url, endpoint_params)  # make the api call
