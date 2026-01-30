from nio import MatrixRoom, RoomMessageText, UploadResponse
import httpx

import utils.utils as utils

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
		"api_key": bot.jellyfin_api_key
	}

	async with httpx.AsyncClient() as client:
		try:
			resp = await client.get(f"{bot.jellyfin_url}/Items", params=params)
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

			for item in items:
				name = item.get("Name", "Inconnu")
				year = item.get("ProductionYear", "N/A")
				mtype = "🎬 Film" if item.get("Type") == "Movie" else "📺 Série"
				plain_text += f"- {name} ({year}) {mtype}\n"
				html_text += f"<li>{name} ({year}) {mtype}</li>"

			html_text += "</ul>"
			await bot.client.room_send(
				room_id=room.room_id,
				message_type="m.room.message",
				content={
					"msgtype": "m.text",
					"body": plain_text,
					"format": "org.matrix.custom.html",
					"formatted_body": html_text
				}
			)
		except:
			await utils.send_msg(bot, room, " ❌ Erreur d'accès au serveur Jellyfin.")