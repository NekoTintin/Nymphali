from nio import MatrixRoom, RoomMessageText

import utils.utils as utils
import aiohttp

async def cmd_help(bot, room: MatrixRoom, event: RoomMessageText, args: list):
	from utils.command_helper import COMMANDS_LIST
	plain_text = "Commandes disponibles :\n"
	html_text = "<h4>Commandes disponibles :</h4><ul>"

	for cmd, content in COMMANDS_LIST.items():
		plain_text += f"- {content['usage']}: {content['desc']}\n"
		html_text += f"<li><strong>{content['usage']}</strong> : {content['desc']}</li>"
    
	html_text += "</ul>"

	await bot.client.room_send(
		room_id=room.room_id,
		message_type="m.room.message",
		content={
			"msgtype": "m.text",
			"body": plain_text,
			"format": "org.matrix.custom.html",
			"formatted_body": html_text}
	)

async def cmd_ping(bot, room: MatrixRoom, event: RoomMessageText, args: list):
	await bot.client.room_send(
		room_id=room.room_id,
		message_type="m.room.message",
		content={"msgtype": "m.text", "body": "Pong !"}
	)

async def cmd_short_url(bot, room: MatrixRoom, event: RoomMessageText, args: list):
	base_url = "https://is.gd/create.php"
	long = args[0]
	params = {
		"format": "simple",
		"url": long}

	async with aiohttp.ClientSession() as session:
		async with session.get(base_url, params=params) as response:
			response.raise_for_status()
			short = await response.text()

		await utils.send_msg(bot, room, f"URL raccourcie: {short}")