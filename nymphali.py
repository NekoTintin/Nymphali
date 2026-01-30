import asyncio
import json
import aiofiles
from nio import AsyncClient, MatrixRoom, RoomMessageText, InviteMemberEvent

from src import invite_callback
from src import message_callback
from src import reaction_callback
from utils.utils import print_with_color

CREDENTIALS_FILE = "data/credentials.json"

class NymphaliBot:
	def __init__(self, credential_file: str=CREDENTIALS_FILE, prefix: str="?"):
		self.homeserver = str
		self.credential_file = credential_file
		self.prefix = prefix
		self.client	= None
		self.state = True
		self.jellyfin = dict()
 
	async def login(self):
		async with aiofiles.open(self.credential_file, "r") as f:
			content = await f.read()
		config = json.loads(content)
		self.homeserver = config["homeserver"]
		self.client = AsyncClient(self.homeserver)

		self.client.access_token = config["access_token"]
		self.client.user_id = config["user_id"]
		self.client.device_id = config["device_id"]
		self.jellyfin.update({
			"url": config["jellyfin_url"],
			"api_key": config["jellyfin_api_key"]
		})

		print_with_color("Nymphali Bot est connecté en tant que " + config["user_id"], "\033[94m")

		# Callbacks
		self.client.add_event_callback(
			lambda room, event: invite_callback.invite_callback(self, room, event), InviteMemberEvent)
 
		self.client.add_event_callback(
			lambda room, event: message_callback.message_callback(self, room, event), RoomMessageText)

		while True:
			try:
				await self.client.sync_forever(timeout=30000, full_state=self.state)
			except Exception as e:
				print_with_color(f"An error occurred during sync: {e}", "\033[91m")
				self.state = False
				await asyncio.sleep(5)

async def main():
	bot = NymphaliBot(CREDENTIALS_FILE)
	await bot.login()
    
asyncio.run(main())