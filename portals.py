import requests
import os
import time

from dataclasses import dataclass
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
auth = os.getenv("auth")


@dataclass
class Model:
    name: str
    image_url: str
    rarity_per_mille: int
    floor: int
    collection: str


@dataclass
class NFT:
    id: str
    bundle_id: Optional[str]
    tg_id: str
    collection_id: str
    name: str
    price: int
    attributes: list
    listed_at = str
    status: str
    photo_url: str
    collection_floor_price: int


class PortalsMarketClient:
    APP_URL = "https://portal-market.com/api"

    def __init__(self, auth_token: str):
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": auth_token,
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
            }
        )

    def search_nfts(
        self, collection="Toy Bear", model="Matrix", limit=20, offset=0
    ) -> list[NFT]:
        search_data = []

        url = f"{self.APP_URL}/nfts/search"
        params = {
            "offset": offset,
            "limit": limit,
            "filter_by_collections": collection,
            "filter_by_models": model,
            "sort_by": "price asc",
            "status": "listed",
        }
        response = self.session.get(url, params=params)
        response_json = response.json().get("results", [])

        for nft in response_json:
            search_data.append(
                NFT(
                    id=nft.get("id"),
                    bundle_id=nft.get("bundle_id"),
                    tg_id=nft.get("tg_id"),
                    collection_id=nft.get("collection_id"),
                    name=nft.get("name"),
                    price=nft.get("price"),
                    attributes=nft.get("attributes"),
                    status=nft.get("status"),
                    photo_url=nft.get("photo_url"),
                    collection_floor_price=nft.get("floor_price"),
                )
            )

        return search_data

    def find_options(self, collection) -> list[Model]:
        collection_data = []
        url = f"{self.APP_URL}/collections/filters?short_names={collection}"
        response = self.session.get(url)

        response_json = response.json()

        floors = response_json["floor_prices"][collection]
        models = response_json["collections"][collection]["models"]
        for model in models:
            collection_data.append(
                Model(
                    name=model.get("name"),
                    image_url=model.get("url"),
                    rarity_per_mille=model.get("rarity_per_mille"),
                    floor=floors["models"].get(model.get("name")),
                    collection=model.get("collection"),
                )
            )
        return collection_data

    def wallet_balance(self):
        url = f"{self.APP_URL}/users/wallets/"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def buy_nft(self, nft_id: str, price: str):
        url = f"{self.APP_URL}/nfts"
        payload = {"nft_details": [{"id": nft_id, "price": price}]}
        response = self.session.post(url, json=payload)

        return response.json()


# Example usage
client = PortalsMarketClient(auth)

result = client.find_options("preciouspeach")
for model in result:
    nfts = client.search_nfts(model.collection, model.name)
    for nft in nfts:
        print(nft)
    time.sleep(3)
