from nio import MatrixRoom, RoomMessageText
import httpx

import utils.utils as utils

emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

async def cmd_jellyfin_search(bot, room: MatrixRoom, event: RoomMessageText, args: list):
	if not args:
		await utils.send_msg(bot, room, "Utilisation : !jfs [requête]")
		return

	query = " ".join(args)
	params = {
		"SearchTerm": query,
		"IncludeItemTypes": "Movie,Series",
		"Limit": 5,
		"Recursive": "true",
		"api_key": bot.jellyfin["api_key"]
	}

	async with httpx.AsyncClient() as client:
		try:
			resp = await client.get(f"{bot.jellyfin['url']}/Items", params=params)
			if resp.status_code != 200:
				await utils.send_msg(bot, room, " ❌ Aucune réponse du serveur Jellyfin.")
				return

			data = resp.json()
			items = data.get("Items", [])
			if not items:
				await utils.send_msg(bot, room, f"🔍 Aucun résultat pour {query}.")
				return

			plain_text = f"🔍 Résultats pour '{query}':\n"
			html_text = f"<h4>Résultats pour '{query}':</h4><ul>"

			for num, item in enumerate(items):
				name = item.get("Name", "Inconnu")
				year = item.get("ProductionYear", "N/A")
				mtype = "🎬 Film" if item.get("Type") == "Movie" else "📺 Série"
				plain_text += f"- {emoji_list[num]} {name} ({year}) {mtype}\n"
				html_text += f"<li>{emoji_list[num]} {name} ({year}) {mtype}</li>"

			html_text += "</ul>"
			resp = await bot.client.room_send(
				room_id=room.room_id,
				message_type="m.room.message",
				content={
					"msgtype": "m.text",
					"body": plain_text,
					"format": "org.matrix.custom.html",
					"formatted_body": html_text
				}
			)

			#for num, item in enumerate(items):
			#	await bot.client.room_send(
			#		room_id=room.room_id,
			#		message_type="m.reaction",
			#		content={
			#			"m.relates_to": {
			#				"rel_type": "m.annotation",
			#				"event_id": resp.event_id,
			#				"key": emoji_list[num]
			#			}
			#		}
			#	)
		except:
			await utils.send_msg(bot, room, " ❌ Erreur d'accès au serveur Jellyfin.")