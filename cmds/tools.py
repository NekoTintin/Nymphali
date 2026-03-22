from nio import MatrixRoom, RoomMessageText, RoomMessagesResponse

import utils.utils as utils
import aiohttp
import asyncio

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

async def cmd_clear_msg(bot, room: MatrixRoom, event: RoomMessageText, args: list) -> None:
	await bot.client.room_redact(room.room_id, event.event_id, reason="Nettoyage du message de commande")
	if not args or args[0] is None:
		return
	try:
		num = int(args[0])
	except:
		return

	lim = min(num, 50)
	resp = await bot.client.room_messages(
		room.room_id,
		limit=lim,
		direction="b"
	)

	if isinstance(resp, RoomMessagesResponse):
		for msg_event in resp.chunk:
			event_type = getattr(msg_event, "type", None)
			
			if event_type == "m.room.message":
				try:
					await bot.client.room_redact(
						room.room_id,
						msg_event.event_id,
						reason="Nettoyage"
					)
				except Exception as e:
					print(f"Erreur lors de la suppression de {msg_event.event_id}: {e}")
			await asyncio.sleep(0.2)