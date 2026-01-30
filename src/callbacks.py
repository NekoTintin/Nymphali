import asyncio
from time import time as tm;
from nio import MatrixRoom, RoomMessageText, InviteMemberEvent

import utils.utils as utils
from utils.command_helper import COMMANDS_LIST

async def invite_callback(bot, room: MatrixRoom, event: InviteMemberEvent):
	target_room_id = getattr(event, "room_id", None) or getattr(room, "room_id", None)

	# Already joined
	if target_room_id in bot.client.rooms:
		print(f"Déjà membre de la salle {target_room_id}, invitation ignorée.")
		return

	print(f"Invitation reçue par {event.sender} dans la salle {target_room_id}")
	print("Acceptation de l'invitation dans 5 secondes...")

	await asyncio.sleep(5)

	try:
		resp = await bot.client.join(target_room_id)
		if hasattr(resp, "room_id") and resp.room_id:
			print(f"Invitation acceptée pour la salle {target_room_id}")
			await asyncio.sleep(1)
			await bot.client.room_send(
				room_id=target_room_id,
				message_type="m.room.message",
				content={
					"msgtype": "m.text",
					"body": "Merci pour l'invitation ! Nymphali est maintenant présent dans cette salle."
				}
			)
		else:
			print(f"Échec de l'acceptation de l'invitation pour la salle {target_room_id}: {resp.message}")
	except Exception as e:
		print(f"Erreur lors de l'acceptation de l'invitation pour la salle {target_room_id}: {e}")

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