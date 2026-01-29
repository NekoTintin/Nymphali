import asyncio
import json
import aiofiles
from nio import AsyncClient, MatrixRoom, RoomMessageText, InviteMemberEvent

import callbacks

CREDENTIALS_FILE = "credentials.json"

class NymphaliBot:
	def __init__(self, homeserver: str, credential_file: str=CREDENTIALS_FILE, prefix: str="?"):
		self.homeserver = homeserver
		self.credential_file = credential_file
		self.prefix = prefix
		self.client	= None
		self.state = True
		self.jellyfin_url = None
		self.jellyfin_api_key = None
 
	async def login(self):
		async with aiofiles.open(self.credential_file, "r") as f:
			content = await f.read()
		config = json.loads(content)
		self.client = AsyncClient(self.homeserver)

		self.client.access_token = config["access_token"]
		self.client.user_id = config["user_id"]
		self.client.device_id = config["device_id"]
		self.jellyfin_url = config["jellyfin_url"]
		self.jellyfin_api_key = config["jellyfin_api_key"]
 
		print("Nymphali Bot est connecté en tant que " + config["user_id"])

		# Callbacks
		self.client.add_event_callback(
			lambda room, event: callbacks.invite_callback(self, room, event), InviteMemberEvent)
 
		self.client.add_event_callback(
			lambda room, event: callbacks.message_callback(self, room, event), RoomMessageText)

		while True:
			try:
				await self.client.sync_forever(timeout=30000, full_state=self.state)
			except Exception as e:
				print(f"An error occurred during sync: {e}")
				self.state = False
				await asyncio.sleep(5)

async def main():
	bot = NymphaliBot("https://matrix.nekotintin.ovh", CREDENTIALS_FILE)
	await bot.login()
    
asyncio.run(main())