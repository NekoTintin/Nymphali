from time import time as tm;
from nio import MatrixRoom, RoomMessageText

from utils.command_helper import COMMANDS_LIST

async def message_callback(bot, room: MatrixRoom, event: RoomMessageText):
	# Skip les messages du bot lui-même ou trop anciens 
	if event.sender == bot.client.user_id:
		return
	if event.server_timestamp < int(tm() * 1000) - 30000:
		return

	print(f"Message reçu dans la salle {room.room_id} de {event.sender}: {event.body}")

	msg = event.body.strip()
	if msg.startswith(bot.prefix):
		cmd = msg[len(bot.prefix):].split()
		if not cmd:
			return

		cmd_name = cmd[0].lower()
		args = cmd[1:]

		func = COMMANDS_LIST.get(cmd_name, {}).get("ptr")
		if func:
			print(f"Exécution de la commande '{cmd_name}' avec les arguments {args} par {event.sender}")
			await func(bot, room, event, args)
		else:
			await bot.client.room_send(
				room_id=room.room_id,
				message_type="m.room.message",
				content={
					"msgtype": "m.text",
					"body": f"Commande inconnue: {cmd_name}"
				}
			)