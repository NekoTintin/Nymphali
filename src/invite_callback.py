import asyncio
from nio import MatrixRoom, InviteMemberEvent

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