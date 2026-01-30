from nio import MatrixRoom, RoomMessageText

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
